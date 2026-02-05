"""Firestore-backed ADK MemoryService"""

from google.adk.memory.base_memory_service import (
    BaseMemoryService,
    SearchMemoryResponse,
)
from google.adk.sessions.session import Session
from google.cloud import firestore  # type: ignore[attr-defined]
from typing_extensions import override

from app.services.adk.memory.converters import (
    dict_to_memory_entry,
    event_to_memory_dict,
    extract_words_lower,
)


class FirestoreMemoryService(BaseMemoryService):
    """Firestore-backed ADK MemoryService

    ADK BaseMemoryServiceを継承し、Firestoreで永続化を行う実装。

    Firestoreコレクション構造:
        /memories/{app_name}/users/{user_id}/entries/{entry_id} - 記憶エントリ
    """

    def __init__(
        self,
        project_id: str | None = None,
        database: str = "(default)",
    ) -> None:
        """初期化

        Args:
            project_id: GCPプロジェクトID（Noneでデフォルト）
            database: Firestoreデータベース名
        """
        self._db = firestore.AsyncClient(project=project_id, database=database)

    def _get_entries_collection(
        self,
        app_name: str,
        user_id: str,
    ) -> firestore.AsyncCollectionReference:
        """記憶エントリコレクションの参照を取得

        Args:
            app_name: アプリ名
            user_id: ユーザーID

        Returns:
            Firestoreコレクション参照
        """
        return (
            self._db.collection("memories")
            .document(app_name)
            .collection("users")
            .document(user_id)
            .collection("entries")
        )

    @override
    async def add_session_to_memory(
        self,
        session: Session,
    ) -> None:
        """セッションを記憶に追加

        セッションのイベントからテキストコンテンツを持つものを抽出し、
        Firestoreに保存する。

        Args:
            session: ADK Session
        """
        entries_collection = self._get_entries_collection(
            session.app_name,
            session.user_id,
        )

        for event in session.events:
            # コンテンツがないイベントはスキップ
            memory_dict = event_to_memory_dict(event, session_id=session.id)
            if memory_dict is None:
                continue

            # Firestoreに保存
            entry_ref = entries_collection.document(event.id)
            await entry_ref.set(memory_dict)

    @override
    async def search_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        query: str,
    ) -> SearchMemoryResponse:
        """記憶を検索

        キーワードベースの検索を行い、クエリに含まれる単語が
        記憶エントリのテキストに含まれる場合にマッチとする。

        Args:
            app_name: アプリ名
            user_id: ユーザーID
            query: 検索クエリ

        Returns:
            SearchMemoryResponse: マッチした記憶のリスト
        """
        entries_collection = self._get_entries_collection(app_name, user_id)

        # クエリから単語を抽出
        query_words = extract_words_lower(query)
        if not query_words:
            return SearchMemoryResponse(memories=[])

        response = SearchMemoryResponse(memories=[])

        # 全エントリを取得してフィルタリング
        # 注意: 大量データの場合はページネーションやインデックスの最適化が必要
        async for doc in entries_collection.stream():
            data = doc.to_dict()
            if not data:
                continue

            # エントリのテキストを抽出
            content = data.get("content", {})
            parts = content.get("parts", [])
            entry_text = " ".join(part.get("text", "") for part in parts if part.get("text"))

            if not entry_text:
                continue

            # キーワードマッチング
            entry_words = extract_words_lower(entry_text)
            if any(query_word in entry_words for query_word in query_words):
                memory_entry = dict_to_memory_entry(data)
                response.memories.append(memory_entry)

        return response
