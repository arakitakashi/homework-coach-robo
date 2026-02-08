"""Encouragement Agent

励まし・休憩提案を担当するエージェント。
"""

from typing import TYPE_CHECKING

from google.adk.agents import Agent

from app.services.adk.agents.prompts.encouragement import ENCOURAGEMENT_SYSTEM_PROMPT
from app.services.adk.tools import record_progress_tool

if TYPE_CHECKING:
    from google.adk.agents import Agent as AgentType

DEFAULT_MODEL = "gemini-2.5-flash"


def create_encouragement_agent(model: str | None = None) -> "AgentType":
    """励ましエージェントを作成する

    Args:
        model: 使用するモデル名（デフォルト: gemini-2.5-flash）

    Returns:
        Agent: ADK Agentインスタンス
    """
    return Agent(
        name="encouragement_agent",
        model=model or DEFAULT_MODEL,
        instruction=ENCOURAGEMENT_SYSTEM_PROMPT,
        description="疲れた、わからない、やめたいなどネガティブな気持ちの子供を励まし、休憩を提案する。",
        tools=[
            record_progress_tool,
        ],
    )
