"""Tests for session factory migration logic"""

import os
from unittest.mock import patch

from app.services.adk.sessions.session_factory import (
    create_session_service,
    should_use_managed_session,
)


class TestShouldUseManagedSession:
    """Tests for should_use_managed_session function"""

    def test_no_agent_engine_id_returns_false(self) -> None:
        """AGENT_ENGINE_ID が未設定の場合、False を返す"""
        with patch.dict(os.environ, {}, clear=True):
            result = should_use_managed_session("user123")
            assert result is False

    def test_empty_agent_engine_id_returns_false(self) -> None:
        """AGENT_ENGINE_ID が空文字列の場合、False を返す"""
        with patch.dict(os.environ, {"AGENT_ENGINE_ID": ""}, clear=True):
            result = should_use_managed_session("user123")
            assert result is False

    def test_migrated_user_returns_true(self) -> None:
        """MIGRATED_USER_IDS に含まれるユーザーの場合、True を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
                "MIGRATED_USER_IDS": "user1,user2,user3",
            },
            clear=True,
        ):
            result = should_use_managed_session("user2")
            assert result is True

    def test_non_migrated_user_returns_false(self) -> None:
        """MIGRATED_USER_IDS に含まれないユーザーの場合、False を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
                "MIGRATED_USER_IDS": "user1,user2,user3",
            },
            clear=True,
        ):
            result = should_use_managed_session("user999")
            assert result is False

    def test_percentage_below_threshold_returns_true(self) -> None:
        """ユーザーハッシュがパーセンテージ未満の場合、True を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
                "MIGRATION_PERCENTAGE": "50",
            },
            clear=True,
        ):
            # ハッシュ値が50未満になるユーザーIDを探す
            for user_id in [f"user{i}" for i in range(100)]:
                if hash(user_id) % 100 < 50:
                    result = should_use_managed_session(user_id)
                    assert result is True
                    break

    def test_percentage_above_threshold_returns_false(self) -> None:
        """ユーザーハッシュがパーセンテージ以上の場合、False を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
                "MIGRATION_PERCENTAGE": "50",
            },
            clear=True,
        ):
            # ハッシュ値が50以上になるユーザーIDを探す
            for user_id in [f"user{i}" for i in range(100)]:
                if hash(user_id) % 100 >= 50:
                    result = should_use_managed_session(user_id)
                    assert result is False
                    break

    def test_invalid_percentage_returns_false(self) -> None:
        """MIGRATION_PERCENTAGE が不正値の場合、False を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
                "MIGRATION_PERCENTAGE": "invalid",
            },
            clear=True,
        ):
            result = should_use_managed_session("user123")
            assert result is False

    def test_zero_percentage_returns_false(self) -> None:
        """MIGRATION_PERCENTAGE が0の場合、False を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
                "MIGRATION_PERCENTAGE": "0",
            },
            clear=True,
        ):
            result = should_use_managed_session("user123")
            assert result is False

    def test_none_user_id_returns_true_for_backward_compatibility(self) -> None:
        """user_id が None の場合、後方互換性のため True を返す"""
        with patch.dict(
            os.environ,
            {
                "AGENT_ENGINE_ID": "agent-123",
            },
            clear=True,
        ):
            result = should_use_managed_session(None)
            assert result is True


class TestCreateSessionService:
    """Tests for create_session_service function"""

    def test_returns_firestore_service_when_no_agent_engine_id(self) -> None:
        """AGENT_ENGINE_ID 未設定時、FirestoreSessionService を返す"""
        with (
            patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}, clear=True),
            patch(
                "app.services.adk.sessions.session_factory.FirestoreSessionService"
            ) as mock_firestore,
        ):
            create_session_service("user123")
            mock_firestore.assert_called_once()

    def test_returns_vertex_ai_service_when_agent_engine_id_set(self) -> None:
        """AGENT_ENGINE_ID 設定時、VertexAiSessionService を返す"""
        with (
            patch.dict(
                os.environ,
                {
                    "AGENT_ENGINE_ID": "agent-123",
                    "MIGRATED_USER_IDS": "user123",
                    "GCP_PROJECT_ID": "test-project",
                    "GCP_LOCATION": "us-central1",
                },
                clear=True,
            ),
            patch("google.adk.sessions.VertexAiSessionService") as mock_vertex,
        ):
            create_session_service("user123")
            mock_vertex.assert_called_once()

    def test_user_id_affects_service_selection(self) -> None:
        """user_id によってサービス選択が変わることを確認"""
        with (
            patch.dict(
                os.environ,
                {
                    "AGENT_ENGINE_ID": "agent-123",
                    "MIGRATED_USER_IDS": "user1",
                    "GOOGLE_CLOUD_PROJECT": "test-project",
                },
                clear=True,
            ),
            patch(
                "app.services.adk.sessions.session_factory.FirestoreSessionService"
            ) as mock_firestore,
            patch("google.adk.sessions.VertexAiSessionService") as mock_vertex,
        ):
            create_session_service("user1")
            mock_vertex.assert_called_once()

            create_session_service("user2")
            mock_firestore.assert_called_once()
