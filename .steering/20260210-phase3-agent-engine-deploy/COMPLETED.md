# COMPLETED - Phase 3: Agent Engine デプロイ (#53)

**完了日**: 2026-02-10
**Pull Request**: #87
**担当者**: Claude Code + @arakitakashi

---

## 実装内容の要約

Phase 3では、Phase 2で実装したADKエージェント（Router Agent + 4サブエージェント）を**Vertex AI Agent Engine**にデプロイし、マネージドインフラ上で実行できる基盤を構築しました。

### 主要実装

#### 1. セッションファクトリ (`session_factory.py`)
- 環境変数ベースで`FirestoreSessionService`と`VertexAiSessionService`を切り替え
- `AGENT_ENGINE_ID`が設定されている場合は`VertexAiSessionService`を返し、未設定の場合は`FirestoreSessionService`にフォールバック
- ローカル開発とAgent Engineデプロイの両方に対応

#### 2. Agent Engineクライアント (`agent_engine_client.py`)
- Agent Engineにデプロイされたエージェントとの通信を管理
- 以下のメソッドを提供:
  - `create_session(user_id)`: セッション作成
  - `stream_query(user_id, session_id, message)`: ストリーミングクエリ
  - `extract_text(event)`: イベント辞書からテキスト抽出

#### 3. テキスト対話エンドポイントの移行 (`dialogue_runner.py`)
- `POST /api/v1/dialogue/run`をAgent Engine経由のSSEストリーミングに切り替え
- 環境変数`AGENT_ENGINE_RESOURCE_NAME`が設定されている場合はAgent Engineを使用
- 未設定の場合はローカルRunnerにフォールバック（既存動作を維持）

#### 4. デプロイ・テストスクリプト
- `scripts/deploy_agent_engine.py`: Router AgentをAgent Engineにデプロイ
- `scripts/test_agent_engine.py`: デプロイ後の動作確認（セッション作成→メッセージ送信→レスポンス確認）

#### 5. 依存関係の追加
- `pyproject.toml`に`google-cloud-aiplatform[agent_engines]`を追加

---

## 実装の詳細

### アーキテクチャの変更

**Before (Phase 2):**
```
Cloud Run (FastAPI)
└── POST /dialogue/run
    └── AgentRunnerService (in-process)
        └── Router Agent + 4 Sub-agents
```

**After (Phase 3):**
```
Cloud Run (FastAPI - thin proxy)
└── POST /dialogue/run
    └── AgentEngineClient
        └── Agent Engine (managed)
            └── Router Agent + 4 Sub-agents
```

### 環境変数

| 変数名 | 説明 | 設定時の動作 |
|--------|------|-------------|
| `AGENT_ENGINE_RESOURCE_NAME` | Agent Engineリソース名 | Agent Engine経由でSSEストリーミング |
| `AGENT_ENGINE_ID` | Agent Engine ID | `VertexAiSessionService`を使用 |
| `GCP_PROJECT_ID` | GCPプロジェクトID | Agent Engine接続時に使用 |
| `GCP_LOCATION` | GCPロケーション | デフォルト: `us-central1` |
| `GCS_STAGING_BUCKET` | デプロイ用GCSバケット | デプロイスクリプトで使用 |

### テスト結果

- **全テスト**: 548 passed
- **Lint**: All checks passed
- **型チェック**: 0 errors, 119 files
- **カバレッジ**: 90%

---

## 発生した問題と解決方法

### 1. Agent Engine APIの型情報不足

**問題**: `agent_engines.get()`, `async_create_session()`, `async_stream_query()`の型情報がSDKで提供されていない

**解決**: `# type: ignore[attr-defined]`を使用して型チェックをバイパス。将来SDKが型情報を提供したら削除予定。

```python
self._remote_app = agent_engines.get(resource_name)  # 型推論可能
session: dict[str, Any] = await self._remote_app.async_create_session(  # type: ignore[attr-defined]
    user_id=user_id,
)
```

### 2. フォールバックロジックの設計

**問題**: ローカル開発時とAgent Engineデプロイ時で動作を切り替える必要がある

