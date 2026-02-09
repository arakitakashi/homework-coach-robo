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
