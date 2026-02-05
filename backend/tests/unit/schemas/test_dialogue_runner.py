"""対話ランナースキーマのテスト"""

import pytest
from pydantic import ValidationError


class TestRunDialogueRequest:
    """RunDialogueRequestのテスト"""

    def test_valid_request(self) -> None:
        """有効なリクエストを作成できる"""
        from app.schemas.dialogue_runner import RunDialogueRequest

        request = RunDialogueRequest(
            user_id="user-123",
            session_id="session-456",
            message="テストメッセージ",
        )

        assert request.user_id == "user-123"
        assert request.session_id == "session-456"
        assert request.message == "テストメッセージ"

    def test_empty_user_id_rejected(self) -> None:
        """空のuser_idは拒否される"""
        from app.schemas.dialogue_runner import RunDialogueRequest

        with pytest.raises(ValidationError):
            RunDialogueRequest(
                user_id="",
                session_id="session-456",
                message="テストメッセージ",
            )

    def test_empty_session_id_rejected(self) -> None:
        """空のsession_idは拒否される"""
        from app.schemas.dialogue_runner import RunDialogueRequest

        with pytest.raises(ValidationError):
            RunDialogueRequest(
                user_id="user-123",
                session_id="",
                message="テストメッセージ",
            )

    def test_empty_message_rejected(self) -> None:
        """空のmessageは拒否される"""
        from app.schemas.dialogue_runner import RunDialogueRequest

        with pytest.raises(ValidationError):
            RunDialogueRequest(
                user_id="user-123",
                session_id="session-456",
                message="",
            )


class TestTextEvent:
    """TextEventのテスト"""

    def test_create_text_event(self) -> None:
        """TextEventを作成できる"""
        from app.schemas.dialogue_runner import TextEvent

        event = TextEvent(text="こんにちは")

        assert event.text == "こんにちは"

    def test_json_serialization(self) -> None:
        """JSON形式にシリアライズできる"""
        from app.schemas.dialogue_runner import TextEvent

        event = TextEvent(text="テスト")
        json_data = event.model_dump_json()

        assert '"text":"テスト"' in json_data


class TestErrorEvent:
    """ErrorEventのテスト"""

    def test_create_error_event(self) -> None:
        """ErrorEventを作成できる"""
        from app.schemas.dialogue_runner import ErrorEvent

        event = ErrorEvent(
            error="セッションが見つかりません",
            code="SESSION_NOT_FOUND",
        )

        assert event.error == "セッションが見つかりません"
        assert event.code == "SESSION_NOT_FOUND"

    def test_json_serialization(self) -> None:
        """JSON形式にシリアライズできる"""
        from app.schemas.dialogue_runner import ErrorEvent

        event = ErrorEvent(error="エラー", code="ERROR")
        json_data = event.model_dump_json()

        assert '"error":"エラー"' in json_data
        assert '"code":"ERROR"' in json_data


class TestDoneEvent:
    """DoneEventのテスト"""

    def test_create_done_event(self) -> None:
        """DoneEventを作成できる"""
        from app.schemas.dialogue_runner import DoneEvent

        event = DoneEvent(session_id="session-123")

        assert event.session_id == "session-123"

    def test_json_serialization(self) -> None:
        """JSON形式にシリアライズできる"""
        from app.schemas.dialogue_runner import DoneEvent

        event = DoneEvent(session_id="session-456")
        json_data = event.model_dump_json()

        assert '"session_id":"session-456"' in json_data
