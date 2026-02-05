# Task List - LLM統合

## Phase 1: 環境セットアップ

- [x] ブランチ作成 (`feature/llm-integration`)
- [x] ステアリングディレクトリ作成
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成

## Phase 2: GeminiClientのテスト作成（TDD - Red）

- [x] `tests/unit/services/adk/dialogue/test_gemini_client.py` 作成
  - [x] `test_gemini_client_implements_protocol`: プロトコル準拠テスト
  - [x] `test_gemini_client_init_with_api_key`: APIキー初期化テスト
  - [x] `test_gemini_client_init_from_env`: 環境変数からの初期化テスト
  - [x] `test_gemini_client_generate_returns_text`: テキスト生成テスト（モック使用）
  - [x] `test_gemini_client_generate_with_system_instruction`: システム指示付きテスト

## Phase 3: GeminiClientの実装（TDD - Green）

- [x] `backend/app/services/adk/dialogue/gemini_client.py` 作成
  - [x] `GeminiClient` クラス実装
  - [x] `generate()` メソッド実装
  - [x] エラーハンドリング実装
- [x] `backend/app/services/adk/dialogue/__init__.py` エクスポート追加

## Phase 4: APIエンドポイント統合テスト（TDD - Red）

- [x] `tests/integration/api/v1/test_dialogue_llm.py` 作成
  - [x] `test_analyze_with_llm_client`: LLMクライアント使用テスト
  - [x] `test_generate_question_with_llm_client`: 質問生成テスト
  - [x] `test_generate_hint_with_llm_client`: ヒント生成テスト
  - [x] `test_fallback_when_no_api_key`: APIキーなし時のフォールバック

## Phase 5: APIエンドポイント統合実装（TDD - Green）

- [x] `backend/app/api/v1/dialogue.py` 更新
  - [x] `get_llm_client()` 依存性追加
  - [x] `get_dialogue_manager()` 更新
  - [x] 各エンドポイントでLLMクライアント使用
- [x] `backend/app/schemas/dialogue.py` 更新
  - [x] `GenerateHintRequest.is_answer_request` フィールド追加

## Phase 6: リファクタリング（TDD - Refactor）

- [x] コードの整理・改善
- [x] Ruff lint修正

## Phase 7: 品質チェック

- [x] Ruff lint実行 (`uv run ruff check app tests`) - エラーなし
- [x] mypy型チェック (`uv run mypy app/`) - エラーなし
- [x] テスト実行 (`uv run pytest tests/ -v`) - 201件パス
- [x] カバレッジ確認 - 98%（目標80%以上達成）

## Phase 8: コミット・PR

- [ ] 変更をコミット
- [ ] COMPLETED.md 作成
- [ ] PRを作成
