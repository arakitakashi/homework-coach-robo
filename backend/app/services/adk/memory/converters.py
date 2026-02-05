"""ADK Memory ↔ Firestore dict 変換関数"""

import re
from datetime import datetime, timezone
from typing import Any

from google.adk.events.event import Event
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types


def extract_text_from_event(event: Event) -> str | None:
    """イベントからテキストを抽出

    Args:
        event: ADK Event

    Returns:
        抽出されたテキスト（テキストがない場合はNone）
    """
    if not event.content or not event.content.parts:
        return None

    texts = [part.text for part in event.content.parts if part.text]
    if not texts:
        return None

    return " ".join(texts)


def event_to_memory_dict(
    event: Event,
    session_id: str,
    custom_metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """ADK EventをFirestore用dictに変換

    Args:
        event: ADK Event
        session_id: セッションID
        custom_metadata: カスタムメタデータ

    Returns:
        Firestore保存用のdict（コンテンツがない場合はNone）
    """
    if not event.content or not event.content.parts:
        return None

    # パーツをdict形式に変換
    parts = []
    for part in event.content.parts:
        part_dict: dict[str, Any] = {}
        if part.text:
            part_dict["text"] = part.text
        if part_dict:
            parts.append(part_dict)

    if not parts:
        return None

    return {
        "event_id": event.id,
        "session_id": session_id,
        "author": event.author,
        "timestamp": event.timestamp,
        "content": {
            "role": event.content.role,
            "parts": parts,
        },
        "custom_metadata": custom_metadata or {},
    }


def dict_to_memory_entry(data: dict[str, Any]) -> MemoryEntry:
    """Firestore dictをADK MemoryEntryに変換

    Args:
        data: Firestoreから取得したdict

    Returns:
        ADK MemoryEntry
    """
    # タイムスタンプをISO形式に変換
    timestamp = data.get("timestamp", 0.0)
    timestamp_iso = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

    # Contentを構築
    content_data = data.get("content", {})
    parts = []
    for part_data in content_data.get("parts", []):
        if "text" in part_data:
            parts.append(types.Part(text=part_data["text"]))

    content = types.Content(
        role=content_data.get("role", "user"),
        parts=parts,
    )

    return MemoryEntry(
        id=data.get("event_id"),
        content=content,
        author=data.get("author"),
        timestamp=timestamp_iso,
        custom_metadata=data.get("custom_metadata", {}),
    )


def extract_words_lower(text: str) -> set[str]:
    """テキストから英単語を抽出（小文字化）

    Args:
        text: 入力テキスト

    Returns:
        小文字化された英単語のセット
    """
    return {word.lower() for word in re.findall(r"[A-Za-z]+", text)}
