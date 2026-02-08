"""Review Agent

セッション振り返り・保護者レポートを担当するエージェント。
"""

from typing import TYPE_CHECKING

from google.adk.agents import Agent

from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT
from app.services.adk.tools import record_progress_tool, search_memory_tool

if TYPE_CHECKING:
    from google.adk.agents import Agent as AgentType

DEFAULT_MODEL = "gemini-2.5-flash"


def create_review_agent(model: str | None = None) -> "AgentType":
    """振り返りエージェントを作成する

    Args:
        model: 使用するモデル名（デフォルト: gemini-2.5-flash）

    Returns:
        Agent: ADK Agentインスタンス
    """
    return Agent(
        name="review_agent",
        model=model or DEFAULT_MODEL,
        instruction=REVIEW_SYSTEM_PROMPT,
        description="今日の学習を振り返り、何を頑張ったかを一緒に確認する。保護者向けのサマリーも作る。",
        tools=[
            record_progress_tool,
            search_memory_tool,  # Phase 2c: セマンティック記憶検索
        ],
    )
