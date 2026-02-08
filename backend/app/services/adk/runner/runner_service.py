"""エージェントランナーサービス

ADK Runnerを使用したエージェント実行サービス。
"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from google.adk import Runner
from google.adk.memory import BaseMemoryService
from google.adk.sessions import BaseSessionService
from google.genai import types

from app.services.adk.agents import create_router_agent

if TYPE_CHECKING:
    from google.adk.events import Event

# デフォルトのアプリ名
DEFAULT_APP_NAME = "homework-coach"


class AgentRunnerService:
    """エージェントランナーサービス

    ADK Runnerを使用して、マルチエージェント構成の対話エージェントを実行する。

    Router Agent が子供の入力を分析し、最適な専門エージェントに委譲する。

    Attributes:
        _session_service: セッション管理サービス
        _memory_service: 記憶管理サービス
        _runner: ADK Runner
    """

    def __init__(
        self,
        session_service: BaseSessionService,
        memory_service: BaseMemoryService,
        app_name: str = DEFAULT_APP_NAME,
    ) -> None:
        """初期化

        Args:
            session_service: セッション管理サービス
            memory_service: 記憶管理サービス
            app_name: アプリケーション名
        """
        self._session_service = session_service
        self._memory_service = memory_service
        self._agent = create_router_agent()
        self._runner = Runner(
            app_name=app_name,
            agent=self._agent,
            session_service=session_service,
            memory_service=memory_service,
        )

    async def run(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ) -> AsyncIterator["Event"]:
        """エージェントを実行しイベントをストリーム

        Args:
            user_id: ユーザーID
            session_id: セッションID
            message: ユーザーメッセージ

        Yields:
            Event: ADKイベント
        """
        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            yield event

    def extract_text(self, event: "Event") -> str | None:
        """イベントからテキストを抽出

        Args:
            event: ADKイベント

        Returns:
            テキスト（存在しない場合はNone）
        """
        if not event.content:
            return None

        if not event.content.parts:
            return None

        texts = [part.text for part in event.content.parts if part.text]
        if not texts:
            return None

        return " ".join(texts)
