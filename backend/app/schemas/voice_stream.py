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


class TextInputMessage(BaseModel):
    """クライアントからのテキスト入力メッセージ"""

    type: Literal["text"]
    text: str
