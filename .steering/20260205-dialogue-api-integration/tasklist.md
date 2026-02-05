# Task List - 対話API統合

## Phase 1: 環境セットアップ

- [x] 設計ドキュメントの確認
- [x] テストディレクトリの確認

## Phase 2: スキーマ定義（TDD）

### 2.1 リクエスト/レスポンススキーマ

- [x] テスト作成: `test_dialogue_runner_schemas.py`
  - [x] RunDialogueRequestのバリデーション
  - [x] TextEventの生成
  - [x] ErrorEventの生成
  - [x] DoneEventの生成
- [x] 実装: `schemas/dialogue_runner.py`
  - [x] RunDialogueRequest
  - [x] TextEvent, ErrorEvent, DoneEvent

## Phase 3: エンドポイント実装（TDD）

### 3.1 依存性注入

- [x] テスト作成: 依存性注入テスト
  - [x] get_session_service()
  - [x] get_memory_service()
  - [x] get_agent_runner_service()
- [x] 実装: 依存性注入関数

### 3.2 SSEジェネレータ

- [x] テスト作成: `test_dialogue_runner.py::test_event_generator_*`
  - [x] テキストイベントの生成
  - [x] 完了イベントの生成（doneイベント）
  - [x] エラーイベントの生成
- [x] 実装: `event_generator()`関数

### 3.3 ストリーミングエンドポイント

- [x] テスト作成: `test_run_dialogue_*`
  - [x] 正常系：ストリーミングレスポンス
  - [x] バリデーションエラー時の422（空メッセージ）
  - [x] バリデーションエラー時の422（必須フィールド欠落）
- [x] 実装: `run_dialogue()`エンドポイント

## Phase 4: ルーター統合

- [x] router.pyに新ルーターを追加
- [x] 統合テスト

## Phase 5: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [x] テストカバレッジ確認（96%）
- [x] リンター・型チェック実行
  - [x] `uv run ruff check app/api/v1/dialogue_runner.py app/schemas/dialogue_runner.py`
  - [x] `uv run mypy app/api/v1/dialogue_runner.py app/schemas/dialogue_runner.py`

## Phase 6: ドキュメント更新

- [x] COMPLETED.md の作成
- [x] CLAUDE.md の更新

---

## 進捗メモ

### 実装方針

1. **TDD厳守**: テストを先に書く ✅
2. **モック活用**: AgentRunnerServiceはモック ✅
3. **SSEフォーマット**: 標準のSSE形式を使用 ✅

### 完了した内容

- スキーマ: 10テスト（全パス）
- エンドポイント: 8テスト（全パス）
- 合計: 309テスト（全体）

### 修正ポイント

- `patch()` から `app.dependency_overrides` への変更
  - FastAPIの依存性注入は `patch()` では完全にモックできない
  - `dependency_overrides` を使用することで、ネストした依存関係も含めて正しくモック可能
