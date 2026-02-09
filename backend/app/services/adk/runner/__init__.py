"""ADK Runner package.

ソクラテス式対話エージェントとランナーサービス。
Agent Engine クライアント。
"""

from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT, create_socratic_agent
from app.services.adk.runner.agent_engine_client import AgentEngineClient
from app.services.adk.runner.runner_service import AgentRunnerService

__all__ = [
    "AgentEngineClient",
    "AgentRunnerService",
    "SOCRATIC_SYSTEM_PROMPT",
    "create_socratic_agent",
]
