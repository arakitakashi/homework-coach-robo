"""Google Gemini APIクライアント（Vertex AI モード）"""

import os

from google import genai
from google.genai import types


class GeminiClient:
    """Google Gemini APIクライアント（LLMClientプロトコル準拠）

    このクラスはSocraticDialogueManagerのLLMClientプロトコルに準拠し、
    Vertex AI経由でGoogle Gemini APIを使用してテキスト生成を行います。

    開発環境・本番環境ともにVertex AIを使用することで、
    環境間の差異をなくし、一貫した動作を保証します。

    Attributes:
        DEFAULT_MODEL: デフォルトで使用するGeminiモデル
        DEFAULT_LOCATION: デフォルトのリージョン
    """

    DEFAULT_MODEL = "gemini-2.5-flash"
    DEFAULT_LOCATION = "us-central1"

    def __init__(
        self,
        project: str | None = None,
        location: str | None = None,
        model: str | None = None,
        system_instruction: str | None = None,
    ) -> None:
        """GeminiClientを初期化する（Vertex AIモード）

        Args:
            project: Google CloudプロジェクトID。Noneの場合は環境変数から取得
                     （GOOGLE_CLOUD_PROJECT）
            location: リージョン。Noneの場合は環境変数またはデフォルト値
                     （GOOGLE_CLOUD_LOCATION、デフォルト: us-central1）
            model: 使用するモデル名。Noneの場合はDEFAULT_MODEL
            system_instruction: システム指示（オプション）

        Raises:
            ValueError: プロジェクトIDが見つからない場合
        """
        # プロジェクトIDの解決
        self._project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")

        if not self._project:
            raise ValueError(
                "Google Cloud project is required. "
                "Set GOOGLE_CLOUD_PROJECT environment variable or pass project parameter."
            )

        # リージョンの解決
        self._location = (
            location or os.environ.get("GOOGLE_CLOUD_LOCATION") or self.DEFAULT_LOCATION
        )

        self._model = model or self.DEFAULT_MODEL
        self._system_instruction = system_instruction

        # Vertex AI モードでクライアントを初期化
        self._client = genai.Client(
            vertexai=True,
            project=self._project,
            location=self._location,
        )

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
