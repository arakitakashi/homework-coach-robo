# Task List - Agent Engine統合による内部完結型Router Agent実装

## Phase 1: 技術調査とアーキテクチャ確認

### 1.1. Agent Engine API仕様の確認

- [ ] デプロイ済みAgent Engineのエンドポイント確認
- [ ] セッション管理API仕様の確認
  - [ ] `create_session` / `async_create_session`
  - [ ] `get_session` / `async_get_session`
  - [ ] `list_sessions` / `async_list_sessions`
  - [ ] `delete_session` / `async_delete_session`
- [ ] Memory Bank API仕様の確認
  - [ ] `async_add_session_to_memory`
  - [ ] `async_search_memory`
- [ ] Agent Engine APIクライアントの実装確認
  - [ ] `backend/app/services/adk/runner/agent_engine_client.py`

### 1.2. 既存コードの理解

- [ ] 現在のVoiceStreamingService実装を確認
  - [ ] `backend/app/services/voice/streaming_service.py`
  - [ ] `create_socratic_agent()`の使用箇所
  - [ ] Runnerの使用方法
- [ ] Router Agent実装を確認
  - [ ] `backend/app/services/adk/agents/router.py`
  - [ ] サブエージェント構成
- [ ] シリアライゼーションスクリプトを確認
  - [ ] `backend/scripts/serialize_agent.py`
  - [ ] 現在のpickle化方法

### 1.3. Terraform設定の確認

- [ ] Agent Engine Terraform設定を確認
  - [ ] `infrastructure/terraform/modules/agent_engine/`
  - [ ] GCS URIs設定
  - [ ] 環境変数設定

## Phase 2: テスト実装（TDD）

### 2.1. Agent Engineラッパーのテスト

- [ ] `tests/unit/services/adk/agent_engine/test_agent_wrapper.py`作成
- [ ] セッション管理のテスト
  - [ ] セッション作成のテスト
  - [ ] セッション取得のテスト（存在する場合）
  - [ ] セッション取得のテスト（存在しない場合）
  - [ ] セッション削除のテスト
- [ ] クエリ実行のテスト
  - [ ] 正常系（イベント受信）
  - [ ] 異常系（Agent Engineエラー）
- [ ] Memory Bank統合のテスト
  - [ ] 記憶追加のテスト
  - [ ] 記憶検索のテスト

### 2.2. VoiceStreamingServiceのテスト

- [ ] `tests/unit/services/voice/test_streaming_service_v2.py`作成
- [ ] Agent Engineモード（use_agent_engine=True）のテスト
  - [ ] 初期化のテスト
  - [ ] イベント受信のテスト
  - [ ] Router Agent統合のテスト
- [ ] Firestoreモード（use_agent_engine=False）のテスト
  - [ ] 後方互換性のテスト
- [ ] エラーハンドリングのテスト
  - [ ] Agent Engine障害時のフォールバック

### 2.3. シリアライゼーションのテスト

- [ ] `tests/unit/scripts/test_serialize_agent.py`作成
- [ ] pickle化の成功テスト
- [ ] Firestore依存排除の確認テスト

## Phase 3: 実装

### 3.1. Agent Engineラッパーの実装

- [ ] `backend/app/services/adk/agent_engine/__init__.py`作成
- [ ] `backend/app/services/adk/agent_engine/agent_wrapper.py`実装
  - [ ] `AgentEngineWrapper`クラス定義
  - [ ] `__init__()`実装
  - [ ] `create_session()`実装
  - [ ] `get_session()`実装
  - [ ] `query()`実装
    - [ ] セッション取得/作成ロジック
    - [ ] Agent Engine APIクライアント統合
    - [ ] イベントyield
  - [ ] `add_to_memory()`実装
  - [ ] `search_memory()`実装
- [ ] エラーハンドリング追加
  - [ ] `AgentEngineError`カスタム例外
  - [ ] リトライロジック
  - [ ] ログ出力

### 3.2. Agent Engine APIクライアントの確認・更新

- [ ] `backend/app/services/adk/runner/agent_engine_client.py`確認
- [ ] 必要に応じて更新
  - [ ] セッション管理API統合
  - [ ] Memory Bank API統合
  - [ ] エラーハンドリング

### 3.3. VoiceStreamingServiceの更新

- [ ] `backend/app/services/voice/streaming_service.py`更新
  - [ ] `create_router_agent()`インポート
  - [ ] `AgentEngineWrapper`インポート
  - [ ] `__init__()`更新
    - [ ] `use_agent_engine`パラメータ追加
    - [ ] Router Agent統合
    - [ ] Agent Engineラッパー初期化
    - [ ] Firestoreモード保持（後方互換）
  - [ ] `receive_events()`更新
    - [ ] Agent Engineモード分岐
    - [ ] イベント変換ロジック
  - [ ] `send_audio()`, `send_text()`の互換性確認

### 3.4. シリアライゼーションスクリプトの更新

