"""AgentRunnerService のテスト"""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


async def async_iter(items: list[Any]) -> AsyncIterator[Any]:
    """リストをasync iteratorに変換するヘルパー"""
    for item in items:
        yield item


class TestAgentRunnerServiceInit:
    """AgentRunnerService初期化のテスト"""

    def test_accepts_session_service(self) -> None:
        """SessionServiceを受け入れる"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        mock_session_service = MagicMock()
        mock_memory_service = MagicMock()

        with (
            patch("app.services.adk.runner.runner_service.Runner"),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=mock_session_service,
                memory_service=mock_memory_service,
            )
            assert service._session_service == mock_session_service

    def test_accepts_memory_service(self) -> None:
        """MemoryServiceを受け入れる"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        mock_session_service = MagicMock()
        mock_memory_service = MagicMock()

        with (
            patch("app.services.adk.runner.runner_service.Runner"),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=mock_session_service,
                memory_service=mock_memory_service,
            )
            assert service._memory_service == mock_memory_service

    def test_creates_runner_with_services(self) -> None:
        """Runnerを正しく初期化する"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        mock_session_service = MagicMock()
        mock_memory_service = MagicMock()
        mock_agent = MagicMock()

        with (
            patch("app.services.adk.runner.runner_service.Runner") as MockRunner,
            patch(
                "app.services.adk.runner.runner_service.create_router_agent",
                return_value=mock_agent,
            ),
        ):
            AgentRunnerService(
                session_service=mock_session_service,
                memory_service=mock_memory_service,
            )
            MockRunner.assert_called_once()
            call_kwargs = MockRunner.call_args[1]
            assert call_kwargs["session_service"] == mock_session_service
            assert call_kwargs["memory_service"] == mock_memory_service
            assert call_kwargs["agent"] == mock_agent

    def test_uses_default_app_name(self) -> None:
        """デフォルトのapp_nameを使用する"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        with (
            patch("app.services.adk.runner.runner_service.Runner") as MockRunner,
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )
            call_kwargs = MockRunner.call_args[1]
            assert call_kwargs["app_name"] == "homework-coach"

    def test_accepts_custom_app_name(self) -> None:
        """カスタムapp_nameを受け入れる"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        with (
            patch("app.services.adk.runner.runner_service.Runner") as MockRunner,
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
                app_name="custom-app",
            )
            call_kwargs = MockRunner.call_args[1]
            assert call_kwargs["app_name"] == "custom-app"


class TestAgentRunnerServiceRun:
    """AgentRunnerService.runメソッドのテスト"""

    @pytest.mark.asyncio
    async def test_sends_user_message(self) -> None:
        """ユーザーメッセージを送信できる"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        mock_runner = MagicMock()
        mock_runner.run_async = MagicMock(return_value=async_iter([]))

        with (
            patch(
                "app.services.adk.runner.runner_service.Runner",
                return_value=mock_runner,
            ),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            events = []
            async for event in service.run(
                user_id="user-123",
                session_id="session-456",
                message="テストメッセージ",
            ):
                events.append(event)

            mock_runner.run_async.assert_called_once()
            call_kwargs = mock_runner.run_async.call_args[1]
            assert call_kwargs["user_id"] == "user-123"
            assert call_kwargs["session_id"] == "session-456"

    @pytest.mark.asyncio
    async def test_streams_events(self) -> None:
        """イベントをストリームで受け取れる"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        mock_event1 = MagicMock()
        mock_event2 = MagicMock()
        mock_runner = MagicMock()
        mock_runner.run_async = MagicMock(return_value=async_iter([mock_event1, mock_event2]))

        with (
            patch(
                "app.services.adk.runner.runner_service.Runner",
                return_value=mock_runner,
            ),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            events = []
            async for event in service.run(
                user_id="user-123",
                session_id="session-456",
                message="テスト",
            ):
                events.append(event)

            assert len(events) == 2
            assert events[0] == mock_event1
            assert events[1] == mock_event2

    @pytest.mark.asyncio
    async def test_creates_content_with_message(self) -> None:
        """メッセージからContentを作成する"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        mock_runner = MagicMock()
        mock_runner.run_async = MagicMock(return_value=async_iter([]))

        with (
            patch(
                "app.services.adk.runner.runner_service.Runner",
                return_value=mock_runner,
            ),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
            patch("app.services.adk.runner.runner_service.types") as mock_types,
        ):
            mock_content = MagicMock()
            mock_types.Content.return_value = mock_content

            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            async for _ in service.run(
                user_id="user-123",
                session_id="session-456",
                message="こんにちは",
            ):
                pass

            # Contentが正しく作成されたか確認
            mock_types.Content.assert_called_once()
            call_kwargs = mock_types.Content.call_args[1]
            assert call_kwargs["role"] == "user"


class TestAgentRunnerServiceExtractText:
    """AgentRunnerService.extract_textメソッドのテスト"""

    def test_extracts_text_from_event(self) -> None:
        """イベントからテキストを抽出する"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        with (
            patch("app.services.adk.runner.runner_service.Runner"),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            mock_event = MagicMock()
            mock_event.content.parts = [MagicMock(text="テスト回答")]

            result = service.extract_text(mock_event)
            assert result == "テスト回答"

    def test_returns_none_for_no_content(self) -> None:
        """コンテンツがない場合はNoneを返す"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        with (
            patch("app.services.adk.runner.runner_service.Runner"),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            mock_event = MagicMock()
            mock_event.content = None

            result = service.extract_text(mock_event)
            assert result is None

    def test_returns_none_for_no_parts(self) -> None:
        """パーツがない場合はNoneを返す"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        with (
            patch("app.services.adk.runner.runner_service.Runner"),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            mock_event = MagicMock()
            mock_event.content.parts = None

            result = service.extract_text(mock_event)
            assert result is None

    def test_joins_multiple_text_parts(self) -> None:
        """複数のテキストパーツを結合する"""
        from app.services.adk.runner.runner_service import AgentRunnerService

        with (
            patch("app.services.adk.runner.runner_service.Runner"),
            patch("app.services.adk.runner.runner_service.create_router_agent"),
        ):
            service = AgentRunnerService(
                session_service=MagicMock(),
                memory_service=MagicMock(),
            )

            mock_event = MagicMock()
            mock_event.content.parts = [
                MagicMock(text="パート1"),
                MagicMock(text="パート2"),
            ]

            result = service.extract_text(mock_event)
            assert result == "パート1 パート2"
