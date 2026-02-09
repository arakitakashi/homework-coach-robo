#!/usr/bin/env python3
"""Agent Engine デプロイ後テストスクリプト

デプロイ済みの Agent Engine にテストクエリを送信し、正常動作を確認する。

Usage:
    uv run python scripts/test_agent_engine.py --resource-name <resource-name>

環境変数:
    AGENT_ENGINE_RESOURCE_NAME: Agent Engine リソース名（--resource-name の代替）
    GCP_PROJECT_ID: GCP プロジェクト ID（--project の代替）
    GCP_LOCATION: GCP ロケーション（--location の代替、デフォルト: us-central1）
"""

import argparse
import asyncio
import os
import sys
from typing import Any


async def test_agent_engine(
    resource_name: str,
    project: str,
    location: str,
) -> bool:
    """Agent Engine にテストクエリを送信する

    Args:
        resource_name: Agent Engine リソース名
        project: GCP プロジェクト ID
        location: GCP ロケーション

    Returns:
        テスト成功の場合 True
    """
    import vertexai
    from vertexai import agent_engines

    vertexai.init(project=project, location=location)

    print(f"Connecting to Agent Engine: {resource_name}")
    remote_app = agent_engines.get(resource_name)

    # テスト 1: セッション作成
    print("\n--- Test 1: Create Session ---")
    session: dict[str, Any] = await remote_app.async_create_session(  # type: ignore[attr-defined]
        user_id="test-user",
    )
    session_id: str = session["id"]
    print(f"  Session created: {session_id}")

    # テスト 2: テキストクエリ（ストリーミング）
    print("\n--- Test 2: Stream Query ---")
    response_texts: list[str] = []
    event_count = 0
    async for event in remote_app.async_stream_query(  # type: ignore[attr-defined]
        user_id="test-user",
        session_id=session_id,
        message="1+1はいくつですか？",
    ):
        event_count += 1
        content = event.get("content")
        if content:
            parts = content.get("parts", [])
            for part in parts:
                text = part.get("text", "")
                if text:
                    response_texts.append(text)
                    print(f"  Event {event_count}: {text[:80]}...")

    full_response = " ".join(response_texts)
    print(f"\n  Total events: {event_count}")
    print(f"  Response length: {len(full_response)} chars")

    # テスト 3: レスポンス検証
    print("\n--- Test 3: Validate Response ---")
    if not response_texts:
        print("  FAIL: No response text received")
        return False
    print(f"  PASS: Got response: {full_response[:100]}...")

    # テスト 4: 2回目のクエリ（セッション継続確認）
    print("\n--- Test 4: Session Continuity ---")
    event_count_2 = 0
    async for _event in remote_app.async_stream_query(  # type: ignore[attr-defined]
        user_id="test-user",
        session_id=session_id,
        message="さっきの問題の答えは何でしたか？",
    ):
        event_count_2 += 1

    print(f"  Total events: {event_count_2}")
    if event_count_2 > 0:
        print("  PASS: Session continuity works")
    else:
        print("  FAIL: No events in follow-up query")
        return False

    print("\n=== All tests passed! ===")
    return True


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Agent Engine デプロイ後テスト",
    )
    parser.add_argument(
        "--resource-name",
        default=os.environ.get("AGENT_ENGINE_RESOURCE_NAME"),
        help="Agent Engine リソース名（env: AGENT_ENGINE_RESOURCE_NAME）",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("GCP_PROJECT_ID"),
        help="GCP プロジェクト ID（env: GCP_PROJECT_ID）",
    )
    parser.add_argument(
        "--location",
        default=os.environ.get("GCP_LOCATION", "us-central1"),
        help="GCP ロケーション（env: GCP_LOCATION、デフォルト: us-central1）",
    )

    args = parser.parse_args()

    if not args.resource_name:
        print(
            "Error: --resource-name or AGENT_ENGINE_RESOURCE_NAME is required",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.project:
        print("Error: --project or GCP_PROJECT_ID is required", file=sys.stderr)
        sys.exit(1)

    success = asyncio.run(
        test_agent_engine(
            resource_name=args.resource_name,
            project=args.project,
            location=args.location,
        )
    )

    if not success:
        print("\nSome tests failed!", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
