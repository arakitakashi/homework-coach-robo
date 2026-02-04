"""セッションストアのテスト"""

from app.services.adk.dialogue.models import DialogueContext, DialogueTone
from app.services.adk.dialogue.session_store import SessionStore


class TestSessionStoreCreate:
    """セッション作成のテスト"""

    def test_create_session(self):
        """セッションを作成できる"""
        store = SessionStore()
        session_id = store.create_session(
            problem="3 + 5 = ?",
            child_grade=2,
        )

        assert session_id is not None
        assert len(session_id) > 0

    def test_create_session_with_character_type(self):
        """キャラクタータイプ付きでセッションを作成できる"""
        store = SessionStore()
        session_id = store.create_session(
            problem="3 + 5 = ?",
            child_grade=1,
            character_type="robot",
        )

        context = store.get_session(session_id)
        assert context is not None

    def test_create_session_generates_unique_ids(self):
        """作成されるセッションIDはユニーク"""
        store = SessionStore()
        ids = set()

        for _ in range(100):
            session_id = store.create_session(problem="test", child_grade=1)
            ids.add(session_id)

        assert len(ids) == 100


class TestSessionStoreGet:
    """セッション取得のテスト"""

    def test_get_existing_session(self):
        """存在するセッションを取得できる"""
        store = SessionStore()
        session_id = store.create_session(problem="3 + 5 = ?", child_grade=2)

        context = store.get_session(session_id)

        assert context is not None
        assert isinstance(context, DialogueContext)
        assert context.problem == "3 + 5 = ?"
        assert context.session_id == session_id
        assert context.current_hint_level == 1
        assert context.tone == DialogueTone.ENCOURAGING
        assert len(context.turns) == 0

    def test_get_nonexistent_session(self):
        """存在しないセッションはNoneを返す"""
        store = SessionStore()
        context = store.get_session("nonexistent-id")

        assert context is None


class TestSessionStoreDelete:
    """セッション削除のテスト"""

    def test_delete_existing_session(self):
        """存在するセッションを削除できる"""
        store = SessionStore()
        session_id = store.create_session(problem="test", child_grade=1)

        result = store.delete_session(session_id)

        assert result is True
        assert store.get_session(session_id) is None

    def test_delete_nonexistent_session(self):
        """存在しないセッションの削除はFalseを返す"""
        store = SessionStore()
        result = store.delete_session("nonexistent-id")

        assert result is False


class TestSessionStoreUpdate:
    """セッション更新のテスト"""

    def test_update_existing_session(self):
        """存在するセッションを更新できる"""
        store = SessionStore()
        session_id = store.create_session(problem="test", child_grade=1)

        # コンテキストを取得して変更
        context = store.get_session(session_id)
        context.current_hint_level = 2
        context.tone = DialogueTone.EMPATHETIC

        # 更新
        result = store.update_session(session_id, context)

        assert result is True

        # 更新されていることを確認
        updated_context = store.get_session(session_id)
        assert updated_context.current_hint_level == 2
        assert updated_context.tone == DialogueTone.EMPATHETIC

    def test_update_nonexistent_session(self):
        """存在しないセッションの更新はFalseを返す"""
        store = SessionStore()
        context = DialogueContext(
            session_id="nonexistent-id",
            problem="test",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        result = store.update_session("nonexistent-id", context)

        assert result is False
