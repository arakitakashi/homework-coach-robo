"""対話APIエンドポイント"""

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.dialogue import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnswerRequestAnalysisRequest,
    AnswerRequestAnalysisResponse,
    CreateSessionRequest,
    GenerateHintRequest,
    GenerateQuestionRequest,
    HintResponse,
    QuestionResponse,
    SessionResponse,
)
from app.services.adk.dialogue.gemini_client import GeminiClient
from app.services.adk.dialogue.manager import LLMClient, SocraticDialogueManager
from app.services.adk.dialogue.models import DialogueTone, QuestionType
from app.services.adk.dialogue.session_store import SessionStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dialogue", tags=["dialogue"])

# シングルトンのセッションストア（MVPフェーズ）
_session_store = SessionStore()

# ヒントレベル名のマッピング
_HINT_LEVEL_NAMES = {
    1: "問題理解の確認",
    2: "既習事項の想起",
    3: "部分的支援",
}


def get_session_store() -> SessionStore:
    """セッションストアを取得する"""
    return _session_store


def get_llm_client() -> LLMClient | None:
    """LLMクライアントを取得する（依存性注入用）

    環境変数からプロジェクトIDを取得し、Vertex AI経由でGeminiClientを生成します。
    プロジェクトIDが設定されていない場合はNoneを返します（フォールバック動作）。
    """
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project:
        return GeminiClient(project=project)
    return None


def get_dialogue_manager(
    llm_client: LLMClient | None = Depends(get_llm_client),
) -> SocraticDialogueManager:
    """対話マネージャを取得する（依存性注入用）"""
    return SocraticDialogueManager(llm_client=llm_client)


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="対話セッションを開始する",
)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    """新しい対話セッションを開始する"""
    store = get_session_store()
    session_id = store.create_session(
        problem=request.problem,
        child_grade=request.child_grade,
        character_type=request.character_type,
    )

    context = store.get_session(session_id)
    created_at = store.get_created_at(session_id)

    # 作成直後なので必ず存在する
    assert context is not None
    assert created_at is not None

    return SessionResponse(
        session_id=session_id,
        problem=context.problem,
        current_hint_level=context.current_hint_level,
        tone=context.tone.value,
        turns_count=len(context.turns),
        created_at=created_at,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="セッション情報を取得する",
)
async def get_session(session_id: str) -> SessionResponse:
    """セッション情報を取得する"""
    store = get_session_store()
    context = store.get_session(session_id)

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )

    created_at = store.get_created_at(session_id)

    # contextが存在する場合、created_atも必ず存在する
    assert created_at is not None

    return SessionResponse(
        session_id=session_id,
        problem=context.problem,
        current_hint_level=context.current_hint_level,
        tone=context.tone.value,
        turns_count=len(context.turns),
        created_at=created_at,
    )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="セッションを終了する",
)
async def delete_session(session_id: str) -> None:
    """セッションを終了（削除）する"""
    store = get_session_store()
    result = store.delete_session(session_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )


@router.post(
    "/sessions/{session_id}/analyze",
    response_model=AnalyzeResponse,
    summary="子供の回答を分析する",
)
async def analyze_response(
    session_id: str,
    request: AnalyzeRequest,
    manager: SocraticDialogueManager = Depends(get_dialogue_manager),
) -> AnalyzeResponse:
    """子供の回答を分析し、次のアクションを推奨する"""
    import json

    store = get_session_store()
    context = store.get_session(session_id)

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )

    # 答えリクエストを検出（キーワードベースのみ、LLMなし）
    answer_request = manager._detect_answer_request_keywords(request.child_response)

    # デフォルト値（フォールバック用）
    understanding_level = 5
    is_correct_direction = True
    needs_clarification = False
    key_insights: list[str] = []

    # LLMクライアントがある場合はLLMで分析
    if manager._llm_client is not None:
        try:
            analysis = await manager.analyze_response(request.child_response, context)
            understanding_level = analysis.understanding_level
            is_correct_direction = analysis.is_correct_direction
            needs_clarification = analysis.needs_clarification
            key_insights = analysis.key_insights
        except (ValueError, json.JSONDecodeError, RuntimeError) as e:
            # LLMエラー時はフォールバック
            logger.warning(f"LLM analysis failed, using fallback: {e}")

    # 質問タイプとトーンを決定
    recommended_question_type = QuestionType.UNDERSTANDING_CHECK.value
    recommended_tone = DialogueTone.ENCOURAGING.value

    # ヒントレベルを進めるべきか判定
    should_advance = context.current_hint_level < 3 and len(context.turns) >= 2

    return AnalyzeResponse(
        understanding_level=understanding_level,
        is_correct_direction=is_correct_direction,
        needs_clarification=needs_clarification,
        key_insights=key_insights,
        recommended_question_type=recommended_question_type,
        recommended_tone=recommended_tone,
        should_advance_hint_level=should_advance,
        answer_request_detected=answer_request.request_type.value != "none",
        answer_request_type=answer_request.request_type.value,
    )


