# Task List - Fix mypy Test Errors

## Phase 1: 準備
- [x] ブランチ作成
- [x] ステアリングディレクトリ作成

## Phase 2: ファイルごとの修正
- [x] test_manager.py (~69 errors → no-untyped-def + union-attr)
- [x] test_dialogue_schemas.py (~40 errors → no-untyped-def + call-arg)
- [x] test_models.py (~36 errors → no-untyped-def + comparison-overlap + arg-type)
- [x] test_dialogue.py (~21 errors → no-untyped-def)
- [x] test_learning_profile.py (~20 errors → no-untyped-def + arg-type)
- [x] test_converters.py (~14 errors → index + arg-type)
- [x] test_session_store.py (~14 errors → no-untyped-def + union-attr + arg-type)
- [x] test_hint_flow.py (~14 errors → no-untyped-def + union-attr)
- [x] test_dialogue_flow.py (~12 errors → no-untyped-def)
- [x] test_dialogue_llm.py (misc → Generator return type)
- [x] test_dialogue_runner.py (no-untyped-def + no-untyped-call)
- [x] tool tests (calculate, curriculum, emotion_analyzer, hint_manager, image_analyzer, progress_recorder)

## Phase 3: 品質チェック
- [x] mypy → 0 errors (264 → 0)
- [x] ruff → clean
- [x] pytest → 526 passed
