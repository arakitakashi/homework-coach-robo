# Task List - Phase 2c+3 統合: Vertex AI Memory Bank

## Phase 1: 環境セットアップ

- [x] `VertexAiMemoryBankService` API の動作確認
- [x] 既存テストが通ることの確認

## Phase 2: メモリサービスファクトリ（#47, #48）

### 2.1 memory_factory テスト・実装（TDD）
- [x] テスト作成: `test_memory_factory.py`
  - AGENT_ENGINE_ID 設定時 → VertexAiMemoryBankService を返す
  - AGENT_ENGINE_ID 未設定時 → FirestoreMemoryService を返す
  - GCP_PROJECT_ID, GCP_LOCATION パラメータの受け渡し
- [x] 実装: `memory_factory.py`
  - `create_memory_service()` ファクトリ関数

### 2.2 Review Agent に load_memory ツール追加（TDD）
- [x] テスト更新: `test_review.py` に `load_memory` ツール検証追加
- [x] 実装更新: `review.py` に `load_memory` ツール追加

### 2.3 DI 更新・エクスポート
- [x] `dialogue_runner.py` の `get_memory_service()` をファクトリベースに変更
- [x] `voice_stream.py` の `get_memory_service()` をファクトリベースに変更
- [x] `memory/__init__.py` のエクスポート更新

## Phase 3: Agent Engine 作成スクリプト（#47）

- [x] スクリプト作成: `scripts/create_agent_engine.py`
  - Agent Engine の作成
  - ID の出力（環境変数設定用）

## Phase 4: 品質チェック

- [x] `uv run ruff check .` パス
- [x] `uv run mypy .` パス（新規ファイルのみ — 既存エラーは対象外）
- [x] `uv run pytest tests/ -v` 全テストパス（504 passed）
- [x] カバレッジ 80% 以上確認（90%）
- [x] セルフコードレビュー
