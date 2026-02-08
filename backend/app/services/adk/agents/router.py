"""Router Agent

教科・状況に応じてサブエージェントに振り分けるルーターエージェント。
"""

from typing import TYPE_CHECKING

from google.adk.agents import Agent

from app.services.adk.agents.encouragement import create_encouragement_agent
from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
from app.services.adk.agents.math_coach import create_math_coach_agent
from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT
from app.services.adk.agents.review import create_review_agent

if TYPE_CHECKING:
    from google.adk.agents import Agent as AgentType

DEFAULT_MODEL = "gemini-2.5-flash"


def create_router_agent(model: str | None = None) -> "AgentType":
    """ルーターエージェントを作成する

    Router Agent はサブエージェントへの振り分けのみを行い、
    自身ではツールを持たない。ADK AutoFlow により、LLM が
    入力内容に基づき適切なサブエージェントに委譲する。

    Args:
        model: 使用するモデル名（デフォルト: gemini-2.5-flash）

    Returns:
        Agent: ADK Agentインスタンス
    """
    return Agent(
        name="router_agent",
        model=model or DEFAULT_MODEL,
        instruction=ROUTER_SYSTEM_PROMPT,
        description="子供の宿題を手伝うロボットチームのリーダー。入力を分析して最適な専門コーチに繋ぐ。",
        sub_agents=[
            create_math_coach_agent(model=model),
            create_japanese_coach_agent(model=model),
            create_encouragement_agent(model=model),
            create_review_agent(model=model),
        ],
    )
