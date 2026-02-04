"""Google Gemini APIクライアント"""

import os

from google import genai
from google.genai import types


class GeminiClient:
    """Google Gemini APIクライアント（LLMClientプロトコル準拠）

    このクラスはSocraticDialogueManagerのLLMClientプロトコルに準拠し、
    Google Gemini APIを使用してテキスト生成を行います。

    Attributes:
        DEFAULT_MODEL: デフォルトで使用するGeminiモデル
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        system_instruction: str | None = None,
    ) -> None:
        """GeminiClientを初期化する

        Args:
            api_key: Google API Key。Noneの場合は環境変数から取得
                     （GOOGLE_API_KEY優先、なければGEMINI_API_KEY）
            model: 使用するモデル名。Noneの場合はDEFAULT_MODEL
            system_instruction: システム指示（オプション）

        Raises:
            ValueError: APIキーが見つからない場合
        """
        # APIキーの解決
        resolved_api_key = (
            api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        )

        if not resolved_api_key:
            raise ValueError("API key is required. Set GOOGLE_API_KEY environment variable.")

        self._api_key = resolved_api_key
        self._model = model or self.DEFAULT_MODEL
        self._system_instruction = system_instruction

        # Gemini クライアントを初期化
        self._client = genai.Client(api_key=self._api_key)

    async def generate(self, prompt: str) -> str:
        """プロンプトからテキストを生成する

        Args:
            prompt: 生成に使用するプロンプト

        Returns:
            生成されたテキスト

        Raises:
            RuntimeError: API呼び出しに失敗した場合、または空の応答の場合
        """
        try:
            # 設定の構築
            config = None
            if self._system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=self._system_instruction,
                )

            # 非同期でコンテンツを生成
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )

            # 応答テキストの取得
            if response.text is None:
                raise RuntimeError("Empty response from LLM")

            return response.text

        except RuntimeError:
            # RuntimeErrorはそのまま再送出
            raise
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}") from e
