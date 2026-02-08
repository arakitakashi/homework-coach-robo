# Task List - Phase 2c: RAG Search Tool 統合

## Phase 1: 環境セットアップ

- [ ] pyproject.toml に `google-cloud-aiplatform` を追加
- [ ] 依存パッケージのインストール確認（`uv sync`）
- [ ] Vertex AI RAG API の認証確認（ローカル: ADC）

## Phase 2: テスト実装（TDD）

- [ ] `test_search_memory.py` の作成
  - [ ] RAG検索の基本動作テスト
  - [ ] user_id フィルタリングのテスト
  - [ ] top_k パラメータのテスト
  - [ ] エラーハンドリングのテスト（Corpus not found, timeout）
  - [ ] フォールバック動作のテスト
- [ ] モックの作成（Vertex AI RAG API）

## Phase 3: 実装

- [ ] `backend/app/services/adk/tools/search_memory.py` の実装
  - [ ] `_search_rag()` 内部関数の実装（Vertex AI RAG統合）
  - [ ] `search_memory_with_context()` 関数の実装
  - [ ] エラーハンドリング（RagSearchError, フォールバック）
  - [ ] `search_memory_tool = FunctionTool(...)` の定義
- [ ] `backend/app/services/adk/tools/__init__.py` にエクスポート追加
- [ ] 型定義の追加（必要に応じて）

## Phase 4: エージェント統合

- [ ] Review Agent に `search_memory_tool` を追加
  - [ ] `backend/app/services/adk/agents/review.py` の `tools` リストに追加
  - [ ] プロンプトに「記憶検索ツールの使い方」を追加

## Phase 5: 品質チェック

- [ ] コードレビュー（セルフレビュー）
- [ ] セキュリティレビュー（データプライバシー、API認証）
- [ ] テストカバレッジ確認（80%以上）
  - [ ] `uv run pytest tests/unit/services/adk/tools/test_search_memory.py --cov=app/services/adk/tools/search_memory --cov-report=term-missing`
- [ ] リンター実行
  - [ ] `uv run ruff check app/services/adk/tools/search_memory.py`
- [ ] 型チェック実行
  - [ ] `uv run mypy app/services/adk/tools/search_memory.py`

## Phase 6: ドキュメント更新

- [ ] `docs/agent-architecture.md` の Phase 2c セクション更新（実装済みステータス）
- [ ] `docs/implementation-status.md` に Phase 2c-1 完了を追記
- [ ] `.steering/20260208-phase2c-rag-search-tool/COMPLETED.md` の作成

## 備考

### Phase 2c-2 以降（本タスク外）

Phase 2c-2（RAG Corpus 作成）以降は別のタスクとして実施:
- Vertex AI Console で Corpus を手動作成
- Firestore memories のインポートスクリプト作成
- FirestoreMemoryService の移行
