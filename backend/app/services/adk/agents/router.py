"""Router Agent

教科・状況・感情に応じてサブエージェントに振り分けるルーターエージェント。
"""

from typing import TYPE_CHECKING

from google.adk.agents import Agent

from app.services.adk.agents.encouragement import create_encouragement_agent
from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
from app.services.adk.agents.math_coach import create_math_coach_agent
from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT
from app.services.adk.agents.review import create_review_agent
from app.services.adk.tools.emotion_analyzer import update_emotion_tool

if TYPE_CHECKING:
    from google.adk.agents import Agent as AgentType

DEFAULT_MODEL = "gemini-2.5-flash"


def create_router_agent(model: str | None = None) -> "AgentType":
    """ルーターエージェントを作成する

    Router Agent は子供の感情を分析し（update_emotion_tool）、
    感情状態と入力内容に基づいてサブエージェントに委譲する。

    Args:
        model: 使用するモデル名（デフォルト: gemini-2.5-flash）

    Returns:
        Agent: ADK Agentインスタンス
    """
    return Agent(
        name="router_agent",
        model=model or DEFAULT_MODEL,
        instruction=ROUTER_SYSTEM_PROMPT,
        description="子供の宿題を手伝うロボットチームのリーダー。感情を分析し、最適な専門コーチに繋ぐ。",
        tools=[update_emotion_tool],
        sub_agents=[
            create_math_coach_agent(model=model),
            create_japanese_coach_agent(model=model),
            create_encouragement_agent(model=model),
            create_review_agent(model=model),
        ],
    )
