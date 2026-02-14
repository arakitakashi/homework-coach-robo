"""WebSocket画像イベント（start_with_image）のテスト

Issue #152: 画像認識結果を使ったセッション開始のWebSocketイベントハンドラ。
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.schemas.voice_stream import ADKEventMessage


def create_app_with_mocks(
    mock_streaming_service: MagicMock,  # noqa: ARG001 - 既存テストとのAPI互換性維持
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


def _make_mock_service(
    events: list[ADKEventMessage] | None = None,
) -> MagicMock:
    """テスト用のVoiceStreamingServiceモックを作成する

    Args:
        events: エージェントから返すイベントリスト（Noneの場合は空）
    """
    mock_service = MagicMock()

    if events is None:
        # 空のasyncジェネレータ
        async def empty_events(
            user_id: str,  # noqa: ARG001
            session_id: str,  # noqa: ARG001
        ) -> Any:
            return
            yield  # noqa: B901 - async generator
    else:
        # 指定イベントを返すasyncジェネレータ
        async def empty_events(
            user_id: str,  # noqa: ARG001
            session_id: str,  # noqa: ARG001
        ) -> Any:
            for event in events:
                yield event

    mock_service.receive_events = empty_events
    mock_service.send_text = MagicMock()
    mock_service.send_audio = MagicMock()
    mock_service.close = MagicMock()

    return mock_service


class TestStartWithImageSuccess:
    """start_with_image 正常系テスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_sends_image_problem_confirmed(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """start_with_image 受信時に image_problem_confirmed を返す"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "3 + 5 = ?",
                            "problem_type": "math",
                        },
                    }
                )
                data = ws.receive_json()
                assert data["type"] == "image_problem_confirmed"
                assert "payload" in data
                assert "problem_id" in data["payload"]
                assert data["payload"]["problem_id"]  # 空でない
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_sends_problem_text_to_agent(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """start_with_image 受信時に問題テキストをエージェントに転送する"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "3 + 5 = ?",
                            "problem_type": "math",
                        },
                    }
                )
                ws.receive_json()  # confirmed を消費

            # send_textが問題テキストを含むメッセージで呼ばれたことを確認
            mock_service.send_text.assert_called_once()
            sent_text = mock_service.send_text.call_args[0][0]
            assert "3 + 5 = ?" in sent_text
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_includes_problem_type_in_agent_message(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """エージェントへの転送メッセージに問題タイプが含まれる"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "漢字を書きましょう",
                            "problem_type": "writing",
                        },
                    }
                )
                ws.receive_json()  # confirmed を消費

            sent_text = mock_service.send_text.call_args[0][0]
            assert "writing" in sent_text or "国語" in sent_text
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_confirmed_includes_coach_response(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """image_problem_confirmed に coach_response が含まれる"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "3 + 5 = ?",
                            "problem_type": "math",
                        },
                    }
                )
                data = ws.receive_json()
                assert "coach_response" in data["payload"]
                assert data["payload"]["coach_response"]  # 空でない
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_optional_image_url(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """image_url はオプショナルで、含まれても正常に処理される"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "3 + 5 = ?",
                            "problem_type": "math",
                            "image_url": "gs://bucket/image.jpg",
                            "metadata": {"source": "camera"},
                        },
                    }
                )
                data = ws.receive_json()
                assert data["type"] == "image_problem_confirmed"
        finally:
            app.dependency_overrides.clear()


class TestStartWithImageError:
    """start_with_image エラー系テスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_missing_payload_returns_error(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """payload 欠落時に image_recognition_error を返す"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        # payload なし
                    }
                )
                data = ws.receive_json()
                assert data["type"] == "image_recognition_error"
                assert data["payload"]["code"] == "INVALID_PAYLOAD"
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_empty_problem_text_returns_error(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """problem_text が空の場合に image_recognition_error を返す"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "",
                            "problem_type": "math",
                        },
                    }
                )
                data = ws.receive_json()
                assert data["type"] == "image_recognition_error"
                assert data["payload"]["code"] == "INVALID_PAYLOAD"
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_missing_problem_text_returns_error(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """problem_text フィールド欠落時に image_recognition_error を返す"""
        mock_service = _make_mock_service()
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_type": "math",
                        },
                    }
                )
                data = ws.receive_json()
                assert data["type"] == "image_recognition_error"
                assert data["payload"]["code"] == "INVALID_PAYLOAD"
        finally:
            app.dependency_overrides.clear()

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_agent_send_failure_returns_error(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """エージェントへの転送失敗時に image_recognition_error を返す"""
        mock_service = _make_mock_service()
        mock_service.send_text = MagicMock(side_effect=RuntimeError("Agent connection failed"))
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json(
                    {
                        "type": "start_with_image",
                        "payload": {
                            "problem_text": "3 + 5 = ?",
                            "problem_type": "math",
                        },
                    }
                )
                data = ws.receive_json()
                assert data["type"] == "image_recognition_error"
                assert data["payload"]["code"] == "AGENT_ERROR"
        finally:
            app.dependency_overrides.clear()


class TestStartWithImageCoexistence:
    """既存テキストメッセージとの共存テスト"""

    @patch("app.api.v1.voice_stream.VoiceStreamingService")
    def test_text_messages_still_work(
        self,
        mock_service_cls: MagicMock,
    ) -> None:
        """既存のテキストメッセージ処理が引き続き動作する"""
        mock_service = _make_mock_service(
            events=[ADKEventMessage(author="agent", turnComplete=True)]
        )
        mock_service_cls.return_value = mock_service

        mock_session_service = MagicMock()
        mock_session_service.get_session = AsyncMock(return_value=MagicMock())

        app = create_app_with_mocks(mock_service, mock_session_service)

        try:
            client = TestClient(app)
            with client.websocket_connect("/ws/user-1/session-1") as ws:
                ws.send_json({"type": "text", "text": "こんにちは"})
                data = ws.receive_json()
                assert data["turnComplete"] is True
        finally:
            app.dependency_overrides.clear()
