"""音声ストリーミングサービスのテスト"""

import base64
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.voice_stream import (
    ADKEventMessage,
)
from app.services.voice.streaming_service import (
    DEFAULT_APP_NAME,
    LIVE_MODEL,
    VoiceStreamingService,
)


def create_mock_event(
    *,
    author: str = "agent",
    turn_complete: bool | None = None,
    interrupted: bool | None = None,
    input_transcription: Any = None,
    output_transcription: Any = None,
    content: Any = None,
    partial: bool | None = None,
    usage_metadata: Any = None,
) -> MagicMock:
    """テスト用のモックEventを作成する"""
    event = MagicMock()
    event.author = author
    event.turn_complete = turn_complete
    event.interrupted = interrupted
    event.input_transcription = input_transcription
    event.output_transcription = output_transcription
    event.content = content
    event.partial = partial
    event.usage_metadata = usage_metadata
    # Phase 2: 属性を明示的に None に設定
    event.tool_execution = None
    event.agent_transition = None
    event.emotion_update = None
    return event


def create_mock_transcription(text: str, finished: bool) -> MagicMock:
    """テスト用のモックTranscriptionを作成する"""
    transcription = MagicMock()
    transcription.text = text
    transcription.finished = finished
    return transcription


def create_mock_content_with_audio(audio_bytes: bytes) -> MagicMock:
    """音声データ付きのモックContentを作成する"""
    blob = MagicMock()
    blob.mime_type = "audio/pcm"
    blob.data = audio_bytes

    part = MagicMock()
    part.inline_data = blob
    part.text = None

    content = MagicMock()
    content.parts = [part]
    return content


