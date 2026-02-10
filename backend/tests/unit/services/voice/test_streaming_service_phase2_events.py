"""Phase 2 WebSocketイベント変換のテスト"""

from unittest.mock import MagicMock, patch

from app.schemas.voice_stream import (
    ADKAgentTransitionEvent,
    ADKEmotionUpdateEvent,
    ADKToolExecutionEvent,
)
from app.services.voice.streaming_service import VoiceStreamingService


def create_mock_event(
    *,
    author: str = "agent",
    turn_complete: bool | None = None,
    tool_execution: dict[str, object] | None = None,
    agent_transition: dict[str, str] | None = None,
    emotion_update: dict[str, object] | None = None,
) -> MagicMock:
    """テスト用のモックEventを作成する

    Args:
        author: イベント発行者
        turn_complete: ターン完了フラグ
        tool_execution: ツール実行イベント（{"tool_name": ..., "status": ..., "result": ...}）
        agent_transition: エージェント遷移イベント（{"from_agent": ..., "to_agent": ..., "reason": ...}）
        emotion_update: 感情更新イベント（{"emotion": ..., "frustration_level": ..., "engagement_level": ...}）
    """
    event = MagicMock()
    event.author = author
    event.turn_complete = turn_complete
    event.interrupted = None
    event.input_transcription = None
    event.output_transcription = None
    event.content = None
    event.partial = None
    event.usage_metadata = None

    # Phase 2: カスタム属性として追加
    event.tool_execution = None
    event.agent_transition = None
    event.emotion_update = None

    if tool_execution:
        tool_exec = MagicMock()
        tool_exec.tool_name = tool_execution.get("tool_name")
        tool_exec.status = tool_execution.get("status")
        tool_exec.result = tool_execution.get("result")
        event.tool_execution = tool_exec

    if agent_transition:
        agent_trans = MagicMock()
        agent_trans.from_agent = agent_transition.get("from_agent")
        agent_trans.to_agent = agent_transition.get("to_agent")
        agent_trans.reason = agent_transition.get("reason")
        event.agent_transition = agent_trans

    if emotion_update:
        emotion_upd = MagicMock()
        emotion_upd.emotion = emotion_update.get("emotion")
        emotion_upd.frustration_level = emotion_update.get("frustration_level")
        emotion_upd.engagement_level = emotion_update.get("engagement_level")
        event.emotion_update = emotion_upd

    return event


class TestConvertEventToMessagePhase2:
    """Phase 2イベント変換のテスト"""

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_tool_execution_event(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """ツール実行イベントを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            author="agent",
            tool_execution={
                "tool_name": "calculate_tool",
                "status": "running",
            },
        )
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.author == "agent"
        assert result.toolExecution is not None
        assert isinstance(result.toolExecution, ADKToolExecutionEvent)
        assert result.toolExecution.toolName == "calculate_tool"
        assert result.toolExecution.status == "running"
        assert result.toolExecution.result is None

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_tool_execution_with_result(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """結果付きツール実行イベントを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            author="agent",
            tool_execution={
                "tool_name": "calculate_tool",
                "status": "completed",
                "result": {"answer": 42},
            },
        )
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.toolExecution is not None
        assert result.toolExecution.toolName == "calculate_tool"
        assert result.toolExecution.status == "completed"
        assert result.toolExecution.result == {"answer": 42}

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_agent_transition_event(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """エージェント遷移イベントを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            author="agent",
            agent_transition={
                "from_agent": "router_agent",
                "to_agent": "math_coach",
                "reason": "算数の問題が検出されました",
            },
        )
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.author == "agent"
        assert result.agentTransition is not None
        assert isinstance(result.agentTransition, ADKAgentTransitionEvent)
        assert result.agentTransition.fromAgent == "router_agent"
        assert result.agentTransition.toAgent == "math_coach"
        assert result.agentTransition.reason == "算数の問題が検出されました"

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_emotion_update_event(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """感情更新イベントを変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            author="agent",
            emotion_update={
                "emotion": "frustrated",
                "frustration_level": 0.7,
                "engagement_level": 0.3,
            },
        )
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.author == "agent"
        assert result.emotionUpdate is not None
        assert isinstance(result.emotionUpdate, ADKEmotionUpdateEvent)
        assert result.emotionUpdate.emotion == "frustrated"
        assert result.emotionUpdate.frustrationLevel == 0.7
        assert result.emotionUpdate.engagementLevel == 0.3

    @patch("app.services.voice.streaming_service.Runner")
    @patch("app.services.voice.streaming_service.create_router_agent")
    def test_converts_multiple_phase2_events(
        self,
        _mock_create_agent: MagicMock,
        _mock_runner_cls: MagicMock,
    ) -> None:
        """複数のPhase 2イベントを同時に変換する"""
        service = VoiceStreamingService(
            session_service=MagicMock(),
            memory_service=MagicMock(),
        )

        event = create_mock_event(
            author="agent",
            turn_complete=True,
            tool_execution={
                "tool_name": "calculate_tool",
                "status": "completed",
                "result": {"answer": 42},
            },
            emotion_update={
                "emotion": "engaged",
                "frustration_level": 0.2,
                "engagement_level": 0.8,
            },
        )
        result = service._convert_event_to_message(event)

        assert result is not None
        assert result.author == "agent"
        assert result.turnComplete is True
        assert result.toolExecution is not None
        assert result.toolExecution.status == "completed"
        assert result.emotionUpdate is not None
        assert result.emotionUpdate.emotion == "engaged"
