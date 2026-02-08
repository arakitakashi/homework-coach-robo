"""RAG data models and utilities."""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RagDocument:
    """Document to be indexed in RAG Corpus.

    Attributes:
        document_id: Unique identifier for the document
        content: Text content to be indexed and searched (Japanese)
        metadata: Additional metadata for filtering and ranking
    """

    document_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RagSearchResult:
    """Search result from RAG Corpus.

    Attributes:
        document_id: ID of the matched document
        content: Matched content
        metadata: Document metadata
        relevance_score: Similarity score (0.0-1.0)
    """

    document_id: str
    content: str
    metadata: dict[str, Any]
    relevance_score: float


def sanitize_content(content: str) -> str:
    """Sanitize content by masking personally identifiable information.

    This function removes or masks PII from content before indexing to RAG Corpus,
    ensuring child privacy protection.

    Args:
        content: Original content that may contain PII

    Returns:
        Sanitized content with PII replaced by generic placeholders

    Examples:
        >>> sanitize_content("たろうくん、頑張ったね！")
        '[子供]、頑張ったね！'

        >>> sanitize_content("お母さんに見せてね。")
        '[保護者]に見せてね。'
    """
    if not content:
        return content

    # Replace child names with [子供]
    # Pattern: common names + くん/さん suffix
    # Examples: たろうくん, はなこさん, ゆうきくん
    content = re.sub(r"[ぁ-ん]{2,4}(くん|さん)", "[子供]", content)

    # Replace common standalone names (太郎, 花子)
    content = re.sub(r"(太郎|花子)", "[子供]", content)

    # Replace parent references with [保護者]
    content = re.sub(r"お母さん", "[保護者]", content)
    content = re.sub(r"お父さん", "[保護者]", content)

    return content
