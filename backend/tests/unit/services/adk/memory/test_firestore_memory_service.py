"""FirestoreMemoryService のテスト"""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.adk.events.event import Event
from google.adk.sessions.session import Session
from google.genai import types


async def async_iter(items: list[Any]) -> AsyncIterator[Any]:
    """リストをasync iteratorに変換するヘルパー"""
    for item in items:
        yield item


class TestAddSessionToMemory:
    """add_session_to_memory メソッドのテスト"""

    @pytest.mark.asyncio
    async def test_adds_session_events_to_memory(self) -> None:
        """セッションのイベントを記憶に追加する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # コレクション/ドキュメント参照のモック
            mock_entries_collection = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.set = AsyncMock()
            mock_entries_collection.document.return_value = mock_doc_ref

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            # テスト用セッション
            session = Session(
                id="session-1",
                app_name="test-app",
                user_id="user-1",
                state={},
                events=[
                    Event(
                        id="event-1",
                        invocation_id="inv-1",
                        author="user",
                        timestamp=1234567890.0,
                        content=types.Content(
                            role="user",
                            parts=[types.Part(text="Hello")],
                        ),
                    ),
                ],
            )

            await service.add_session_to_memory(session)

            # Firestoreに書き込まれたか確認
            mock_doc_ref.set.assert_called_once()
            call_args = mock_doc_ref.set.call_args[0][0]
            assert call_args["session_id"] == "session-1"
            assert call_args["author"] == "user"

    @pytest.mark.asyncio
    async def test_adds_multiple_events(self) -> None:
        """複数イベントのセッションを追加する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_entries_collection = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.set = AsyncMock()
            mock_entries_collection.document.return_value = mock_doc_ref

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            session = Session(
                id="session-1",
                app_name="test-app",
                user_id="user-1",
                state={},
                events=[
                    Event(
                        id="event-1",
                        invocation_id="inv-1",
                        author="user",
                        timestamp=1234567890.0,
                        content=types.Content(
                            role="user",
                            parts=[types.Part(text="Question")],
                        ),
                    ),
                    Event(
                        id="event-2",
                        invocation_id="inv-1",
                        author="model",
                        timestamp=1234567891.0,
                        content=types.Content(
                            role="model",
                            parts=[types.Part(text="Answer")],
                        ),
                    ),
                ],
            )

            await service.add_session_to_memory(session)

            # 2回書き込まれたか確認
            assert mock_doc_ref.set.call_count == 2

    @pytest.mark.asyncio
    async def test_skips_events_without_content(self) -> None:
        """コンテンツなしイベントはスキップする"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_entries_collection = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.set = AsyncMock()
            mock_entries_collection.document.return_value = mock_doc_ref

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            session = Session(
                id="session-1",
                app_name="test-app",
                user_id="user-1",
                state={},
                events=[
                    Event(
                        id="event-1",
                        invocation_id="inv-1",
                        author="user",
                        timestamp=1234567890.0,
                        # コンテンツなし
                    ),
                    Event(
                        id="event-2",
                        invocation_id="inv-1",
                        author="user",
                        timestamp=1234567891.0,
                        content=types.Content(
                            role="user",
                            parts=[types.Part(text="Valid content")],
                        ),
                    ),
                ],
            )

            await service.add_session_to_memory(session)

            # 1回のみ書き込まれたか確認（コンテンツありのイベントのみ）
            assert mock_doc_ref.set.call_count == 1

    @pytest.mark.asyncio
    async def test_handles_empty_session(self) -> None:
        """イベントなしセッションを処理する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            service = FirestoreMemoryService()

            session = Session(
                id="session-1",
                app_name="test-app",
                user_id="user-1",
                state={},
                events=[],
            )

            # エラーなく完了する
            await service.add_session_to_memory(session)


