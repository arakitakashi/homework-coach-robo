"""Agent Engine クライアント

Vertex AI Agent Engine にデプロイされたエージェントとの通信を管理する。
セッション作成、ストリーミングクエリ、テキスト抽出を提供する。
"""

import logging
from collections.abc import AsyncIterator
from typing import Any

from vertexai import agent_engines

logger = logging.getLogger(__name__)


class AgentEngineClient:
    """Agent Engine クライアント

    デプロイされたエージェントへの接続を管理し、
    セッション作成・ストリーミングクエリを提供する。

    Attributes:
        resource_name: Agent Engine リソース名
        _remote_app: Agent Engine リモートアプリ
    """

    def __init__(self, resource_name: str) -> None:
        """初期化

        Args:
            resource_name: Agent Engine リソース名
                (例: projects/p/locations/l/reasoningEngines/123)
        """
        self.resource_name = resource_name
        self._remote_app = agent_engines.get(resource_name)
        logger.info("Connected to Agent Engine: %s", resource_name)

    async def create_session(self, user_id: str) -> str:
        """Agent Engine でセッションを作成する

        Args:
            user_id: ユーザーID

        Returns:
            セッションID
        """
        session: dict[str, Any] = await self._remote_app.create_session(  # type: ignore[attr-defined]
            user_id=user_id,
        )
        session_id: str = session["id"]
        logger.info("Created session: %s for user: %s", session_id, user_id)
        return session_id

    async def stream_query(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ) -> AsyncIterator[dict[str, Any]]:
        """Agent Engine にクエリを送信しストリーミングで応答を受信する

        Args:
            user_id: ユーザーID
            session_id: セッションID
            message: ユーザーメッセージ

        Yields:
            Agent Engine からのイベント辞書
        """
        async for event in self._remote_app.stream_query(  # type: ignore[attr-defined]
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            yield event

    def extract_text(self, event: dict[str, Any]) -> str | None:
        """イベント辞書からテキストを抽出する

        Args:
            event: Agent Engine イベント辞書

        Returns:
            テキスト（存在しない場合は None）
        """
        content = event.get("content")
        if not content:
            return None

        parts = content.get("parts")
        if not parts:
            return None

        texts = [p["text"] for p in parts if "text" in p]
        if not texts:
            return None

        return " ".join(texts)
