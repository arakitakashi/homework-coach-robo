# Task List - Agent Engine統合による内部完結型Router Agent実装（簡素化版）

## 🎉 タスクの大幅簡素化

AgentEngineWrapper実装が不要になったため、タスクが大幅に削減されました。

## Phase 1: 技術調査とアーキテクチャ確認

### 1.1. VertexAiSessionServiceの確認

- [x] ADK公式ドキュメント確認
  - [x] セッション管理の概要
  - [x] ADK統合時のセッション管理方法
- [ ] VertexAiSessionServiceのインポート確認
  ```python
  from google.adk.sessions import VertexAiSessionService
  ```
- [ ] `run_live()`のサポート状況確認
  - [ ] LiveRequestQueue との互換性
  - [ ] 音声ストリーミング動作確認

### 1.2. 既存コードの理解

- [x] 現在のVoiceStreamingService実装確認
  - [x] `backend/app/services/voice/streaming_service.py`
  - [x] `create_socratic_agent()`の使用箇所
  - [x] Runnerの使用方法
- [x] Router Agent実装確認
  - [x] `backend/app/services/adk/agents/router.py`
  - [x] サブエージェント構成
- [ ] シリアライゼーションスクリプト確認
  - [ ] `backend/scripts/serialize_agent.py`
  - [ ] 現在のpickle化方法

### 1.3. 環境変数の確認

- [ ] Terraformで設定されている環境変数確認
  - [ ] `PROJECT_ID`
  - [ ] `LOCATION`
  - [ ] `AGENT_ENGINE_ID`
- [ ] `.env.example`の更新計画

## Phase 2: テスト実装（TDD）

### 2.1. VoiceStreamingServiceのテスト

- [ ] `tests/unit/services/voice/test_streaming_service_v2.py`作成
- [ ] VertexAiSessionServiceモードのテスト
  - [ ] 初期化のテスト
  - [ ] Router Agent統合のテスト
  - [ ] セッション管理のテスト
- [ ] Firestoreモードのテスト
  - [ ] 後方互換性のテスト
- [ ] エラーハンドリングのテスト
  - [ ] VertexAiSessionService初期化失敗
  - [ ] セッション作成失敗

### 2.2. シリアライゼーションのテスト

- [ ] `tests/unit/scripts/test_serialize_agent.py`作成
- [ ] pickle化の成功テスト
- [ ] Firestore依存排除の確認テスト

## Phase 3: 実装

### 3.1. VoiceStreamingServiceの更新

- [ ] `backend/app/services/voice/streaming_service.py`更新
  - [ ] `create_router_agent()`インポート
    ```python
    from app.services.adk.agents.router import create_router_agent
    ```
  - [ ] `VertexAiSessionService`インポート
    ```python
    from google.adk.sessions import VertexAiSessionService
    ```
  - [ ] `__init__()`更新
    - [ ] `use_agent_engine`パラメータ追加
    - [ ] Router Agent統合
      ```python
      self._agent = create_router_agent(model=LIVE_MODEL)
      ```
    - [ ] VertexAiSessionService初期化
      ```python
      self._session_service = VertexAiSessionService(
          project_id=project_id,
          location=location,
          agent_engine_id=agent_engine_id,
      )
      ```
    - [ ] Firestoreモード保持（後方互換）
  - [ ] `receive_events()`の確認
    - [ ] 既存のrun_live()が動作するか確認
    - [ ] 必要に応じて修正

### 3.2. シリアライゼーションスクリプトの更新

- [ ] `backend/scripts/serialize_agent.py`更新
  - [ ] `create_router_agent()`使用
  - [ ] `VertexAiSessionService`統合
  - [ ] Firestore依存排除
  - [ ] pickle化確認ロジック

### 3.3. 環境変数・設定の追加

- [ ] `.env.example`更新
  ```bash
  USE_AGENT_ENGINE=true
  PROJECT_ID=your-project-id
  LOCATION=us-central1
  AGENT_ENGINE_ID=your-agent-engine-id
  ```
- [ ] `backend/app/core/config.py`更新
  - [ ] `USE_AGENT_ENGINE`設定追加
  - [ ] `PROJECT_ID`, `LOCATION`, `AGENT_ENGINE_ID`設定追加

## Phase 4: 統合テスト

### 4.1. E2Eテストの作成

- [ ] `tests/integration/test_agent_engine_flow.py`作成
- [ ] VoiceStreamingService E2Eテスト
  - [ ] セッション作成→クエリ→イベント受信フロー
  - [ ] Router Agentサブエージェント切り替え
  - [ ] ツール実行確認

### 4.2. 既存テストの更新

- [ ] `tests/integration/test_voice_stream_flow.py`更新
  - [ ] VertexAiSessionServiceモードでのテスト追加
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
  - [ ] VertexAiSessionServiceの説明追加
  - [ ] アーキテクチャ図更新

## Phase 6: PR作成とCI/CD確認

- [ ] コミット
  - [ ] テストコミット
  - [ ] 実装コミット（VoiceStreamingService更新）
  - [ ] 実装コミット（シリアライゼーション更新）
  - [ ] ドキュメント更新コミット
- [ ] PR作成
  - [ ] タイトル: `feat(adk): Agent Engine統合とPhase 2 Router Agent統合`
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

## 実装メモ

### 参照すべきファイル

- `backend/app/services/voice/streaming_service.py` - 現在の実装
- `backend/app/services/adk/agents/router.py` - Phase 2 Router Agent
- `backend/scripts/serialize_agent.py` - シリアライゼーション

### 技術調査リンク

- [Agent Engine概要](https://docs.cloud.google.com/agent-builder/agent-engine/overview?hl=ja)
- [ADKセッション管理](https://docs.cloud.google.com/agent-builder/agent-engine/sessions/manage-sessions-adk?hl=ja)
- [ADKドキュメント](https://github.com/google/adk)

### 既知の課題

1. **run_live()のサポート状況**: VertexAiSessionServiceが`run_live()`をサポートしているかを確認する必要がある
2. **LiveRequestQueueとの互換性**: 音声ストリーミングが正常に動作するかを確認する必要がある
3. **パフォーマンス**: Firestoreと比較してレイテンシを測定する必要がある

## タスク削減のまとめ

**削減されたタスク**:
- ❌ AgentEngineWrapperクラスの実装（不要）
- ❌ agent_engine_client.pyの大幅な更新（最小限の確認のみ）
- ❌ 複雑なセッション管理ロジック（Agent Engineが自動処理）

**残るタスク**:
- ✅ VoiceStreamingServiceの最小限の変更（2箇所のみ）
- ✅ シリアライゼーションスクリプトの最小限の変更
- ✅ テストの更新
