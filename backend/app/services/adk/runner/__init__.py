"""ADK Runner package.

ソクラテス式対話エージェントとランナーサービス。
Agent Engine クライアント。Agent Engine デプロイ用ラッパー。
"""

from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT, create_socratic_agent
from app.services.adk.runner.agent_engine_client import AgentEngineClient
from app.services.adk.runner.homework_coach_agent import HomeworkCoachAgent
from app.services.adk.runner.runner_service import AgentRunnerService

__all__ = [
    "AgentEngineClient",
    "AgentRunnerService",
    "HomeworkCoachAgent",
    "SOCRATIC_SYSTEM_PROMPT",
    "create_socratic_agent",
]
