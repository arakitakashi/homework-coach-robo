"""FirestoreSessionServiceのテスト"""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.sessions.base_session_service import GetSessionConfig
from google.adk.sessions.session import Session

from app.services.adk.sessions.firestore_session_service import (
    FirestoreSessionService,
)


async def async_iter(items: list[Any]) -> AsyncIterator[Any]:
    """リストをasync iteratorに変換するヘルパー"""
    for item in items:
        yield item


@pytest.fixture
def mock_firestore_client() -> MagicMock:
    """モックFirestoreクライアント"""
    return MagicMock()


@pytest.fixture
def service(mock_firestore_client: MagicMock) -> FirestoreSessionService:
    """テスト用FirestoreSessionService"""
    with patch(
        "app.services.adk.sessions.firestore_session_service.firestore.AsyncClient",
        return_value=mock_firestore_client,
    ):
        return FirestoreSessionService()


def create_mock_doc(exists: bool, data: dict[str, Any] | None = None) -> MagicMock:
    """モックドキュメントを作成するヘルパー"""
    mock_doc = MagicMock()
    mock_doc.exists = exists
    if data:
        mock_doc.to_dict.return_value = data
    return mock_doc


class TestCreateSession:
    """create_sessionメソッドのテスト"""

    async def test_creates_new_session(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """新規セッションを作成"""
        # Arrange
        mock_doc = create_mock_doc(exists=False)
        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)
        mock_doc_ref.set = AsyncMock()

        # app_state と user_state 用のモック（存在しない）
        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_doc_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        session = await service.create_session(
            app_name="homework_coach",
            user_id="user-123",
            state={"problem": "1+1=?"},
            session_id="session-456",
        )

        # Assert
        assert session.id == "session-456"
        assert session.app_name == "homework_coach"
        assert session.user_id == "user-123"
        assert session.state["problem"] == "1+1=?"
        mock_doc_ref.set.assert_called_once()

    async def test_creates_session_with_generated_id(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """session_id未指定でUUIDを生成"""
        # Arrange
        mock_doc = create_mock_doc(exists=False)
        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)
        mock_doc_ref.set = AsyncMock()

        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_doc_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        session = await service.create_session(
            app_name="homework_coach",
            user_id="user-123",
        )

        # Assert
        assert session.id != ""
        assert len(session.id) == 36  # UUID format

    async def test_raises_error_on_duplicate_session_id(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """既存のsession_idで作成するとAlreadyExistsError"""
        # Arrange
        mock_doc = create_mock_doc(exists=True)

        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)

        mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

        # Act & Assert
        with pytest.raises(AlreadyExistsError):
            await service.create_session(
                app_name="homework_coach",
                user_id="user-123",
                session_id="existing-session",
            )

    async def test_extracts_app_state_on_create(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """app:プレフィックスの状態をapp_stateコレクションに保存"""
        # Arrange
        mock_doc = create_mock_doc(exists=False)
        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)
        mock_doc_ref.set = AsyncMock()

        mock_app_state_ref = MagicMock()
        mock_app_state_ref.set = AsyncMock()
        mock_app_state_ref.get = AsyncMock(
            return_value=create_mock_doc(exists=True, data={"version": "1.0"})
        )

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_doc_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        session = await service.create_session(
            app_name="homework_coach",
            user_id="user-123",
            state={"app:version": "1.0", "problem": "1+1=?"},
            session_id="session-456",
        )

        # Assert
        mock_app_state_ref.set.assert_called()
        # マージ後のセッションにapp:versionが含まれる
        assert session.state.get("app:version") == "1.0"

    async def test_extracts_user_state_on_create(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """user:プレフィックスの状態をuser_stateコレクションに保存"""
        # Arrange
        mock_doc = create_mock_doc(exists=False)
        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)
        mock_doc_ref.set = AsyncMock()

        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_ref = MagicMock()
        mock_user_state_ref.set = AsyncMock()
        mock_user_state_ref.get = AsyncMock(
            return_value=create_mock_doc(exists=True, data={"name": "太郎"})
        )

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_doc_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        session = await service.create_session(
            app_name="homework_coach",
            user_id="user-123",
            state={"user:name": "太郎", "problem": "1+1=?"},
            session_id="session-456",
        )

        # Assert
        mock_user_state_ref.set.assert_called()
        assert session.state.get("user:name") == "太郎"


