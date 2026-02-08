"""記憶検索ツール

子供の過去の学習履歴や苦手分野をセマンティック検索する。
Vertex AI RAG Engineを使用し、障害時はFirestoreにフォールバックする。
"""

import logging
import os
from typing import Any

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]
from pydantic import BaseModel, Field

from app.services.adk.memory.firestore_memory_service import FirestoreMemoryService
from app.services.adk.rag.corpus_service import RagCorpusService

logger = logging.getLogger(__name__)

# Initialize services
# Note: In production, these should be injected via dependency injection
_project_id = os.getenv("GCP_PROJECT_ID", "homework-coach-dev")
_location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
_corpus_name = os.getenv("RAG_CORPUS_NAME", "homework-coach-memory-store")

rag_corpus_service = RagCorpusService(project_id=_project_id, location=_location)
firestore_memory_service = FirestoreMemoryService()


class SearchMemoryInput(BaseModel):
    """Input schema for search_memory function."""

    query: str = Field(description="検索クエリ（日本語）")
    user_id: str = Field(description="子供のユーザーID")
    category: str | None = Field(
        default=None,
        description="カテゴリフィルタ: dialogue, weak_area, success, curriculum",
    )
    min_relevance_score: float = Field(
        default=0.5,
        description="最小関連度スコア（0.0-1.0）",
    )


async def search_memory(
    query: str,
    user_id: str,
    category: str | None = None,
    min_relevance_score: float = 0.5,
) -> str:
    """子供の過去の学習履歴や苦手分野を検索する。

    Vertex AI RAG Engineを使用してセマンティック検索を行う。
    RAGが利用できない場合はFirestoreキーワード検索にフォールバックする。

    Args:
        query: 検索クエリ（日本語）
        user_id: 子供のユーザーID
        category: カテゴリフィルタ（dialogue, weak_area, success, curriculum）
        min_relevance_score: 最小関連度スコア（0.0-1.0、デフォルト: 0.5）

    Returns:
        検索結果の要約テキスト

    Examples:
        - 「繰り上がりの足し算で苦手だったパターンは？」
        - 「前回、自力で解けた問題は？」
        - 「2年生の掛け算の学習目標は？」
    """
    return await _search_memory_with_fallback(
        SearchMemoryInput(
            query=query,
            user_id=user_id,
            category=category,
            min_relevance_score=min_relevance_score,
        )
    )


async def _search_memory_with_fallback(input_data: SearchMemoryInput) -> str:
    """Search memory with RAG → Firestore fallback logic.

    Args:
        input_data: Search input parameters

    Returns:
        Formatted search results as text
    """
    try:
        # Try Vertex AI RAG search first
        filter_metadata: dict[str, Any] = {"user_id": input_data.user_id}
        if input_data.category:
            filter_metadata["category"] = input_data.category

        results = await rag_corpus_service.search(
            corpus_name=_corpus_name,
            query=input_data.query,
            top_k=5,
            filter_metadata=filter_metadata,
            min_relevance_score=input_data.min_relevance_score,
        )

        if results:
            logger.info(
                "RAG search succeeded",
                extra={
                    "user_id": input_data.user_id,
                    "query": input_data.query[:50],
                    "count": len(results),
                },
            )
            return _format_rag_results(results)

        # No results from RAG, fallback to Firestore
        logger.warning(
            "RAG returned 0 results, falling back to Firestore",
            extra={"user_id": input_data.user_id, "query": input_data.query[:50]},
        )

    except Exception as e:
        # RAG error, fallback to Firestore
        logger.error(
            f"RAG search failed: {e}, falling back to Firestore",
            extra={"user_id": input_data.user_id, "query": input_data.query[:50]},
        )

    # Fallback to Firestore keyword search
    try:
        firestore_results = await firestore_memory_service.search(
            query=input_data.query,
            user_id=input_data.user_id,
            category=input_data.category,
        )

        if firestore_results:
            logger.info(
                "Firestore fallback search succeeded",
                extra={
                    "user_id": input_data.user_id,
                    "count": len(firestore_results),
                },
            )
            return _format_firestore_results(firestore_results)

        return "関連する学習履歴が見つかりませんでした。"

    except Exception as e:
        logger.error(
            f"Firestore fallback also failed: {e}",
            extra={"user_id": input_data.user_id},
        )
        return "検索中にエラーが発生しました。"


def _format_rag_results(results: list[Any]) -> str:
    """Format RAG search results as text.

    Args:
        results: List of RagSearchResult objects

    Returns:
        Formatted text for agent consumption
    """
    if not results:
        return "関連する学習履歴が見つかりませんでした。"

    formatted_lines = ["以下の関連する学習履歴が見つかりました：\n"]

    for i, result in enumerate(results[:3], 1):  # Top 3 results
        score_percent = int(result.relevance_score * 100)
        formatted_lines.append(
            f"{i}. {result.content} " f"（関連度: {score_percent}%）"
        )

    return "\n".join(formatted_lines)


def _format_firestore_results(results: list[dict[str, Any]]) -> str:
    """Format Firestore search results as text.

    Args:
        results: List of Firestore memory documents

    Returns:
        Formatted text for agent consumption
    """
    if not results:
        return "関連する学習履歴が見つかりませんでした。"

    formatted_lines = ["以下の関連する学習履歴が見つかりました（キーワード検索）：\n"]

    for i, result in enumerate(results[:3], 1):  # Top 3 results
        content = result.get("content", "")
        category = result.get("category", "")
        formatted_lines.append(f"{i}. {content} （カテゴリ: {category}）")

    return "\n".join(formatted_lines)


# Create the ADK FunctionTool
search_memory_tool = FunctionTool(func=search_memory)
