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


def should_use_managed_session(user_id: str | None) -> bool:
    """ユーザーIDに基づいてマネージドセッションを使用するか判定する

    判定順序:
    1. AGENT_ENGINE_ID が未設定 → False
    2. user_id が None（後方互換性） → True
    3. MIGRATED_USER_IDS にユーザーIDが含まれる → True
    4. MIGRATION_PERCENTAGE によるハッシュ判定 → True/False
    5. デフォルト → False

    Args:
        user_id: ユーザーID（None の場合は段階的移行をスキップ）

    Returns:
        bool: マネージドセッションを使用する場合 True
    """
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()
    if not agent_engine_id:
        return False

    # 後方互換性: user_id が None の場合、段階的移行をスキップ
    if user_id is None:
        logger.info("user_id is None, using managed session (backward compatibility)")
        return True

    # 明示的に移行済みとマークされたユーザー
    migrated_users = os.environ.get("MIGRATED_USER_IDS", "").split(",")
    if user_id in migrated_users:
        logger.info("User %s is in MIGRATED_USER_IDS, using managed session", user_id)
        return True

    # パーセンテージベースのロールアウト
    percentage_str = os.environ.get("MIGRATION_PERCENTAGE", "0").strip()
    try:
        percentage = int(percentage_str)
    except ValueError:
        logger.warning("Invalid MIGRATION_PERCENTAGE: %s", percentage_str)
        return False

    if percentage > 0:
        user_hash = hash(user_id) % 100
        use_managed = user_hash < percentage
        logger.info(
            "User %s hash %d, percentage %d, using managed: %s",
            user_id,
            user_hash,
            percentage,
            use_managed,
        )
        return use_managed

    return False


def create_session_service(user_id: str | None = None) -> BaseSessionService:
    """環境変数とユーザーIDに基づいてセッションサービスを作成する

    Args:
        user_id: ユーザーID（段階的移行判定に使用）

    環境変数:
        AGENT_ENGINE_ID: Agent Engine ID（設定時は VertexAiSessionService）
        MIGRATED_USER_IDS: 移行済みユーザーID（カンマ区切り）
        MIGRATION_PERCENTAGE: 移行率（0-100%）
        GCP_PROJECT_ID: GCP プロジェクト ID（オプション）
        GCP_LOCATION: GCP ロケーション（オプション）

    Returns:
        BaseSessionService: セッションサービスインスタンス
    """
    if should_use_managed_session(user_id):
        return _create_vertex_ai_session_service()
    return FirestoreSessionService()


def _create_vertex_ai_session_service() -> BaseSessionService:
    """VertexAiSessionService を作成する（内部ヘルパー）

    Returns:
        BaseSessionService: VertexAiSessionService インスタンス
    """
    from google.adk.sessions import VertexAiSessionService

    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()
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
