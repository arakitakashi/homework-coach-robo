"""Math Coach Agent

算数に特化したソクラテス式対話コーチエージェント。
"""

from typing import TYPE_CHECKING

from google.adk.agents import Agent

from app.services.adk.agents.prompts.math_coach import MATH_COACH_SYSTEM_PROMPT
from app.services.adk.tools import (
    calculate_tool,
    check_curriculum_tool,
    manage_hint_tool,
    record_progress_tool,
)

if TYPE_CHECKING:
    from google.adk.agents import Agent as AgentType

DEFAULT_MODEL = "gemini-2.5-flash"


def create_math_coach_agent(model: str | None = None) -> "AgentType":
    """算数コーチエージェントを作成する

    Args:
        model: 使用するモデル名（デフォルト: gemini-2.5-flash）

    Returns:
        Agent: ADK Agentインスタンス
    """
    return Agent(
        name="math_coach",
        model=model or DEFAULT_MODEL,
        instruction=MATH_COACH_SYSTEM_PROMPT,
        description="算数の問題を解く手助けをする専門コーチ。計算、文章題、図形などに対応。",
        tools=[
            calculate_tool,
            manage_hint_tool,
            check_curriculum_tool,
            record_progress_tool,
        ],
    )
