# Task List - Vertex AI 統一

## Phase 1: 環境セットアップ

- [x] ブランチ作成 (`refactor/unify-vertex-ai`)
- [x] ステアリングディレクトリ作成
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成

## Phase 2: GeminiClientのテスト更新（TDD - Red）

- [x] `test_gemini_client.py` 更新
  - [x] `test_init_with_project`: プロジェクトID指定テスト
  - [x] `test_init_from_env_project`: 環境変数からのプロジェクト取得テスト
  - [x] `test_init_without_project_raises_error`: プロジェクト未設定エラーテスト
  - [x] `test_init_with_location`: リージョン指定テスト
  - [x] API Key 関連テストの削除

## Phase 3: GeminiClientの実装更新（TDD - Green）

- [x] `gemini_client.py` 更新
  - [x] コンストラクタを Vertex AI モードに変更
  - [x] `project` / `location` パラメータ追加
  - [x] API Key 関連コードの削除
  - [x] エラーメッセージの更新

## Phase 4: APIエンドポイント更新

- [x] `dialogue.py` 更新
  - [x] `get_llm_client()` を Vertex AI モードに変更
  - [x] 環境変数チェックの更新

## Phase 5: 統合テスト更新

- [x] `test_dialogue_llm.py` 確認
  - [x] モックが引き続き動作することを確認

## Phase 6: 品質チェック

- [x] Ruff lint実行 (`uv run ruff check app tests`) - エラーなし
- [x] mypy型チェック (`uv run mypy app/`) - エラーなし
- [x] テスト実行 (`uv run pytest tests/ -v`) - 202件パス
- [x] カバレッジ確認 - 98%

## Phase 7: ドキュメント更新

- [x] CLAUDE.md 更新（セットアップ手順）

## Phase 8: コミット・PR

- [x] 変更をコミット
- [x] COMPLETED.md 作成
- [ ] PRを作成
