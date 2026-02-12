#!/usr/bin/env python3
"""Agent Engine デプロイスクリプト

Router Agent を Vertex AI Agent Engine にデプロイする。
既存の Agent Engine インスタンスを更新、または新規作成する。

Usage:
    uv run python scripts/deploy_agent_engine.py --project <project-id>

環境変数:
    GCP_PROJECT_ID: GCP プロジェクト ID（--project の代替）
    GCP_LOCATION: GCP ロケーション（--location の代替、デフォルト: us-central1）
    GCS_STAGING_BUCKET: GCS ステージングバケット名（--bucket の代替）
    AGENT_ENGINE_RESOURCE_NAME: 既存リソース名（更新時に使用、--resource-name の代替）
"""

import argparse
import os
import sys

# backend ディレクトリを PYTHONPATH に追加
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def deploy_agent(
    project: str,
    location: str,
    staging_bucket: str,
    resource_name: str | None = None,
) -> str:
    """Router Agent を Agent Engine にデプロイする

    Args:
        project: GCP プロジェクト ID
        location: GCP ロケーション
        staging_bucket: GCS ステージングバケット名
        resource_name: 既存リソース名（更新時）

    Returns:
        Agent Engine リソース名
    """
    import vertexai

    from app.services.adk.agents import create_router_agent
    from app.services.adk.runner.homework_coach_agent import HomeworkCoachAgent

    vertexai.init(project=project, location=location)

    print(f"Project: {project}")
    print(f"Location: {location}")
    print(f"Staging bucket: gs://{staging_bucket}")

    # Router Agent を作成
    print("\nCreating Router Agent...")
    root_agent = create_router_agent()

    # HomeworkCoachAgent でラップ（AdkApp の代わりに使用）
    print("Wrapping with HomeworkCoachAgent...")
    agent_wrapper = HomeworkCoachAgent(root_agent)

    if resource_name:
        # 既存の Agent Engine を更新
        print(f"\nUpdating existing Agent Engine: {resource_name}")
        remote_app = agent_engines_update(
            resource_name=resource_name,
            agent=agent_wrapper,
            staging_bucket=staging_bucket,
        )
    else:
        # 新規作成
        print("\nCreating new Agent Engine...")
        client = vertexai.Client(project=project, location=location)
        remote_app = client.agent_engines.create(
            agent=agent_wrapper,
            config={
                "display_name": "homework-coach-router-agent",
                "description": "宿題コーチロボット - Router Agent (Phase 3)",
                "staging_bucket": f"gs://{staging_bucket}",
                "requirements": [
                    "google-cloud-aiplatform[adk,agent_engines]>=1.126.1",
                    "google-adk>=1.23.0",
                    "google-cloud-firestore>=2.19.0",
                ],
            },
        )

    result_name: str = remote_app.api_resource.name  # type: ignore[attr-defined]
    engine_id = result_name.split("/")[-1]

    print("\nDeployment successful!")
    print(f"  Resource name: {result_name}")
    print(f"  Engine ID: {engine_id}")
    print("\nSet the following environment variables:")
    print(f"  export AGENT_ENGINE_RESOURCE_NAME={result_name}")
    print(f"  export AGENT_ENGINE_ID={engine_id}")

    return result_name


def agent_engines_update(
    resource_name: str,
    agent: object,
    staging_bucket: str,
) -> object:
    """既存の Agent Engine を更新する

    Args:
        resource_name: 既存リソース名
        agent: HomeworkCoachAgent インスタンス
        staging_bucket: GCS ステージングバケット名

    Returns:
        更新後の remote_app
    """
    from vertexai import agent_engines

    remote_app = agent_engines.get(resource_name)
    remote_app.update(  # type: ignore[call-arg]
        agent=agent,
        config={
            "staging_bucket": f"gs://{staging_bucket}",
            "requirements": [
                "google-cloud-aiplatform[adk,agent_engines]>=1.126.1",
                "google-adk>=1.23.0",
                "google-cloud-firestore>=2.19.0",
            ],
        },
    )
    return remote_app


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Router Agent を Agent Engine にデプロイする",
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
    parser.add_argument(
        "--bucket",
        default=os.environ.get("GCS_STAGING_BUCKET"),
        help="GCS ステージングバケット名（env: GCS_STAGING_BUCKET）",
    )
    parser.add_argument(
        "--resource-name",
        default=os.environ.get("AGENT_ENGINE_RESOURCE_NAME"),
        help="既存リソース名（更新時、env: AGENT_ENGINE_RESOURCE_NAME）",
    )

    args = parser.parse_args()

    if not args.project:
        print("Error: --project or GCP_PROJECT_ID is required", file=sys.stderr)
        sys.exit(1)

    if not args.bucket:
        print("Error: --bucket or GCS_STAGING_BUCKET is required", file=sys.stderr)
        sys.exit(1)

    # 空文字列の resource_name を None として扱う（GitHub Secrets 未設定時対策）
    resource_name = args.resource_name if args.resource_name else None

    deploy_agent(
        project=args.project,
        location=args.location,
        staging_bucket=args.bucket,
        resource_name=resource_name,
    )


if __name__ == "__main__":
    main()
