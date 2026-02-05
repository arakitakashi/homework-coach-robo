"""コンバーター関数のテスト"""

from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.sessions.session import Session

from app.services.adk.sessions.converters import (
    dict_to_event,
    dict_to_session,
    event_to_dict,
    extract_state_delta,
    session_to_dict,
)


class TestSessionToDict:
    """session_to_dict関数のテスト"""

    def test_converts_basic_session(self) -> None:
        """基本的なSessionをdictに変換"""
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
            state={"problem": "1+1=?"},
            last_update_time=1234567890.0,
        )

        result = session_to_dict(session)

        assert result["id"] == "session-123"
        assert result["app_name"] == "homework_coach"
        assert result["user_id"] == "user-456"
        assert result["state"] == {"problem": "1+1=?"}
        assert result["last_update_time"] == 1234567890.0

    def test_converts_session_with_empty_state(self) -> None:
        """空の状態を持つSessionをdictに変換"""
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
        )

        result = session_to_dict(session)

        assert result["state"] == {}

    def test_excludes_events_from_dict(self) -> None:
        """eventsはdictに含めない（別途サブコレクションに保存）"""
        event = Event(author="user")
        session = Session(
            id="session-123",
            app_name="homework_coach",
            user_id="user-456",
            events=[event],
        )

        result = session_to_dict(session)

        assert "events" not in result


class TestDictToSession:
    """dict_to_session関数のテスト"""

    def test_converts_basic_dict_to_session(self) -> None:
        """基本的なdictをSessionに変換"""
        data = {
            "id": "session-123",
            "app_name": "homework_coach",
            "user_id": "user-456",
            "state": {"problem": "1+1=?"},
            "last_update_time": 1234567890.0,
        }

        result = dict_to_session(data)

        assert isinstance(result, Session)
        assert result.id == "session-123"
        assert result.app_name == "homework_coach"
        assert result.user_id == "user-456"
        assert result.state == {"problem": "1+1=?"}
        assert result.last_update_time == 1234567890.0

    def test_converts_dict_with_events_list(self) -> None:
        """eventsリスト付きのdictをSessionに変換"""
        data = {
            "id": "session-123",
            "app_name": "homework_coach",
            "user_id": "user-456",
            "state": {},
            "last_update_time": 0.0,
        }
        events = [Event(author="user"), Event(author="agent")]

        result = dict_to_session(data, events=events)

        assert len(result.events) == 2


class TestEventToDict:
    """event_to_dict関数のテスト"""

    def test_converts_basic_event(self) -> None:
        """基本的なEventをdictに変換"""
        event = Event(
            id="event-123",
            invocation_id="inv-456",
            author="user",
            timestamp=1234567890.0,
        )

        result = event_to_dict(event)

        assert result["id"] == "event-123"
        assert result["invocation_id"] == "inv-456"
        assert result["author"] == "user"
        assert result["timestamp"] == 1234567890.0

    def test_converts_event_with_state_delta(self) -> None:
        """state_delta付きのEventをdictに変換"""
        event = Event(
            author="agent",
            actions=EventActions(state_delta={"problem": "2+2=?"}),
        )

        result = event_to_dict(event)

        assert result["actions"]["state_delta"] == {"problem": "2+2=?"}

    def test_converts_event_with_partial_flag(self) -> None:
        """partial=TrueのEventをdictに変換"""
        event = Event(
            author="agent",
            partial=True,
        )

        result = event_to_dict(event)

        assert result["partial"] is True


class TestDictToEvent:
    """dict_to_event関数のテスト"""

    def test_converts_basic_dict_to_event(self) -> None:
        """基本的なdictをEventに変換"""
        data = {
            "id": "event-123",
            "invocation_id": "inv-456",
            "author": "user",
            "timestamp": 1234567890.0,
        }

        result = dict_to_event(data)

        assert isinstance(result, Event)
        assert result.id == "event-123"
        assert result.invocation_id == "inv-456"
        assert result.author == "user"

    def test_converts_dict_with_actions(self) -> None:
        """actions付きのdictをEventに変換"""
        data = {
            "id": "event-123",
            "author": "agent",
            "actions": {
                "state_delta": {"key": "value"},
            },
        }

        result = dict_to_event(data)

        assert result.actions.state_delta == {"key": "value"}


class TestExtractStateDelta:
    """extract_state_delta関数のテスト"""

    def test_extracts_app_state(self) -> None:
        """app:プレフィックスの状態を抽出"""
        state = {"app:config": "value"}

        result = extract_state_delta(state)

        assert result["app"] == {"config": "value"}
        assert result["user"] == {}
        assert result["session"] == {}

    def test_extracts_user_state(self) -> None:
        """user:プレフィックスの状態を抽出"""
        state = {"user:preference": "dark"}

        result = extract_state_delta(state)

        assert result["app"] == {}
        assert result["user"] == {"preference": "dark"}
        assert result["session"] == {}

    def test_extracts_session_state(self) -> None:
        """プレフィックスなしの状態をセッション状態として抽出"""
        state = {"problem": "1+1=?", "hint_level": 1}

        result = extract_state_delta(state)

        assert result["app"] == {}
        assert result["user"] == {}
        assert result["session"] == {"problem": "1+1=?", "hint_level": 1}

    def test_extracts_mixed_state(self) -> None:
        """混合状態を適切に分類"""
        state = {
            "app:version": "1.0",
            "user:name": "太郎",
            "problem": "2+3=?",
        }

        result = extract_state_delta(state)

        assert result["app"] == {"version": "1.0"}
        assert result["user"] == {"name": "太郎"}
        assert result["session"] == {"problem": "2+3=?"}

    def test_excludes_temp_state(self) -> None:
        """temp:プレフィックスの状態は除外"""
        state = {
            "temp:cache": "temporary",
            "problem": "1+1=?",
        }

        result = extract_state_delta(state)

        assert "cache" not in result["app"]
        assert "cache" not in result["user"]
        assert "cache" not in result["session"]
        assert result["session"] == {"problem": "1+1=?"}

    def test_handles_empty_state(self) -> None:
        """空の状態を処理"""
        result = extract_state_delta({})

        assert result == {"app": {}, "user": {}, "session": {}}

    def test_handles_none_state(self) -> None:
        """Noneを処理"""
        result = extract_state_delta(None)

        assert result == {"app": {}, "user": {}, "session": {}}
