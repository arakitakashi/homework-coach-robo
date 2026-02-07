"""E2Eテスト用 MockAgentRunnerService

Gemini APIへの接続を行わず、定型レスポンスを返すモックサービス。
E2E_MODE=true 時に AgentRunnerService の代替として使用される。
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class _MockPart:
    """ADK Event.content.parts の要素を模擬"""

    text: str | None = None


@dataclass
class _MockContent:
    """ADK Event.content を模擬"""

    parts: list[_MockPart] = field(default_factory=list)


@dataclass
class _MockEvent:
    """ADK Event を模擬"""

    content: _MockContent | None = None


# ソクラテス式対話の定型レスポンス
_SOCRATIC_RESPONSES: list[str] = [
    "いい質問だね！",
    "いっしょに考えよう！",
    "この問題は何を聞いていると思う？",
]


class MockAgentRunnerService:
    """E2Eテスト用モックエージェントランナーサービス

    Gemini APIを呼び出さず、定型レスポンスをストリーミングで返す。
    """

    def __init__(self, **kwargs: Any) -> None:  # noqa: ARG002 - DI互換のため
        pass

    async def run(
        self,
        user_id: str,  # noqa: ARG002
        session_id: str,  # noqa: ARG002
        message: str,  # noqa: ARG002
    ) -> AsyncIterator[_MockEvent]:
        """定型レスポンスをイベントとしてストリーム"""
        for text in _SOCRATIC_RESPONSES:
            yield _MockEvent(content=_MockContent(parts=[_MockPart(text=text)]))

    def extract_text(self, event: _MockEvent) -> str | None:
        """イベントからテキストを抽出"""
        if not event.content:
            return None
        if not event.content.parts:
            return None
        texts = [part.text for part in event.content.parts if part.text]
        if not texts:
            return None
        return " ".join(texts)
