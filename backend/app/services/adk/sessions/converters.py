"""ADK Session/Event ↔ Firestore dict 変換関数"""

from typing import Any

from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.sessions.session import Session

# ADK State プレフィックス定数
APP_PREFIX = "app:"
USER_PREFIX = "user:"
TEMP_PREFIX = "temp:"


def session_to_dict(session: Session) -> dict[str, Any]:
    """SessionオブジェクトをFirestore用dictに変換

    注意: eventsはサブコレクションに保存するため、このdictには含めない

    Args:
        session: ADK Sessionオブジェクト

    Returns:
        Firestore保存用のdict
    """
    return {
        "id": session.id,
        "app_name": session.app_name,
        "user_id": session.user_id,
        "state": session.state,
        "last_update_time": session.last_update_time,
    }


def dict_to_session(
    data: dict[str, Any],
    events: list[Event] | None = None,
) -> Session:
    """Firestore dictをSessionオブジェクトに変換

    Args:
        data: Firestoreから取得したdict
        events: 関連するEventリスト（オプション）

    Returns:
        ADK Sessionオブジェクト
    """
    return Session(
        id=data["id"],
        app_name=data["app_name"],
        user_id=data["user_id"],
        state=data.get("state", {}),
        events=events or [],
        last_update_time=data.get("last_update_time", 0.0),
    )


def event_to_dict(event: Event) -> dict[str, Any]:
    """EventオブジェクトをFirestore用dictに変換

    Args:
        event: ADK Eventオブジェクト

    Returns:
        Firestore保存用のdict
    """
    result: dict[str, Any] = {
        "id": event.id,
        "invocation_id": event.invocation_id,
        "author": event.author,
        "timestamp": event.timestamp,
    }

    # partial フラグ
    if event.partial:
        result["partial"] = True

    # actions（state_deltaを含む）
    if event.actions:
        actions_dict: dict[str, Any] = {}
        if event.actions.state_delta:
            actions_dict["state_delta"] = event.actions.state_delta
        if actions_dict:
            result["actions"] = actions_dict

    return result


def dict_to_event(data: dict[str, Any]) -> Event:
    """Firestore dictをEventオブジェクトに変換

    Args:
        data: Firestoreから取得したdict

    Returns:
        ADK Eventオブジェクト
    """
    # EventActionsの構築
    actions = EventActions()
    if "actions" in data and data["actions"] and "state_delta" in data["actions"]:
        actions = EventActions(state_delta=data["actions"]["state_delta"])

    return Event(
        id=data.get("id", ""),
        invocation_id=data.get("invocation_id", ""),
        author=data["author"],
        timestamp=data.get("timestamp", 0.0),
        partial=data.get("partial", False),
        actions=actions,
    )


def extract_state_delta(
    state: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """状態をスコープ別に分類

    プレフィックスに基づいて状態を分類:
    - app: アプリスコープ（app:プレフィックス）
    - user: ユーザースコープ（user:プレフィックス）
    - session: セッションスコープ（プレフィックスなし）
    - temp: は除外

    Args:
        state: 分類する状態dict

    Returns:
        {"app": {...}, "user": {...}, "session": {...}}
    """
    result: dict[str, dict[str, Any]] = {"app": {}, "user": {}, "session": {}}

    if not state:
        return result

    for key, value in state.items():
        if key.startswith(APP_PREFIX):
            # app:プレフィックスを除去してappに格納
            result["app"][key[len(APP_PREFIX) :]] = value
        elif key.startswith(USER_PREFIX):
            # user:プレフィックスを除去してuserに格納
            result["user"][key[len(USER_PREFIX) :]] = value
        elif key.startswith(TEMP_PREFIX):
            # temp:は除外
            continue
        else:
            # プレフィックスなしはsessionに格納
            result["session"][key] = value

    return result
