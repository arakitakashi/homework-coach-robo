"""画像認識関連のAPIスキーマ

宿題プリント画像のアップロード・認識に使用するリクエスト/レスポンス定義。
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RecognitionType(str, Enum):
    """認識タイプ"""

    HOMEWORK_PROBLEM = "homework_problem"
    HANDWRITING = "handwriting"
    DIAGRAM = "diagram"


class RecognizeImageRequest(BaseModel):
    """画像認識リクエスト"""

    image: str = Field(..., min_length=1, description="base64エンコードされた画像データ")
    recognition_type: RecognitionType = Field(
        default=RecognitionType.HOMEWORK_PROBLEM,
        description="認識タイプ",
    )
    expected_subject: str | None = Field(default=None, description="予想される教科")


class ProblemDetail(BaseModel):
    """認識された問題の詳細"""

    text: str = Field(..., description="問題文のテキスト")
    type: str = Field(
        ..., description="問題タイプ（arithmetic, word_problem, kanji, reading, other）"
    )
    difficulty: int = Field(..., description="難易度")
    expression: str | None = Field(default=None, description="計算式（算数の場合のみ）")


class RecognizeImageResponse(BaseModel):
    """画像認識成功レスポンス"""

    success: bool = Field(..., description="認識成功フラグ")
    problems: list[ProblemDetail] = Field(..., description="認識された問題リスト")
    confidence: float = Field(..., ge=0.0, le=1.0, description="認識の信頼度（0.0-1.0）")
    needs_confirmation: bool = Field(..., description="子供に確認が必要かどうか")


class RecognizeImageErrorResponse(BaseModel):
    """画像認識エラーレスポンス"""

    success: bool = Field(default=False, description="常にFalse")
    error_type: str = Field(
        ...,
        description="エラータイプ（recognition_failed, low_confidence, invalid_image, image_too_large）",
    )
    message: str = Field(..., description="エラーメッセージ")
    suggestions: list[str] = Field(default_factory=list, description="改善提案")
