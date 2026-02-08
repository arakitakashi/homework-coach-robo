"""Unit tests for search_memory_tool."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.adk.tools.search_memory import (
    SearchMemoryInput,
    _search_memory_with_fallback,
)


class TestSearchMemoryTool:
    """Tests for search_memory_tool functionality."""

    @pytest.mark.asyncio
    async def test_search_memory_with_rag_success(self) -> None:
        """Test successful search using RAG."""
        with patch("app.services.adk.tools.search_memory.rag_corpus_service") as mock_service:
            mock_service.search = AsyncMock()
            mock_service.search.return_value = [
                type(
                    "RagSearchResult",
                    (),
                    {
                        "content": "繰り上がりの足し算で3回つまずいた",
                        "metadata": {"subject": "math"},
                        "relevance_score": 0.92,
                    },
                )()
            ]

            result = await _search_memory_with_fallback(
                SearchMemoryInput(
                    query="繰り上がりで苦手だったパターンは？",
                    user_id="user-123",
                )
            )

            assert "検索結果が見つかりました" in result
            assert "繰り上がり" in result
            mock_service.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_memory_rag_empty_fallback_to_firestore(self) -> None:
        """Test fallback to Firestore when RAG returns empty results."""
        with (
            patch("app.services.adk.tools.search_memory.rag_corpus_service") as mock_rag,
            patch("app.services.adk.tools.search_memory.firestore_memory_service") as mock_fs,
        ):
            # RAG returns empty
            mock_rag.search = AsyncMock(return_value=[])

            # Firestore returns results
            mock_fs.search = AsyncMock()
            mock_fs.search.return_value = [
                {"content": "Firestoreからの結果", "category": "weak_area"}
            ]

            result = await _search_memory_with_fallback(
                SearchMemoryInput(
                    query="テストクエリ",
                    user_id="user-123",
                )
            )

            # Should fallback to Firestore
            assert "Firestore" in result or "結果" in result
            mock_fs.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_memory_rag_error_fallback_to_firestore(self) -> None:
        """Test fallback to Firestore when RAG fails with error."""
        with (
            patch("app.services.adk.tools.search_memory.rag_corpus_service") as mock_rag,
            patch("app.services.adk.tools.search_memory.firestore_memory_service") as mock_fs,
        ):
            # RAG raises exception
            mock_rag.search = AsyncMock(side_effect=Exception("RAG API Error"))

            # Firestore returns results
            mock_fs.search = AsyncMock()
            mock_fs.search.return_value = [
                {"content": "Firestoreフォールバック結果", "category": "dialogue"}
            ]

            result = await _search_memory_with_fallback(
                SearchMemoryInput(
                    query="テストクエリ",
                    user_id="user-123",
                )
            )

            # Should fallback to Firestore without raising error
            assert "結果" in result
            mock_fs.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_memory_both_empty(self) -> None:
        """Test when both RAG and Firestore return no results."""
        with (
            patch("app.services.adk.tools.search_memory.rag_corpus_service") as mock_rag,
            patch("app.services.adk.tools.search_memory.firestore_memory_service") as mock_fs,
        ):
            mock_rag.search = AsyncMock(return_value=[])
            mock_fs.search = AsyncMock(return_value=[])

            result = await _search_memory_with_fallback(
                SearchMemoryInput(
                    query="存在しない内容",
                    user_id="user-123",
                )
            )

            assert "見つかりませんでした" in result or "ありません" in result

    @pytest.mark.asyncio
    async def test_search_memory_filters_low_relevance(self) -> None:
        """Test that low relevance results are filtered out."""
        with patch("app.services.adk.tools.search_memory.rag_corpus_service") as mock_service:
            mock_service.search = AsyncMock()
            mock_service.search.return_value = [
                type(
                    "RagSearchResult",
                    (),
                    {
                        "content": "高関連度コンテンツ",
                        "metadata": {},
                        "relevance_score": 0.85,
                    },
                )(),
                type(
                    "RagSearchResult",
                    (),
                    {
                        "content": "低関連度コンテンツ",
                        "metadata": {},
                        "relevance_score": 0.3,
                    },
                )(),
            ]

            result = await _search_memory_with_fallback(
                SearchMemoryInput(
                    query="テスト",
                    user_id="user-123",
                    min_relevance_score=0.5,
                )
            )

            # Should only include high relevance content
            assert "高関連度" in result
            assert "低関連度" not in result

    @pytest.mark.asyncio
    async def test_search_memory_with_category_filter(self) -> None:
        """Test searching with category metadata filter."""
        with patch("app.services.adk.tools.search_memory.rag_corpus_service") as mock_service:
            mock_service.search = AsyncMock()
            mock_service.search.return_value = [
                type(
                    "RagSearchResult",
                    (),
                    {
                        "content": "苦手分野の結果",
                        "metadata": {"category": "weak_area"},
                        "relevance_score": 0.88,
                    },
                )()
            ]

            result = await _search_memory_with_fallback(
                SearchMemoryInput(
                    query="苦手分野",
                    user_id="user-123",
                    category="weak_area",
                )
            )

            assert "苦手分野" in result
            # Verify that search was called with category filter
            call_args = mock_service.search.call_args
            assert call_args is not None
            filter_metadata = call_args.kwargs.get("filter_metadata", {})
            assert filter_metadata.get("category") == "weak_area"
