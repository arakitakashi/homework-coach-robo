"""対話APIエンドポイント"""

from fastapi import APIRouter, HTTPException, status

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
from app.services.adk.dialogue.manager import SocraticDialogueManager
from app.services.adk.dialogue.models import DialogueTone, QuestionType
from app.services.adk.dialogue.session_store import SessionStore

router = APIRouter(prefix="/dialogue", tags=["dialogue"])

# シングルトンのセッションストアとマネージャ（MVPフェーズ）
_session_store = SessionStore()
_dialogue_manager = SocraticDialogueManager()

# ヒントレベル名のマッピング
_HINT_LEVEL_NAMES = {
    1: "問題理解の確認",
    2: "既習事項の想起",
    3: "部分的支援",
}


def get_session_store() -> SessionStore:
    """セッションストアを取得する"""
    return _session_store


def get_dialogue_manager() -> SocraticDialogueManager:
    """対話マネージャを取得する"""
    return _dialogue_manager


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
async def analyze_response(session_id: str, request: AnalyzeRequest) -> AnalyzeResponse:
    """子供の回答を分析し、次のアクションを推奨する"""
    store = get_session_store()
    manager = get_dialogue_manager()
    context = store.get_session(session_id)

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )

    # 答えリクエストを検出（キーワードベースのみ、LLMなし）
    answer_request = manager._detect_answer_request_keywords(request.child_response)

    # MVPフェーズ: シンプルなルールベースの分析
    # LLM統合は後続フェーズで実装
    understanding_level = 5  # デフォルト中間値
    is_correct_direction = True
    needs_clarification = False

    # 質問タイプとトーンを決定
    recommended_question_type = QuestionType.UNDERSTANDING_CHECK.value
    recommended_tone = DialogueTone.ENCOURAGING.value

    # ヒントレベルを進めるべきか判定
    should_advance = context.current_hint_level < 3 and len(context.turns) >= 2

    return AnalyzeResponse(
        understanding_level=understanding_level,
        is_correct_direction=is_correct_direction,
        needs_clarification=needs_clarification,
        key_insights=[],
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
async def generate_question(session_id: str, request: GenerateQuestionRequest) -> QuestionResponse:
    """次の質問を生成する"""
    store = get_session_store()
    context = store.get_session(session_id)

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "セッションが見つかりません"},
        )

    # 質問タイプとトーンを決定（指定されていない場合はデフォルト）
    question_type = request.question_type or QuestionType.UNDERSTANDING_CHECK.value
    tone = request.tone or DialogueTone.ENCOURAGING.value

    # MVPフェーズ: テンプレートベースの質問生成
    # LLM統合は後続フェーズで実装
    question_templates = {
        QuestionType.UNDERSTANDING_CHECK.value: "この問題は何を聞いていると思う？",
        QuestionType.THINKING_GUIDE.value: "もし○○だったらどうなるかな？",
        QuestionType.HINT.value: "前に似たような問題をやったよね？",
    }

    question = question_templates.get(question_type, "この問題について考えてみよう")

    return QuestionResponse(
        question=question,
        question_type=question_type,
        tone=tone,
    )


@router.post(
    "/sessions/{session_id}/hint",
    response_model=HintResponse,
    summary="ヒントを生成する",
)
async def generate_hint(session_id: str, request: GenerateHintRequest) -> HintResponse:
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

    # MVPフェーズ: テンプレートベースのヒント生成
    hint_templates = {
        1: "この問題は何を聞いていると思う？",
        2: "前に似たような問題をやったよね？思い出してみよう。",
        3: "じゃあ、最初のステップだけ一緒にやろう。",
    }

    hint = hint_templates.get(hint_level, "一緒に考えてみよう")
    hint_level_name = _HINT_LEVEL_NAMES.get(hint_level, "不明")

    return HintResponse(
        hint=hint,
        hint_level=hint_level,
        hint_level_name=hint_level_name,
        is_answer_request_response=False,
    )


@router.post(
    "/analyze-answer-request",
    response_model=AnswerRequestAnalysisResponse,
    summary="答えリクエストを検出する",
)
async def analyze_answer_request(
    request: AnswerRequestAnalysisRequest,
) -> AnswerRequestAnalysisResponse:
    """子供の発言から答えリクエストを検出する（セッション不要）"""
    manager = get_dialogue_manager()

    # キーワードベースの検出
    analysis = manager._detect_answer_request_keywords(request.child_response)

    return AnswerRequestAnalysisResponse(
        request_type=analysis.request_type.value,
        confidence=analysis.confidence,
        detected_phrases=analysis.detected_phrases,
    )
