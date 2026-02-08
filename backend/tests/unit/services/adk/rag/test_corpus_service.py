"""Unit tests for RagCorpusService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.adk.rag.corpus_service import RagCorpusService
from app.services.adk.rag.models import RagDocument, RagSearchResult


class TestRagCorpusService:
    """Tests for RagCorpusService."""

    @pytest.fixture
    def service(self) -> RagCorpusService:
        """Create a RagCorpusService instance."""
        return RagCorpusService(
            project_id="test-project",
            location="us-central1",
        )

    @pytest.mark.asyncio
    async def test_create_corpus(self, service: RagCorpusService) -> None:
        """Test creating a RAG corpus."""
        with patch("google.cloud.aiplatform.RagCorpus") as mock_rag_corpus:
            mock_instance = MagicMock()
            mock_instance.name = "projects/test-project/locations/us-central1/ragCorpora/test-corpus"
            mock_rag_corpus.create.return_value = mock_instance

            corpus_name = await service.create_corpus(
                corpus_name="test-corpus",
                description="Test corpus for unit tests",
            )

            assert corpus_name == "projects/test-project/locations/us-central1/ragCorpora/test-corpus"
            mock_rag_corpus.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_document(self, service: RagCorpusService) -> None:
        """Test indexing a single document."""
        document = RagDocument(
            document_id="test-doc-1",
            content="これは算数の問題です。",
            metadata={"subject": "math", "grade": 2},
        )

        with patch.object(service, "_index_document_api", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = "test-doc-1"

            doc_id = await service.index_document(
                corpus_name="test-corpus",
                document=document,
            )

            assert doc_id == "test-doc-1"
            mock_index.assert_called_once_with("test-corpus", document)

    @pytest.mark.asyncio
    async def test_index_documents_batch(self, service: RagCorpusService) -> None:
        """Test batch indexing multiple documents."""
        documents = [
            RagDocument(
                document_id=f"test-doc-{i}",
                content=f"ドキュメント {i}",
                metadata={"index": i},
            )
            for i in range(1, 4)
        ]

        with patch.object(service, "_index_documents_batch_api", new_callable=AsyncMock) as mock_batch:
            mock_batch.return_value = ["test-doc-1", "test-doc-2", "test-doc-3"]

            doc_ids = await service.index_documents_batch(
                corpus_name="test-corpus",
                documents=documents,
            )

            assert len(doc_ids) == 3
            assert doc_ids == ["test-doc-1", "test-doc-2", "test-doc-3"]
            mock_batch.assert_called_once_with("test-corpus", documents)

    @pytest.mark.asyncio
    async def test_search(self, service: RagCorpusService) -> None:
        """Test searching in RAG corpus."""
        with patch.object(service, "_search_api", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                RagSearchResult(
                    document_id="test-doc-1",
                    content="繰り上がりの足し算",
                    metadata={"subject": "math"},
                    relevance_score=0.95,
                ),
                RagSearchResult(
                    document_id="test-doc-2",
                    content="繰り下がりの引き算",
                    metadata={"subject": "math"},
                    relevance_score=0.82,
                ),
            ]

            results = await service.search(
                corpus_name="test-corpus",
                query="繰り上がりで苦手だったパターンは？",
                top_k=5,
            )

            assert len(results) == 2
            assert results[0].document_id == "test-doc-1"
            assert results[0].relevance_score == 0.95
            assert results[1].document_id == "test-doc-2"
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_metadata_filter(self, service: RagCorpusService) -> None:
        """Test searching with metadata filtering."""
        with patch.object(service, "_search_api", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                RagSearchResult(
                    document_id="test-doc-1",
                    content="2年生の掛け算",
                    metadata={"subject": "math", "grade": 2},
                    relevance_score=0.88,
                ),
            ]

            results = await service.search(
                corpus_name="test-corpus",
                query="掛け算",
                top_k=5,
                filter_metadata={"grade": 2},
            )

            assert len(results) == 1
            assert results[0].metadata["grade"] == 2
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_empty_results(self, service: RagCorpusService) -> None:
        """Test search returning no results."""
        with patch.object(service, "_search_api", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []

            results = await service.search(
                corpus_name="test-corpus",
                query="存在しない内容",
                top_k=5,
            )

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_relevance_threshold(self, service: RagCorpusService) -> None:
        """Test filtering results by relevance score threshold."""
        with patch.object(service, "_search_api", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                RagSearchResult(
                    document_id="test-doc-1",
                    content="高関連度コンテンツ",
                    metadata={},
                    relevance_score=0.95,
                ),
                RagSearchResult(
                    document_id="test-doc-2",
                    content="低関連度コンテンツ",
                    metadata={},
                    relevance_score=0.45,
                ),
            ]

            # Service should filter out results below threshold (0.5)
            results = await service.search(
                corpus_name="test-corpus",
                query="テスト",
                top_k=5,
                min_relevance_score=0.5,
            )

            assert len(results) == 1
            assert results[0].relevance_score >= 0.5

    @pytest.mark.asyncio
    async def test_error_handling_on_index(self, service: RagCorpusService) -> None:
        """Test error handling during indexing."""
        document = RagDocument(
            document_id="test-doc-1",
            content="テスト",
        )

        with patch.object(service, "_index_document_api", new_callable=AsyncMock) as mock_index:
            mock_index.side_effect = Exception("API Error")

            with pytest.raises(Exception) as exc_info:
                await service.index_document("test-corpus", document)

            assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_error_handling_on_search(self, service: RagCorpusService) -> None:
        """Test error handling during search."""
        with patch.object(service, "_search_api", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = Exception("Search API Error")

            with pytest.raises(Exception) as exc_info:
                await service.search("test-corpus", "クエリ")

            assert "Search API Error" in str(exc_info.value)
