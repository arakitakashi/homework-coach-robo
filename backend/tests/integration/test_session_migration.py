"""Integration tests for session migration script"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from scripts.migrate_sessions import migrate_sessions


class TestMigrateSessions:
    """Tests for migrate_sessions function"""

    @pytest.mark.asyncio
    async def test_migrate_sessions_success(self) -> None:
        """正常な移行フローを確認"""
        # モックセッションサービス作成
        mock_firestore_service = MagicMock()
        mock_firestore_service.list_all_session_ids = AsyncMock(
            return_value=["session_1", "session_2", "session_3"]
        )
        mock_firestore_service.get_session_data_by_id = AsyncMock(
            side_effect=[
                {"id": "session_1", "user_id": "user1", "state": {}},
                {"id": "session_2", "user_id": "user2", "state": {}},
                {"id": "session_3", "user_id": "user3", "state": {}},
            ]
        )

        mock_vertex_service = MagicMock()
        mock_vertex_service.store_session = AsyncMock()

        # 移行実行（dry_run=False）
        stats = await migrate_sessions(
            firestore_service=mock_firestore_service,
            vertex_service=mock_vertex_service,
            dry_run=False,
        )

        # 期待結果の確認
        assert stats["success"] == 3
        assert stats["failed"] == 0
        assert stats["skipped"] == 0
        assert mock_vertex_service.store_session.call_count == 3

    @pytest.mark.asyncio
    async def test_migrate_sessions_dry_run(self) -> None:
        """dry-runモードで実際の移行を行わないことを確認"""
        mock_firestore_service = MagicMock()
        mock_firestore_service.list_all_session_ids = AsyncMock(
            return_value=["session_1", "session_2"]
        )
        mock_firestore_service.get_session_data_by_id = AsyncMock(
            side_effect=[
                {"id": "session_1", "user_id": "user1", "state": {}},
                {"id": "session_2", "user_id": "user2", "state": {}},
            ]
        )

        mock_vertex_service = MagicMock()
        mock_vertex_service.store_session = AsyncMock()

        # 移行実行（dry_run=True）
        stats = await migrate_sessions(
            firestore_service=mock_firestore_service,
            vertex_service=mock_vertex_service,
            dry_run=True,
        )

        # dry-runなのでstore_sessionは呼ばれない
        assert mock_vertex_service.store_session.call_count == 0
        assert stats["success"] == 2  # dry-runでも成功としてカウント

    @pytest.mark.asyncio
    async def test_migrate_sessions_skip_missing(self) -> None:
        """存在しないセッションをスキップすることを確認"""
        mock_firestore_service = MagicMock()
        mock_firestore_service.list_all_session_ids = AsyncMock(
            return_value=["session_1", "session_2", "session_3"]
        )
        # session_2は存在しない（Noneを返す）
        mock_firestore_service.get_session_data_by_id = AsyncMock(
            side_effect=[
                {"id": "session_1", "user_id": "user1", "state": {}},
                None,  # session_2は存在しない
                {"id": "session_3", "user_id": "user3", "state": {}},
            ]
        )

        mock_vertex_service = MagicMock()
        mock_vertex_service.store_session = AsyncMock()

        # 移行実行
        stats = await migrate_sessions(
            firestore_service=mock_firestore_service,
            vertex_service=mock_vertex_service,
            dry_run=False,
        )

        # 期待結果の確認
        assert stats["success"] == 2
        assert stats["skipped"] == 1
        assert stats["failed"] == 0
        assert mock_vertex_service.store_session.call_count == 2

    @pytest.mark.asyncio
    async def test_migrate_sessions_retry_on_failure(self) -> None:
        """失敗時のリトライ動作を確認"""
        mock_firestore_service = MagicMock()
        mock_firestore_service.list_all_session_ids = AsyncMock(return_value=["session_1"])
        mock_firestore_service.get_session_data_by_id = AsyncMock(
            return_value={"id": "session_1", "user_id": "user1", "state": {}}
        )

        mock_vertex_service = MagicMock()
        # 最初の2回は失敗、3回目で成功
        mock_vertex_service.store_session = AsyncMock(
            side_effect=[
                Exception("Temporary error"),
                Exception("Temporary error"),
                None,  # 3回目で成功
            ]
        )

        # 移行実行
        stats = await migrate_sessions(
            firestore_service=mock_firestore_service,
            vertex_service=mock_vertex_service,
            dry_run=False,
        )

        # 3回目で成功したことを確認
        assert stats["success"] == 1
        assert stats["failed"] == 0
        assert mock_vertex_service.store_session.call_count == 3
