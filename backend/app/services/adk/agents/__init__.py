"""ADK マルチエージェント定義。

Phase 2b: Router Agent + 4つの専門サブエージェント。
"""

from app.services.adk.agents.encouragement import create_encouragement_agent
from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
from app.services.adk.agents.math_coach import create_math_coach_agent
from app.services.adk.agents.review import create_review_agent
from app.services.adk.agents.router import create_router_agent

__all__ = [
    "create_router_agent",
    "create_math_coach_agent",
    "create_japanese_coach_agent",
    "create_encouragement_agent",
    "create_review_agent",
]
