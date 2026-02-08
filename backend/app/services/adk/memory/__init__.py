"""ADK memory package.

Memory service for ADK integration.
Supports FirestoreMemoryService (default) and VertexAiMemoryBankService (via AGENT_ENGINE_ID).
"""

from app.services.adk.memory.converters import (
    dict_to_memory_entry,
    event_to_memory_dict,
    extract_text_from_event,
    extract_words_lower,
)
from app.services.adk.memory.firestore_memory_service import FirestoreMemoryService
from app.services.adk.memory.memory_factory import create_memory_service

__all__ = [
    "FirestoreMemoryService",
    "create_memory_service",
    "extract_text_from_event",
    "event_to_memory_dict",
    "dict_to_memory_entry",
    "extract_words_lower",
]
