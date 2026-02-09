"""対話API LLM統合テスト"""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.v1.dialogue import get_llm_client
from app.main import app
from app.services.adk.dialogue.gemini_client import GeminiClient


@pytest.fixture
def client() -> TestClient:
    """テストクライアントを作成"""
    return TestClient(app)


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """モックLLMクライアントを作成"""
    mock_client = MagicMock(spec=GeminiClient)
    mock_client.generate = AsyncMock()
    return mock_client


@pytest.fixture
def override_llm_client(mock_llm_client: MagicMock) -> Generator[None, None, None]:
    """LLMクライアントの依存性をオーバーライド"""
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    yield
    app.dependency_overrides.clear()


class TestAnalyzeWithLLM:
    """LLMを使用した回答分析テスト"""

    def test_analyze_with_llm_client(
        self,
        client: TestClient,
        mock_llm_client: MagicMock,
        override_llm_client: None,  # noqa: ARG002 - pytest fixture
    ) -> None:
        """LLMクライアントを使用して回答を分析する"""
        # Arrange: セッション作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # LLMの応答をモック
        mock_llm_client.generate.return_value = """{
            "understanding_level": 7,
            "is_correct_direction": true,
            "needs_clarification": false,
            "key_insights": ["足し算の概念を理解している"]
        }"""

        # Act
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": "8だと思う"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["understanding_level"] == 7
        assert data["is_correct_direction"] is True
        assert data["needs_clarification"] is False
        assert "足し算の概念を理解している" in data["key_insights"]

    def test_analyze_fallback_without_llm(
        self,
        client: TestClient,
    ) -> None:
        """LLMクライアントがない場合はフォールバック応答を返す"""
        # Arrange: LLMクライアントをNoneに設定
        app.dependency_overrides[get_llm_client] = lambda: None

        try:
            # セッション作成
            create_response = client.post(
                "/api/v1/dialogue/sessions",
                json={"problem": "3 + 5 = ?", "child_grade": 1},
            )
            session_id = create_response.json()["session_id"]

            # Act
            response = client.post(
                f"/api/v1/dialogue/sessions/{session_id}/analyze",
                json={"child_response": "8だと思う"},
            )

            # Assert: フォールバック応答
            assert response.status_code == 200
            data = response.json()
            assert "understanding_level" in data
            # フォールバック時はデフォルト値
            assert data["understanding_level"] == 5
        finally:
            app.dependency_overrides.clear()


class TestGenerateQuestionWithLLM:
    """LLMを使用した質問生成テスト"""

    def test_generate_question_with_llm_client(
        self,
        client: TestClient,
        mock_llm_client: MagicMock,
        override_llm_client: None,  # noqa: ARG002 - pytest fixture
    ) -> None:
        """LLMクライアントを使用して質問を生成する"""
        # Arrange: セッション作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # LLMの応答をモック
        mock_llm_client.generate.return_value = "この問題で何を求めればいいか、わかるかな？"

        # Act
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/question",
            json={"question_type": "understanding_check", "tone": "encouraging"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "この問題で何を求めればいいか、わかるかな？"
        assert data["question_type"] == "understanding_check"

    def test_generate_question_fallback_without_llm(
        self,
        client: TestClient,
    ) -> None:
        """LLMクライアントがない場合はテンプレート応答を返す"""
        # Arrange: LLMクライアントをNoneに設定
        app.dependency_overrides[get_llm_client] = lambda: None

        try:
            # セッション作成
            create_response = client.post(
                "/api/v1/dialogue/sessions",
                json={"problem": "3 + 5 = ?", "child_grade": 1},
            )
            session_id = create_response.json()["session_id"]

            # Act
            response = client.post(
                f"/api/v1/dialogue/sessions/{session_id}/question",
                json={"question_type": "understanding_check"},
            )

            # Assert: テンプレート応答
            assert response.status_code == 200
            data = response.json()
            assert data["question"] == "この問題は何を聞いていると思う？"
        finally:
            app.dependency_overrides.clear()


class TestGenerateHintWithLLM:
    """LLMを使用したヒント生成テスト"""

    def test_generate_hint_with_llm_client(
        self,
        client: TestClient,
        mock_llm_client: MagicMock,
        override_llm_client: None,  # noqa: ARG002 - pytest fixture
    ) -> None:
        """LLMクライアントを使用してヒントを生成する"""
        # Arrange: セッション作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # LLMの応答をモック
        mock_llm_client.generate.return_value = (
            "まず、3個のりんごがあるとして、そこに5個追加したら何個になるかな？"
        )

        # Act
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "りんご" in data["hint"]
        assert data["hint_level"] == 1

    def test_generate_hint_fallback_without_llm(
        self,
        client: TestClient,
    ) -> None:
        """LLMクライアントがない場合はテンプレートヒントを返す"""
        # Arrange: LLMクライアントをNoneに設定
        app.dependency_overrides[get_llm_client] = lambda: None

        try:
            # セッション作成
            create_response = client.post(
                "/api/v1/dialogue/sessions",
                json={"problem": "3 + 5 = ?", "child_grade": 1},
            )
            session_id = create_response.json()["session_id"]

            # Act
            response = client.post(
                f"/api/v1/dialogue/sessions/{session_id}/hint",
                json={},
            )

            # Assert: テンプレートヒント
            assert response.status_code == 200
            data = response.json()
            assert data["hint"] == "この問題は何を聞いていると思う？"
        finally:
            app.dependency_overrides.clear()


class TestLLMErrorHandling:
    """LLMエラーハンドリングテスト"""

    def test_llm_error_returns_fallback(
        self,
        client: TestClient,
        mock_llm_client: MagicMock,
        override_llm_client: None,  # noqa: ARG002 - pytest fixture
    ) -> None:
        """LLMエラー時にフォールバック応答を返す"""
        # Arrange: セッション作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # LLMがエラーを返すようにモック
        mock_llm_client.generate.side_effect = RuntimeError("LLM API Error")

        # Act
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/question",
            json={"question_type": "understanding_check"},
        )

        # Assert: エラー時はフォールバック
        assert response.status_code == 200
        data = response.json()
        # フォールバックテンプレート
        assert data["question"] == "この問題は何を聞いていると思う？"

    def test_llm_invalid_json_returns_fallback(
        self,
        client: TestClient,
        mock_llm_client: MagicMock,
        override_llm_client: None,  # noqa: ARG002 - pytest fixture
    ) -> None:
        """LLMが無効なJSONを返した場合にフォールバック"""
        # Arrange: セッション作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # LLMが無効なJSONを返すようにモック
        mock_llm_client.generate.return_value = "これは有効なJSONではありません"

        # Act
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": "8だと思う"},
        )

        # Assert: JSON解析エラー時はフォールバック
        assert response.status_code == 200
        data = response.json()
        assert data["understanding_level"] == 5  # デフォルト値
