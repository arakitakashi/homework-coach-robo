"""対話関連のAPIスキーマ"""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """セッション作成リクエスト"""

    problem: str = Field(..., min_length=1, description="問題文")
    child_grade: int = Field(..., ge=1, le=3, description="学年（1-3）")
    character_type: str | None = Field(
        default=None, description="キャラクタータイプ（robot, wizard, astronaut）"
    )


class SessionResponse(BaseModel):
    """セッション情報レスポンス"""

    session_id: str = Field(..., description="セッションID")
    problem: str = Field(..., description="問題文")
    current_hint_level: int = Field(..., ge=1, le=3, description="現在のヒントレベル")
    tone: str = Field(..., description="対話トーン")
    turns_count: int = Field(..., ge=0, description="ターン数")
    created_at: datetime = Field(..., description="作成日時")


class AnalyzeRequest(BaseModel):
    """回答分析リクエスト"""

    child_response: str = Field(..., min_length=1, description="子供の回答")


class AnalyzeResponse(BaseModel):
    """回答分析レスポンス"""

    understanding_level: int = Field(..., ge=0, le=10, description="理解度（0-10）")
    is_correct_direction: bool = Field(..., description="正しい方向に向かっているか")
    needs_clarification: bool = Field(..., description="追加説明が必要か")
    key_insights: list[str] = Field(default_factory=list, description="重要な気づき")
    recommended_question_type: str = Field(..., description="推奨される質問タイプ")
    recommended_tone: str = Field(..., description="推奨される対話トーン")
    should_advance_hint_level: bool = Field(..., description="ヒントレベルを進めるべきか")
    answer_request_detected: bool = Field(..., description="答えリクエストが検出されたか")
    answer_request_type: str = Field(
        default="none", description="答えリクエストタイプ（none, explicit, implicit）"
    )


class GenerateQuestionRequest(BaseModel):
    """質問生成リクエスト"""

    question_type: str | None = Field(
        default=None,
        description="質問タイプ（未指定時は自動決定）",
    )
    tone: str | None = Field(
        default=None,
        description="対話トーン（未指定時は自動決定）",
    )


class QuestionResponse(BaseModel):
    """質問生成レスポンス"""

    question: str = Field(..., description="生成された質問")
    question_type: str = Field(..., description="使用した質問タイプ")
    tone: str = Field(..., description="使用した対話トーン")


class GenerateHintRequest(BaseModel):
    """ヒント生成リクエスト"""

    force_level: int | None = Field(
        default=None,
        ge=1,
        le=3,
        description="強制的に指定するヒントレベル（未指定時は現在レベル）",
    )
    is_answer_request: bool = Field(
        default=False,
        description="答えリクエストへの対応かどうか",
    )


class HintResponse(BaseModel):
    """ヒント生成レスポンス"""

    hint: str = Field(..., description="生成されたヒント")
    hint_level: int = Field(..., ge=1, le=3, description="ヒントレベル（1-3）")
    hint_level_name: str = Field(..., description="ヒントレベル名")
    is_answer_request_response: bool = Field(..., description="答えリクエストへの対応かどうか")


class AnswerRequestAnalysisRequest(BaseModel):
    """答えリクエスト分析リクエスト"""

    child_response: str = Field(..., min_length=1, description="子供の発言")


class AnswerRequestAnalysisResponse(BaseModel):
    """答えリクエスト分析レスポンス"""

    request_type: str = Field(..., description="リクエストタイプ（none, explicit, implicit）")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度（0.0-1.0）")
    detected_phrases: list[str] = Field(default_factory=list, description="検出されたフレーズ")
