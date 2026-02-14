"""画像認識APIエンドポイントのテスト"""

import base64
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPIテストクライアント"""
    return TestClient(app)


def _make_valid_image_base64() -> str:
    """テスト用の有効なbase64画像データを生成する"""
    # 1x1ピクセルの最小JPEG（実際のJPEGバイナリ）
    return base64.b64encode(b"\xff\xd8\xff\xe0" + b"\x00" * 100).decode()


def _make_vision_result(
    problems: list[dict[str, Any]] | None = None,
    confidence: float = 0.95,
    needs_confirmation: bool = False,
) -> dict[str, Any]:
    """テスト用のVision API結果を生成する"""
    if problems is None:
        problems = [
            {
                "text": "3 + 5 = ?",
                "type": "arithmetic",
                "difficulty": 1,
                "expression": "3 + 5",
            }
        ]
    return {
        "problems": problems,
        "confidence": confidence,
        "needs_confirmation": needs_confirmation,
    }


class TestRecognizeImage:
    """POST /api/v1/vision/recognize のテスト"""

    def test_recognize_image_success(self, client: TestClient) -> None:
        """正常に画像を認識できる"""
        image_data = _make_valid_image_base64()
        mock_result = _make_vision_result()

        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            response = client.post(
                "/api/v1/vision/recognize",
                json={"image": image_data},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["problems"]) == 1
        assert data["problems"][0]["text"] == "3 + 5 = ?"
        assert data["confidence"] == 0.95
        assert data["needs_confirmation"] is False

    def test_recognize_image_with_options(self, client: TestClient) -> None:
        """認識タイプと教科を指定できる"""
        image_data = _make_valid_image_base64()
        mock_result = _make_vision_result()

        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_analyze:
            response = client.post(
                "/api/v1/vision/recognize",
                json={
                    "image": image_data,
                    "recognition_type": "handwriting",
                    "expected_subject": "算数",
                },
            )

        assert response.status_code == 200
        # analyze_homework_imageにexpected_subjectが渡されていることを確認
        mock_analyze.assert_called_once()
        call_kwargs = mock_analyze.call_args
        assert call_kwargs[1]["expected_subject"] == "算数"

    def test_recognize_image_empty_image(self, client: TestClient) -> None:
        """空の画像データで422を返す"""
        response = client.post(
            "/api/v1/vision/recognize",
            json={"image": ""},
        )

        assert response.status_code == 422

    def test_recognize_image_missing_image(self, client: TestClient) -> None:
        """imageフィールドなしで422を返す"""
        response = client.post(
            "/api/v1/vision/recognize",
            json={},
        )

        assert response.status_code == 422

    def test_recognize_image_vision_api_error(self, client: TestClient) -> None:
        """Vision APIエラー時にエラーレスポンスを返す"""
        image_data = _make_valid_image_base64()

        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value={"error": "画像分析に失敗しました。もう一度試してください。"},
        ):
            response = client.post(
                "/api/v1/vision/recognize",
                json={"image": image_data},
            )

        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error_type"] == "recognition_failed"

    def test_recognize_image_low_confidence(self, client: TestClient) -> None:
        """低信頼度の場合はneeds_confirmationがTrueになる"""
        image_data = _make_valid_image_base64()
        mock_result = _make_vision_result(confidence=0.3, needs_confirmation=True)

        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            response = client.post(
                "/api/v1/vision/recognize",
                json={"image": image_data},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0.3
        assert data["needs_confirmation"] is True

    def test_recognize_image_invalid_base64(self, client: TestClient) -> None:
        """不正なbase64データの場合にエラーレスポンスを返す"""
        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value={"error": "画像データのデコードに失敗しました"},
        ):
            response = client.post(
                "/api/v1/vision/recognize",
                json={"image": "not-valid-base64!!!"},
            )

        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error_type"] == "recognition_failed"

    def test_recognize_image_too_large(self, client: TestClient) -> None:
        """画像サイズ超過の場合にエラーレスポンスを返す"""
        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value={"error": "画像サイズが大きすぎます（上限10MB）"},
        ):
            response = client.post(
                "/api/v1/vision/recognize",
                json={"image": "large-image-data"},
            )

        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error_type"] == "image_too_large"

    def test_recognize_image_multiple_problems(self, client: TestClient) -> None:
        """複数の問題を認識できる"""
        image_data = _make_valid_image_base64()
        mock_result = _make_vision_result(
            problems=[
                {"text": "3 + 5 = ?", "type": "arithmetic", "difficulty": 1, "expression": "3 + 5"},
                {"text": "7 - 2 = ?", "type": "arithmetic", "difficulty": 1, "expression": "7 - 2"},
            ],
        )

        with patch(
            "app.api.v1.vision.analyze_homework_image",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            response = client.post(
                "/api/v1/vision/recognize",
                json={"image": image_data},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) == 2
