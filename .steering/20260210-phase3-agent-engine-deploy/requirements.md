# Requirements - Phase 3: Agent Engine デプロイ (#53)

## 背景・目的

Phase 2a〜2d で ADK エージェント（Router Agent + 4つのサブエージェント + 6つのツール）の実装が完了した。
現在は Cloud Run 上で FastAPI サーバーがエージェントをインプロセスで実行している。

Phase 3 では、エージェントを Vertex AI Agent Engine にデプロイし、マネージドインフラ上で実行する。
これにより以下のメリットが得られる：

- **マネージド運用**: スケーリング・監視・ログの自動管理
- **セッション管理の統合**: VertexAiSessionService による統合セッション管理
- **Memory Bank**: VertexAiMemoryBankService による意味検索ベースの長期記憶
- **トレーシング**: Cloud Trace による可観測性

## 要求事項

### 機能要件

1. **デプロイスクリプトの拡張**
   - 既存の `create_agent_engine.py` を拡張し、Router Agent を Agent Engine にデプロイ
   - `AdkApp` ラッパーで Agent コードをパッケージング
   - 必要な依存関係（requirements）とパッケージを指定

2. **テキスト対話エンドポイントの移行**
   - `POST /api/v1/dialogue/run` (SSE) を Agent Engine API に接続
   - `remote_app.async_stream_query()` でストリーミング応答を取得
   - 既存の SSE イベント形式（text/error/done）を維持

3. **セッション管理の移行**
   - `FirestoreSessionService` → `VertexAiSessionService` への切り替え
   - セッションファクトリパターンの導入（環境変数ベース切り替え）
   - 既存のセッション API 互換性を維持

4. **テスト用スクリプト**
   - デプロイされたエージェントの動作確認スクリプト
   - セッション作成 → メッセージ送信 → レスポンス確認

### 非機能要件

- テストカバレッジ 80% 以上を維持
- mypy / ruff エラーなし
- 既存テストの回帰なし

### 制約条件

- **音声ストリーミング（WebSocket + Gemini Live API）は Phase 3 の範囲外**
  - `run_live()` は Agent Engine の HTTP API では未サポート
  - 音声ストリーミングは引き続き Cloud Run でローカル Runner を使用
  - ただし VertexAiSessionService は共有可能
- Agent Engine のデプロイには GCS ステージングバケットが必要
- `google-cloud-aiplatform[adk,agent_engines]` パッケージが必要

## 対象範囲

### In Scope

- デプロイスクリプトの拡張（`scripts/deploy_agent_engine.py`）
- Agent Engine クライアントラッパーの作成
- テキスト対話エンドポイントの Agent Engine 接続
- セッションサービスのファクトリパターン化
- テスト用スクリプト
- 既存テストの更新（モック対応）

### Out of Scope

- 音声ストリーミング（WebSocket）の Agent Engine 移行
- CI/CD パイプラインへの Agent Engine デプロイ統合（別 Issue）
- 本番環境へのデプロイ（開発環境のみ）
- A/B テスト基盤（#55 で対応）

## 成功基準

1. Router Agent が Agent Engine にデプロイされ、テキストメッセージに応答できる
2. テキスト対話エンドポイントが Agent Engine 経由で動作する
3. セッションが Agent Engine で管理される
4. 全テストがパスし、カバレッジ 80% 以上
5. mypy / ruff エラーなし
