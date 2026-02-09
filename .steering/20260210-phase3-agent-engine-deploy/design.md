# Design - Phase 3: Agent Engine デプロイ

## アーキテクチャ概要

### 現在のアーキテクチャ（Cloud Run インプロセス実行）

```
Cloud Run (FastAPI)
├── POST /dialogue/run (SSE)
│   └── AgentRunnerService
│       └── Runner.run_async()
│           └── Router Agent (in-process)
│               └── 4 Sub-agents + 6 Tools
│
└── WebSocket /ws/{user_id}/{session_id}
    └── VoiceStreamingService
        └── Runner.run_live()
            └── Socratic Agent (legacy, in-process)

Persistence:
├── FirestoreSessionService
└── FirestoreMemoryService / VertexAiMemoryBankService
```

### Phase 3 ターゲットアーキテクチャ

```
Cloud Run (FastAPI - thin proxy)
├── POST /dialogue/run (SSE)
│   └── AgentEngineClient
│       └── remote_app.async_stream_query()
│           └── Agent Engine (managed)
│               └── Router Agent + 4 Sub-agents + 6 Tools
│
└── WebSocket /ws/{user_id}/{session_id}
    └── VoiceStreamingService (変更なし)
        └── Runner.run_live()
            └── Socratic Agent (in-process, 音声専用)

Session:
├── VertexAiSessionService (Agent Engine 統合) ← NEW
└── FirestoreSessionService (フォールバック / 音声用)

Memory:
└── VertexAiMemoryBankService (Agent Engine で自動有効化)
```

## 技術選定

### デプロイ方式

**Python SDK 方式を採用**（CLI 方式ではなく）

理由:
- スクリプトとして自動化しやすい
- CI/CD パイプラインに統合しやすい
- パラメータを環境変数で制御可能

```python
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

remote_app = client.agent_engines.create(
    agent=adk_app,
    config={
        "staging_bucket": f"gs://{BUCKET_NAME}",
        "requirements": ["google-cloud-aiplatform[adk,agent_engines]"],
        "extra_packages": ["./backend/app"],
    },
)
```

### Agent Engine クライアント

Agent Engine にデプロイされたエージェントとの通信は Python SDK を使用:

```python
# 接続
remote_app = agent_engines.get(resource_name)

# セッション作成
session = await remote_app.async_create_session(user_id="...")

# クエリ（ストリーミング）
async for event in remote_app.async_stream_query(
    user_id="...",
    session_id="...",
    message="...",
):
    # イベント処理
```

## ファイル構成

### 新規ファイル

```
backend/
├── scripts/
│   ├── deploy_agent_engine.py   # Agent Engine デプロイスクリプト（拡張版）
│   └── test_agent_engine.py     # デプロイ後テストスクリプト
├── app/
│   └── services/
│       └── adk/
│           ├── runner/
│           │   └── agent_engine_client.py  # Agent Engine クライアント
│           └── sessions/
│               └── session_factory.py      # セッションファクトリ
└── tests/
    └── unit/
        └── services/
            └── adk/
                ├── runner/
                │   └── test_agent_engine_client.py
                └── sessions/
                    └── test_session_factory.py
```

### 変更ファイル

```
backend/
├── app/
│   ├── api/v1/
│   │   └── dialogue_runner.py    # Agent Engine 経由に切り替え
│   └── services/
│       └── adk/
│           ├── runner/
│           │   └── __init__.py   # エクスポート追加
│           └── sessions/
│               └── __init__.py   # エクスポート追加
└── pyproject.toml                # google-cloud-aiplatform[agent_engines] 追加
```

## データ設計

### セッションファクトリ

環境変数ベースの切り替え:

| 環境変数 | 値 | セッションサービス |
|---------|---|-------------------|
| `AGENT_ENGINE_ID` | 未設定 | `FirestoreSessionService` |
| `AGENT_ENGINE_ID` | 設定済み | `VertexAiSessionService` |

### Agent Engine クライアント設定

| 環境変数 | 説明 | デフォルト |
|---------|------|-----------|
| `AGENT_ENGINE_RESOURCE_NAME` | デプロイ済みエージェントのリソース名 | なし（必須） |
| `GCP_PROJECT_ID` | GCP プロジェクト ID | なし |
| `GCP_LOCATION` | GCP ロケーション | `us-central1` |
| `GCS_STAGING_BUCKET` | デプロイ用 GCS バケット | なし（デプロイ時のみ必須） |

## エラーハンドリング

### Agent Engine 接続エラー

- Agent Engine が利用不可 → `AGENT_ENGINE_RESOURCE_NAME` 未設定時はローカル Runner にフォールバック
- 接続タイムアウト → クライアントに 503 Service Unavailable

### デプロイエラー

- GCS バケット未作成 → 明確なエラーメッセージ
- 権限不足 → IAM ロール確認手順を表示

## セキュリティ考慮事項

- Agent Engine のサービスアカウントに Firestore アクセス権が必要（ツールが Firestore を操作するため）
- GCS ステージングバケットは非公開設定
- Agent Engine エンドポイントは認証必須（サービスアカウントまたは OAuth）

## パフォーマンス考慮事項

- Agent Engine 呼び出しはネットワーク経由のため、ローカル実行より数百 ms のレイテンシ増
- SSE ストリーミングで体感レイテンシを軽減
- 初回リクエストはコールドスタートの可能性あり

## 代替案と採用理由

| 案 | メリット | デメリット | 採用 |
|---|---------|-----------|------|
| **A: Python SDK デプロイ** | 自動化しやすい、CI/CD統合可能 | SDK バージョン依存 | ✅ |
| B: ADK CLI デプロイ | シンプル | スクリプト統合が困難 | ❌ |
| C: 全エンドポイント移行 | 完全マネージド | 音声ストリーミング未対応 | ❌ |
