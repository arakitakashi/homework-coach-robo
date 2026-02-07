"""音声ストリーミングサービス

ADK Runner.run_live() + LiveRequestQueueを使用した
双方向音声ストリーミングサービス。
"""

import base64
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from google.adk import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.memory import BaseMemoryService
from google.adk.runners import RunConfig  # type: ignore[attr-defined]
from google.adk.sessions import BaseSessionService
from google.genai import types

from app.schemas.voice_stream import (
    ADKContentPart,
    ADKEventMessage,
    ADKInlineData,
    ADKTranscription,
)
from app.services.adk.runner.agent import create_socratic_agent

if TYPE_CHECKING:
    from google.adk.events import Event

logger = logging.getLogger(__name__)

# Vertex AI Live API対応モデル
# Vertex AI: gemini-live-2.5-flash-native-audio
# Gemini API (非Vertex): gemini-2.5-flash-native-audio-preview-12-2025
LIVE_MODEL = "gemini-live-2.5-flash-native-audio"

# デフォルトのアプリ名
DEFAULT_APP_NAME = "homework-coach"


class VoiceStreamingService:
    """音声ストリーミングサービス

    ADK Runner.run_live() + LiveRequestQueueを使用して
    Gemini Live APIと双方向音声ストリーミングを行う。
    """

    def __init__(
        self,
        session_service: BaseSessionService,
        memory_service: BaseMemoryService,
        app_name: str = DEFAULT_APP_NAME,
    ) -> None:
        self._session_service = session_service
        self._memory_service = memory_service
        self._agent = create_socratic_agent(model=LIVE_MODEL)
        self._runner = Runner(
            app_name=app_name,
            agent=self._agent,
            session_service=session_service,
            memory_service=memory_service,
        )
        self._queue = LiveRequestQueue()  # type: ignore[no-untyped-call]
        self._run_config = RunConfig(
            response_modalities=["AUDIO"],
        )

    def send_audio(self, data: bytes) -> None:
        """音声データをGemini Live APIに送信する

        Args:
            data: PCM 16-bit 16kHz 音声バイナリデータ
        """
        blob = types.Blob(mime_type="audio/pcm", data=data)
        self._queue.send_realtime(blob)

    def send_text(self, text: str) -> None:
        """テキストメッセージをGemini Live APIに送信する

        Args:
            text: テキストメッセージ
        """
        content = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )
        self._queue.send_content(content)

    async def receive_events(
        self,
        user_id: str,
        session_id: str,
    ) -> AsyncIterator[ADKEventMessage]:
        """Gemini Live APIからイベントを受信する

        Args:
            user_id: ユーザーID
            session_id: セッションID

        Yields:
            ADKEventMessage: フロントエンド互換のイベントメッセージ
        """
        async for event in self._runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=self._queue,
            run_config=self._run_config,
        ):
            message = self._convert_event_to_message(event)
            if message is not None:
                yield message

    def _convert_event_to_message(self, event: "Event") -> ADKEventMessage | None:
        """ADK EventをフロントエンドのADKEventMessage形式に変換する

        Args:
            event: ADK Event

        Returns:
            ADKEventMessage（変換不要なイベントはNone）
        """
        has_relevant_data = False
        kwargs: dict[str, object] = {"author": event.author}

        # ターン完了
        if event.turn_complete:
            kwargs["turnComplete"] = True
            has_relevant_data = True

        # 中断
        if event.interrupted:
            kwargs["interrupted"] = True
            has_relevant_data = True

        # 入力トランスクリプション
        if event.input_transcription and event.input_transcription.text:
            kwargs["inputTranscription"] = ADKTranscription(
                text=event.input_transcription.text,
                finished=event.input_transcription.finished or False,
            )
            has_relevant_data = True

        # 出力トランスクリプション
        if event.output_transcription and event.output_transcription.text:
            kwargs["outputTranscription"] = ADKTranscription(
                text=event.output_transcription.text,
                finished=event.output_transcription.finished or False,
            )
            has_relevant_data = True

        # コンテンツ（音声データ）
        if event.content and event.content.parts:
            parts: list[ADKContentPart] = []
            for part in event.content.parts:
                if part.inline_data and part.inline_data.data:
                    b64_data = base64.b64encode(part.inline_data.data).decode("utf-8")
                    parts.append(
                        ADKContentPart(
                            inlineData=ADKInlineData(
                                mimeType=part.inline_data.mime_type or "audio/pcm",
                                data=b64_data,
                            )
                        )
                    )
                elif part.text:
                    parts.append(ADKContentPart(text=part.text))

            if parts:
                kwargs["content"] = {"parts": parts}
                has_relevant_data = True

        if not has_relevant_data:
            return None

        return ADKEventMessage(**kwargs)  # type: ignore[arg-type]

    def close(self) -> None:
        """ストリーミングをクローズする"""
        self._queue.close()  # type: ignore[no-untyped-call]
