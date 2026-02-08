"""記憶検索ツール

Vertex AI RAG Engine を使用したセマンティック記憶検索ツール。
"""

from typing import Any

from google.adk.tools import FunctionTool, ToolContext  # type: ignore[attr-defined]

# TODO: Import aiplatform when implementing actual RAG integration
# from google.cloud import aiplatform  # type: ignore[attr-defined]


class RagSearchError(Exception):
    """RAG検索エラー"""


class RagCorpusNotFoundError(RagSearchError):
    """Corpusが見つからない"""


class RagSearchTimeoutError(RagSearchError):
    """検索タイムアウト"""


async def _search_rag(
    query: str,
    user_id: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """Vertex AI RAG で記憶を検索する

    Args:
        query: 検索クエリ
        user_id: ユーザーID
        top_k: 返却する記憶の最大数

    Returns:
        dict: {
            "memories": list[{
                "content": str,
                "metadata": dict,
                "relevance_score": float
            }],
            "query": str,
            "total_results": int
        }

    Raises:
        RagCorpusNotFoundError: Corpus が見つからない
        RagSearchError: 検索エラー
    """
    # TODO: Vertex AI RAG API との統合を実装
    # Phase 2c-2 で Corpus が作成されてから実装予定

    # 現在は空の結果を返す（テストのためのスタブ）
    return {
        "memories": [],
        "query": query,
        "total_results": 0,
    }


async def search_memory_with_context(
    query: str,
    top_k: int = 5,
    ctx: ToolContext | None = None,
) -> dict[str, Any]:
    """ToolContext経由でuser_idを取得して記憶を検索する

    Args:
        query: 検索クエリ（例: "繰り上がりの足し算"）
        top_k: 返却する記憶の最大数
        ctx: ToolContext（セッション状態へのアクセス）

    Returns:
        dict: {
            "memories": list[{
                "content": str,
                "metadata": dict,
                "relevance_score": float
            }],
            "query": str,
            "total_results": int
        }

    Raises:
        ValueError: ctx が None または user_id が見つからない
        RagSearchError: RAG検索エラー
    """
    if ctx is None:
        raise ValueError("ToolContext is required")

    user_id = ctx.state.get("user_id")
    if not user_id:
        raise ValueError("user_id not found in session state")

    # Vertex AI RAG検索を実行
    return await _search_rag(query, user_id, top_k)


# ADK FunctionTool として定義
search_memory_tool = FunctionTool(func=search_memory_with_context)
