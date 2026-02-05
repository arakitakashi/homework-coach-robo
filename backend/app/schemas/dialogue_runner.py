"""対話ランナーのスキーマ定義

ストリーミングエンドポイント用のリクエスト/レスポンススキーマ。
"""

from pydantic import BaseModel, Field


class RunDialogueRequest(BaseModel):
    """対話実行リクエスト"""

    user_id: str = Field(..., min_length=1, description="ユーザーID")
    session_id: str = Field(..., min_length=1, description="セッションID")
    message: str = Field(..., min_length=1, description="ユーザーメッセージ")


class TextEvent(BaseModel):
    """テキストイベント（SSE用）"""

    text: str = Field(..., description="テキストチャンク")


class ErrorEvent(BaseModel):
    """エラーイベント（SSE用）"""

    error: str = Field(..., description="エラーメッセージ")
    code: str = Field(..., description="エラーコード")


class DoneEvent(BaseModel):
    """完了イベント（SSE用）"""

    session_id: str = Field(..., description="セッションID")