class TestSearchMemory:
    """search_memory メソッドのテスト"""

    @pytest.mark.asyncio
    async def test_searches_memory_by_keyword(self) -> None:
        """キーワードで記憶を検索する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # 検索結果のモック
            mock_doc1 = MagicMock()
            mock_doc1.to_dict.return_value = {
                "event_id": "event-1",
                "session_id": "session-1",
                "author": "user",
                "timestamp": 1234567890.0,
                "content": {
                    "role": "user",
                    "parts": [{"text": "Hello world test"}],
                },
                "custom_metadata": {},
            }

            mock_entries_collection = MagicMock()
            mock_entries_collection.stream.return_value = async_iter([mock_doc1])

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            result = await service.search_memory(
                app_name="test-app",
                user_id="user-1",
                query="hello",
            )

            assert len(result.memories) == 1
            assert result.memories[0].author == "user"

    @pytest.mark.asyncio
    async def test_returns_empty_for_no_match(self) -> None:
        """マッチなしの場合は空リストを返す"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_doc1 = MagicMock()
            mock_doc1.to_dict.return_value = {
                "event_id": "event-1",
                "session_id": "session-1",
                "author": "user",
                "timestamp": 1234567890.0,
                "content": {
                    "role": "user",
                    "parts": [{"text": "Hello world"}],
                },
                "custom_metadata": {},
            }

            mock_entries_collection = MagicMock()
            mock_entries_collection.stream.return_value = async_iter([mock_doc1])

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            result = await service.search_memory(
                app_name="test-app",
                user_id="user-1",
                query="nonexistent",
            )

            assert len(result.memories) == 0

    @pytest.mark.asyncio
    async def test_matches_multiple_keywords(self) -> None:
        """複数キーワードでマッチする"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_doc1 = MagicMock()
            mock_doc1.to_dict.return_value = {
                "event_id": "event-1",
                "session_id": "session-1",
                "author": "user",
                "timestamp": 1234567890.0,
                "content": {
                    "role": "user",
                    "parts": [{"text": "Math addition problem"}],
                },
                "custom_metadata": {},
            }

            mock_doc2 = MagicMock()
            mock_doc2.to_dict.return_value = {
                "event_id": "event-2",
                "session_id": "session-1",
                "author": "user",
                "timestamp": 1234567891.0,
                "content": {
                    "role": "user",
                    "parts": [{"text": "Another topic"}],
                },
                "custom_metadata": {},
            }

            mock_entries_collection = MagicMock()
            mock_entries_collection.stream.return_value = async_iter([mock_doc1, mock_doc2])

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            result = await service.search_memory(
                app_name="test-app",
                user_id="user-1",
                query="math addition",
            )

            # math または addition を含むドキュメントがマッチ
            assert len(result.memories) == 1

    @pytest.mark.asyncio
    async def test_handles_empty_collection(self) -> None:
        """空のコレクションを処理する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_entries_collection = MagicMock()
            mock_entries_collection.stream.return_value = async_iter([])

            mock_users_collection = MagicMock()
            mock_users_collection.document.return_value.collection.return_value = (
                mock_entries_collection
            )

            mock_app_doc = MagicMock()
            mock_app_doc.collection.return_value = mock_users_collection

            mock_memories_collection = MagicMock()
            mock_memories_collection.document.return_value = mock_app_doc

            mock_client.collection.return_value = mock_memories_collection

            service = FirestoreMemoryService()

            result = await service.search_memory(
                app_name="test-app",
                user_id="user-1",
                query="anything",
            )

            assert len(result.memories) == 0


class TestInitialization:
    """初期化のテスト"""

    def test_initializes_with_default_database(self) -> None:
        """デフォルトデータベースで初期化する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            FirestoreMemoryService()
            mock_client_class.assert_called_once_with(project=None, database="(default)")

    def test_initializes_with_custom_project(self) -> None:
        """カスタムプロジェクトIDで初期化する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            FirestoreMemoryService(project_id="my-project")
            mock_client_class.assert_called_once_with(project="my-project", database="(default)")

    def test_initializes_with_custom_database(self) -> None:
        """カスタムデータベースで初期化する"""
        from app.services.adk.memory.firestore_memory_service import (
            FirestoreMemoryService,
        )

        with patch("google.cloud.firestore.AsyncClient") as mock_client_class:
            FirestoreMemoryService(database="custom-db")
            mock_client_class.assert_called_once_with(project=None, database="custom-db")
