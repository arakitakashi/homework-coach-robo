#!/usr/bin/env python3
"""Agent Engine 作成スクリプト

Vertex AI Agent Engine を作成し、Memory Bank 用のインフラをセットアップする。
作成された Agent Engine ID を環境変数 AGENT_ENGINE_ID として設定する。

Usage:
    uv run python scripts/create_agent_engine.py --project <project-id> --location <location>

環境変数:
    GCP_PROJECT_ID: GCP プロジェクト ID（--project の代替）
    GCP_LOCATION: GCP ロケーション（--location の代替、デフォルト: us-central1）
"""

import argparse
import os
import sys


def create_agent_engine(project: str, location: str) -> str:
    """Agent Engine を作成する

    Args:
        project: GCP プロジェクト ID
        location: GCP ロケーション

    Returns:
        Agent Engine ID
    """
    import vertexai

    client = vertexai.Client(project=project, location=location)

    print(f"Creating Agent Engine in project={project}, location={location}...")

    agent_engine = client.agent_engines.create(
        config={
            "display_name": "homework-coach-engine",
            "description": "宿題コーチロボット - Memory Bank 用 Agent Engine",
        }
    )

    engine_id: str = agent_engine.api_resource.name.split("/")[-1]

    print("\nAgent Engine created successfully!")
    print(f"  Resource name: {agent_engine.api_resource.name}")
    print(f"  Engine ID: {engine_id}")
    print("\nSet the following environment variable:")
    print(f"  export AGENT_ENGINE_ID={engine_id}")

    return engine_id


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Vertex AI Agent Engine を作成する",
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

    if not args.project:
        print("Error: --project or GCP_PROJECT_ID is required", file=sys.stderr)
        sys.exit(1)

    create_agent_engine(project=args.project, location=args.location)


if __name__ == "__main__":
    main()
