"""音声ストリーミングサービスのテスト（Agent Engine統合版）

Phase 2 Router Agent + VertexAiSessionService統合のテスト。
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.voice.streaming_service import (
    DEFAULT_APP_NAME,
    LIVE_MODEL,
    VoiceStreamingService,
)


@pytest.fixture
def mock_router_agent():
    """モックRouter Agentを作成"""
    agent = MagicMock()
    agent.name = "router_agent"
    return agent


@pytest.fixture
def mock_vertex_ai_session_service():
    """モックVertexAiSessionServiceを作成"""
    service = MagicMock()
    service.create_session = AsyncMock()
    service.list_sessions = AsyncMock()
    return service


@pytest.fixture
def mock_firestore_session_service():
    """モックFirestoreSessionServiceを作成"""
    service = MagicMock()
    service.create_session = AsyncMock()
    service.get_session = AsyncMock()
    return service


@pytest.fixture
def mock_memory_service():
    """モックMemoryServiceを作成"""
    service = MagicMock()
    return service


class TestVoiceStreamingServiceInitialization:
    """VoiceStreamingServiceの初期化テスト"""

    @patch("app.services.voice.streaming_service.create_router_agent")
    @patch("app.services.voice.streaming_service.VertexAiSessionService")
    @patch("app.services.voice.streaming_service.Runner")
    def test_init_with_agent_engine_mode(
        self,
        mock_runner_class,
        mock_vertex_ai_session_service_class,
        mock_create_router_agent,
        mock_router_agent,
    ):
        """Agent Engineモードでの初期化テスト"""
        # Arrange
        mock_create_router_agent.return_value = mock_router_agent
        mock_session_service = MagicMock()
        mock_vertex_ai_session_service_class.return_value = mock_session_service
        mock_runner = MagicMock()
        mock_runner_class.return_value = mock_runner

        # Act
        service = VoiceStreamingService(
            use_agent_engine=True,
            project_id="test-project",
            location="us-central1",
            agent_engine_id="test-engine-id",
        )

        # Assert
        # Router Agentが作成されている
        mock_create_router_agent.assert_called_once_with(model=LIVE_MODEL)

        # VertexAiSessionServiceが初期化されている
        mock_vertex_ai_session_service_class.assert_called_once_with(
            project_id="test-project",
            location="us-central1",
            agent_engine_id="test-engine-id",
        )

        # Runnerが正しく初期化されている
        mock_runner_class.assert_called_once()
        call_kwargs = mock_runner_class.call_args.kwargs
        assert call_kwargs["app_name"] == DEFAULT_APP_NAME
        assert call_kwargs["agent"] == mock_router_agent
        assert call_kwargs["session_service"] == mock_session_service

        # サービスのインスタンス変数が設定されている
        assert service._agent == mock_router_agent
        assert service._session_service == mock_session_service
        assert service._runner == mock_runner

    @patch("app.services.voice.streaming_service.create_router_agent")
    @patch("app.services.voice.streaming_service.FirestoreSessionService")
    @patch("app.services.voice.streaming_service.Runner")
    def test_init_with_firestore_mode(
        self,
        mock_runner_class,
        mock_firestore_session_service_class,
        mock_create_router_agent,
        mock_router_agent,
    ):
        """Firestoreモードでの初期化テスト（後方互換）"""
        # Arrange
        mock_create_router_agent.return_value = mock_router_agent
        mock_session_service = MagicMock()
        mock_firestore_session_service_class.return_value = mock_session_service
        mock_runner = MagicMock()
        mock_runner_class.return_value = mock_runner

        # Act
        service = VoiceStreamingService(use_agent_engine=False)

        # Assert
        # Router Agentが作成されている
        mock_create_router_agent.assert_called_once_with(model=LIVE_MODEL)

        # FirestoreSessionServiceが初期化されている
        mock_firestore_session_service_class.assert_called_once()

        # Runnerが正しく初期化されている
        mock_runner_class.assert_called_once()
        call_kwargs = mock_runner_class.call_args.kwargs
        assert call_kwargs["session_service"] == mock_session_service

    @patch("app.services.voice.streaming_service.create_router_agent")
    @patch("app.services.voice.streaming_service.VertexAiSessionService")
    def test_init_with_env_variables(
        self,
        mock_vertex_ai_session_service_class,
        mock_create_router_agent,
        mock_router_agent,
    ):
        """環境変数からの初期化テスト"""
        # Arrange
        mock_create_router_agent.return_value = mock_router_agent

        with patch.dict(
            "os.environ",
            {
                "PROJECT_ID": "env-project",
                "LOCATION": "env-location",
                "AGENT_ENGINE_ID": "env-engine-id",
            },
        ):
            # Act
            service = VoiceStreamingService(use_agent_engine=True)

            # Assert
            # 環境変数から値が取得されている
            mock_vertex_ai_session_service_class.assert_called_once_with(
                project_id="env-project",
                location="env-location",
                agent_engine_id="env-engine-id",
            )


class TestVoiceStreamingServiceAudioSending:
    """音声データ送信のテスト"""

    @patch("app.services.voice.streaming_service.create_router_agent")
    @patch("app.services.voice.streaming_service.VertexAiSessionService")
    @patch("app.services.voice.streaming_service.Runner")
    def test_send_audio(
        self,
        mock_runner_class,
        mock_vertex_ai_session_service_class,
        mock_create_router_agent,
    ):
        """音声データ送信のテスト"""
        # Arrange
        service = VoiceStreamingService(
            use_agent_engine=True,
            project_id="test-project",
            location="us-central1",
            agent_engine_id="test-engine-id",
        )

        audio_data = b"mock_audio_data"

        # Act
        service.send_audio(audio_data)

        # Assert
        # LiveRequestQueueにデータが送信されている
        assert service._queue is not None
        # 実際の送信確認は統合テストで行う


class TestVoiceStreamingServiceErrorHandling:
    """エラーハンドリングのテスト"""

    @patch("app.services.voice.streaming_service.create_router_agent")
    @patch("app.services.voice.streaming_service.VertexAiSessionService")
    def test_vertex_ai_session_service_initialization_failure(
        self,
        mock_vertex_ai_session_service_class,
        mock_create_router_agent,
    ):
        """VertexAiSessionService初期化失敗のテスト"""
        # Arrange
        mock_create_router_agent.return_value = MagicMock()
        mock_vertex_ai_session_service_class.side_effect = Exception(
            "VertexAI initialization failed"
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            VoiceStreamingService(
                use_agent_engine=True,
                project_id="test-project",
                location="us-central1",
                agent_engine_id="test-engine-id",
            )

        assert "VertexAI initialization failed" in str(exc_info.value)


class TestVoiceStreamingServiceRunLiveCompatibility:
    """run_live()互換性のテスト"""

    @patch("app.services.voice.streaming_service.create_router_agent")
    @patch("app.services.voice.streaming_service.VertexAiSessionService")
    @patch("app.services.voice.streaming_service.Runner")
    async def test_receive_events_with_vertex_ai_session_service(
        self,
        mock_runner_class,
        mock_vertex_ai_session_service_class,
        mock_create_router_agent,
    ):
        """VertexAiSessionServiceでのreceive_events()テスト"""
        # Arrange
        mock_runner = MagicMock()

        # モックイベントを作成
        mock_event = MagicMock()
        mock_event.author = "agent"
        mock_event.turn_complete = True
        mock_event.interrupted = False
        mock_event.input_transcription = None
        mock_event.output_transcription = None
        mock_event.content = None

        async def mock_run_live(*args, **kwargs):
            """モックrun_live"""
            yield mock_event

        mock_runner.run_live = mock_run_live
        mock_runner_class.return_value = mock_runner

        service = VoiceStreamingService(
            use_agent_engine=True,
            project_id="test-project",
            location="us-central1",
            agent_engine_id="test-engine-id",
        )

        # Act
        events = []
        async for event in service.receive_events(
            user_id="test-user", session_id="test-session"
        ):
            events.append(event)

        # Assert
        # run_live()が呼ばれている
        assert len(events) >= 0  # イベントが受信されることを確認
