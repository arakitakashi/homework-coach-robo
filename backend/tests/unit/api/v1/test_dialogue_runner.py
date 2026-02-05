"""対話ランナーAPIのテスト"""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


async def async_iter(items: list[Any]) -> AsyncIterator[Any]:
    """リストをasync iteratorに変換するヘルパー"""
    for item in items:
        yield item


class TestRunDialogueEndpoint:
    """POST /api/v1/dialogue/run のテスト"""

    def test_returns_streaming_response(self) -> None:
        """ストリーミングレスポンスを返す"""
        from app.api.v1.dialogue_runner import get_agent_runner_service
        from app.main import app

        # AgentRunnerServiceをモック
        mock_event = MagicMock()
        mock_event.content.parts = [MagicMock(text="テスト回答")]

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value="テスト回答")

        # FastAPIのdependency_overridesを使用
        app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner

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
        from app.api.v1.dialogue_runner import get_agent_runner_service
        from app.main import app

        mock_event = MagicMock()
        mock_event.content.parts = [MagicMock(text="テスト")]

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([mock_event]))
        mock_runner.extract_text = MagicMock(return_value="テスト")

        app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner

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
        from app.api.v1.dialogue_runner import get_agent_runner_service
        from app.main import app

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=async_iter([]))
        mock_runner.extract_text = MagicMock(return_value=None)

        app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner

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
        from app.api.v1.dialogue_runner import get_agent_runner_service
        from app.main import app

        mock_runner = MagicMock()
        app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner

        try:
            client = TestClient(app)

            # 空のmessage
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
        from app.api.v1.dialogue_runner import get_agent_runner_service
        from app.main import app

        mock_runner = MagicMock()
        app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner

        try:
            client = TestClient(app)

            # session_idが欠落
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

        events = []
        async for event in event_generator(
            runner=mock_runner,
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

        events = []
        async for event in event_generator(
            runner=mock_runner,
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

        async def error_generator():
            raise RuntimeError("テストエラー")
            yield  # noqa: B901

        mock_runner = MagicMock()
        mock_runner.run = MagicMock(return_value=error_generator())

        events = []
        async for event in event_generator(
            runner=mock_runner,
            user_id="user-123",
            session_id="session-456",
            message="テスト",
        ):
            events.append(event)

        assert len(events) == 1
        assert "event: error" in events[0]
        assert "テストエラー" in events[0]
