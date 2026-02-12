#!/usr/bin/env python3
"""Router Agent をpickleファイルにシリアライズ

Agent Engine にデプロイするため、Router Agent を cloudpickle で
シリアライズして pickle.pkl ファイルを生成する。

Usage:
    uv run python scripts/serialize_agent.py

Output:
    - pickle.pkl: シリアライズされたエージェント
"""

from __future__ import annotations

import os
import sys
from collections.abc import Generator
from typing import Any

# backend ディレクトリを PYTHONPATH に追加
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def main() -> None:
    """エージェントをシリアライズ"""
    try:
        import cloudpickle

        from app.services.adk.agents import create_router_agent

        print("Creating Router Agent...")
        root_agent = create_router_agent()

        print("Creating AgentEngine-compatible wrapper...")

        from google.adk import Runner
        from google.adk.agents import Agent
        from google.genai import types

        from app.services.adk.memory.memory_factory import create_memory_service
        from app.services.adk.sessions.session_factory import create_session_service

        # Simple wrapper class that exposes query method for Agent Engine
        # This is serialized directly without AdkApp wrapper
        class HomeworkCoachAgent:
            """Agent wrapper for Agent Engine deployment

            Agent Engine プロキシ (agent_engines.get()) は、デプロイ済みオブジェクトの
            sync メソッド (create_session, stream_query) から async_create_session,
            async_stream_query を自動生成する。そのため sync 版のみ定義すればよい。
            """

            def __init__(self, agent: Agent) -> None:
                self._agent = agent
                self._runner: Runner | None = None  # Lazy initialization

            def _get_runner(self) -> Runner:
                """Lazy initialization of Runner (after deserialization)"""
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
                import asyncio

                runner = self._get_runner()

                session = asyncio.run(
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
                import asyncio

                runner = self._get_runner()

                # Content を作成
                content = types.Content(
                    role="user",
                    parts=[types.Part(text=message)],
                )

                # 非同期イベントを同期的に収集し、dict 形式で yield
                async def collect_events() -> list[dict[str, Any]]:
                    events: list[dict[str, Any]] = []
                    async for event in runner.run_async(
                        user_id=user_id,
                        session_id=session_id,
                        new_message=content,
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    events.append(
                                        {
                                            "content": {
                                                "parts": [{"text": part.text}],
                                            },
                                        }
                                    )
                    return events

                yield from asyncio.run(collect_events())

            def query(self, message: str) -> str:
                """Query the agent with a message

                Args:
                    message: User message/query

                Returns:
                    Agent response as string
                """
                import asyncio

                # Create content from message
                content = types.Content(
                    role="user",
                    parts=[types.Part(text=message)],
                )

                # Run agent and collect response
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

                # Run async code in sync context
                return asyncio.run(run_query())

        agent_wrapper = HomeworkCoachAgent(root_agent)

        output_file = "pickle.pkl"
        print("Serializing directly (without AdkApp)...")
        with open(output_file, "wb") as f:
            cloudpickle.dump(agent_wrapper, f)

        print(f"✓ Successfully serialized to {output_file}")
        print(f"  File size: {os.path.getsize(output_file)} bytes")

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
