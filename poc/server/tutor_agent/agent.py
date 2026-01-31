"""宿題コーチエージェント定義"""

from google.adk.agents import Agent
from .prompts import SYSTEM_INSTRUCTION

# ADK規約: root_agentという名前で定義
root_agent = Agent(
    name="homework_tutor",
    # Google AI Studio (Gemini Live API) 用モデル
    # refs/adk-python/contributing/samples/live_bidi_streaming_single_agent/agent.py と同じモデル
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    description="小学生向け宿題サポートエージェント - ソクラテス式対話で子供の思考を導く",
    instruction=SYSTEM_INSTRUCTION,
)
