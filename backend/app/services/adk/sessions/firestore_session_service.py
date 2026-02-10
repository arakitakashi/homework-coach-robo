"""Firestore-backed ADK SessionService"""

import time
import uuid
from typing import Any

from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.events.event import Event
from google.adk.sessions.base_session_service import (
    BaseSessionService,
    GetSessionConfig,
    ListSessionsResponse,
)
from google.adk.sessions.session import Session
from google.cloud import firestore  # type: ignore[attr-defined]
from typing_extensions import override

from app.services.adk.sessions.converters import (
    dict_to_event,
    dict_to_session,
    event_to_dict,
    extract_state_delta,
    session_to_dict,
)

# ADK State プレフィックス定数
APP_PREFIX = "app:"
USER_PREFIX = "user:"
TEMP_PREFIX = "temp:"


class FirestoreSessionService(BaseSessionService):
    """Firestore-backed ADK SessionService

    ADK BaseSessionServiceを継承し、Firestoreで永続化を行う実装。

    Firestoreコレクション構造:
        /sessions/{session_id} - セッションメタデータと状態
        /sessions/{session_id}/events/{event_id} - イベント
        /app_state/{app_name} - アプリスコープの状態
        /user_state/{app_name}/users/{user_id} - ユーザースコープの状態
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

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> Session:
        """セッション作成

        Args:
            app_name: アプリ名
            user_id: ユーザーID
            state: 初期状態
            session_id: セッションID（未指定でUUID生成）

        Returns:
            作成されたSession

        Raises:
            AlreadyExistsError: 既存のsession_idで作成しようとした場合
        """
        # セッションID生成
        session_id = session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())

        # 既存セッションチェック
        session_ref = self._db.collection("sessions").document(session_id)
        existing_doc = await session_ref.get()
        if existing_doc.exists:
            raise AlreadyExistsError(  # type: ignore[no-untyped-call]
                f"Session with id {session_id} already exists."
            )

        # 状態をスコープ別に分類
        state_deltas = extract_state_delta(state)
        app_state_delta = state_deltas["app"]
        user_state_delta = state_deltas["user"]
        session_state = state_deltas["session"]

        # アプリ状態を保存
        if app_state_delta:
            app_state_ref = self._db.collection("app_state").document(app_name)
            await app_state_ref.set(app_state_delta, merge=True)

        # ユーザー状態を保存
        if user_state_delta:
            user_state_ref = (
                self._db.collection("user_state")
                .document(app_name)
                .collection("users")
                .document(user_id)
            )
            await user_state_ref.set(user_state_delta, merge=True)

        # セッションを作成
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=session_state or {},
            last_update_time=time.time(),
        )

        # Firestoreに保存
        await session_ref.set(session_to_dict(session))

        # 返却用にapp/user状態をマージ
        merged_session = await self._merge_state(app_name, user_id, session)
        return merged_session

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: GetSessionConfig | None = None,
    ) -> Session | None:
        """セッション取得

        Args:
            app_name: アプリ名
            user_id: ユーザーID
            session_id: セッションID
            config: 取得設定（イベントフィルタリング）

        Returns:
            Session（存在しない場合はNone）
        """
        # セッションドキュメント取得
        session_ref = self._db.collection("sessions").document(session_id)
        session_doc = await session_ref.get()

        if not session_doc.exists:
            return None

        # イベント取得
        events: list[Event] = []
        events_collection = session_ref.collection("events")

        if config and config.num_recent_events:
            # 最新N件のみ取得
            events_query = events_collection.order_by("timestamp").limit_to_last(
                config.num_recent_events
            )
            async for event_doc in events_query.stream():
                events.append(dict_to_event(event_doc.to_dict()))
        elif config and config.after_timestamp:
            # 指定タイムスタンプ以降のみ取得
            events_query = events_collection.order_by("timestamp").where(
                "timestamp", ">", config.after_timestamp
            )
            async for event_doc in events_query.stream():
                events.append(dict_to_event(event_doc.to_dict()))
        else:
            # 全件取得
            async for event_doc in events_collection.order_by("timestamp").stream():
                events.append(dict_to_event(event_doc.to_dict()))

        # Sessionオブジェクト構築
        session = dict_to_session(session_doc.to_dict(), events=events)

        # app/user状態をマージ
        merged_session = await self._merge_state(app_name, user_id, session)
        return merged_session

    @override
    async def list_sessions(
        self,
        *,
        app_name: str,
        user_id: str | None = None,
    ) -> ListSessionsResponse:
        """セッション一覧取得

        Args:
            app_name: アプリ名
            user_id: ユーザーID（未指定で全ユーザー）

        Returns:
            ListSessionsResponse
        """
        sessions: list[Session] = []

        sessions_collection = self._db.collection("sessions")

        if user_id is not None:
            # 特定ユーザーのセッション
            query = sessions_collection.where("app_name", "==", app_name).where(
                "user_id", "==", user_id
            )
        else:
            # 全ユーザーのセッション
            query = sessions_collection.where("app_name", "==", app_name)

        async for session_doc in query.stream():
            session_data = session_doc.to_dict()
            session = dict_to_session(session_data, events=[])

            # list_sessionsではイベントを含めない（仕様通り）
            session_user_id = session_data["user_id"]
            merged_session = await self._merge_state(app_name, session_user_id, session)
            sessions.append(merged_session)

        return ListSessionsResponse(sessions=sessions)

    @override
    async def delete_session(
        self,
        *,
        app_name: str,  # noqa: ARG002 - ADKインターフェース準拠
        user_id: str,  # noqa: ARG002 - ADKインターフェース準拠
        session_id: str,
    ) -> None:
        """セッション削除

        Args:
            app_name: アプリ名
            user_id: ユーザーID
            session_id: セッションID
        """
        session_ref = self._db.collection("sessions").document(session_id)
        session_doc = await session_ref.get()

        if not session_doc.exists:
            return

        # イベントサブコレクションを削除
        events_collection = session_ref.collection("events")
        async for event_doc in events_collection.stream():
            await event_doc.reference.delete()

        # セッション自体を削除
        await session_ref.delete()

    @override
    async def append_event(
        self,
        session: Session,
        event: Event,
    ) -> Event:
        """イベント追加（永続化付き）

        Args:
            session: セッション
            event: 追加するイベント

        Returns:
            追加されたイベント
        """
        # 部分イベントは永続化しない
        if event.partial:
            return event

        # temp:キーを除去（親クラスのメソッドを使用）
        event = self._trim_temp_delta_state(event)

        # セッション状態を更新（親クラスのメソッドを使用）
        self._update_session_state(session, event)

        # イベントをセッションに追加
        session.events.append(event)
        session.last_update_time = event.timestamp

        # Firestoreに永続化
        session_ref = self._db.collection("sessions").document(session.id)

        # イベントを保存
        event_ref = session_ref.collection("events").document(event.id)
        await event_ref.set(event_to_dict(event))

        # セッションのlast_update_timeと状態を更新
        update_data: dict[str, Any] = {"last_update_time": event.timestamp}

        # 状態差分をスコープ別に分類して永続化
        if event.actions and event.actions.state_delta:
            state_deltas = extract_state_delta(event.actions.state_delta)

            # セッション状態を更新
            if state_deltas["session"]:
                # Firestoreのstate fieldをマージ更新
                update_data["state"] = session.state

            # アプリ状態を更新
            if state_deltas["app"]:
                app_state_ref = self._db.collection("app_state").document(session.app_name)
                await app_state_ref.set(state_deltas["app"], merge=True)

            # ユーザー状態を更新
            if state_deltas["user"]:
                user_state_ref = (
                    self._db.collection("user_state")
                    .document(session.app_name)
                    .collection("users")
                    .document(session.user_id)
                )
                await user_state_ref.set(state_deltas["user"], merge=True)

        await session_ref.update(update_data)

        return event

    async def _merge_state(
        self,
        app_name: str,
        user_id: str,
        session: Session,
    ) -> Session:
        """app状態とuser状態をセッション状態にマージ

        Args:
            app_name: アプリ名
            user_id: ユーザーID
            session: マージ対象のSession

        Returns:
            状態がマージされたSession
        """
        # アプリ状態を取得
        app_state_ref = self._db.collection("app_state").document(app_name)
        app_state_doc = await app_state_ref.get()
        if app_state_doc.exists:
            app_state = app_state_doc.to_dict() or {}
            for key, value in app_state.items():
                session.state[f"{APP_PREFIX}{key}"] = value

        # ユーザー状態を取得
        user_state_ref = (
            self._db.collection("user_state")
            .document(app_name)
            .collection("users")
            .document(user_id)
        )
        user_state_doc = await user_state_ref.get()
        if user_state_doc.exists:
            user_state = user_state_doc.to_dict() or {}
            for key, value in user_state.items():
                session.state[f"{USER_PREFIX}{key}"] = value

        return session

    async def list_all_session_ids(self) -> list[str]:
        """全セッションIDのリストを取得する

        データ移行などで使用するヘルパーメソッド。
        全セッションのIDを取得して返す。

        Returns:
            セッションIDのリスト

        Note:
            大量のセッションがある場合はメモリを消費する可能性があります。
        """
        session_ids: list[str] = []
        sessions_ref = self._db.collection("sessions")

        async for doc in sessions_ref.stream():
            session_ids.append(doc.id)

        return session_ids

    async def get_session_data_by_id(self, session_id: str) -> dict[str, Any] | None:
        """セッションIDのみでセッションデータを取得する

        移行などの管理操作で使用するヘルパーメソッド。
        session_idだけでFirestoreドキュメントを読み取り、生データ（辞書）を返す。

        Args:
            session_id: セッションID

        Returns:
            セッションデータの辞書（存在しない場合はNone）

        Note:
            通常のアプリケーションロジックでは、app_nameとuser_idを指定する
            get_sessionメソッドを使用してください。このメソッドは移行などの
            特殊な用途でのみ使用します。
        """
        session_ref = self._db.collection("sessions").document(session_id)
        session_doc = await session_ref.get()

        if not session_doc.exists:
            return None

        return session_doc.to_dict()  # type: ignore[no-any-return]
