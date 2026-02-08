"""Indexing service for batch processing Firestore memories to RAG Corpus."""

import logging
from typing import Any

from app.services.adk.memory.firestore_memory_service import FirestoreMemoryService
from app.services.adk.rag.corpus_service import RagCorpusService
from app.services.adk.rag.models import RagDocument, sanitize_content

logger = logging.getLogger(__name__)

# Batch size for indexing (Vertex AI RAG API limit)
BATCH_SIZE = 100


class IndexingService:
    """Service for batch indexing Firestore memories to RAG Corpus.

    This service retrieves memories from Firestore and indexes them into
    Vertex AI RAG Corpus for semantic search.

    Attributes:
        corpus_name: Name of the target RAG Corpus
        corpus_service: RagCorpusService instance
        memory_service: FirestoreMemoryService instance
    """

    def __init__(
        self,
        corpus_name: str,
        corpus_service: RagCorpusService | None = None,
        memory_service: FirestoreMemoryService | None = None,
    ) -> None:
        """Initialize the indexing service.

        Args:
            corpus_name: Name of the RAG Corpus
            corpus_service: Optional RagCorpusService instance (for testing)
            memory_service: Optional FirestoreMemoryService instance (for testing)
        """
        self.corpus_name = corpus_name
        self.corpus_service = corpus_service or RagCorpusService(
            project_id="homework-coach-dev",  # TODO: from env
            location="us-central1",
        )
        self.memory_service = memory_service or FirestoreMemoryService()

    async def index_session_memories(self, session_id: str) -> int:
        """Index all memories from a single session.

        Args:
            session_id: Session ID to index

        Returns:
            Number of memories indexed

        Raises:
            Exception: If indexing fails
        """
        try:
            # Fetch memories from Firestore
            memories = await self._fetch_session_memories(session_id)

            if not memories:
                logger.info(
                    "No memories to index",
                    extra={"session_id": session_id},
                )
                return 0

            # Convert to RagDocuments with PII sanitization
            documents = [self._convert_to_rag_document(mem) for mem in memories]

            # Batch index
            indexed_count = 0
            for i in range(0, len(documents), BATCH_SIZE):
                batch = documents[i : i + BATCH_SIZE]

                doc_ids = await self.corpus_service.index_documents_batch(
                    corpus_name=self.corpus_name,
                    documents=batch,
                )

                indexed_count += len(doc_ids)

                # Mark as indexed in Firestore
                await self._mark_as_indexed(session_id, doc_ids)

                logger.info(
                    f"Indexed batch {i // BATCH_SIZE + 1}",
                    extra={
                        "session_id": session_id,
                        "batch_size": len(batch),
                        "total_indexed": indexed_count,
                    },
                )

            logger.info(
                "Session indexing complete",
                extra={
                    "session_id": session_id,
                    "total_indexed": indexed_count,
                },
            )
            return indexed_count

        except Exception as e:
            logger.error(
                f"Failed to index session memories: {e}",
                extra={"session_id": session_id},
            )
            raise

    async def index_user_memories(self, user_id: str) -> int:
        """Index all memories for a user across all sessions.

        Args:
            user_id: User ID to index

        Returns:
            Total number of memories indexed

        Raises:
            Exception: If indexing fails
        """
        try:
            # Fetch all sessions for user
            session_ids = await self._fetch_user_sessions(user_id)

            if not session_ids:
                logger.info("No sessions found for user", extra={"user_id": user_id})
                return 0

            total_indexed = 0
            for session_id in session_ids:
                count = await self.index_session_memories(session_id)
                total_indexed += count

            logger.info(
                "User indexing complete",
                extra={
                    "user_id": user_id,
                    "sessions_processed": len(session_ids),
                    "total_indexed": total_indexed,
                },
            )
            return total_indexed

        except Exception as e:
            logger.error(
                f"Failed to index user memories: {e}",
                extra={"user_id": user_id},
            )
            raise

    def _convert_to_rag_document(self, firestore_doc: dict[str, Any]) -> RagDocument:
        """Convert Firestore memory document to RagDocument.

        Args:
            firestore_doc: Firestore document dict

        Returns:
            RagDocument with sanitized content
        """
        content = firestore_doc.get("content", "")

        # Sanitize PII before indexing
        sanitized_content = sanitize_content(content)

        # Extract metadata
        metadata = firestore_doc.get("metadata", {})
        metadata["category"] = firestore_doc.get("category", "")

        return RagDocument(
            document_id=firestore_doc["id"],
            content=sanitized_content,
            metadata=metadata,
        )

    async def _fetch_session_memories(self, session_id: str) -> list[dict[str, Any]]:
        """Fetch all memories from a session.

        Args:
            session_id: Session ID

        Returns:
            List of Firestore memory documents

        Note:
            This is a stub implementation. In production, this should query
            Firestore's sessions/{session_id}/memories collection.
        """
        # TODO: Implement actual Firestore query
        # Example:
        # return await self.memory_service.get_session_memories(session_id)

        logger.info(
            "Fetching session memories (stub)",
            extra={"session_id": session_id},
        )
        return []

    async def _fetch_user_sessions(self, user_id: str) -> list[str]:
        """Fetch all session IDs for a user.

        Args:
            user_id: User ID

        Returns:
            List of session IDs

        Note:
            This is a stub implementation. In production, this should query
            Firestore's sessions collection filtered by user_id.
        """
        # TODO: Implement actual Firestore query
        # Example:
        # return await self.memory_service.get_user_sessions(user_id)

        logger.info(
            "Fetching user sessions (stub)",
            extra={"user_id": user_id},
        )
        return []

    async def _mark_as_indexed(self, session_id: str, document_ids: list[str]) -> None:
        """Mark memories as indexed in Firestore.

        Updates the 'rag_indexed' flag to avoid re-indexing.

        Args:
            session_id: Session ID
            document_ids: List of memory document IDs to mark

        Note:
            This is a stub implementation. In production, this should update
            Firestore documents with {rag_indexed: true, rag_document_id: id}.
        """
        # TODO: Implement actual Firestore update
        # Example:
        # for doc_id in document_ids:
        #     await self.memory_service.update_memory(
        #         session_id, doc_id, {"rag_indexed": True}
        #     )

        logger.info(
            "Marked memories as indexed (stub)",
            extra={
                "session_id": session_id,
                "count": len(document_ids),
            },
        )
