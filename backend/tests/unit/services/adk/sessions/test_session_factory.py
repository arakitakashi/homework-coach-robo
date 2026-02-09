"""セッションファクトリのテスト

環境変数に基づいて適切なセッションサービスを返すファクトリのテスト。
"""

from unittest.mock import MagicMock, patch

from app.services.adk.sessions.session_factory import create_session_service

# パッチパス
_FIRESTORE_SESSION_PATCH = "app.services.adk.sessions.session_factory.FirestoreSessionService"
_VERTEX_SESSION_PATCH = "google.adk.sessions.VertexAiSessionService"


class TestCreateSessionServiceDefault:
    """AGENT_ENGINE_ID が未設定の場合"""

    @patch(_FIRESTORE_SESSION_PATCH)
    def test_returns_firestore_session_service(
        self,
        mock_firestore_cls: MagicMock,
    ) -> None:
        """デフォルトで FirestoreSessionService を返す"""
        mock_instance = MagicMock()
        mock_firestore_cls.return_value = mock_instance

        with patch.dict("os.environ", {}, clear=True):
            service = create_session_service()

        assert service is mock_instance
        mock_firestore_cls.assert_called_once()

    @patch(_FIRESTORE_SESSION_PATCH)
    def test_returns_firestore_when_empty_string(
        self,
        mock_firestore_cls: MagicMock,
    ) -> None:
        """空文字列の場合も FirestoreSessionService を返す"""
        mock_instance = MagicMock()
        mock_firestore_cls.return_value = mock_instance

        with patch.dict("os.environ", {"AGENT_ENGINE_ID": ""}, clear=True):
            service = create_session_service()

        assert service is mock_instance

    @patch(_FIRESTORE_SESSION_PATCH)
    def test_returns_firestore_when_whitespace_only(
        self,
        mock_firestore_cls: MagicMock,
    ) -> None:
        """スペースのみの場合も FirestoreSessionService を返す"""
        mock_instance = MagicMock()
        mock_firestore_cls.return_value = mock_instance

        with patch.dict("os.environ", {"AGENT_ENGINE_ID": "  "}, clear=True):
            service = create_session_service()

        assert service is mock_instance


class TestCreateSessionServiceWithAgentEngine:
    """AGENT_ENGINE_ID が設定されている場合"""

    @patch(_VERTEX_SESSION_PATCH)
    def test_returns_vertex_ai_session_service(
        self,
        mock_vertex_cls: MagicMock,
    ) -> None:
        """VertexAiSessionService を返す"""
        mock_instance = MagicMock()
        mock_vertex_cls.return_value = mock_instance

        with patch.dict(
            "os.environ",
            {"AGENT_ENGINE_ID": "test-engine-id"},
            clear=True,
        ):
            service = create_session_service()

        assert service is mock_instance

    @patch(_VERTEX_SESSION_PATCH)
    def test_passes_agent_engine_id(
        self,
        mock_vertex_cls: MagicMock,
    ) -> None:
        """agent_engine_id を正しく渡す"""
        with patch.dict(
            "os.environ",
            {"AGENT_ENGINE_ID": "my-engine-123"},
            clear=True,
        ):
            create_session_service()

        mock_vertex_cls.assert_called_once()
        call_kwargs = mock_vertex_cls.call_args[1]
        assert call_kwargs["agent_engine_id"] == "my-engine-123"

    @patch(_VERTEX_SESSION_PATCH)
    def test_passes_project_and_location(
        self,
        mock_vertex_cls: MagicMock,
    ) -> None:
        """GCP_PROJECT_ID と GCP_LOCATION を渡す"""
        with patch.dict(
            "os.environ",
            {
                "AGENT_ENGINE_ID": "engine-1",
                "GCP_PROJECT_ID": "my-project",
                "GCP_LOCATION": "asia-northeast1",
            },
            clear=True,
        ):
            create_session_service()

        call_kwargs = mock_vertex_cls.call_args[1]
        assert call_kwargs["project"] == "my-project"
        assert call_kwargs["location"] == "asia-northeast1"

    @patch(_VERTEX_SESSION_PATCH)
    def test_none_when_project_not_set(
        self,
        mock_vertex_cls: MagicMock,
    ) -> None:
        """GCP_PROJECT_ID 未設定で None を渡す"""
        with patch.dict(
            "os.environ",
            {"AGENT_ENGINE_ID": "engine-1"},
            clear=True,
        ):
            create_session_service()

        call_kwargs = mock_vertex_cls.call_args[1]
        assert call_kwargs["project"] is None
        assert call_kwargs["location"] is None

    @patch(_VERTEX_SESSION_PATCH)
    def test_strips_whitespace_from_agent_engine_id(
        self,
        mock_vertex_cls: MagicMock,
    ) -> None:
        """AGENT_ENGINE_ID の前後空白を除去する"""
        with patch.dict(
            "os.environ",
            {"AGENT_ENGINE_ID": "  engine-stripped  "},
            clear=True,
        ):
            create_session_service()

        call_kwargs = mock_vertex_cls.call_args[1]
        assert call_kwargs["agent_engine_id"] == "engine-stripped"

    @patch(_FIRESTORE_SESSION_PATCH)
    def test_does_not_call_firestore_when_engine_id_set(
        self,
        mock_firestore_cls: MagicMock,
    ) -> None:
        """AGENT_ENGINE_ID 設定時に FirestoreSessionService を呼ばない"""
        with (
            patch.dict(
                "os.environ",
                {"AGENT_ENGINE_ID": "engine-1"},
                clear=True,
            ),
            patch(_VERTEX_SESSION_PATCH),
        ):
            create_session_service()

        mock_firestore_cls.assert_not_called()
