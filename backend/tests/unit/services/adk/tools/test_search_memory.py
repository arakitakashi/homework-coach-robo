"""search_memory_tool のユニットテスト"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from google.adk.tools import ToolContext  # type: ignore[attr-defined]
from pytest import fixture, mark, raises

from app.services.adk.tools.search_memory import (
    RagCorpusNotFoundError,
    RagSearchError,
    search_memory_with_context,
)


@fixture
def mock_tool_context() -> ToolContext:
    """ToolContext のモック"""
    ctx = MagicMock(spec=ToolContext)
    ctx.state = {"user_id": "test_user_123"}
    return ctx


@fixture
def mock_rag_search_success() -> dict[str, Any]:
    """RAG検索成功時のレスポンスモック"""
    return {
        "memories": [
            {
                "content": "前回、繰り上がりの足し算で3回つまずいた",
                "metadata": {
                    "user_id": "test_user_123",
                    "session_id": "session_456",
                    "timestamp": "2026-02-01T10:00:00Z",
                    "memory_type": "weakness",
                    "subject": "math",
                },
                "relevance_score": 0.95,
            },
            {
                "content": "前回は自力で繰り上がりの問題を解けた",
                "metadata": {
                    "user_id": "test_user_123",
                    "session_id": "session_789",
                    "timestamp": "2026-02-02T11:00:00Z",
                    "memory_type": "success",
                    "subject": "math",
                },
                "relevance_score": 0.88,
            },
        ],
        "query": "繰り上がりの足し算",
        "total_results": 2,
    }


class TestSearchMemoryTool:
    """search_memory_tool のテストクラス"""

    @mark.asyncio
    async def test_search_memory_success(
        self,
        mock_tool_context: ToolContext,
        mock_rag_search_success: dict[str, Any],
    ) -> None:
        """RAG検索が成功する場合"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_rag_search_success

            result = await search_memory_with_context(
                query="繰り上がりの足し算",
                top_k=5,
                ctx=mock_tool_context,
            )

            assert result["query"] == "繰り上がりの足し算"
            assert result["total_results"] == 2
            assert len(result["memories"]) == 2
            assert result["memories"][0]["content"] == "前回、繰り上がりの足し算で3回つまずいた"
            assert result["memories"][0]["relevance_score"] == 0.95

            mock_search.assert_called_once_with("繰り上がりの足し算", "test_user_123", 5)

    @mark.asyncio
    async def test_search_memory_no_context(self) -> None:
        """ToolContext が None の場合はエラー"""
        with raises(ValueError, match="ToolContext is required"):
            await search_memory_with_context(
                query="繰り上がりの足し算",
                ctx=None,
            )

    @mark.asyncio
    async def test_search_memory_no_user_id(self) -> None:
        """user_id がセッション状態にない場合はエラー"""
        ctx = MagicMock(spec=ToolContext)
        ctx.state = {}  # user_id なし

        with raises(ValueError, match="user_id not found in session state"):
            await search_memory_with_context(
                query="繰り上がりの足し算",
                ctx=ctx,
            )

    @mark.asyncio
    async def test_search_memory_empty_results(
        self,
        mock_tool_context: ToolContext,
    ) -> None:
        """検索結果が空の場合"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = {
                "memories": [],
                "query": "存在しないキーワード",
                "total_results": 0,
            }

            result = await search_memory_with_context(
                query="存在しないキーワード",
                ctx=mock_tool_context,
            )

            assert result["total_results"] == 0
            assert len(result["memories"]) == 0

    @mark.asyncio
    async def test_search_memory_top_k_parameter(
        self,
        mock_tool_context: ToolContext,
    ) -> None:
        """top_k パラメータが正しく渡される"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = {
                "memories": [],
                "query": "test",
                "total_results": 0,
            }

            await search_memory_with_context(
                query="test",
                top_k=10,
                ctx=mock_tool_context,
            )

            mock_search.assert_called_once_with("test", "test_user_123", 10)

    @mark.asyncio
    async def test_search_memory_corpus_not_found(
        self,
        mock_tool_context: ToolContext,
    ) -> None:
        """Corpus が見つからない場合はエラー"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.side_effect = RagCorpusNotFoundError("Corpus not found")

            with raises(RagCorpusNotFoundError):
                await search_memory_with_context(
                    query="test",
                    ctx=mock_tool_context,
                )

    @mark.asyncio
    async def test_search_memory_rag_error(
        self,
        mock_tool_context: ToolContext,
    ) -> None:
        """RAG検索エラーが発生した場合"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.side_effect = RagSearchError("Search failed")

            with raises(RagSearchError):
                await search_memory_with_context(
                    query="test",
                    ctx=mock_tool_context,
                )

    @mark.asyncio
    async def test_search_memory_user_id_filtering(
        self,
        mock_tool_context: ToolContext,
        mock_rag_search_success: dict[str, Any],
    ) -> None:
        """user_id によるフィルタリングが正しく動作する"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_rag_search_success

            result = await search_memory_with_context(
                query="test",
                ctx=mock_tool_context,
            )

            # 全ての結果が同じ user_id を持つ
            for memory in result["memories"]:
                assert memory["metadata"]["user_id"] == "test_user_123"

    @mark.asyncio
    async def test_search_memory_relevance_score_ordering(
        self,
        mock_tool_context: ToolContext,
    ) -> None:
        """relevance_score の降順でソートされている"""
        with patch(
            "app.services.adk.tools.search_memory._search_rag",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = {
                "memories": [
                    {
                        "content": "高スコア",
                        "metadata": {"user_id": "test_user_123"},
                        "relevance_score": 0.95,
                    },
                    {
                        "content": "中スコア",
                        "metadata": {"user_id": "test_user_123"},
                        "relevance_score": 0.75,
                    },
                    {
                        "content": "低スコア",
                        "metadata": {"user_id": "test_user_123"},
                        "relevance_score": 0.60,
                    },
                ],
                "query": "test",
                "total_results": 3,
            }

            result = await search_memory_with_context(
                query="test",
                ctx=mock_tool_context,
            )

            scores = [m["relevance_score"] for m in result["memories"]]
            assert scores == [0.95, 0.75, 0.60]  # 降順
