"""セッションサービスファクトリ

環境変数に基づいて適切なセッションサービスを返す。
AGENT_ENGINE_ID が設定されている場合は VertexAiSessionService を、
未設定の場合は FirestoreSessionService をフォールバックとして返す。
"""

import logging
import os

from google.adk.sessions import BaseSessionService

from app.services.adk.sessions.firestore_session_service import FirestoreSessionService

logger = logging.getLogger(__name__)


def create_session_service() -> BaseSessionService:
    """環境変数に基づいてセッションサービスを作成する

    環境変数:
        AGENT_ENGINE_ID: Agent Engine ID（設定時は VertexAiSessionService）
        GCP_PROJECT_ID: GCP プロジェクト ID（オプション）
        GCP_LOCATION: GCP ロケーション（オプション）

    Returns:
        BaseSessionService: セッションサービスインスタンス
    """
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()

    if not agent_engine_id:
        logger.info("AGENT_ENGINE_ID not set, using FirestoreSessionService")
        return FirestoreSessionService()

    from google.adk.sessions import VertexAiSessionService

    project = os.environ.get("GCP_PROJECT_ID") or None
    location = os.environ.get("GCP_LOCATION") or None

    logger.info(
        "Using VertexAiSessionService with agent_engine_id=%s",
        agent_engine_id,
    )

    return VertexAiSessionService(
        project=project,
        location=location,
        agent_engine_id=agent_engine_id,
    )