**解決**: 環境変数による切り替えとフォールバックロジックを実装:
- `AGENT_ENGINE_RESOURCE_NAME`未設定時はローカルRunnerを使用（開発環境）
- 設定時はAgent Engineを使用（本番環境）
- セッションサービスも同様にファクトリパターンで切り替え

### 3. WebSocket音声ストリーミングの扱い

**問題**: Agent EngineのHTTP APIは`run_live()`（WebSocket音声ストリーミング）に未対応

**解決**: Phase 3の範囲外として、音声ストリーミングは引き続きCloud Runでローカル実行を維持。テキスト対話のみAgent Engine経由に移行。

---

## 今後の改善点

### 短期（Phase 3完了後）

1. **Issue #54: セッション管理の完全移行**
   - 現在は`FirestoreSessionService`と`VertexAiSessionService`が並存
   - データ移行計画を策定し、段階的に`VertexAiSessionService`に統一

2. **CI/CDパイプラインへの統合**
   - Agent Engineデプロイをデプロイワークフローに組み込む
   - デプロイ後の自動テストを実行

### 中期（Phase 4以降）

3. **Issue #55: A/Bテスト基盤**
   - ローカルRunnerとAgent Engineの性能比較
   - トラフィック分割による段階的移行

4. **音声ストリーミングのAgent Engine対応検討**
   - Agent EngineがWebSocket/`run_live()`をサポートした場合に移行検討
   - 現時点では未サポートのため保留

5. **本番環境へのデプロイ**
   - 開発環境で十分な動作確認後、本番環境にデプロイ
   - モニタリング・アラートの設定

---

## 学んだこと (Lessons Learned)

### 技術的な学び

1. **Agent Engineのデプロイモデル**
   - Python SDKを使った`AdkApp`デプロイはCI/CD統合に適している
   - GCSステージングバケットが必須（パッケージと依存関係のアップロード）
   - `extra_packages`で`./backend/app`を指定することで、カスタムコードをデプロイ可能

2. **ファクトリパターンの有効性**
   - セッションサービスをファクトリで抽象化することで、ローカル開発と本番環境の切り替えがスムーズ
   - テストでもモック化が容易

3. **型安全性とのバランス**
   - サードパーティSDKが型情報を提供していない場合、`type: ignore`を使用しつつ、実行時の型チェック（`isinstance`, `assert`）でカバー

### プロセス的な学び

1. **段階的移行の重要性**
   - いきなり全エンドポイントを移行せず、テキスト対話のみを先に移行
   - フォールバックロジックを実装することで、問題発生時のロールバックが容易

2. **環境変数による制御**
   - 環境変数で動作を切り替えることで、コード変更なしに本番環境と開発環境を管理可能
   - デプロイスクリプトも環境変数で制御できるため、CI/CD統合が容易

3. **テストカバレッジの維持**
   - Agent Engineクライアントはモックでテスト
   - 実際のAgent Engine接続はデプロイ後テストスクリプトで確認
   - ローカルテストと統合テストの役割分担が重要

---

## 関連リソース

- **Issue**: #53 (Phase 3: Agent Engine デプロイ基盤)
- **Pull Request**: #87
- **ドキュメント**:
  - `docs/agent-architecture.md` (Phase 3追記)
  - `docs/implementation-status.md` (完了済み機能一覧)
- **コミット**:
  - fe0357d: feat(sessions): add session service factory for Agent Engine
  - 603efb4: feat(runner): add Agent Engine client wrapper
  - 458b5bd: feat(api): route text dialogue through Agent Engine with fallback
  - cdad39e: feat(scripts): add Agent Engine deploy and test scripts

---

## まとめ

Phase 3では、ADKエージェントをマネージドインフラ（Agent Engine）にデプロイする基盤を構築しました。これにより、スケーリング・監視・ログの自動管理が可能になり、運用負荷を削減できます。

テキスト対話エンドポイントはAgent Engine経由に移行しましたが、音声ストリーミングは引き続きCloud Runで実行します。今後は、Issue #54でセッション管理を完全にAgent Engineに移行し、Issue #55でA/Bテスト基盤を構築する予定です。

**Phase 3: Agent Engine デプロイ基盤の構築完了 ✅**
