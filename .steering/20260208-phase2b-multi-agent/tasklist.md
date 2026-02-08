# Task List - Phase 2b: マルチエージェント構成

## Phase 1: 環境セットアップ

- [x] `backend/app/services/adk/agents/` ディレクトリ作成
- [x] `backend/app/services/adk/agents/prompts/` ディレクトリ作成
- [x] `tests/unit/services/adk/agents/` ディレクトリ作成

## Phase 2: プロンプト作成

- [x] Router Agent プロンプト作成（`prompts/router.py`）
- [x] Math Coach Agent プロンプト作成（`prompts/math_coach.py`）
- [x] Japanese Coach Agent プロンプト作成（`prompts/japanese_coach.py`）
- [x] Encouragement Agent プロンプト作成（`prompts/encouragement.py`）
- [x] Review Agent プロンプト作成（`prompts/review.py`）
- [x] プロンプト `__init__.py` 作成

## Phase 3: エージェント実装（TDD）

### 3.1 Math Coach Agent (#43)
- [x] テスト作成: `test_math_coach.py`
- [x] 実装: `math_coach.py`

### 3.2 Japanese Coach Agent (#44)
- [x] テスト作成: `test_japanese_coach.py`
- [x] 実装: `japanese_coach.py`

### 3.3 Encouragement Agent (#45)
- [x] テスト作成: `test_encouragement.py`
- [x] 実装: `encouragement.py`

### 3.4 Review Agent (#46)
- [x] テスト作成: `test_review.py`
- [x] 実装: `review.py`

### 3.5 Router Agent (#42)
- [x] テスト作成: `test_router.py`
- [x] 実装: `router.py`
- [x] `agents/__init__.py` 作成

## Phase 4: 統合

- [x] `runner_service.py` の変更（create_router_agent を使用）
- [x] `runner_service.py` のテスト更新
- [x] 既存エンドポイントとの後方互換性テスト

## Phase 5: 品質チェック

- [x] `uv run ruff check .` パス
- [x] `uv run mypy .` パス（新規ファイルのみ、既存エラーは対象外）
- [x] `uv run pytest tests/ -v` 全テストパス（494 passed）
- [x] カバレッジ 80% 以上確認（90%）
- [x] セルフコードレビュー
