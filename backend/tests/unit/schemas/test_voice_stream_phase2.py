"""Phase 2 WebSocketイベントスキーマのテスト"""

from app.schemas.voice_stream import (
    ADKAgentTransitionEvent,
    ADKEmotionUpdateEvent,
    ADKEventMessage,
    ADKToolExecutionEvent,
)


class TestADKToolExecutionEvent:
    """ADKToolExecutionEventのテスト"""

    def test_create_with_required_fields(self) -> None:
        """必須フィールドでインスタンス作成"""
        event = ADKToolExecutionEvent(
            toolName="calculate_tool",
            status="running",
        )
        assert event.toolName == "calculate_tool"
        assert event.status == "running"
        assert event.result is None

    def test_create_with_result(self) -> None:
        """結果付きでインスタンス作成"""
        event = ADKToolExecutionEvent(
            toolName="calculate_tool",
            status="completed",
            result={"answer": 42},
        )
        assert event.toolName == "calculate_tool"
        assert event.status == "completed"
        assert event.result == {"answer": 42}


class TestADKAgentTransitionEvent:
    """ADKAgentTransitionEventのテスト"""

    def test_create_with_all_fields(self) -> None:
        """全フィールドでインスタンス作成"""
        event = ADKAgentTransitionEvent(
            fromAgent="router_agent",
            toAgent="math_coach",
            reason="算数の問題が検出されました",
        )
        assert event.fromAgent == "router_agent"
        assert event.toAgent == "math_coach"
        assert event.reason == "算数の問題が検出されました"


class TestADKEmotionUpdateEvent:
    """ADKEmotionUpdateEventのテスト"""

    def test_create_with_all_fields(self) -> None:
        """全フィールドでインスタンス作成"""
        event = ADKEmotionUpdateEvent(
            emotion="frustrated",
            frustrationLevel=0.7,
            engagementLevel=0.3,
        )
        assert event.emotion == "frustrated"
        assert event.frustrationLevel == 0.7
        assert event.engagementLevel == 0.3


class TestADKEventMessagePhase2:
    """ADKEventMessage Phase 2フィールドのテスト"""

    def test_event_with_tool_execution(self) -> None:
        """toolExecutionフィールド付きイベント"""
        event = ADKEventMessage(
            author="agent",
            toolExecution=ADKToolExecutionEvent(
                toolName="calculate_tool",
                status="running",
            ),
        )
        assert event.author == "agent"
        assert event.toolExecution is not None
        assert event.toolExecution.toolName == "calculate_tool"
        assert event.toolExecution.status == "running"

    def test_event_with_agent_transition(self) -> None:
        """agentTransitionフィールド付きイベント"""
        event = ADKEventMessage(
            author="agent",
            agentTransition=ADKAgentTransitionEvent(
                fromAgent="router_agent",
                toAgent="math_coach",
                reason="算数の問題が検出されました",
            ),
        )
        assert event.author == "agent"
        assert event.agentTransition is not None
        assert event.agentTransition.fromAgent == "router_agent"
        assert event.agentTransition.toAgent == "math_coach"

    def test_event_with_emotion_update(self) -> None:
        """emotionUpdateフィールド付きイベント"""
        event = ADKEventMessage(
            author="agent",
            emotionUpdate=ADKEmotionUpdateEvent(
                emotion="frustrated",
                frustrationLevel=0.7,
                engagementLevel=0.3,
            ),
        )
        assert event.author == "agent"
        assert event.emotionUpdate is not None
        assert event.emotionUpdate.emotion == "frustrated"
        assert event.emotionUpdate.frustrationLevel == 0.7

    def test_event_with_multiple_phase2_fields(self) -> None:
        """複数のPhase 2フィールド付きイベント"""
        event = ADKEventMessage(
            author="agent",
            turnComplete=True,
            toolExecution=ADKToolExecutionEvent(
                toolName="calculate_tool",
                status="completed",
                result={"answer": 42},
            ),
            emotionUpdate=ADKEmotionUpdateEvent(
                emotion="engaged",
                frustrationLevel=0.2,
                engagementLevel=0.8,
            ),
        )
        assert event.author == "agent"
        assert event.turnComplete is True
        assert event.toolExecution is not None
        assert event.toolExecution.status == "completed"
        assert event.emotionUpdate is not None
        assert event.emotionUpdate.emotion == "engaged"
