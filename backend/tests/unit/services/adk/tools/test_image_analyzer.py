"""analyze_image_tool のテスト"""

import base64
from unittest.mock import AsyncMock, MagicMock, patch


class TestAnalyzeHomeworkImage:
    """analyze_homework_image 関数のテスト"""

    async def test_returns_problems_list(self) -> None:
        """問題のリストを返す"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        mock_response = MagicMock()
        mock_response.text = (
            '{"problems": [{"text": "3 + 5 = ", "type": "arithmetic",'
            ' "difficulty": 1, "expression": "3 + 5"}],'
            ' "confidence": 0.95, "needs_confirmation": false}'
        )

        with patch(
            "app.services.adk.tools.image_analyzer._call_gemini_vision",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await analyze_homework_image(
                image_data=base64.b64encode(b"fake_image").decode(),
                expected_subject="math",
            )

        assert "problems" in result
        assert isinstance(result["problems"], list)
        assert len(result["problems"]) == 1
        assert result["problems"][0]["text"] == "3 + 5 = "

    async def test_returns_confidence(self) -> None:
        """信頼度を返す"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        mock_response = MagicMock()
        mock_response.text = '{"problems": [], "confidence": 0.85, "needs_confirmation": true}'

        with patch(
            "app.services.adk.tools.image_analyzer._call_gemini_vision",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await analyze_homework_image(
                image_data=base64.b64encode(b"fake_image").decode(),
            )

        assert result["confidence"] == 0.85
        assert result["needs_confirmation"] is True

    async def test_empty_image_data_returns_error(self) -> None:
        """空のimage_dataはエラーを返す"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        result = await analyze_homework_image(image_data="")
        assert "error" in result

    async def test_too_large_image_returns_error(self) -> None:
        """大きすぎる画像はエラーを返す"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        # 10MB超のbase64データ
        large_data = base64.b64encode(b"x" * (10 * 1024 * 1024 + 1)).decode()
        result = await analyze_homework_image(image_data=large_data)
        assert "error" in result

    async def test_api_error_returns_error_dict(self) -> None:
        """API呼び出しエラー時にエラーdictを返す"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        with patch(
            "app.services.adk.tools.image_analyzer._call_gemini_vision",
            new_callable=AsyncMock,
            side_effect=Exception("API error"),
        ):
            result = await analyze_homework_image(
                image_data=base64.b64encode(b"fake_image").decode(),
            )

        assert "error" in result

    async def test_invalid_json_response_returns_error(self) -> None:
        """無効なJSONレスポンスはエラーを返す"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        mock_response = MagicMock()
        mock_response.text = "not valid json"

        with patch(
            "app.services.adk.tools.image_analyzer._call_gemini_vision",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await analyze_homework_image(
                image_data=base64.b64encode(b"fake_image").decode(),
            )

        assert "error" in result

    async def test_returns_required_keys_on_success(self) -> None:
        """成功時に必要なキーがすべて含まれる"""
        from app.services.adk.tools.image_analyzer import analyze_homework_image

        mock_response = MagicMock()
        mock_response.text = (
            '{"problems": [{"text": "1 + 1 = ", "type": "arithmetic",'
            ' "difficulty": 1, "expression": "1 + 1"}],'
            ' "confidence": 0.9, "needs_confirmation": false}'
        )

        with patch(
            "app.services.adk.tools.image_analyzer._call_gemini_vision",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await analyze_homework_image(
                image_data=base64.b64encode(b"fake_image").decode(),
            )

        assert "problems" in result
        assert "confidence" in result
        assert "needs_confirmation" in result


class TestAnalyzeImageTool:
    """analyze_image_tool FunctionTool のテスト"""

    def test_is_function_tool_instance(self) -> None:
        """FunctionTool インスタンスである"""
        from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

        from app.services.adk.tools.image_analyzer import analyze_image_tool

        assert isinstance(analyze_image_tool, FunctionTool)
