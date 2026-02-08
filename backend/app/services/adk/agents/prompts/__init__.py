"""エージェント別プロンプト定義。

各エージェントのシステムプロンプトを提供する。
"""

from app.services.adk.agents.prompts.encouragement import ENCOURAGEMENT_SYSTEM_PROMPT
from app.services.adk.agents.prompts.japanese_coach import JAPANESE_COACH_SYSTEM_PROMPT
from app.services.adk.agents.prompts.math_coach import MATH_COACH_SYSTEM_PROMPT
from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT
from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

__all__ = [
    "ROUTER_SYSTEM_PROMPT",
    "MATH_COACH_SYSTEM_PROMPT",
    "JAPANESE_COACH_SYSTEM_PROMPT",
    "ENCOURAGEMENT_SYSTEM_PROMPT",
    "REVIEW_SYSTEM_PROMPT",
]
