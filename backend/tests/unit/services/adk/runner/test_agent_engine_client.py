"""Agent Engine クライアントのテスト

Agent Engine にデプロイされたエージェントとの通信を管理するクライアントのテスト。
"""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.adk.runner.agent_engine_client import AgentEngineClient


class TestAgentEngineClientInit:
    """初期化テスト"""

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    def test_connects_to_agent_engine(
        self,
        mock_agent_engines: MagicMock,
    ) -> None:
        """リソース名で Agent Engine に接続する"""
        mock_remote_app = MagicMock()
        mock_agent_engines.get.return_value = mock_remote_app

        client = AgentEngineClient(resource_name="projects/p/locations/l/reasoningEngines/123")

        mock_agent_engines.get.assert_called_once_with(
            "projects/p/locations/l/reasoningEngines/123"
        )
        assert client._remote_app is mock_remote_app

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    def test_stores_resource_name(
        self,
        mock_agent_engines: MagicMock,  # noqa: ARG002
    ) -> None:
        """リソース名を保持する"""
        client = AgentEngineClient(resource_name="my-resource")
        assert client.resource_name == "my-resource"


class TestCreateSession:
    """セッション作成テスト"""

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    async def test_creates_session(
        self,
        mock_agent_engines: MagicMock,
    ) -> None:
        """セッションを作成して ID を返す"""
        mock_remote_app = MagicMock()
        mock_remote_app.async_create_session = AsyncMock(
            return_value={"id": "session-abc", "user_id": "user-1"}
        )
        mock_agent_engines.get.return_value = mock_remote_app

        client = AgentEngineClient(resource_name="test-resource")
        session_id = await client.create_session(user_id="user-1")

        assert session_id == "session-abc"
        mock_remote_app.async_create_session.assert_called_once_with(user_id="user-1")


class TestStreamQuery:
    """ストリームクエリテスト"""

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    async def test_streams_events(
        self,
        mock_agent_engines: MagicMock,
    ) -> None:
        """イベントをストリームで受信する"""
        events = [
            {"content": {"parts": [{"text": "こんにちは"}]}},
            {"content": {"parts": [{"text": "何かお手伝いしましょうか？"}]}},
        ]

        async def mock_stream(**kwargs: object) -> AsyncIterator[dict[str, Any]]:  # noqa: ARG001
            for event in events:
                yield event

        mock_remote_app = MagicMock()
        mock_remote_app.async_stream_query = mock_stream
        mock_agent_engines.get.return_value = mock_remote_app

        client = AgentEngineClient(resource_name="test-resource")
        received: list[dict[str, Any]] = []
        async for event in client.stream_query(
            user_id="user-1",
            session_id="session-1",
            message="こんにちは",
        ):
            received.append(event)

        assert len(received) == 2
        assert received[0]["content"]["parts"][0]["text"] == "こんにちは"

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    async def test_passes_correct_params(
        self,
        mock_agent_engines: MagicMock,
    ) -> None:
        """正しいパラメータを渡す"""
        call_kwargs: dict[str, object] = {}

        async def mock_stream(**kwargs: object) -> AsyncIterator[dict[str, Any]]:
            call_kwargs.update(kwargs)
            return
            yield  # noqa: B027 - make it an async generator

        mock_remote_app = MagicMock()
        mock_remote_app.async_stream_query = mock_stream
        mock_agent_engines.get.return_value = mock_remote_app

        client = AgentEngineClient(resource_name="test-resource")
        async for _ in client.stream_query(
            user_id="u-1",
            session_id="s-1",
            message="テストメッセージ",
        ):
            pass

        assert call_kwargs["user_id"] == "u-1"
        assert call_kwargs["session_id"] == "s-1"
        assert call_kwargs["message"] == "テストメッセージ"


class TestExtractText:
    """テキスト抽出テスト"""

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    def test_extracts_text_from_event(
        self,
        mock_agent_engines: MagicMock,  # noqa: ARG002
    ) -> None:
        """イベントからテキストを抽出する"""
        client = AgentEngineClient(resource_name="test")
        event = {"content": {"parts": [{"text": "答えは42です"}]}}
        text = client.extract_text(event)
        assert text == "答えは42です"

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    def test_returns_none_for_no_content(
        self,
        mock_agent_engines: MagicMock,  # noqa: ARG002
    ) -> None:
        """content がない場合 None を返す"""
        client = AgentEngineClient(resource_name="test")
        assert client.extract_text({}) is None

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    def test_returns_none_for_no_text_parts(
        self,
        mock_agent_engines: MagicMock,  # noqa: ARG002
    ) -> None:
        """text パートがない場合 None を返す"""
        client = AgentEngineClient(resource_name="test")
        event = {"content": {"parts": [{"inlineData": {"data": "..."}}]}}
        assert client.extract_text(event) is None

    @patch("app.services.adk.runner.agent_engine_client.agent_engines")
    def test_joins_multiple_text_parts(
        self,
        mock_agent_engines: MagicMock,  # noqa: ARG002
    ) -> None:
        """複数のテキストパートを結合する"""
        client = AgentEngineClient(resource_name="test")
        event = {"content": {"parts": [{"text": "こんにちは"}, {"text": "世界"}]}}
        text = client.extract_text(event)
        assert text == "こんにちは 世界"
