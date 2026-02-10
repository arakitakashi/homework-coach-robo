# Task List - Phase 2 WebSocket Events Implementation

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリ作成
- [x] requirements.md作成
- [x] design.md作成
- [x] tasklist.md作成
- [ ] mainブランチの最新を確認
- [ ] 既存コードの理解（voice_stream.py, streaming_service.py）

## Phase 2: テスト実装（TDD）

### 2.1. voice_stream.pyスキーマのテスト

- [ ] `tests/unit/schemas/test_voice_stream.py`作成
- [ ] ToolExecutionEventのバリデーションテスト
  - [ ] 正常系（started/completed/failed）
  - [ ] 異常系（不正なstatus値）
- [ ] AgentTransitionEventのバリデーションテスト
  - [ ] 正常系（from_agent, to_agent）
  - [ ] 異常系（必須フィールド欠損）
- [ ] EmotionUpdateEventのバリデーションテスト
  - [ ] 正常系（level 1-5範囲）
  - [ ] 異常系（level範囲外）
- [ ] Phase2Event Union型のテスト

### 2.2. streaming_service.pyロジックのテスト

- [ ] `tests/unit/services/test_streaming_service_phase2.py`作成
- [ ] `_send_phase2_event()`のテスト
  - [ ] WebSocket送信成功
  - [ ] WebSocket送信失敗時のエラーハンドリング
- [ ] `_handle_tool_execution()`のテスト
  - [ ] ツール実行開始イベント送信
  - [ ] ツール実行完了イベント送信
  - [ ] ツール実行失敗イベント送信
- [ ] `_handle_agent_transition()`のテスト
  - [ ] エージェント遷移イベント送信
- [ ] `_handle_emotion_update()`のテスト
  - [ ] 感情更新イベント送信

## Phase 3: 実装

### 3.1. voice_stream.pyスキーマ追加

- [ ] ToolExecutionData定義
- [ ] ToolExecutionEvent定義
- [ ] AgentTransitionData定義
- [ ] AgentTransitionEvent定義
- [ ] EmotionUpdateData定義
- [ ] EmotionUpdateEvent定義
- [ ] Phase2Event Union型定義
- [ ] __all__にエクスポート追加

### 3.2. streaming_service.py実装

- [ ] `_send_phase2_event()`ヘルパーメソッド実装
- [ ] `_sanitize_tool_data()`機密情報フィルタ実装
- [ ] `_handle_tool_execution()`実装
  - [ ] 開始イベント送信
  - [ ] ツール実行
  - [ ] 完了/失敗イベント送信
- [ ] `_handle_agent_transition()`実装
  - [ ] Router Agent→サブエージェント遷移検知
  - [ ] 遷移イベント送信
- [ ] `_handle_emotion_update()`実装
  - [ ] update_emotion_tool実行検知
  - [ ] 感情更新イベント送信

### 3.3. AgentRunnerServiceとの統合

- [ ] ツール実行フックの追加
- [ ] エージェント遷移フックの追加

## Phase 4: 統合テスト

- [ ] `tests/integration/test_phase2_websocket_flow.py`作成
- [ ] WebSocket接続→ツール実行→イベント受信フロー
- [ ] WebSocket接続→エージェント遷移→イベント受信フロー
- [ ] WebSocket接続→感情更新→イベント受信フロー
- [ ] 既存イベント（dialogue, progressUpdate）との共存確認

## Phase 5: 品質チェック

- [ ] ローカルでのテスト実行
  - [ ] `cd backend && uv run pytest tests/ -v`
  - [ ] 全テスト通過確認
- [ ] 型チェック
  - [ ] `cd backend && uv run mypy .`
  - [ ] エラーゼロ確認
- [ ] Lint
  - [ ] `cd backend && uv run ruff check app tests`
  - [ ] エラーゼロ確認
- [ ] カバレッジ確認
  - [ ] `cd backend && uv run pytest tests/ --cov=app --cov-report=term-missing`
  - [ ] 80%以上確認
- [ ] セキュリティレビュー
  - [ ] `/security-review`スキル使用
  - [ ] 機密情報フィルタリング確認
- [ ] ドキュメント更新
  - [ ] `CLAUDE.md`のDevelopment Context更新
  - [ ] `docs/implementation-status.md`更新
  - [ ] ステアリングディレクトリ一覧追加

## Phase 6: デプロイ準備

- [ ] コミット
  - [ ] テストコミット
  - [ ] 実装コミット
  - [ ] ドキュメント更新コミット
- [ ] PR作成
  - [ ] タイトル: `feat(backend): Phase 2 WebSocket events (toolExecution, agentTransition, emotionUpdate)`
  - [ ] 説明: requirements.mdの内容を要約
  - [ ] Closes #94
- [ ] CI/CDパイプライン確認
  - [ ] Backend CIパス
  - [ ] E2E CIパス（フロントエンドとの統合）

## 実装メモ

### 参照すべきファイル

- `backend/app/schemas/voice_stream.py` - 既存のWebSocketイベントスキーマ
- `backend/app/services/streaming_service.py` - 既存のWebSocket送信ロジック
- `backend/app/services/adk/runner/runner_service.py` - ADK Runner実装
- `backend/app/services/adk/agents/router.py` - Router Agent実装
- `backend/app/services/adk/tools/emotion_analyzer.py` - 感情分析ツール
- `frontend/types/phase2.ts` - フロントエンド側の型定義（参考）

### 既知の課題

1. **Agent Engine経由のイベント取得**: 現状はローカルRunnerのみ対応。Agent Engine経由の場合は別途対応が必要（将来）
2. **Memory Bank統合**: 現状はメモリイベントは送信しない（別issue）
3. **パフォーマンス測定**: 本番環境でのイベント送信オーバーヘッド測定は別途実施
