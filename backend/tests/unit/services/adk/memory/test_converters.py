"""メモリコンバーター関数のテスト"""

from google.adk.events.event import Event
from google.adk.memory.memory_entry import MemoryEntry
from google.genai import types


class TestExtractTextFromEvent:
    """extract_text_from_event関数のテスト"""

    def test_extracts_text_from_single_part(self) -> None:
        """単一パートからテキストを抽出する"""
        from app.services.adk.memory.converters import extract_text_from_event

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(
                role="user",
                parts=[types.Part(text="Hello, this is a test message")],
            ),
        )

        result = extract_text_from_event(event)

        assert result == "Hello, this is a test message"

    def test_extracts_text_from_multiple_parts(self) -> None:
        """複数パートからテキストを結合して抽出する"""
        from app.services.adk.memory.converters import extract_text_from_event

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(
                role="user",
                parts=[
                    types.Part(text="First part"),
                    types.Part(text="Second part"),
                ],
            ),
        )

        result = extract_text_from_event(event)

        assert result == "First part Second part"

    def test_returns_none_for_event_without_content(self) -> None:
        """コンテンツなしイベントはNoneを返す"""
        from app.services.adk.memory.converters import extract_text_from_event

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
        )

        result = extract_text_from_event(event)

        assert result is None

    def test_returns_none_for_event_without_parts(self) -> None:
        """パーツなしイベントはNoneを返す"""
        from app.services.adk.memory.converters import extract_text_from_event

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(role="user", parts=[]),
        )

        result = extract_text_from_event(event)

        assert result is None

    def test_skips_parts_without_text(self) -> None:
        """テキストなしパーツはスキップする"""
        from app.services.adk.memory.converters import extract_text_from_event

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(
                role="user",
                parts=[
                    types.Part(text="Has text"),
                    types.Part(),  # テキストなし
                    types.Part(text="Also has text"),
                ],
            ),
        )

        result = extract_text_from_event(event)

        assert result == "Has text Also has text"


class TestEventToMemoryDict:
    """event_to_memory_dict関数のテスト"""

    def test_converts_basic_event(self) -> None:
        """基本的なイベントをdictに変換する"""
        from app.services.adk.memory.converters import event_to_memory_dict

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(
                role="user",
                parts=[types.Part(text="Test message")],
            ),
        )

        result = event_to_memory_dict(event, session_id="session-1")

        assert result is not None
        assert result["event_id"] == "event-1"
        assert result["session_id"] == "session-1"
        assert result["author"] == "user"
        assert result["timestamp"] == 1234567890.0
        assert result["content"]["role"] == "user"
        assert len(result["content"]["parts"]) == 1
        assert result["content"]["parts"][0]["text"] == "Test message"

    def test_converts_event_with_model_author(self) -> None:
        """モデルからのイベントを変換する"""
        from app.services.adk.memory.converters import event_to_memory_dict

        event = Event(
            id="event-2",
            invocation_id="inv-1",
            author="model",
            timestamp=1234567891.0,
            content=types.Content(
                role="model",
                parts=[types.Part(text="Response from model")],
            ),
        )

        result = event_to_memory_dict(event, session_id="session-1")

        assert result is not None
        assert result["author"] == "model"
        assert result["content"]["role"] == "model"

    def test_converts_event_with_multiple_parts(self) -> None:
        """複数パーツのイベントを変換する"""
        from app.services.adk.memory.converters import event_to_memory_dict

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(
                role="user",
                parts=[
                    types.Part(text="Part 1"),
                    types.Part(text="Part 2"),
                ],
            ),
        )

        result = event_to_memory_dict(event, session_id="session-1")

        assert result is not None
        assert len(result["content"]["parts"]) == 2
        assert result["content"]["parts"][0]["text"] == "Part 1"
        assert result["content"]["parts"][1]["text"] == "Part 2"

    def test_includes_custom_metadata(self) -> None:
        """カスタムメタデータを含める"""
        from app.services.adk.memory.converters import event_to_memory_dict

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
            content=types.Content(
                role="user",
                parts=[types.Part(text="Test")],
            ),
        )
        custom_metadata = {"memory_type": "learning_insight", "tags": ["math"]}

        result = event_to_memory_dict(
            event, session_id="session-1", custom_metadata=custom_metadata
        )

        assert result is not None
        assert result["custom_metadata"] == custom_metadata

    def test_returns_none_for_event_without_content(self) -> None:
        """コンテンツなしイベントはNoneを返す"""
        from app.services.adk.memory.converters import event_to_memory_dict

        event = Event(
            id="event-1",
            invocation_id="inv-1",
            author="user",
            timestamp=1234567890.0,
        )

        result = event_to_memory_dict(event, session_id="session-1")

        assert result is None


