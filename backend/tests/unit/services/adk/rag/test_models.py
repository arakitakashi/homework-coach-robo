"""Unit tests for RAG models."""

import pytest

from app.services.adk.rag.models import RagDocument, sanitize_content


class TestRagDocument:
    """Tests for RagDocument dataclass."""

    def test_create_minimal_document(self) -> None:
        """Test creating a document with minimal required fields."""
        doc = RagDocument(
            document_id="test-doc-1",
            content="これは算数の問題です。",
        )

        assert doc.document_id == "test-doc-1"
        assert doc.content == "これは算数の問題です。"
        assert doc.metadata == {}

    def test_create_document_with_metadata(self) -> None:
        """Test creating a document with metadata."""
        metadata = {
            "user_id": "user-123",
            "session_id": "session-456",
            "category": "dialogue",
            "subject": "math",
            "grade": 2,
            "timestamp": "2026-02-08T10:00:00Z",
            "problem_type": "addition",
            "difficulty": 3,
            "outcome": "self_solved",
        }

        doc = RagDocument(
            document_id="test-doc-2",
            content="23 + 45 を自分で解けた！",
            metadata=metadata,
        )

        assert doc.document_id == "test-doc-2"
        assert doc.content == "23 + 45 を自分で解けた！"
        assert doc.metadata["user_id"] == "user-123"
        assert doc.metadata["grade"] == 2
        assert doc.metadata["outcome"] == "self_solved"

    def test_document_id_required(self) -> None:
        """Test that document_id is required."""
        with pytest.raises(TypeError):
            RagDocument(content="テスト")  # type: ignore

    def test_content_required(self) -> None:
        """Test that content is required."""
        with pytest.raises(TypeError):
            RagDocument(document_id="test-doc")  # type: ignore


class TestSanitizeContent:
    """Tests for sanitize_content function."""

    def test_sanitize_child_name_kun(self) -> None:
        """Test sanitizing child name with くん suffix."""
        content = "たろうくん、今日は頑張ったね！"
        result = sanitize_content(content)
        assert result == "[子供]、今日は頑張ったね！"

    def test_sanitize_child_name_san(self) -> None:
        """Test sanitizing child name with さん suffix."""
        content = "はなこさん、よくできました！"
        result = sanitize_content(content)
        assert result == "[子供]、よくできました！"

    def test_sanitize_parent_name_mother(self) -> None:
        """Test sanitizing parent name (mother)."""
        content = "お母さんに見せてあげようね。"
        result = sanitize_content(content)
        assert result == "[保護者]に見せてあげようね。"

    def test_sanitize_parent_name_father(self) -> None:
        """Test sanitizing parent name (father)."""
        content = "お父さんが帰ってきたら報告しよう。"
        result = sanitize_content(content)
        assert result == "[保護者]が帰ってきたら報告しよう。"

    def test_sanitize_multiple_names(self) -> None:
        """Test sanitizing multiple names in one content."""
        content = "ゆうきくんとお母さんで一緒に復習してね。"
        result = sanitize_content(content)
        assert result == "[子供]と[保護者]で一緒に復習してね。"

    def test_sanitize_common_names(self) -> None:
        """Test sanitizing common Japanese children's names."""
        test_cases = [
            ("太郎は23を答えました。", "[子供]は23を答えました。"),
            ("花子が問題を解いています。", "[子供]が問題を解いています。"),
            ("けんたくん、すごい！", "[子供]、すごい！"),
        ]

        for content, expected in test_cases:
            result = sanitize_content(content)
            assert result == expected

    def test_sanitize_no_pii(self) -> None:
        """Test that content without PII is unchanged."""
        content = "23 + 45 = 68 です。よくできましたね！"
        result = sanitize_content(content)
        assert result == content

    def test_sanitize_empty_string(self) -> None:
        """Test sanitizing empty string."""
        result = sanitize_content("")
        assert result == ""

    def test_sanitize_preserves_math_content(self) -> None:
        """Test that mathematical content is preserved."""
        content = "繰り上がりの計算で23 + 45を解きました。"
        result = sanitize_content(content)
        # Should preserve numbers and mathematical expressions
        assert "23 + 45" in result