- [ ] `backend/scripts/serialize_agent.py`更新
  - [ ] `create_router_agent()`使用
  - [ ] `AgentEngineWrapper`統合
  - [ ] Firestore依存排除
  - [ ] pickle化確認ロジック

### 3.5. 環境変数・設定の追加

- [ ] `.env.example`更新
  - [ ] `USE_AGENT_ENGINE=true`追加
  - [ ] Agent Engine関連の環境変数追加
- [ ] `backend/app/core/config.py`更新
  - [ ] `USE_AGENT_ENGINE`設定追加

## Phase 4: 統合テスト

### 4.1. E2Eテストの作成

- [ ] `tests/integration/test_agent_engine_flow.py`作成
- [ ] VoiceStreamingService E2Eテスト
  - [ ] セッション作成→クエリ→イベント受信フロー
  - [ ] Router Agentサブエージェント切り替え
  - [ ] ツール実行確認
- [ ] Memory Bank統合E2Eテスト
  - [ ] 記憶追加→検索フロー

### 4.2. 既存テストの更新

- [ ] `tests/integration/test_voice_stream_flow.py`更新
  - [ ] Agent Engineモードでのテスト追加
  - [ ] Firestoreモードの後方互換テスト

## Phase 5: デプロイとドキュメント

### 5.1. Agent Engineデプロイ

- [ ] pickleファイル生成
  ```bash
  cd backend && uv run python scripts/serialize_agent.py
  ```
- [ ] GCSにアップロード
  ```bash
  gsutil cp pickle.pkl gs://[BUCKET]/agents/
  ```
- [ ] Agent Engineに反映
  - [ ] Terraform apply
  - [ ] デプロイ確認

### 5.2. ローカルテストの実行

- [ ] Backend lint
  ```bash
  cd backend && uv run ruff check app tests
  ```
- [ ] Backend型チェック
  ```bash
  cd backend && uv run mypy .
  ```
- [ ] Backend単体テスト
  ```bash
  cd backend && uv run pytest tests/unit/ -v
  ```
- [ ] Backend統合テスト
  ```bash
  cd backend && uv run pytest tests/integration/ -v
  ```
- [ ] カバレッジ確認
  ```bash
  cd backend && uv run pytest tests/ --cov=app --cov-report=term-missing
  ```

### 5.3. ドキュメント更新

- [ ] `CLAUDE.md`更新
  - [ ] Development Context更新
  - [ ] Agent Engine統合状況追記
- [ ] `docs/implementation-status.md`更新
  - [ ] 完了済み機能に追加
  - [ ] ステアリングディレクトリ一覧更新
- [ ] `docs/agent-architecture.md`更新
  - [ ] Agent Engineラッパーの説明追加
  - [ ] アーキテクチャ図更新
- [ ] `README.md`更新（必要に応じて）
  - [ ] セットアップ手順にAgent Engine設定を追加

## Phase 6: PR作成とCI/CD確認

- [ ] コミット
  - [ ] テストコミット
  - [ ] 実装コミット（Agent Engineラッパー）
  - [ ] 実装コミット（VoiceStreamingService更新）
  - [ ] 実装コミット（シリアライゼーション更新）
  - [ ] ドキュメント更新コミット
- [ ] PR作成
  - [ ] タイトル: `feat(adk): Agent Engine統合による内部完結型Router Agent実装`
  - [ ] 説明: requirements.mdの内容を要約
  - [ ] Closes #98
- [ ] CI/CDパイプライン確認
  - [ ] Backend CIパス
  - [ ] Frontend CIパス（影響なし確認）
  - [ ] E2E CIパス

## Phase 7: issue #94への復帰

- [ ] issue #98完了確認
- [ ] `.steering/20260211-phase2-websocket-events/`に復帰
- [ ] `SUSPENDED.md`を`RESUMED.md`に更新
- [ ] Phase 2 WebSocketイベント送信の実装開始
  - [ ] Agent Engineラッパー経由でのイベント取得
  - [ ] `toolExecution`, `agentTransition`, `emotionUpdate`送信

## 実装メモ

### 参照すべきファイル

- `backend/app/services/voice/streaming_service.py` - 現在の実装
- `backend/app/services/adk/agents/router.py` - Phase 2 Router Agent
- `backend/app/services/adk/runner/agent_engine_client.py` - Agent Engine APIクライアント
- `backend/scripts/serialize_agent.py` - シリアライゼーション
- `infrastructure/terraform/modules/agent_engine/` - Terraform設定

### 技術調査リンク

- [Agent Engine概要](https://docs.cloud.google.com/agent-builder/agent-engine/overview?hl=ja)
- [ADKドキュメント](https://github.com/google/adk)

### 既知の課題

1. **Agent Engine API仕様の不確実性**: ドキュメントが完全ではない可能性があるため、実装時に調査が必要
2. **LiveRequestQueueとの統合**: Agent Engineが`LiveRequestQueue`をサポートしているかを確認する必要がある
3. **パフォーマンス**: Firestoreと比較してレイテンシを測定する必要がある