class TestDictToMemoryEntry:
    """dict_to_memory_entry関数のテスト"""

    def test_converts_basic_dict(self) -> None:
        """基本的なdictをMemoryEntryに変換する"""
        from app.services.adk.memory.converters import dict_to_memory_entry

        data = {
            "event_id": "event-1",
            "session_id": "session-1",
            "author": "user",
            "timestamp": 1234567890.0,
            "content": {
                "role": "user",
                "parts": [{"text": "Test message"}],
            },
            "custom_metadata": {},
        }

        result = dict_to_memory_entry(data)

        assert isinstance(result, MemoryEntry)
        assert result.author == "user"
        assert result.content.role == "user"
        assert result.content.parts is not None
        assert len(result.content.parts) == 1

    def test_converts_dict_with_custom_metadata(self) -> None:
        """カスタムメタデータ付きdictを変換する"""
        from app.services.adk.memory.converters import dict_to_memory_entry

        data = {
            "event_id": "event-1",
            "session_id": "session-1",
            "author": "user",
            "timestamp": 1234567890.0,
            "content": {
                "role": "user",
                "parts": [{"text": "Test"}],
            },
            "custom_metadata": {"memory_type": "learning_insight"},
        }

        result = dict_to_memory_entry(data)

        assert result.custom_metadata == {"memory_type": "learning_insight"}

    def test_formats_timestamp_as_iso(self) -> None:
        """タイムスタンプをISO形式に変換する"""
        from app.services.adk.memory.converters import dict_to_memory_entry

        data = {
            "event_id": "event-1",
            "session_id": "session-1",
            "author": "user",
            "timestamp": 1234567890.0,
            "content": {
                "role": "user",
                "parts": [{"text": "Test"}],
            },
            "custom_metadata": {},
        }

        result = dict_to_memory_entry(data)

        assert result.timestamp is not None
        # ISO形式のタイムスタンプ
        assert "2009-02-13" in result.timestamp  # 1234567890はこの日付


class TestExtractWordsLower:
    """extract_words_lower関数のテスト"""

    def test_extracts_english_words(self) -> None:
        """英単語を抽出する"""
        from app.services.adk.memory.converters import extract_words_lower

        result = extract_words_lower("Hello World Test")

        assert result == {"hello", "world", "test"}

    def test_converts_to_lowercase(self) -> None:
        """小文字に変換する"""
        from app.services.adk.memory.converters import extract_words_lower

        result = extract_words_lower("HELLO World TeSt")

        assert result == {"hello", "world", "test"}

    def test_handles_japanese_text(self) -> None:
        """日本語テキストは英単語のみ抽出"""
        from app.services.adk.memory.converters import extract_words_lower

        result = extract_words_lower("こんにちは Hello 世界 World")

        assert result == {"hello", "world"}

    def test_handles_empty_string(self) -> None:
        """空文字列は空セットを返す"""
        from app.services.adk.memory.converters import extract_words_lower

        result = extract_words_lower("")

        assert result == set()

    def test_handles_numbers_and_special_chars(self) -> None:
        """数字と特殊文字は除外"""
        from app.services.adk.memory.converters import extract_words_lower

        result = extract_words_lower("Hello 123 World! Test@example.com")

        assert result == {"hello", "world", "test", "example", "com"}
