# Task List - Phase 3: Agent Engine デプロイ (#53)

## Phase 1: 環境セットアップ

- [x] `google-cloud-aiplatform[agent_engines]` を pyproject.toml に追加
- [x] 新規ディレクトリ・ファイル構成の確認

## Phase 2: セッションファクトリ（TDD）

- [x] テスト作成: `test_session_factory.py`
- [x] 実装: `session_factory.py`（環境変数ベースで Firestore / VertexAi 切り替え）
- [x] ruff/mypy チェック通過

## Phase 3: Agent Engine クライアント（TDD）

- [x] テスト作成: `test_agent_engine_client.py`
- [x] 実装: `agent_engine_client.py`（remote_app ラッパー）
- [x] ruff/mypy チェック通過

## Phase 4: テキスト対話エンドポイントの切り替え

- [x] テスト更新: `test_dialogue_runner.py`（Agent Engine 対応）
- [x] 実装: `dialogue_runner.py` を Agent Engine 経由に切り替え（フォールバック付き）
- [x] ruff/mypy チェック通過

## Phase 5: デプロイスクリプト

- [x] `scripts/deploy_agent_engine.py` 作成（Router Agent デプロイ）
- [x] `scripts/test_agent_engine.py` 作成（デプロイ後テスト）

## Phase 6: 品質チェック

- [x] 全テスト通過: `uv run pytest tests/ -v` → 548 passed
- [x] Lint通過: `uv run ruff check .` → All checks passed
- [x] 型チェック通過: `uv run mypy .` → 0 errors, 119 files
- [x] カバレッジ80%以上確認 → 90%
- [x] ドキュメント更新（CLAUDE.md, docs/implementation-status.md, docs/agent-architecture.md）
