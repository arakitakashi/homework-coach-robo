"""対話APIエンドポイントのテスト"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    return TestClient(app)


class TestCreateSession:
    """POST /api/v1/dialogue/sessions のテスト"""

    def test_create_session_success(self, client):
        """セッションを作成できる"""
        response = client.post(
            "/api/v1/dialogue/sessions",
            json={
                "problem": "3 + 5 = ?",
                "child_grade": 2,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["problem"] == "3 + 5 = ?"
        assert data["current_hint_level"] == 1
        assert data["tone"] == "encouraging"
        assert data["turns_count"] == 0

    def test_create_session_with_character_type(self, client):
        """キャラクタータイプ付きでセッションを作成できる"""
        response = client.post(
            "/api/v1/dialogue/sessions",
            json={
                "problem": "7 - 3 = ?",
                "child_grade": 1,
                "character_type": "robot",
            },
        )

        assert response.status_code == 201

    def test_create_session_validation_error(self, client):
        """バリデーションエラーで400を返す"""
        # problemが空
        response = client.post(
            "/api/v1/dialogue/sessions",
            json={
                "problem": "",
                "child_grade": 2,
            },
        )
        assert response.status_code == 422

        # child_gradeが範囲外
        response = client.post(
            "/api/v1/dialogue/sessions",
            json={
                "problem": "test",
                "child_grade": 5,
            },
        )
        assert response.status_code == 422


class TestGetSession:
    """GET /api/v1/dialogue/sessions/{session_id} のテスト"""

    def test_get_existing_session(self, client):
        """存在するセッションを取得できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "test", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # セッションを取得
        response = client.get(f"/api/v1/dialogue/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["problem"] == "test"

    def test_get_nonexistent_session(self, client):
        """存在しないセッションで404を返す"""
        response = client.get("/api/v1/dialogue/sessions/nonexistent-id")

        assert response.status_code == 404


class TestDeleteSession:
    """DELETE /api/v1/dialogue/sessions/{session_id} のテスト"""

    def test_delete_existing_session(self, client):
        """存在するセッションを削除できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "test", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # セッションを削除
        response = client.delete(f"/api/v1/dialogue/sessions/{session_id}")

        assert response.status_code == 204

        # 削除されていることを確認
        get_response = client.get(f"/api/v1/dialogue/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_session(self, client):
        """存在しないセッションの削除で404を返す"""
        response = client.delete("/api/v1/dialogue/sessions/nonexistent-id")

        assert response.status_code == 404


class TestAnalyzeResponse:
    """POST /api/v1/dialogue/sessions/{session_id}/analyze のテスト"""

    def test_analyze_response_success(self, client):
        """回答を分析できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 2},
        )
        session_id = create_response.json()["session_id"]

        # 回答を分析
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": "8だと思う"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "understanding_level" in data
        assert "is_correct_direction" in data
        assert "recommended_question_type" in data
        assert "recommended_tone" in data

    def test_analyze_response_nonexistent_session(self, client):
        """存在しないセッションで404を返す"""
        response = client.post(
            "/api/v1/dialogue/sessions/nonexistent-id/analyze",
            json={"child_response": "test"},
        )

        assert response.status_code == 404

    def test_analyze_response_validation_error(self, client):
        """バリデーションエラーで422を返す"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "test", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # 空の回答
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": ""},
        )

        assert response.status_code == 422


class TestGenerateQuestion:
    """POST /api/v1/dialogue/sessions/{session_id}/question のテスト"""

    def test_generate_question_success(self, client):
        """質問を生成できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 2},
        )
        session_id = create_response.json()["session_id"]

        # 質問を生成
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/question",
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert "question_type" in data
        assert "tone" in data

    def test_generate_question_with_params(self, client):
        """パラメータ指定で質問を生成できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 2},
        )
        session_id = create_response.json()["session_id"]

        # パラメータ指定で質問を生成
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/question",
            json={"question_type": "hint", "tone": "empathetic"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["question_type"] == "hint"
        assert data["tone"] == "empathetic"

    def test_generate_question_nonexistent_session(self, client):
        """存在しないセッションで404を返す"""
        response = client.post(
            "/api/v1/dialogue/sessions/nonexistent-id/question",
            json={},
        )

        assert response.status_code == 404


class TestGenerateHint:
    """POST /api/v1/dialogue/sessions/{session_id}/hint のテスト"""

    def test_generate_hint_success(self, client):
        """ヒントを生成できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 2},
        )
        session_id = create_response.json()["session_id"]

        # ヒントを生成
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert "hint" in data
        assert "hint_level" in data
        assert "hint_level_name" in data
        assert "is_answer_request_response" in data

    def test_generate_hint_with_force_level(self, client):
        """レベル指定でヒントを生成できる"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 2},
        )
        session_id = create_response.json()["session_id"]

        # レベル2を強制指定
        response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={"force_level": 2},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["hint_level"] == 2

    def test_generate_hint_nonexistent_session(self, client):
        """存在しないセッションで404を返す"""
        response = client.post(
            "/api/v1/dialogue/sessions/nonexistent-id/hint",
            json={},
        )

        assert response.status_code == 404


class TestAnalyzeAnswerRequest:
    """POST /api/v1/dialogue/analyze-answer-request のテスト"""

    def test_analyze_explicit_answer_request(self, client):
        """明示的な答えリクエストを検出できる"""
        response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": "答え教えて！"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["request_type"] == "explicit"
        assert data["confidence"] >= 0.8
        assert len(data["detected_phrases"]) > 0

    def test_analyze_implicit_answer_request(self, client):
        """暗示的な答えリクエストを検出できる"""
        response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": "もうできない、むずかしいよ"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["request_type"] == "implicit"

    def test_analyze_no_answer_request(self, client):
        """通常の発言は答えリクエストではない"""
        response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": "8だと思う"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["request_type"] == "none"

    def test_analyze_validation_error(self, client):
        """バリデーションエラーで422を返す"""
        response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": ""},
        )

        assert response.status_code == 422
