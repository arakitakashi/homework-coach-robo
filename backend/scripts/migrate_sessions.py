#!/usr/bin/env python3
"""Firestoreセッションを Agent Engine に移行するスクリプト

Usage:
    python scripts/migrate_sessions.py [--dry-run] [--verbose]

Environment Variables:
    AGENT_ENGINE_ID: Agent Engine ID（必須）
    GCP_PROJECT_ID: GCP プロジェクト ID（オプション）
    GCP_LOCATION: GCP ロケーション（オプション）
"""

import argparse
import asyncio
import logging
import sys
from typing import Any

from app.services.adk.sessions.firestore_session_service import FirestoreSessionService
from app.services.adk.sessions.session_factory import _create_vertex_ai_session_service

logger = logging.getLogger(__name__)

# リトライ設定
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # 秒

# 並列処理設定
MAX_CONCURRENT = 10


async def migrate_single_session(
    session_id: str,
    firestore_service: FirestoreSessionService,
    vertex_service: Any,
    dry_run: bool = False,
) -> tuple[str, str]:
    """単一セッションを移行する

    Args:
        session_id: セッションID
        firestore_service: Firestoreセッションサービス
        vertex_service: VertexAiセッションサービス
        dry_run: True の場合、実際には移行しない

    Returns:
        (session_id, status): statusは "success", "failed", "skipped" のいずれか
    """
    try:
        # Firestoreからセッション読み取り
        session_data = await firestore_service.get_session_data_by_id(session_id)

        if session_data is None:
            logger.warning("Session %s not found, skipping", session_id)
            return (session_id, "skipped")

        if not dry_run:
            # Agent Engineに保存（リトライロジック付き）
            for attempt in range(MAX_RETRIES):
                try:
                    await vertex_service.store_session(session_id, session_data)
                    break
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(
                            "Failed to store session %s (attempt %d/%d): %s",
                            session_id,
                            attempt + 1,
                            MAX_RETRIES,
                            e,
                        )
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        # 最終試行でも失敗
                        raise

        logger.info("Migrated session %s", session_id)
        return (session_id, "success")

    except Exception as e:
        logger.error("Failed to migrate session %s: %s", session_id, e)
        return (session_id, "failed")


async def migrate_sessions(
    firestore_service: FirestoreSessionService | None = None,
    vertex_service: Any | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    """全セッションを移行する

    Args:
        firestore_service: Firestoreセッションサービス（テスト用）
        vertex_service: VertexAiセッションサービス（テスト用）
        dry_run: True の場合、実際には移行せず検証のみ

    Returns:
        統計情報 {"success": 10, "failed": 1, "skipped": 2}
    """
    # サービスの初期化（引数がない場合は新規作成）
    if firestore_service is None:
        firestore_service = FirestoreSessionService()
    if vertex_service is None:
        vertex_service = _create_vertex_ai_session_service()

    # Firestoreから全セッションIDを取得
    logger.info("Fetching all session IDs from Firestore...")
    session_ids = await firestore_service.list_all_session_ids()
    total = len(session_ids)
    logger.info("Found %d sessions to migrate", total)

    if total == 0:
        logger.info("No sessions to migrate")
        return {"success": 0, "failed": 0, "skipped": 0}

    # 統計情報
    stats = {"success": 0, "failed": 0, "skipped": 0}

    # 並列処理でセッションを移行
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def migrate_with_semaphore(session_id: str) -> tuple[str, str]:
        async with semaphore:
            return await migrate_single_session(
                session_id,
                firestore_service,
                vertex_service,
                dry_run,
            )

    # 全セッションを並列処理
    logger.info("Starting migration (dry_run=%s, max_concurrent=%d)", dry_run, MAX_CONCURRENT)
    results = await asyncio.gather(*[migrate_with_semaphore(sid) for sid in session_ids])

    # 結果を集計
    for _, status in results:
        stats[status] += 1

        # 進捗ログ（1000セッションごと）
        migrated = stats["success"] + stats["failed"] + stats["skipped"]
        if migrated % 1000 == 0:
            logger.info("Progress: %d/%d sessions processed", migrated, total)

    return stats


def main() -> int:
    """メイン関数

    Returns:
        終了コード（0: 成功, 1: 失敗）
    """
    # 引数パース
    parser = argparse.ArgumentParser(description="Migrate Firestore sessions to Agent Engine")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually migrating",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    # ログ設定
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 移行実行
    logger.info("Starting session migration (dry_run=%s)", args.dry_run)

    try:
        stats = asyncio.run(migrate_sessions(dry_run=args.dry_run))
    except Exception as e:
        logger.error("Migration failed: %s", e, exc_info=True)
        return 1

    # 結果サマリー
    logger.info("Migration complete:")
    logger.info("  Success: %d", stats["success"])
    logger.info("  Failed:  %d", stats["failed"])
    logger.info("  Skipped: %d", stats["skipped"])

    # 失敗があれば終了コード1
    return 1 if stats["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
