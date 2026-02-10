"""Tests for FirestoreSessionService helper methods"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.adk.sessions.firestore_session_service import FirestoreSessionService


@pytest.fixture
def mock_firestore_client() -> MagicMock:
    """Firestoreクライアントのモック"""
    return MagicMock()


@pytest.fixture
def service(mock_firestore_client: MagicMock) -> FirestoreSessionService:
    """FirestoreSessionService インスタンス（モック付き）"""
    with patch(
        "app.services.adk.sessions.firestore_session_service.firestore.AsyncClient",
        return_value=mock_firestore_client,
    ):
        return FirestoreSessionService()


class TestListAllSessionIds:
    """Tests for list_all_session_ids method"""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_sessions(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """セッションが存在しない場合、空リストを返す"""
        # Firestoreのcollection().stream()が空のリストを返す
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = iter([])
        mock_firestore_client.collection.return_value.stream.return_value = mock_stream

        result = await service.list_all_session_ids()

        assert result == []
        mock_firestore_client.collection.assert_called_once_with("sessions")

    @pytest.mark.asyncio
    async def test_returns_all_session_ids(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """全セッションIDを返す"""
        # モックドキュメント作成
        mock_doc1 = MagicMock()
        mock_doc1.id = "session_abc123"
        mock_doc2 = MagicMock()
        mock_doc2.id = "session_def456"
        mock_doc3 = MagicMock()
        mock_doc3.id = "session_ghi789"

        # stream()が3つのドキュメントを返す
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = iter([mock_doc1, mock_doc2, mock_doc3])
        mock_firestore_client.collection.return_value.stream.return_value = mock_stream

        result = await service.list_all_session_ids()

        assert result == ["session_abc123", "session_def456", "session_ghi789"]
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_handles_large_number_of_sessions(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """大量のセッションIDを処理できる"""
        # 1000個のモックドキュメント作成
        mock_docs = [MagicMock() for _ in range(1000)]
        for i, doc in enumerate(mock_docs):
            doc.id = f"session_{i:06d}"

        # stream()が1000個のドキュメントを返す
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = iter(mock_docs)
        mock_firestore_client.collection.return_value.stream.return_value = mock_stream

        result = await service.list_all_session_ids()

        assert len(result) == 1000
        assert result[0] == "session_000000"
        assert result[999] == "session_000999"

    @pytest.mark.asyncio
    async def test_uses_correct_collection_name(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """正しいコレクション名（sessions）を使用する"""
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = iter([])
        mock_firestore_client.collection.return_value.stream.return_value = mock_stream

        await service.list_all_session_ids()

        mock_firestore_client.collection.assert_called_once_with("sessions")


class TestGetSessionDataById:
    """Tests for get_session_data_by_id method"""

    @pytest.mark.asyncio
    async def test_returns_none_when_session_not_found(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """セッションが存在しない場合、Noneを返す"""
        # ドキュメントが存在しない
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_firestore_client.collection.return_value.document.return_value.get = AsyncMock(
            return_value=mock_doc
        )

        result = await service.get_session_data_by_id("nonexistent_session")

        assert result is None
        mock_firestore_client.collection.assert_called_once_with("sessions")
        mock_firestore_client.collection.return_value.document.assert_called_once_with(
            "nonexistent_session"
        )

    @pytest.mark.asyncio
    async def test_returns_session_data_when_found(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """セッションが存在する場合、辞書データを返す"""
        # ドキュメントが存在する
        mock_doc = MagicMock()
        mock_doc.exists = True
        session_data = {
            "id": "session_123",
            "app_name": "homework_coach",
            "user_id": "user_456",
            "state": {"problem": "2 + 2 = ?"},
            "last_update_time": 1234567890.0,
        }
        mock_doc.to_dict.return_value = session_data
        mock_firestore_client.collection.return_value.document.return_value.get = AsyncMock(
            return_value=mock_doc
        )

        result = await service.get_session_data_by_id("session_123")

        assert result == session_data
        mock_firestore_client.collection.assert_called_once_with("sessions")
        mock_firestore_client.collection.return_value.document.assert_called_once_with(
            "session_123"
        )

    @pytest.mark.asyncio
    async def test_uses_correct_collection_and_document_path(
        self,
        service: FirestoreSessionService,
        mock_firestore_client: MagicMock,
    ) -> None:
        """正しいコレクション名とドキュメントパスを使用する"""
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_firestore_client.collection.return_value.document.return_value.get = AsyncMock(
            return_value=mock_doc
        )

        await service.get_session_data_by_id("test_session_id")

        mock_firestore_client.collection.assert_called_once_with("sessions")
        mock_firestore_client.collection.return_value.document.assert_called_once_with(
            "test_session_id"
        )
