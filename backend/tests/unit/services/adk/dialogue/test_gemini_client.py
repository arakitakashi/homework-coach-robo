"""GeminiClientのユニットテスト"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.adk.dialogue.gemini_client import GeminiClient
from app.services.adk.dialogue.manager import LLMClient


class TestGeminiClientProtocol:
    """GeminiClientがLLMClientプロトコルに準拠しているかテスト"""

    def test_gemini_client_implements_protocol(self) -> None:
        """GeminiClientがLLMClientプロトコルを実装している"""
        # Arrange & Act
        client = GeminiClient(api_key="test-api-key")

        # Assert
        assert isinstance(client, LLMClient)

    def test_gemini_client_has_generate_method(self) -> None:
        """GeminiClientがgenerateメソッドを持っている"""
        # Arrange
        client = GeminiClient(api_key="test-api-key")

        # Assert
        assert hasattr(client, "generate")
        assert callable(client.generate)


class TestGeminiClientInit:
    """GeminiClientの初期化テスト"""

    def test_init_with_api_key(self) -> None:
        """APIキーを指定して初期化できる"""
        # Arrange & Act
        client = GeminiClient(api_key="test-api-key")

        # Assert
        assert client._api_key == "test-api-key"

    def test_init_with_custom_model(self) -> None:
        """カスタムモデルを指定して初期化できる"""
        # Arrange & Act
        client = GeminiClient(api_key="test-api-key", model="gemini-2.5-pro")

        # Assert
        assert client._model == "gemini-2.5-pro"

    def test_init_with_default_model(self) -> None:
        """デフォルトモデルが設定される"""
        # Arrange & Act
        client = GeminiClient(api_key="test-api-key")

        # Assert
        assert client._model == GeminiClient.DEFAULT_MODEL

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "env-api-key"})
    def test_init_from_env_google_api_key(self) -> None:
        """GOOGLE_API_KEY環境変数から初期化できる"""
        # Arrange & Act
        client = GeminiClient()

        # Assert
        assert client._api_key == "env-api-key"

    @patch.dict("os.environ", {"GEMINI_API_KEY": "gemini-env-key"}, clear=True)
    def test_init_from_env_gemini_api_key(self) -> None:
        """GEMINI_API_KEY環境変数から初期化できる（後方互換性）"""
        # Arrange & Act
        client = GeminiClient()

        # Assert
        assert client._api_key == "gemini-env-key"

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "google-key", "GEMINI_API_KEY": "gemini-key"})
    def test_google_api_key_takes_precedence(self) -> None:
        """GOOGLE_API_KEYがGEMINI_API_KEYより優先される"""
        # Arrange & Act
        client = GeminiClient()

        # Assert
        assert client._api_key == "google-key"

    @patch.dict("os.environ", {}, clear=True)
    def test_init_without_api_key_raises_error(self) -> None:
        """APIキーなしで初期化するとエラー"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="API key is required"):
            GeminiClient()


class TestGeminiClientGenerate:
    """GeminiClientのgenerate()メソッドテスト"""

    @pytest.mark.asyncio
    async def test_generate_returns_text(self) -> None:
        """generate()がテキストを返す"""
        # Arrange
        client = GeminiClient(api_key="test-api-key")

        mock_response = MagicMock()
        mock_response.text = "Generated response"

        mock_genai_client = MagicMock()
        mock_genai_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with patch.object(client, "_client", mock_genai_client):
            # Act
            result = await client.generate("Test prompt")

            # Assert
            assert result == "Generated response"

    @pytest.mark.asyncio
    async def test_generate_calls_api_with_correct_params(self) -> None:
        """generate()が正しいパラメータでAPIを呼び出す"""
        # Arrange
        client = GeminiClient(api_key="test-api-key", model="gemini-2.5-flash")

        mock_response = MagicMock()
        mock_response.text = "Response"

        mock_genai_client = MagicMock()
        mock_genai_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with patch.object(client, "_client", mock_genai_client):
            # Act
            await client.generate("Test prompt")

            # Assert
            mock_genai_client.aio.models.generate_content.assert_called_once()
            call_kwargs = mock_genai_client.aio.models.generate_content.call_args.kwargs
            assert call_kwargs["model"] == "gemini-2.5-flash"
            assert call_kwargs["contents"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_generate_with_system_instruction(self) -> None:
        """システム指示付きでgenerate()が動作する"""
        # Arrange
        system_instruction = "You are a helpful assistant."
        client = GeminiClient(api_key="test-api-key", system_instruction=system_instruction)

        mock_response = MagicMock()
        mock_response.text = "Response with system instruction"

        mock_genai_client = MagicMock()
        mock_genai_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with patch.object(client, "_client", mock_genai_client):
            # Act
            result = await client.generate("Test prompt")

            # Assert
            assert result == "Response with system instruction"
            call_kwargs = mock_genai_client.aio.models.generate_content.call_args.kwargs
            assert "config" in call_kwargs

    @pytest.mark.asyncio
    async def test_generate_handles_api_error(self) -> None:
        """APIエラー時に適切な例外を発生させる"""
        # Arrange
        client = GeminiClient(api_key="test-api-key")

        mock_genai_client = MagicMock()
        mock_genai_client.aio.models.generate_content = AsyncMock(
            side_effect=Exception("API Error")
        )

        with (
            patch.object(client, "_client", mock_genai_client),
            pytest.raises(RuntimeError, match="LLM generation failed"),
        ):
            await client.generate("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_handles_empty_response(self) -> None:
        """空の応答時にエラーを発生させる"""
        # Arrange
        client = GeminiClient(api_key="test-api-key")

        mock_response = MagicMock()
        mock_response.text = None

        mock_genai_client = MagicMock()
        mock_genai_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with (
            patch.object(client, "_client", mock_genai_client),
            pytest.raises(RuntimeError, match="Empty response"),
        ):
            await client.generate("Test prompt")
