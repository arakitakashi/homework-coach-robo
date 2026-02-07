"""E2Eテスト用 MockVoiceStreamingService

Gemini Live APIへの接続を行わず、定型イベントを返すモックサービス。
E2E_MODE=true 時に VoiceStreamingService の代替として使用される。
"""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.schemas.voice_stream import (
    ADKEventMessage,
    ADKTranscription,
)

# 応答待ち時間（秒）
_RESPONSE_DELAY = 0.3


class MockVoiceStreamingService:
    """E2Eテスト用モック音声ストリーミングサービス

    Gemini Live APIを呼び出さず、定型イベントを返す。
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ARG002 - DI互換のため
        self._closed = False
        self._text_queue: asyncio.Queue[str] = asyncio.Queue()

    def send_audio(self, data: bytes) -> None:  # noqa: ARG002
        """音声データを受信（E2Eモードでは無視）"""

    def send_text(self, text: str) -> None:
        """テキストメッセージを受信してキューに追加"""
        self._text_queue.put_nowait(text)

    async def receive_events(
        self,
        user_id: str,  # noqa: ARG002
        session_id: str,  # noqa: ARG002
    ) -> AsyncIterator[ADKEventMessage]:
        """定型イベントをストリーム"""
        while not self._closed:
            try:
                text = await asyncio.wait_for(self._text_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            # 入力トランスクリプション
            yield ADKEventMessage(
                author="user",
                inputTranscription=ADKTranscription(text=text, finished=True),
            )

            await asyncio.sleep(_RESPONSE_DELAY)

            # 出力トランスクリプション
            response = f"「{text}」について、いっしょに考えよう！"
            yield ADKEventMessage(
                author="model",
                outputTranscription=ADKTranscription(text=response, finished=True),
            )

            # ターン完了
            yield ADKEventMessage(
                author="model",
                turnComplete=True,
            )

    def close(self) -> None:
        """ストリーミングをクローズ"""
        self._closed = True
