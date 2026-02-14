"""音声ストリームWebSocketエンドポイントのテスト"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.voice_stream import (
    ADKContentPart,
    ADKEventMessage,
    ADKInlineData,
    ADKTranscription,
)


def create_app_with_mocks(
    _mock_streaming_service: MagicMock,
    mock_session_service: MagicMock | None = None,
) -> Any:
    """テスト用にモックを注入したFastAPIアプリを作成する"""
    from app.api.v1.voice_stream import get_memory_service, get_session_service
    from app.main import app

    if mock_session_service is None:
        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=None)
        mock_session_service.create_session = AsyncMock(return_value=None)

    app.dependency_overrides[get_session_service] = lambda: mock_session_service
    app.dependency_overrides[get_memory_service] = lambda: MagicMock()

    return app


class TestWebSocketConnection:
    """WebSocket接続のテスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_websocket_connects_successfully(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """WebSocket接続が成功する"""
        mock_service = MagicMock()

        async def empty_events(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            return
            yield  # noqa: B901 - async generator

        mock_service.receive_events = empty_events
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1"):
                pass  # 接続成功を確認
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_websocket_receives_turn_complete(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """ターン完了イベントを受信する"""
        mock_service = MagicMock()

        async def event_generator(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            yield ADKEventMessage(author="agent", turnComplete=True)

        mock_service.receive_events = event_generator
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                data = ws.receive_json()
                assert data["turnComplete"] is True
                assert data["author"] == "agent"
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_websocket_receives_transcription(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """トランスクリプションイベントを受信する"""
        mock_service = MagicMock()

        async def event_generator(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            yield ADKEventMessage(
                inputTranscription=ADKTranscription(text="テスト入力", finished=True),
            )

        mock_service.receive_events = event_generator
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                data = ws.receive_json()
                assert data["inputTranscription"]["text"] == "テスト入力"
                assert data["inputTranscription"]["finished"] is True
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_websocket_receives_audio_content(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """音声コンテンツイベントを受信する"""
        mock_service = MagicMock()

        async def event_generator(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            yield ADKEventMessage(
                author="agent",
                content={
                    "parts": [
                        ADKContentPart(
                            inlineData=ADKInlineData(mimeType="audio/pcm", data="dGVzdA==")
                        )
                    ]
                },
            )

        mock_service.receive_events = event_generator
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                data = ws.receive_json()
                assert data["content"]["parts"][0]["inlineData"]["mimeType"] == "audio/pcm"
                assert data["content"]["parts"][0]["inlineData"]["data"] == "dGVzdA=="
        finally:
            app.dependency_overrides.clear()


class TestWebSocketSendText:
    """テキストメッセージ送信のテスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_sends_text_message(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """テキストメッセージを送信する"""
        mock_service = MagicMock()

        async def event_generator(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            yield ADKEventMessage(author="agent", turnComplete=True)

        mock_service.receive_events = event_generator
        mock_service.send_text = MagicMock()
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json({"type": "text", "text": "こんにちは"})
                # ターン完了を受信して接続確認
                data = ws.receive_json()
                assert data["turnComplete"] is True
        finally:
            app.dependency_overrides.clear()


class TestWebSocketSendAudio:
    """音声データ送信のテスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_sends_binary_audio(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """バイナリ音声データを送信する"""
        mock_service = MagicMock()

        async def event_generator(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            yield ADKEventMessage(author="agent", turnComplete=True)

        mock_service.receive_events = event_generator
        mock_service.send_audio = MagicMock()
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_bytes(b"\x00\x01\x02\x03")
                data = ws.receive_json()
                assert data["turnComplete"] is True
        finally:
            app.dependency_overrides.clear()


class TestSessionCreation:
    """セッション管理のテスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_creates_session_if_not_exists(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """セッションが存在しない場合は作成する"""
        mock_service = MagicMock()

        async def empty_events(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            return
            yield  # noqa: B901

        mock_service.receive_events = empty_events
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=None)
        mock_session_service.create_session = AsyncMock(return_value=None)

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1"):
                pass

            mock_session_service.create_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_skips_session_creation_if_exists(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """セッションが存在する場合は作成しない"""
        mock_service = MagicMock()

        async def empty_events(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            return
            yield  # noqa: B901

        mock_service.receive_events = empty_events
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())
        mock_session_service.create_session = AsyncMock()

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1"):
                pass

            mock_session_service.create_session.assert_not_called()
        finally:
            app.dependency_overrides.clear()


class TestCleanup:
    """クリーンアップのテスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_closes_service_on_disconnect(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """切断時にサービスをクローズする"""
        mock_service = MagicMock()

        async def empty_events(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            return
            yield  # noqa: B901

        mock_service.receive_events = empty_events
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1"):
                pass

            mock_service.close.assert_called_once()
        finally:
            app.dependency_overrides.clear()


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_session_init_failure_sends_error_to_client(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """セッション初期化失敗時にクライアントにエラーを送信する"""
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(
            side_effect=RuntimeError("Firestore connection failed")
        )

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                data = ws.receive_json()
                assert "error" in data
                assert "セッション" in data["error"]
        finally:
            app.dependency_overrides.clear()

    def test_service_init_failure_sends_error_to_client(
        self,
    ) -> None:
        """VoiceStreamingService初期化失敗時にクライアントにエラーを送信する"""
        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        with patch(
            "app.api.v1.voice_stream.VoiceStreamingService",
            side_effect=RuntimeError("Agent creation failed"),
        ):
            app = create_app_with_mocks(MagicMock(), mock_session_service)

            try:
                client = TestClient(app)
                with client.websocket_connect("/ws/user-1/session-1") as ws:
                    data = ws.receive_json()
                    assert "error" in data
                    assert "音声サービス" in data["error"]
            finally:
                app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_agent_stream_error_sends_error_to_client(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """エージェントストリームエラー時にクライアントにエラーを送信する"""
        mock_service = MagicMock()

        async def failing_events(user_id: str, session_id: str) -> Any:  # noqa: ARG001
            raise RuntimeError("Gemini API connection failed")
            yield  # noqa: B901 - async generator

        mock_service.receive_events = failing_events
        mock_service.close = MagicMock()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                data = ws.receive_json()
                assert "error" in data
                assert "AI" in data["error"]
        finally:
            app.dependency_overrides.clear()
