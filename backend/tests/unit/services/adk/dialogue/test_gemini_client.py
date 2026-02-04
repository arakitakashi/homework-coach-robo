"""GeminiClientのユニットテスト（Vertex AI モード）"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.adk.dialogue.gemini_client import GeminiClient
from app.services.adk.dialogue.manager import LLMClient


class TestGeminiClientProtocol:
    """GeminiClientがLLMClientプロトコルに準拠しているかテスト"""

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_gemini_client_implements_protocol(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """GeminiClientがLLMClientプロトコルを実装している"""
        # Arrange & Act
        client = GeminiClient(project="test-project")

        # Assert
        assert isinstance(client, LLMClient)

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_gemini_client_has_generate_method(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """GeminiClientがgenerateメソッドを持っている"""
        # Arrange
        client = GeminiClient(project="test-project")

        # Assert
        assert hasattr(client, "generate")
        assert callable(client.generate)


class TestGeminiClientInit:
    """GeminiClientの初期化テスト"""

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_init_with_project(self, mock_client: MagicMock) -> None:
        """プロジェクトIDを指定して初期化できる"""
        # Arrange & Act
        client = GeminiClient(project="test-project")

        # Assert
        assert client._project == "test-project"
        mock_client.assert_called_once_with(
            vertexai=True,
            project="test-project",
            location="us-central1",
        )

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_init_with_custom_location(self, mock_client: MagicMock) -> None:
        """カスタムリージョンを指定して初期化できる"""
        # Arrange & Act
        client = GeminiClient(project="test-project", location="asia-northeast1")

        # Assert
        assert client._location == "asia-northeast1"
        mock_client.assert_called_once_with(
            vertexai=True,
            project="test-project",
            location="asia-northeast1",
        )

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_init_with_custom_model(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """カスタムモデルを指定して初期化できる"""
        # Arrange & Act
        client = GeminiClient(project="test-project", model="gemini-2.5-pro")

        # Assert
        assert client._model == "gemini-2.5-pro"

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_init_with_default_model(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """デフォルトモデルが設定される"""
        # Arrange & Act
        client = GeminiClient(project="test-project")

        # Assert
        assert client._model == GeminiClient.DEFAULT_MODEL

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    def test_init_with_default_location(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """デフォルトリージョンが設定される"""
        # Arrange & Act
        client = GeminiClient(project="test-project")

        # Assert
        assert client._location == "us-central1"

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    @patch.dict("os.environ", {"GOOGLE_CLOUD_PROJECT": "env-project"})
    def test_init_from_env_project(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """GOOGLE_CLOUD_PROJECT環境変数から初期化できる"""
        # Arrange & Act
        client = GeminiClient()

        # Assert
        assert client._project == "env-project"

    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    @patch.dict("os.environ", {"GOOGLE_CLOUD_LOCATION": "asia-northeast1"})
    def test_init_from_env_location(
        self,
        mock_client: MagicMock,  # noqa: ARG002
    ) -> None:
        """GOOGLE_CLOUD_LOCATION環境変数からリージョンを取得できる"""
        # Arrange & Act
        client = GeminiClient(project="test-project")

        # Assert
        assert client._location == "asia-northeast1"

    @patch.dict("os.environ", {}, clear=True)
    def test_init_without_project_raises_error(self) -> None:
        """プロジェクトIDなしで初期化するとエラー"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Google Cloud project is required"):
            GeminiClient()


class TestGeminiClientGenerate:
    """GeminiClientのgenerate()メソッドテスト"""

    @pytest.mark.asyncio
    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    async def test_generate_returns_text(self, mock_client_class: MagicMock) -> None:
        """generate()がテキストを返す"""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "Generated response"

        mock_client_instance = MagicMock()
        mock_client_instance.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        client = GeminiClient(project="test-project")

        # Act
        result = await client.generate("Test prompt")

        # Assert
        assert result == "Generated response"

    @pytest.mark.asyncio
    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    async def test_generate_calls_api_with_correct_params(
        self, mock_client_class: MagicMock
    ) -> None:
        """generate()が正しいパラメータでAPIを呼び出す"""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "Response"

        mock_client_instance = MagicMock()
        mock_client_instance.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        client = GeminiClient(project="test-project", model="gemini-2.5-flash")

        # Act
        await client.generate("Test prompt")

        # Assert
        mock_client_instance.aio.models.generate_content.assert_called_once()
        call_kwargs = mock_client_instance.aio.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert call_kwargs["contents"] == "Test prompt"

    @pytest.mark.asyncio
    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    async def test_generate_with_system_instruction(self, mock_client_class: MagicMock) -> None:
        """システム指示付きでgenerate()が動作する"""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "Response with system instruction"

        mock_client_instance = MagicMock()
        mock_client_instance.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        system_instruction = "You are a helpful assistant."
        client = GeminiClient(project="test-project", system_instruction=system_instruction)

        # Act
        result = await client.generate("Test prompt")

        # Assert
        assert result == "Response with system instruction"
        call_kwargs = mock_client_instance.aio.models.generate_content.call_args.kwargs
        assert "config" in call_kwargs

    @pytest.mark.asyncio
    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    async def test_generate_handles_api_error(self, mock_client_class: MagicMock) -> None:
        """APIエラー時に適切な例外を発生させる"""
        # Arrange
        mock_client_instance = MagicMock()
        mock_client_instance.aio.models.generate_content = AsyncMock(
            side_effect=Exception("API Error")
        )
        mock_client_class.return_value = mock_client_instance

        client = GeminiClient(project="test-project")

        # Act & Assert
        with pytest.raises(RuntimeError, match="LLM generation failed"):
            await client.generate("Test prompt")

    @pytest.mark.asyncio
    @patch("app.services.adk.dialogue.gemini_client.genai.Client")
    async def test_generate_handles_empty_response(self, mock_client_class: MagicMock) -> None:
        """空の応答時にエラーを発生させる"""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = None

        mock_client_instance = MagicMock()
        mock_client_instance.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        client = GeminiClient(project="test-project")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Empty response"):
            await client.generate("Test prompt")