class TestGetSession:
    """get_sessionメソッドのテスト"""

    async def test_gets_existing_session(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """存在するセッションを取得"""
        # Arrange
        mock_session_doc = create_mock_doc(
            exists=True,
            data={
                "id": "session-123",
                "app_name": "homework_coach",
                "user_id": "user-456",
                "state": {"problem": "1+1=?"},
                "last_update_time": 1234567890.0,
            },
        )

        mock_session_ref = MagicMock()
        mock_session_ref.get = AsyncMock(return_value=mock_session_doc)

        # events サブコレクション（空）
        mock_events_query = MagicMock()
        mock_events_query.stream.return_value = async_iter([])
        mock_events_collection = MagicMock()
        mock_events_collection.order_by.return_value = mock_events_query
        mock_session_ref.collection.return_value = mock_events_collection

        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_session_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        session = await service.get_session(
            app_name="homework_coach",
            user_id="user-456",
            session_id="session-123",
        )

        # Assert
        assert session is not None
        assert session.id == "session-123"
        assert session.state["problem"] == "1+1=?"

    async def test_returns_none_for_nonexistent_session(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """存在しないセッションにはNoneを返す"""
        # Arrange
        mock_doc = create_mock_doc(exists=False)

        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)

        mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

        # Act
        session = await service.get_session(
            app_name="homework_coach",
            user_id="user-456",
            session_id="nonexistent",
        )

        # Assert
        assert session is None

    async def test_merges_app_and_user_state(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """app状態とuser状態をセッション状態にマージ"""
        # Arrange
        mock_session_doc = create_mock_doc(
            exists=True,
            data={
                "id": "session-123",
                "app_name": "homework_coach",
                "user_id": "user-456",
                "state": {"problem": "1+1=?"},
                "last_update_time": 0.0,
            },
        )

        mock_session_ref = MagicMock()
        mock_session_ref.get = AsyncMock(return_value=mock_session_doc)

        mock_events_query = MagicMock()
        mock_events_query.stream.return_value = async_iter([])
        mock_events_collection = MagicMock()
        mock_events_collection.order_by.return_value = mock_events_query
        mock_session_ref.collection.return_value = mock_events_collection

        mock_app_state_doc = create_mock_doc(exists=True, data={"version": "1.0"})
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=True, data={"name": "太郎"})
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_session_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        session = await service.get_session(
            app_name="homework_coach",
            user_id="user-456",
            session_id="session-123",
        )

        # Assert
        assert session is not None
        assert session.state["problem"] == "1+1=?"
        assert session.state["app:version"] == "1.0"
        assert session.state["user:name"] == "太郎"

    async def test_applies_num_recent_events_config(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """GetSessionConfig.num_recent_eventsを適用"""
        # Arrange
        mock_session_doc = create_mock_doc(
            exists=True,
            data={
                "id": "session-123",
                "app_name": "homework_coach",
                "user_id": "user-456",
                "state": {},
                "last_update_time": 0.0,
            },
        )

        mock_session_ref = MagicMock()
        mock_session_ref.get = AsyncMock(return_value=mock_session_doc)

        # 2件のイベント（最新のみ）
        mock_event_docs = []
        for i in range(2):
            event_doc = MagicMock()
            event_doc.to_dict.return_value = {
                "id": f"event-{i + 3}",  # 最新2件
                "author": "user",
                "timestamp": float(i + 3),
            }
            mock_event_docs.append(event_doc)

        mock_events_query = MagicMock()
        mock_events_query.stream.return_value = async_iter(mock_event_docs)
        mock_limited_query = MagicMock()
        mock_limited_query.stream.return_value = async_iter(mock_event_docs)
        mock_events_query.limit_to_last.return_value = mock_limited_query
        mock_events_collection = MagicMock()
        mock_events_collection.order_by.return_value = mock_events_query
        mock_session_ref.collection.return_value = mock_events_collection

        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            mock = MagicMock()
            if name == "sessions":
                mock.document.return_value = mock_session_ref
            elif name == "app_state":
                mock.document.return_value = mock_app_state_ref
            elif name == "user_state":
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
            return mock

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        config = GetSessionConfig(num_recent_events=2)
        session = await service.get_session(
            app_name="homework_coach",
            user_id="user-456",
            session_id="session-123",
            config=config,
        )

        # Assert
        assert session is not None
        assert len(session.events) == 2


class TestListSessions:
    """list_sessionsメソッドのテスト"""

    async def test_lists_user_sessions(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """ユーザーのセッション一覧を取得"""
        # Arrange
        mock_session_docs = [
            MagicMock(
                to_dict=MagicMock(
                    return_value={
                        "id": "session-1",
                        "app_name": "homework_coach",
                        "user_id": "user-123",
                        "state": {},
                        "last_update_time": 0.0,
                    }
                )
            ),
            MagicMock(
                to_dict=MagicMock(
                    return_value={
                        "id": "session-2",
                        "app_name": "homework_coach",
                        "user_id": "user-123",
                        "state": {},
                        "last_update_time": 0.0,
                    }
                )
            ),
        ]

        mock_query = MagicMock()
        mock_filtered_query = MagicMock()
        mock_filtered_query.stream.return_value = async_iter(mock_session_docs)
        mock_query.where.return_value.where.return_value = mock_filtered_query

        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            if name == "sessions":
                return mock_query
            elif name == "app_state":
                mock = MagicMock()
                mock.document.return_value = mock_app_state_ref
                return mock
            elif name == "user_state":
                mock = MagicMock()
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
                return mock
            return MagicMock()

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        response = await service.list_sessions(
            app_name="homework_coach",
            user_id="user-123",
        )

        # Assert
        assert len(response.sessions) == 2
        assert response.sessions[0].id == "session-1"
        assert response.sessions[1].id == "session-2"

    async def test_lists_all_sessions_without_user_id(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """user_id未指定で全セッションを取得"""
        # Arrange
        mock_session_doc = MagicMock(
            to_dict=MagicMock(
                return_value={
                    "id": "session-1",
                    "app_name": "homework_coach",
                    "user_id": "user-123",
                    "state": {},
                    "last_update_time": 0.0,
                }
            )
        )

        mock_query = MagicMock()
        mock_filtered_query = MagicMock()
        mock_filtered_query.stream.return_value = async_iter([mock_session_doc])
        mock_query.where.return_value = mock_filtered_query

        mock_app_state_doc = create_mock_doc(exists=False)
        mock_app_state_ref = MagicMock()
        mock_app_state_ref.get = AsyncMock(return_value=mock_app_state_doc)

        mock_user_state_doc = create_mock_doc(exists=False)
        mock_user_state_ref = MagicMock()
        mock_user_state_ref.get = AsyncMock(return_value=mock_user_state_doc)

        def collection_side_effect(name: str) -> MagicMock:
            if name == "sessions":
                return mock_query
            elif name == "app_state":
                mock = MagicMock()
                mock.document.return_value = mock_app_state_ref
                return mock
            elif name == "user_state":
                mock = MagicMock()
                mock.document.return_value.collection.return_value.document.return_value = (
                    mock_user_state_ref
                )
                return mock
            return MagicMock()

        mock_firestore_client.collection.side_effect = collection_side_effect

        # Act
        response = await service.list_sessions(
            app_name="homework_coach",
        )

        # Assert
        assert len(response.sessions) == 1

    async def test_returns_empty_list_when_no_sessions(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """セッションがない場合は空のリスト"""
        # Arrange
        mock_query = MagicMock()
        mock_filtered_query = MagicMock()
        mock_filtered_query.stream.return_value = async_iter([])
        mock_query.where.return_value.where.return_value = mock_filtered_query

        mock_firestore_client.collection.return_value = mock_query

        # Act
        response = await service.list_sessions(
            app_name="homework_coach",
            user_id="user-123",
        )

        # Assert
        assert len(response.sessions) == 0


class TestDeleteSession:
    """delete_sessionメソッドのテスト"""

    async def test_deletes_existing_session(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """存在するセッションを削除"""
        # Arrange
        mock_doc = create_mock_doc(exists=True)

        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)
        mock_doc_ref.delete = AsyncMock()

        # events サブコレクション（1件）
        mock_event_doc = MagicMock()
        mock_event_doc.reference.delete = AsyncMock()

        mock_events_collection = MagicMock()
        mock_events_collection.stream.return_value = async_iter([mock_event_doc])
        mock_doc_ref.collection.return_value = mock_events_collection

        mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

        # Act
        await service.delete_session(
            app_name="homework_coach",
            user_id="user-456",
            session_id="session-123",
        )

        # Assert
        mock_doc_ref.delete.assert_called_once()
        mock_event_doc.reference.delete.assert_called_once()

    async def test_does_not_raise_on_nonexistent_session(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """存在しないセッションの削除はエラーにならない"""
        # Arrange
        mock_doc = create_mock_doc(exists=False)

        mock_doc_ref = MagicMock()
        mock_doc_ref.get = AsyncMock(return_value=mock_doc)

        mock_firestore_client.collection.return_value.document.return_value = mock_doc_ref

        # Act & Assert (should not raise)
        await service.delete_session(
            app_name="homework_coach",
            user_id="user-456",
            session_id="nonexistent",
        )


class TestAppendEvent:
    """append_eventメソッドのテスト"""

    async def test_appends_event_and_persists(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """イベントを追加して永続化"""
        # Arrange
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
            state={"problem": "1+1=?"},
        )

        event = Event(
            author="user",
            invocation_id="inv-123",
        )

        mock_session_ref = MagicMock()
        mock_session_ref.update = AsyncMock()
        mock_event_ref = MagicMock()
        mock_event_ref.set = AsyncMock()
        mock_session_ref.collection.return_value.document.return_value = mock_event_ref

        mock_firestore_client.collection.return_value.document.return_value = mock_session_ref

        # Act
        result = await service.append_event(session, event)

        # Assert
        assert result.author == "user"
        assert len(session.events) == 1
        mock_event_ref.set.assert_called_once()
        mock_session_ref.update.assert_called_once()

    async def test_does_not_persist_partial_event(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """partial=Trueのイベントは永続化しない"""
        # Arrange
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
        )

        event = Event(
            author="agent",
            partial=True,
        )

        # Act
        result = await service.append_event(session, event)

        # Assert
        assert result.partial is True
        # Firestoreには何も書き込まれない
        mock_firestore_client.collection.assert_not_called()

    async def test_updates_state_delta(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """state_deltaをセッション状態に適用"""
        # Arrange
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
            state={"problem": "1+1=?"},
        )

        event = Event(
            author="agent",
            actions=EventActions(state_delta={"hint_level": 2}),
        )

        mock_session_ref = MagicMock()
        mock_session_ref.update = AsyncMock()
        mock_event_ref = MagicMock()
        mock_event_ref.set = AsyncMock()
        mock_session_ref.collection.return_value.document.return_value = mock_event_ref

        mock_firestore_client.collection.return_value.document.return_value = mock_session_ref

        # Act
        await service.append_event(session, event)

        # Assert
        assert session.state["hint_level"] == 2

    async def test_excludes_temp_state_from_persistence(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """temp:プレフィックスの状態は永続化しない"""
        # Arrange
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
        )

        event = Event(
            author="agent",
            actions=EventActions(state_delta={"temp:cache": "value", "problem": "2+2=?"}),
        )

        mock_session_ref = MagicMock()
        mock_session_ref.update = AsyncMock()
        mock_event_ref = MagicMock()
        mock_event_ref.set = AsyncMock()
        mock_session_ref.collection.return_value.document.return_value = mock_event_ref

        mock_firestore_client.collection.return_value.document.return_value = mock_session_ref

        # Act
        await service.append_event(session, event)

        # Assert
        # temp:cacheはstate_deltaから除外されている
        event_dict = mock_event_ref.set.call_args[0][0]
        if "actions" in event_dict and "state_delta" in event_dict["actions"]:
            assert "temp:cache" not in event_dict["actions"]["state_delta"]

    async def test_updates_last_update_time(
        self, service: FirestoreSessionService, mock_firestore_client: MagicMock
    ) -> None:
        """last_update_timeを更新"""
        # Arrange
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
            last_update_time=0.0,
        )

        event = Event(
            author="user",
            timestamp=1234567890.0,
        )

        mock_session_ref = MagicMock()
        mock_session_ref.update = AsyncMock()
        mock_event_ref = MagicMock()
        mock_event_ref.set = AsyncMock()
        mock_session_ref.collection.return_value.document.return_value = mock_event_ref

        mock_firestore_client.collection.return_value.document.return_value = mock_session_ref

        # Act
        await service.append_event(session, event)

        # Assert
        assert session.last_update_time == 1234567890.0
        update_call = mock_session_ref.update.call_args[0][0]
        assert update_call["last_update_time"] == 1234567890.0