@router.post(
    "/sessions/{session_id}/question",
    response_model=QuestionResponse,
    summary="質問を生成する",
)
async def generate_question(
    session_id: str,
    request: GenerateQuestionRequest,
    manager: SocraticDialogueManager = Depends(get_dialogue_manager),
) -> QuestionResponse:
    """次の質問を生成する"""
    store = get_session_store()
    context = store.get_session(session_id)

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )

    # 質問タイプとトーンを決定（指定されていない場合はデフォルト）
    question_type_str = request.question_type or QuestionType.UNDERSTANDING_CHECK.value
    tone_str = request.tone or DialogueTone.ENCOURAGING.value

    # テンプレート（フォールバック用）
    question_templates = {
        QuestionType.UNDERSTANDING_CHECK.value: "この問題は何を聞いていると思う？",
        QuestionType.THINKING_GUIDE.value: "もし○○だったらどうなるかな？",
        QuestionType.HINT.value: "前に似たような問題をやったよね？",
    }

    # LLMクライアントがある場合はLLMで生成
    question = question_templates.get(question_type_str, "この問題について考えてみよう")

    if manager._llm_client is not None:
        try:
            question_type = QuestionType(question_type_str)
            tone = DialogueTone(tone_str)
            question = await manager.generate_question(context, question_type, tone)
        except (ValueError, RuntimeError) as e:
            # LLMエラー時はフォールバック
            logger.warning(f"LLM question generation failed, using fallback: {e}")

    return QuestionResponse(
        question=question,
        question_type=question_type_str,
        tone=tone_str,
    )


@router.post(
    "/sessions/{session_id}/hint",
    response_model=HintResponse,
    summary="ヒントを生成する",
)
async def generate_hint(
    session_id: str,
    request: GenerateHintRequest,
    manager: SocraticDialogueManager = Depends(get_dialogue_manager),
) -> HintResponse:
    """ヒントを生成する"""
    store = get_session_store()
    context = store.get_session(session_id)

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )

    # ヒントレベルを決定
    hint_level = request.force_level or context.current_hint_level

    # テンプレート（フォールバック用）
    hint_templates = {
        1: "この問題は何を聞いていると思う？",
        2: "前に似たような問題をやったよね？思い出してみよう。",
        3: "じゃあ、最初のステップだけ一緒にやろう。",
    }

    hint = hint_templates.get(hint_level, "一緒に考えてみよう")
    is_answer_request_response = False

    # LLMクライアントがある場合はLLMで生成
    if manager._llm_client is not None:
        try:
            # ヒントレベルをコンテキストに反映
            context.current_hint_level = hint_level
            hint = await manager.generate_hint_response(
                context,
                is_answer_request=request.is_answer_request,
            )
            is_answer_request_response = request.is_answer_request
        except (ValueError, RuntimeError) as e:
            # LLMエラー時はフォールバック
            logger.warning(f"LLM hint generation failed, using fallback: {e}")

    hint_level_name = _HINT_LEVEL_NAMES.get(hint_level, "不明")

    return HintResponse(
        hint=hint,
        hint_level=hint_level,
        hint_level_name=hint_level_name,
        is_answer_request_response=is_answer_request_response,
    )


@router.post(
    "/analyze-answer-request",
    response_model=AnswerRequestAnalysisResponse,
    summary="答えリクエストを検出する",
)
async def analyze_answer_request(
    request: AnswerRequestAnalysisRequest,
    manager: SocraticDialogueManager = Depends(get_dialogue_manager),
) -> AnswerRequestAnalysisResponse:
    """子供の発言から答えリクエストを検出する（セッション不要）"""
    # キーワードベースの検出（LLMクライアントがあればLLM補助も使用）
    analysis = await manager.detect_answer_request(request.child_response)

    return AnswerRequestAnalysisResponse(
        request_type=analysis.request_type.value,
        confidence=analysis.confidence,
        detected_phrases=analysis.detected_phrases,
    )
