"""対話APIの統合テスト"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPIテストクライアント"""
    return TestClient(app)


class TestCompleteSessionFlow:
    """完全なセッションフローのテスト"""

    def test_complete_session_flow(self, client: TestClient) -> None:
        """セッション作成→分析→質問→ヒント→削除の完全フロー"""
        # 1. セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "3 + 5 = ?", "child_grade": 2},
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["session_id"]

        # 2. セッション情報を取得
        get_response = client.get(f"/api/v1/dialogue/sessions/{session_id}")
        assert get_response.status_code == 200
        assert get_response.json()["problem"] == "3 + 5 = ?"

        # 3. 子供の回答を分析
        analyze_response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": "8だと思う"},
        )
        assert analyze_response.status_code == 200
        analysis = analyze_response.json()
        assert "understanding_level" in analysis
        assert "recommended_question_type" in analysis

        # 4. 質問を生成
        question_response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/question",
            json={},
        )
        assert question_response.status_code == 200
        assert "question" in question_response.json()

        # 5. ヒントを生成
        hint_response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={},
        )
        assert hint_response.status_code == 200
        hint = hint_response.json()
        assert hint["hint_level"] == 1
        assert hint["hint_level_name"] == "問題理解の確認"

        # 6. セッションを終了
        delete_response = client.delete(f"/api/v1/dialogue/sessions/{session_id}")
        assert delete_response.status_code == 204

        # 7. 削除後は取得できない
        get_after_delete = client.get(f"/api/v1/dialogue/sessions/{session_id}")
        assert get_after_delete.status_code == 404


class TestHintProgressionFlow:
    """ヒント進行フローのテスト"""

    def test_hint_level_progression(self, client: TestClient) -> None:
        """ヒントレベルの進行テスト"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "12 - 7 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # レベル1のヒント
        hint1 = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={"force_level": 1},
        )
        assert hint1.json()["hint_level"] == 1
        assert hint1.json()["hint_level_name"] == "問題理解の確認"

        # レベル2のヒント
        hint2 = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={"force_level": 2},
        )
        assert hint2.json()["hint_level"] == 2
        assert hint2.json()["hint_level_name"] == "既習事項の想起"

        # レベル3のヒント
        hint3 = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/hint",
            json={"force_level": 3},
        )
        assert hint3.json()["hint_level"] == 3
        assert hint3.json()["hint_level_name"] == "部分的支援"

        # クリーンアップ
        client.delete(f"/api/v1/dialogue/sessions/{session_id}")


class TestAnswerRequestDetectionFlow:
    """答えリクエスト検出フローのテスト"""

    def test_explicit_answer_request_in_session(self, client: TestClient) -> None:
        """セッション内での明示的な答えリクエスト検出"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "5 + 3 = ?", "child_grade": 2},
        )
        session_id = create_response.json()["session_id"]

        # 明示的な答えリクエストを分析
        analyze_response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": "もう答え教えて！"},
        )
        assert analyze_response.status_code == 200
        analysis = analyze_response.json()
        assert analysis["answer_request_detected"] is True
        assert analysis["answer_request_type"] == "explicit"

        # クリーンアップ
        client.delete(f"/api/v1/dialogue/sessions/{session_id}")

    def test_implicit_answer_request_in_session(self, client: TestClient) -> None:
        """セッション内での暗示的な答えリクエスト検出"""
        # セッションを作成
        create_response = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "8 - 3 = ?", "child_grade": 1},
        )
        session_id = create_response.json()["session_id"]

        # 暗示的な答えリクエストを分析
        analyze_response = client.post(
            f"/api/v1/dialogue/sessions/{session_id}/analyze",
            json={"child_response": "できない...むずかしいよ"},
        )
        assert analyze_response.status_code == 200
        analysis = analyze_response.json()
        assert analysis["answer_request_detected"] is True
        assert analysis["answer_request_type"] == "implicit"

        # クリーンアップ
        client.delete(f"/api/v1/dialogue/sessions/{session_id}")

    def test_standalone_answer_request_detection(self, client: TestClient) -> None:
        """スタンドアロンの答えリクエスト検出"""
        # 明示的
        explicit_response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": "正解を教えて"},
        )
        assert explicit_response.json()["request_type"] == "explicit"

        # 暗示的
        implicit_response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": "わからない"},
        )
        assert implicit_response.json()["request_type"] == "implicit"

        # なし
        none_response = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": "8だと思う"},
        )
        assert none_response.json()["request_type"] == "none"


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_nonexistent_session_errors(self, client: TestClient) -> None:
        """存在しないセッションに対するエラー"""
        fake_id = "nonexistent-session-12345"

        # GET
        get_response = client.get(f"/api/v1/dialogue/sessions/{fake_id}")
        assert get_response.status_code == 404

        # DELETE
        delete_response = client.delete(f"/api/v1/dialogue/sessions/{fake_id}")
        assert delete_response.status_code == 404

        # analyze
        analyze_response = client.post(
            f"/api/v1/dialogue/sessions/{fake_id}/analyze",
            json={"child_response": "test"},
        )
        assert analyze_response.status_code == 404

        # question
        question_response = client.post(
            f"/api/v1/dialogue/sessions/{fake_id}/question",
            json={},
        )
        assert question_response.status_code == 404

        # hint
        hint_response = client.post(
            f"/api/v1/dialogue/sessions/{fake_id}/hint",
            json={},
        )
        assert hint_response.status_code == 404

    def test_validation_errors(self, client: TestClient) -> None:
        """バリデーションエラー"""
        # 空の問題文
        response1 = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "", "child_grade": 2},
        )
        assert response1.status_code == 422

        # 範囲外の学年
        response2 = client.post(
            "/api/v1/dialogue/sessions",
            json={"problem": "test", "child_grade": 10},
        )
        assert response2.status_code == 422

        # 空の子供の回答
        response3 = client.post(
            "/api/v1/dialogue/analyze-answer-request",
            json={"child_response": ""},
        )
        assert response3.status_code == 422
