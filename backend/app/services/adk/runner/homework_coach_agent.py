"""HomeworkCoachAgent - Agent Engine デプロイ用ラッパークラス

Agent Engine にデプロイするための Router Agent ラッパー。
serialize_agent.py と deploy_agent_engine.py の両方から共有される。

Agent Engine プロキシ (agent_engines.get()) は、デプロイ済みオブジェクトの
sync メソッド (create_session, stream_query) から async_create_session,
async_stream_query を自動生成する。そのため sync 版のみ定義すればよい。
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Coroutine, Generator
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

from google.adk import Runner
from google.adk.agents import Agent
from google.genai import types

from app.services.adk.memory.memory_factory import create_memory_service
from app.services.adk.sessions.session_factory import create_session_service

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _run_coroutine_sync(coro: Coroutine[Any, Any, T]) -> T:
    """コルーチンを同期的に実行する（既存イベントループ内でも安全に動作）

    Agent Engine サーバー環境では既にイベントループが動作しているため、
    asyncio.run() を直接呼ぶと RuntimeError が発生する。
    その場合は別スレッドでイベントループを作成して実行する。

    Args:
        coro: 実行するコルーチン

    Returns:
        コルーチンの戻り値
    """
    try:
        loop = asyncio.get_running_loop()
        logger.info("Existing event loop detected (%s), running in separate thread", loop)
        # 既存イベントループが存在 → 別スレッドで実行
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            result = future.result()
            logger.info("Coroutine completed in separate thread")
            return result
    except RuntimeError:
        # イベントループなし → 直接実行
        logger.info("No running event loop, executing directly")
        return asyncio.run(coro)


class HomeworkCoachAgent:
    """Agent wrapper for Agent Engine deployment

    Router Agent を Agent Engine 上で動作させるためのラッパー。
    create_session, stream_query, query メソッドを提供する。
    """

    def __init__(self, agent: Agent) -> None:
        self._agent = agent
        self._runner: Runner | None = None  # Lazy initialization

    def register_operations(self) -> dict[str, list[str]]:
        """Agent Engine プロキシに公開するメソッドを登録

        Agent Engine にカスタムメソッド（create_session, stream_query）を
        登録するための設定を返す。デフォルトの query メソッドも含める。

        Returns:
            メソッド登録情報
                - "": 同期メソッドのリスト
                - "stream": ストリーミングメソッドのリスト
        """
        return {
            "": ["query", "create_session"],
            "stream": ["stream_query"],
        }

    def _get_runner(self) -> Runner:
        """Runner を遅延初期化する（デシリアライズ後に初めて呼ばれる）"""
        if self._runner is None:
            session_service = create_session_service()
            memory_service = create_memory_service()
            self._runner = Runner(
                app_name="homework-coach-agent-engine",
                agent=self._agent,
                session_service=session_service,
                memory_service=memory_service,
            )
        return self._runner

    def create_session(self, *, user_id: str) -> dict[str, Any]:
        """Agent Engine 用のセッションを作成する

        Agent Engine プロキシが async_create_session を自動生成するため、
        sync 版のみ定義する。

        Args:
            user_id: ユーザーID

        Returns:
            セッション情報 {"id": session_id}
        """
        runner = self._get_runner()

        session = _run_coroutine_sync(
            runner.session_service.create_session(
                app_name="homework-coach-agent-engine",
                user_id=user_id,
            )
        )
        return {"id": session.id}

    def stream_query(
        self,
        *,
        user_id: str,
        session_id: str,
        message: str,
    ) -> Generator[dict[str, Any], None, None]:
        """Agent Engine にクエリを送信しストリーミングで応答を返す

        Agent Engine プロキシが async_stream_query を自動生成するため、
        sync 版のみ定義する。各イベントは AgentEngineClient.extract_text()
        が期待する {"content": {"parts": [{"text": "..."}]}} 形式で返す。

        Args:
            user_id: ユーザーID
            session_id: セッションID
            message: ユーザーメッセージ

        Yields:
            イベント辞書
        """
        runner = self._get_runner()

        # Content を作成
        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        # 非同期イベントを同期的に収集し、dict 形式で yield
        async def collect_events() -> list[dict[str, Any]]:
            events: list[dict[str, Any]] = []
            logger.info("collect_events: starting run_async for session=%s", session_id)
            try:
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content,
                ):
                    has_content = bool(event.content and event.content.parts)
                    logger.info(
                        "collect_events: received event, has_content=%s, author=%s",
                        has_content,
                        getattr(event, "author", "unknown"),
                    )
                    if has_content:
                        for part in event.content.parts:
                            if part.text:
                                events.append(
                                    {
                                        "content": {
                                            "parts": [{"text": part.text}],
                                        },
                                    }
                                )
            except Exception:
                logger.exception("collect_events: error during run_async")
                raise
            logger.info("collect_events: completed with %d text events", len(events))
            return events

        yield from _run_coroutine_sync(collect_events())

    def query(self, message: str) -> str:
        """Query the agent with a message

        Args:
            message: ユーザーメッセージ

        Returns:
            エージェントの応答文字列
        """
        # Content を作成
        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        # 非同期実行して応答テキストを収集
        async def run_query() -> str:
            runner = self._get_runner()
            response_texts: list[str] = []
            async for event in runner.run_async(
                user_id="api-user",
                session_id="api-session",
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_texts.append(part.text)
            return " ".join(response_texts)

        return _run_coroutine_sync(run_query())
