"""ADK sessions package.

Firestore-backed session service for ADK integration.
Session factory for environment-based service selection.
"""

from app.services.adk.sessions.converters import (
    dict_to_event,
    dict_to_session,
    event_to_dict,
    extract_state_delta,
    session_to_dict,
)
from app.services.adk.sessions.firestore_session_service import (
    FirestoreSessionService,
)
from app.services.adk.sessions.session_factory import (
    create_session_service,
    should_use_managed_session,
)

__all__ = [
    "FirestoreSessionService",
    "create_session_service",
    "should_use_managed_session",
    "session_to_dict",
    "dict_to_session",
    "event_to_dict",
    "dict_to_event",
    "extract_state_delta",
]
