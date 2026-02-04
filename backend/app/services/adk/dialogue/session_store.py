"""セッションストア（インメモリ）"""

import uuid
from datetime import datetime

from app.services.adk.dialogue.models import DialogueContext, DialogueTone


class SessionStore:
    """インメモリセッションストア

    セッション（DialogueContext）を管理するシンプルなストア。
    MVPフェーズではインメモリで十分。後続フェーズでRedis/Firestoreに置き換え可能。
    """

    def __init__(self) -> None:
        """SessionStoreを初期化する"""
        self._sessions: dict[str, DialogueContext] = {}
        self._created_at: dict[str, datetime] = {}

    def create_session(
        self,
        problem: str,
        child_grade: int,
        character_type: str | None = None,
    ) -> str:
        """新しいセッションを作成する

        Args:
            problem: 問題文
            child_grade: 学年（1-3）
            character_type: キャラクタータイプ（オプション）

        Returns:
            セッションID
        """
        session_id = str(uuid.uuid4())

        context = DialogueContext(
            session_id=session_id,
            problem=problem,
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        self._sessions[session_id] = context
        self._created_at[session_id] = datetime.now()

        return session_id

    def get_session(self, session_id: str) -> DialogueContext | None:
        """セッションを取得する

        Args:
            session_id: セッションID

        Returns:
            DialogueContext、存在しない場合はNone
        """
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """セッションを削除する

        Args:
            session_id: セッションID

        Returns:
            削除成功ならTrue、存在しなければFalse
        """
        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]
        del self._created_at[session_id]
        return True

    def update_session(self, session_id: str, context: DialogueContext) -> bool:
        """セッションを更新する

        Args:
            session_id: セッションID
            context: 更新するDialogueContext

        Returns:
            更新成功ならTrue、存在しなければFalse
        """
        if session_id not in self._sessions:
            return False

        self._sessions[session_id] = context
        return True

    def get_created_at(self, session_id: str) -> datetime | None:
        """セッションの作成日時を取得する

        Args:
            session_id: セッションID

        Returns:
            作成日時、存在しない場合はNone
        """
        return self._created_at.get(session_id)
