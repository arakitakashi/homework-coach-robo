"""Japanese Coach Agent

国語に特化したソクラテス式対話コーチエージェント。
"""

from typing import TYPE_CHECKING

from google.adk.agents import Agent

from app.services.adk.agents.prompts.japanese_coach import JAPANESE_COACH_SYSTEM_PROMPT
from app.services.adk.tools import (
    check_curriculum_tool,
    manage_hint_tool,
    record_progress_tool,
)

if TYPE_CHECKING:
    from google.adk.agents import Agent as AgentType

DEFAULT_MODEL = "gemini-2.5-flash"


def create_japanese_coach_agent(model: str | None = None) -> "AgentType":
    """国語コーチエージェントを作成する

    Args:
        model: 使用するモデル名（デフォルト: gemini-2.5-flash）

    Returns:
        Agent: ADK Agentインスタンス
    """
    return Agent(
        name="japanese_coach",
        model=model or DEFAULT_MODEL,
        instruction=JAPANESE_COACH_SYSTEM_PROMPT,
        description="国語の問題を解く手助けをする専門コーチ。漢字、読解、作文に対応。",
        tools=[
            manage_hint_tool,
            check_curriculum_tool,
            record_progress_tool,
        ],
    )
