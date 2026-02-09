"""対話ランナーAPIのテスト"""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient


async def async_iter(items: list[Any]) -> AsyncIterator[Any]:
    """リストをasync iteratorに変換するヘルパー"""
    for item in items:
        yield item


def create_mock_session_service() -> MagicMock:
    """モックセッションサービスを作成するヘルパー"""
    mock_service = MagicMock()
    mock_service.get_session = AsyncMock(return_value=None)
    mock_service.create_session = AsyncMock(return_value=None)
    return mock_service


def _override_deps_local_runner(
    app: Any,
    mock_runner: MagicMock,
) -> None:
    """ローカル Runner 用の依存関係オーバーライド"""
    from app.api.v1.dialogue_runner import (
        get_agent_engine_client,
        get_agent_runner_service,
        get_session_service,
    )

    app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner
    app.dependency_overrides[get_session_service] = create_mock_session_service
    app.dependency_overrides[get_agent_engine_client] = lambda: None


class TestRunDialogueEndpoint:
    """POST /api/v1/dialogue/run のテスト"""

    def test_returns_streaming_response(self) -> None:
        """ストリーミングレスポンスを返す"""
        from app.main import app

        mock_event = MagicMock()
        mock_event.content.parts = [MagicMock(text="テスト回答")]

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value="テスト回答")

        _override_deps_local_runner(app, mock_runner)

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-123",
                    "session_id": "session-456",
                    "message": "テストメッセージ",
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        finally:
            app.dependency_overrides.clear()

    def test_streams_text_events(self) -> None:
        """テキストイベントをストリームで送信する"""
        from app.main import app

        mock_event = MagicMock()
        mock_event.content.parts = [MagicMock(text="テスト")]

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value="テスト")

        _override_deps_local_runner(app, mock_runner)

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-123",
                    "session_id": "session-456",
                    "message": "テスト",
                },
            )

            content = response.text
            assert "event: text" in content
            assert '"text":"テスト"' in content
        finally:
            app.dependency_overrides.clear()

    def test_sends_done_event_on_completion(self) -> None:
        """完了時にdoneイベントを送信する"""
        from app.main import app

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([]))
        mock_runner.extract_text = MagicMock(return_value=None)

        _override_deps_local_runner(app, mock_runner)

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-123",
                    "session_id": "session-456",
                    "message": "テスト",
                },
            )

            content = response.text
            assert "event: done" in content
            assert "session-456" in content
        finally:
            app.dependency_overrides.clear()

    def test_validation_error_returns_422(self) -> None:
        """バリデーションエラーで422を返す"""
        from app.main import app

        mock_runner = MagicMock()
        _override_deps_local_runner(app, mock_runner)

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-123",
                    "session_id": "session-456",
                    "message": "",
                },
            )

            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_missing_fields_returns_422(self) -> None:
        """必須フィールド欠落で422を返す"""
        from app.main import app

        mock_runner = MagicMock()
        _override_deps_local_runner(app, mock_runner)

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-123",
                    "message": "テスト",
                },
            )

            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


class TestRunDialogueWithAgentEngine:
    """Agent Engine 使用時の POST /api/v1/dialogue/run テスト"""

    def test_uses_agent_engine_when_client_provided(self) -> None:
        """Agent Engine クライアントが提供されている場合に使用する"""
        from app.api.v1.dialogue_runner import (
            get_agent_engine_client,
            get_agent_runner_service,
            get_session_service,
        )
        from app.main import app

        async def mock_stream(
            user_id: str,  # noqa: ARG001
            session_id: str,  # noqa: ARG001
            message: str,  # noqa: ARG001
        ) -> AsyncIterator[dict[str, Any]]:
            yield {"content": {"parts": [{"text": "Agent Engine回答"}]}}

        mock_engine_client = MagicMock()
        mock_engine_client.stream_query = mock_stream
        mock_engine_client.extract_text = MagicMock(return_value="Agent Engine回答")

        mock_runner = MagicMock()

        app.dependency_overrides[get_agent_engine_client] = lambda: mock_engine_client
        app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner
        app.dependency_overrides[get_session_service] = create_mock_session_service

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-1",
                    "session_id": "session-1",
                    "message": "テスト",
                },
            )

            assert response.status_code == 200
            content = response.text
            assert "event: text" in content
            assert "Agent Engine回答" in content
            assert "event: done" in content
        finally:
            app.dependency_overrides.clear()

    def test_falls_back_to_local_runner(self) -> None:
        """Agent Engine クライアントが None の場合はローカル Runner を使用する"""
        from app.main import app

        mock_event = MagicMock()
        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value="ローカル回答")

        _override_deps_local_runner(app, mock_runner)

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/dialogue/run",
                json={
                    "user_id": "user-1",
                    "session_id": "session-1",
                    "message": "テスト",
                },
            )

            content = response.text
            assert "ローカル回答" in content
        finally:
            app.dependency_overrides.clear()


