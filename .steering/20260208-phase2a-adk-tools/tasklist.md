# Task List - Phase 2a: ADK Function Tools

## Phase 1: 環境セットアップ

- [ ] `backend/app/services/adk/tools/` ディレクトリ作成
- [ ] `backend/tests/unit/services/adk/tools/` ディレクトリ作成
- [ ] ADK FunctionTool importの確認

## Phase 2: calculate_tool (#37)

- [ ] テスト作成: `test_calculate.py`
- [ ] 実装: `calculate.py`
- [ ] ruff/mypy チェック通過

## Phase 3: manage_hint_tool (#38)

- [ ] テスト作成: `test_hint_manager.py`
- [ ] 実装: `hint_manager.py`
- [ ] ruff/mypy チェック通過

## Phase 4: record_progress_tool (#39)

- [ ] テスト作成: `test_progress_recorder.py`
- [ ] 実装: `progress_recorder.py`
- [ ] ruff/mypy チェック通過

## Phase 5: check_curriculum_tool (#40)

- [ ] テスト作成: `test_curriculum.py`
- [ ] 実装: `curriculum.py`
- [ ] ruff/mypy チェック通過

## Phase 6: analyze_image_tool (#41)

- [ ] テスト作成: `test_image_analyzer.py`
- [ ] 実装: `image_analyzer.py`
- [ ] ruff/mypy チェック通過

## Phase 7: エージェント統合

- [ ] テスト更新: `test_agent.py`にツール統合テスト追加
- [ ] `agent.py`更新: ツールリスト追加
- [ ] `tools/__init__.py`でエクスポート

## Phase 8: 品質チェック

- [ ] 全テスト通過: `uv run pytest tests/ -v`
- [ ] Lint通過: `uv run ruff check .`
- [ ] 型チェック通過: `uv run mypy .`
- [ ] カバレッジ80%以上確認
