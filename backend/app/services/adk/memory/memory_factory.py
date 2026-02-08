"""メモリサービスファクトリ

環境変数に基づいて適切なメモリサービスを返す。
AGENT_ENGINE_ID が設定されている場合は VertexAiMemoryBankService を、
未設定の場合は FirestoreMemoryService をフォールバックとして返す。
"""

import logging
import os

from google.adk.memory import BaseMemoryService

from app.services.adk.memory.firestore_memory_service import FirestoreMemoryService

logger = logging.getLogger(__name__)


def create_memory_service() -> BaseMemoryService:
    """環境変数に基づいてメモリサービスを作成する

    環境変数:
        AGENT_ENGINE_ID: Agent Engine ID（設定時は VertexAiMemoryBankService）
        GCP_PROJECT_ID: GCP プロジェクト ID（オプション）
        GCP_LOCATION: GCP ロケーション（オプション）

    Returns:
        BaseMemoryService: メモリサービスインスタンス
    """
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()

    if not agent_engine_id:
        logger.info("AGENT_ENGINE_ID not set, using FirestoreMemoryService")
        return FirestoreMemoryService()

    from google.adk.memory import VertexAiMemoryBankService

    project = os.environ.get("GCP_PROJECT_ID") or None
    location = os.environ.get("GCP_LOCATION") or None

    logger.info(
        "Using VertexAiMemoryBankService with agent_engine_id=%s",
        agent_engine_id,
    )

    return VertexAiMemoryBankService(
        project=project,
        location=location,
        agent_engine_id=agent_engine_id,
    )
