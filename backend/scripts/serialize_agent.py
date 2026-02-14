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

# backend ディレクトリを PYTHONPATH に追加
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def main() -> None:
    """エージェントをシリアライズ"""
    try:
        import cloudpickle

        from app.services.adk.agents import create_router_agent
        from app.services.adk.runner.homework_coach_agent import HomeworkCoachAgent

        print("Creating Router Agent...")
        root_agent = create_router_agent()

        print("Creating AgentEngine-compatible wrapper...")
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
