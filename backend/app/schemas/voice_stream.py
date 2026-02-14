"""音声ストリームWebSocketメッセージスキーマ

フロントエンドVoiceWebSocketClientとの互換性を持つADKEvent形式を定義。
"""

from typing import Literal

from pydantic import BaseModel


class ADKTranscription(BaseModel):
    """トランスクリプション（音声→テキスト変換結果）"""

    text: str
    finished: bool


class ADKInlineData(BaseModel):
    """インラインデータ（音声バイナリなど）"""

    mimeType: str
    data: str


class ADKContentPart(BaseModel):
    """コンテンツパート（テキストまたはインラインデータ）"""

    text: str | None = None
    inlineData: ADKInlineData | None = None


class ADKToolExecutionEvent(BaseModel):
    """Phase 2a: ツール実行イベント"""

    toolName: str
    status: str
    result: dict[str, object] | None = None


class ADKAgentTransitionEvent(BaseModel):
    """Phase 2b: エージェント遷移イベント"""

    fromAgent: str
    toAgent: str
    reason: str


class ADKEmotionUpdateEvent(BaseModel):
    """Phase 2d: 感情更新イベント"""

    emotion: str
    frustrationLevel: float
    engagementLevel: float


class ADKEventMessage(BaseModel):
    """サーバーからクライアントへのADKイベントメッセージ

    フロントエンドのADKEvent型と互換性を持つJSON形式。
    """

    author: str | None = None
    turnComplete: bool | None = None
    interrupted: bool | None = None
    inputTranscription: ADKTranscription | None = None
    outputTranscription: ADKTranscription | None = None
    content: dict[str, list[ADKContentPart]] | None = None
    # Phase 2: Additional event fields
    toolExecution: ADKToolExecutionEvent | None = None
    agentTransition: ADKAgentTransitionEvent | None = None
    emotionUpdate: ADKEmotionUpdateEvent | None = None


class TextInputMessage(BaseModel):
    """クライアントからのテキスト入力メッセージ"""

    type: Literal["text"]
    text: str


# --- 画像イベント関連スキーマ（Issue #152） ---


class StartWithImagePayload(BaseModel):
    """start_with_image イベントのペイロード

    フロントエンドから画像認識済みの問題データを受け取る。
    """

    problem_text: str
    problem_type: str
    image_url: str | None = None
    metadata: dict[str, object] | None = None


class ImageProblemConfirmedPayload(BaseModel):
    """image_problem_confirmed レスポンスのペイロード"""

    problem_id: str
    coach_response: str


class ImageProblemConfirmedMessage(BaseModel):
    """サーバー → クライアント: 画像問題確認レスポンス"""

    type: Literal["image_problem_confirmed"] = "image_problem_confirmed"
    payload: ImageProblemConfirmedPayload


class ImageRecognitionErrorPayload(BaseModel):
    """image_recognition_error レスポンスのペイロード"""

    error: str
    code: str


class ImageRecognitionErrorMessage(BaseModel):
    """サーバー → クライアント: 画像認識エラーレスポンス"""

    type: Literal["image_recognition_error"] = "image_recognition_error"
    payload: ImageRecognitionErrorPayload