class TestVoiceStreamingServiceInit:
    """VoiceStreamingService初期化のテスト"""

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_creates_runner_with_correct_config(
        self,
        mock_create_agent: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        """Runnerが正しい設定で作成される"""
        mock_session_service = MagicMock()
        mock_memory_service = MagicMock()
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        service = VoiceStreamingService(
            session_service=mock_session_service,
            memory_service=mock_memory_service,
        )

        mock_create_agent.assert_called_once_with(model=LIVE_MODEL)
        mock_runner_cls.assert_called_once_with(
            app_name=DEFAULT_APP_NAME,
            agent=mock_agent,
            session_service=mock_session_service,
            memory_service=mock_memory_service,
        )
        assert service is not None

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_custom_app_name(
        self,
        _mock_create_agent: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        """カスタムアプリ名を指定できる"""
        VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
            app_name="custom-app",
        )

        mock_runner_cls.assert_called_once()
        call_kwargs = mock_runner_cls.call_args[1]
        assert call_kwargs["app_name"] == "custom-app"


class TestSendAudio:
    """send_audioメソッドのテスト"""

    @patch("app.services.voice.streaming_service.LiveRequestQueue")
    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_sends_blob_to_queue(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
        mock_queue_cls: MagicMock,
    ) -> None:
        """音声データをBlobとしてキューに送信する"""
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        audio_data = b"\x00\x01\x02\x03"
        service.send_audio(audio_data)

        mock_queue.send_realtime.assert_called_once()
        call_args = mock_queue.send_realtime.call_args
        blob = call_args[0][0]
        assert blob.mime_type == "audio/pcm"
        assert blob.data == audio_data


class TestSendText:
    """send_textメソッドのテスト"""

    @patch("app.services.voice.streaming_service.LiveRequestQueue")
    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_sends_content_to_queue(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
        mock_queue_cls: MagicMock,
    ) -> None:
        """テキストをContentとしてキューに送信する"""
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        service.send_text("こんにちは")

        mock_queue.send_content.assert_called_once()
        call_args = mock_queue.send_content.call_args
        content = call_args[0][0]
        assert content.role == "user"
        assert content.parts[0].text == "こんにちは"


class TestClose:
    """closeメソッドのテスト"""

    @patch("app.services.voice.streaming_service.LiveRequestQueue")
    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_closes_queue(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
        mock_queue_cls: MagicMock,
    ) -> None:
        """キューをクローズする"""
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        service.close()

        mock_queue.close.assert_called_once()


class TestConvertEventToMessage:
    """_convert_event_to_messageメソッドのテスト"""

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_turn_complete(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """ターン完了イベントを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(author="agent", turn_complete=True)
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.turnComplete is True
        assert result.author == "agent"

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_interrupted(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """中断イベントを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(interrupted=True)
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.interrupted is True

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_input_transcription(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """入力トランスクリプションを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        transcription = create_mock_transcription("ユーザー入力", True)
        event = create_mock_event(input_transcription=transcription)
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.inputTranscription is not None
        assert result.inputTranscription.text == "ユーザー入力"
        assert result.inputTranscription.finished is True

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_output_transcription(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """出力トランスクリプションを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        transcription = create_mock_transcription("AI応答", False)
        event = create_mock_event(output_transcription=transcription)
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.outputTranscription is not None
        assert result.outputTranscription.text == "AI応答"
        assert result.outputTranscription.finished is False

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_audio_content(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """音声コンテンツをbase64エンコードして変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        audio_bytes = b"\x00\x01\x02\x03"
        content = create_mock_content_with_audio(audio_bytes)
        event = create_mock_event(author="agent", content=content)
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.content is not None
        assert len(result.content["parts"]) == 1

        part = result.content["parts"][0]
        assert part.inlineData is not None
        assert part.inlineData.mimeType == "audio/pcm"
        expected_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        assert part.inlineData.data == expected_b64

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_skips_usage_metadata_events(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """usage_metadataのみのイベントはスキップする"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            usage_metadata=MagicMock(),
            turn_complete=None,
            interrupted=None,
            input_transcription=None,
            output_transcription=None,
            content=None,
        )
        result = service._convert_event_to_message(event)

        assert result is None

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_skips_partial_events_without_content(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """コンテンツのないpartialイベントはスキップする"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            partial=True,
            turn_complete=None,
            interrupted=None,
            input_transcription=None,
            output_transcription=None,
            content=None,
        )
        result = service._convert_event_to_message(event)

        assert result is None


class TestReceiveEvents:
    """receive_eventsメソッドのテスト"""

    @pytest.mark.asyncio
    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    async def test_yields_converted_events(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """変換されたイベントをyieldする"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        # run_liveがasync generatorを返すようモック
        turn_complete_event = create_mock_event(author="agent", turn_complete=True)

        async def mock_run_live(**_kwargs: Any) -> Any:
            yield turn_complete_event

        service._runner.run_live = mock_run_live  # type: ignore[method-assign]

        events: list[ADKEventMessage] = []
        async for event in service.receive_events(user_id="user-1", session_id="session-1"):
            events.append(event)

        assert len(events) == 1
        assert events[0].turnComplete is True

    @pytest.mark.asyncio
    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    async def test_skips_non_convertible_events(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """変換不可能なイベントはスキップする"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        # usage_metadataのみのイベント（変換不可）
        skip_event = create_mock_event(
            usage_metadata=MagicMock(),
            turn_complete=None,
            interrupted=None,
            input_transcription=None,
            output_transcription=None,
            content=None,
        )
        # turnCompleteイベント（変換可）
        valid_event = create_mock_event(author="agent", turn_complete=True)

        async def mock_run_live(**_kwargs: Any) -> Any:
            yield skip_event
            yield valid_event

        service._runner.run_live = mock_run_live  # type: ignore[method-assign]

        events: list[ADKEventMessage] = []
        async for event in service.receive_events(user_id="user-1", session_id="session-1"):
            events.append(event)

        assert len(events) == 1
        assert events[0].turnComplete is True


class TestConstants:
    """定数のテスト"""

    def test_live_model(self) -> None:
        """Live APIモデル名が正しい"""
        assert LIVE_MODEL == "gemini-live-2.5-flash-native-audio"

    def test_default_app_name(self) -> None:
        """デフォルトアプリ名が正しい"""
        assert DEFAULT_APP_NAME == "homework-coach"
