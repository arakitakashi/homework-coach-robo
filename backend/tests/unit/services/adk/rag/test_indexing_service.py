"""Unit tests for IndexingService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.adk.rag.indexing_service import IndexingService
from app.services.adk.rag.models import RagDocument


class TestIndexingService:
    """Tests for IndexingService."""

    @pytest.fixture
    def service(self) -> IndexingService:
        """Create an IndexingService instance."""
        return IndexingService(corpus_name="test-corpus")

    @pytest.mark.asyncio
    async def test_index_session_memories(self, service: IndexingService) -> None:
        """Test indexing memories from a single session."""
        session_id = "session-123"

        mock_memories = [
            {
                "id": "mem-1",
                "content": "23 + 45 を自力で解けた",
                "category": "success",
                "metadata": {"subject": "math", "grade": 2},
            },
            {
                "id": "mem-2",
                "content": "繰り上がりで苦手",
                "category": "weak_area",
                "metadata": {"subject": "math", "grade": 2},
            },
        ]

        with (
            patch.object(service, "_fetch_session_memories", new_callable=AsyncMock) as mock_fetch,
            patch.object(service.corpus_service, "index_documents_batch", new_callable=AsyncMock) as mock_index,
        ):
            mock_fetch.return_value = mock_memories
            mock_index.return_value = ["mem-1", "mem-2"]

            indexed_count = await service.index_session_memories(session_id)

            assert indexed_count == 2
            mock_fetch.assert_called_once_with(session_id)
            mock_index.assert_called_once()

            # Verify RagDocument conversion
            call_args = mock_index.call_args
            documents = call_args[1]["documents"]
            assert len(documents) == 2
            assert documents[0].document_id == "mem-1"
            assert "23 + 45" in documents[0].content

    @pytest.mark.asyncio
    async def test_index_user_memories(self, service: IndexingService) -> None:
        """Test indexing all memories for a user."""
        user_id = "user-123"

        mock_sessions = ["session-1", "session-2"]
        mock_memories = [
            {
                "id": "mem-1",
                "content": "1回目の成功",
                "category": "success",
                "metadata": {},
            }
        ]

        with (
            patch.object(service, "_fetch_user_sessions", new_callable=AsyncMock) as mock_sessions_fetch,
            patch.object(service, "_fetch_session_memories", new_callable=AsyncMock) as mock_mem_fetch,
            patch.object(service.corpus_service, "index_documents_batch", new_callable=AsyncMock) as mock_index,
        ):
            mock_sessions_fetch.return_value = mock_sessions
            mock_mem_fetch.return_value = mock_memories
            mock_index.return_value = ["mem-1"]

            indexed_count = await service.index_user_memories(user_id)

            # Should index memories from 2 sessions
            assert indexed_count == 2  # 1 memory × 2 sessions
            assert mock_mem_fetch.call_count == 2

    @pytest.mark.asyncio
    async def test_index_session_memories_with_sanitization(self, service: IndexingService) -> None:
        """Test that PII is sanitized before indexing."""
        session_id = "session-123"

        mock_memories = [
            {
                "id": "mem-1",
                "content": "たろうくんが頑張った",  # Contains PII
                "category": "dialogue",
                "metadata": {},
            }
        ]

        with (
            patch.object(service, "_fetch_session_memories", new_callable=AsyncMock) as mock_fetch,
            patch.object(service.corpus_service, "index_documents_batch", new_callable=AsyncMock) as mock_index,
        ):
            mock_fetch.return_value = mock_memories
            mock_index.return_value = ["mem-1"]

            await service.index_session_memories(session_id)

            # Verify content was sanitized
            call_args = mock_index.call_args
            documents = call_args[1]["documents"]
            assert "[子供]" in documents[0].content
            assert "たろうくん" not in documents[0].content

    @pytest.mark.asyncio
    async def test_index_session_memories_empty(self, service: IndexingService) -> None:
        """Test indexing session with no memories."""
        session_id = "session-empty"

        with patch.object(service, "_fetch_session_memories", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []

            indexed_count = await service.index_session_memories(session_id)

            assert indexed_count == 0

    @pytest.mark.asyncio
    async def test_index_session_memories_updates_flag(self, service: IndexingService) -> None:
        """Test that indexed memories are flagged in Firestore."""
        session_id = "session-123"

        mock_memories = [
            {
                "id": "mem-1",
                "content": "テスト",
                "category": "dialogue",
                "metadata": {},
            }
        ]

        with (
            patch.object(service, "_fetch_session_memories", new_callable=AsyncMock) as mock_fetch,
            patch.object(service.corpus_service, "index_documents_batch", new_callable=AsyncMock) as mock_index,
            patch.object(service, "_mark_as_indexed", new_callable=AsyncMock) as mock_mark,
        ):
            mock_fetch.return_value = mock_memories
            mock_index.return_value = ["mem-1"]

            await service.index_session_memories(session_id)

            # Verify flag was updated
            mock_mark.assert_called_once_with(session_id, ["mem-1"])

    @pytest.mark.asyncio
    async def test_convert_to_rag_document(self, service: IndexingService) -> None:
        """Test conversion from Firestore document to RagDocument."""
        firestore_doc = {
            "id": "mem-1",
            "content": "算数の問題を解いた",
            "category": "dialogue",
            "metadata": {
                "user_id": "user-123",
                "subject": "math",
                "grade": 2,
                "timestamp": "2026-02-08T10:00:00Z",
            },
        }

        rag_doc = service._convert_to_rag_document(firestore_doc)

        assert isinstance(rag_doc, RagDocument)
        assert rag_doc.document_id == "mem-1"
        assert "算数" in rag_doc.content
        assert rag_doc.metadata["category"] == "dialogue"
        assert rag_doc.metadata["subject"] == "math"

    @pytest.mark.asyncio
    async def test_batch_processing(self, service: IndexingService) -> None:
        """Test that large batches are split correctly."""
        session_id = "session-large"

        # Create 150 mock memories (exceeds typical batch size of 100)
        mock_memories = [
            {
                "id": f"mem-{i}",
                "content": f"記憶 {i}",
                "category": "dialogue",
                "metadata": {},
            }
            for i in range(150)
        ]

        with (
            patch.object(service, "_fetch_session_memories", new_callable=AsyncMock) as mock_fetch,
            patch.object(service.corpus_service, "index_documents_batch", new_callable=AsyncMock) as mock_index,
        ):
            mock_fetch.return_value = mock_memories
            mock_index.return_value = [f"mem-{i}" for i in range(150)]

            indexed_count = await service.index_session_memories(session_id)

            assert indexed_count == 150
            # Should be called twice (100 + 50)
            assert mock_index.call_count == 2