class TestAgentEngineEventGenerator:
    """Agent Engine イベントジェネレータのテスト"""

    @pytest.mark.asyncio
    async def test_generates_text_events(self) -> None:
        """テキストイベントを生成する"""
        from app.api.v1.dialogue_runner import agent_engine_event_generator

        async def mock_stream(
            user_id: str,  # noqa: ARG001
            session_id: str,  # noqa: ARG001
            message: str,  # noqa: ARG001
        ) -> AsyncIterator[dict[str, Any]]:
            yield {"content": {"parts": [{"text": "テスト回答"}]}}

        mock_client = MagicMock()
        mock_client.stream_query = mock_stream
        mock_client.extract_text = MagicMock(return_value="テスト回答")

        events = []
        async for event in agent_engine_event_generator(
            engine_client=mock_client,
            user_id="user-1",
            session_id="session-1",
            message="テスト",
        ):
            events.append(event)

        assert len(events) == 2
        assert "event: text" in events[0]
        assert "テスト回答" in events[0]
        assert "event: done" in events[1]

    @pytest.mark.asyncio
    async def test_handles_exception(self) -> None:
        """例外発生時にエラーイベントを生成する"""
        from app.api.v1.dialogue_runner import agent_engine_event_generator

        async def error_stream(
            user_id: str,  # noqa: ARG001
            session_id: str,  # noqa: ARG001
            message: str,  # noqa: ARG001
        ) -> AsyncIterator[dict[str, Any]]:
            raise RuntimeError("Agent Engine エラー")
            yield  # noqa: B901

        mock_client = MagicMock()
        mock_client.stream_query = error_stream

        events = []
        async for event in agent_engine_event_generator(
            engine_client=mock_client,
            user_id="user-1",
            session_id="session-1",
            message="テスト",
        ):
            events.append(event)

        assert len(events) == 1
        assert "event: error" in events[0]
        assert "AGENT_ENGINE_ERROR" in events[0]


class TestEventGenerator:
    """イベントジェネレータのテスト"""

    @pytest.mark.asyncio
    async def test_generates_text_events(self) -> None:
        """テキストイベントを生成する"""
        from app.api.v1.dialogue_runner import event_generator

        mock_event = MagicMock()

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value="テスト回答")

        mock_session_service = create_mock_session_service()

        events = []
        async for event in event_generator(
            runner=mock_runner,
            session_service=mock_session_service,
            user_id="user-123",
            session_id="session-456",
            message="テスト",
        ):
            events.append(event)

        # テキストイベント + doneイベント
        assert len(events) == 2
        assert "event: text" in events[0]
        assert '"text":"テスト回答"' in events[0]
        assert "event: done" in events[1]

    @pytest.mark.asyncio
    async def test_skips_empty_text(self) -> None:
        """テキストがない場合はスキップする"""
        from app.api.v1.dialogue_runner import event_generator

        mock_event = MagicMock()

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value=None)

        mock_session_service = create_mock_session_service()

        events = []
        async for event in event_generator(
            runner=mock_runner,
            session_service=mock_session_service,
            user_id="user-123",
            session_id="session-456",
            message="テスト",
        ):
            events.append(event)

        # doneイベントのみ
        assert len(events) == 1
        assert "event: done" in events[0]

    @pytest.mark.asyncio
    async def test_handles_exception(self) -> None:
        """例外発生時にエラーイベントを生成する"""
        from app.api.v1.dialogue_runner import event_generator

        async def error_generator() -> AsyncIterator[Any]:
            raise RuntimeError("テストエラー")
            yield  # noqa: B901

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=error_generator())

        mock_session_service = create_mock_session_service()

        events = []
        async for event in event_generator(
            runner=mock_runner,
            session_service=mock_session_service,
            user_id="user-123",
            session_id="session-456",
            message="テスト",
        ):
            events.append(event)

        assert len(events) == 1
        assert "event: error" in events[0]
        assert "テストエラー" in events[0]
