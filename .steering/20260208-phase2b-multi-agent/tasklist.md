# Task List - Phase 2b: マルチエージェント構成

## Phase 1: 環境セットアップ

- [ ] `backend/app/services/adk/agents/` ディレクトリ作成
- [ ] `backend/app/services/adk/agents/prompts/` ディレクトリ作成
- [ ] `tests/unit/services/adk/agents/` ディレクトリ作成

## Phase 2: プロンプト作成

- [ ] Router Agent プロンプト作成（`prompts/router.py`）
- [ ] Math Coach Agent プロンプト作成（`prompts/math_coach.py`）
- [ ] Japanese Coach Agent プロンプト作成（`prompts/japanese_coach.py`）
- [ ] Encouragement Agent プロンプト作成（`prompts/encouragement.py`）
- [ ] Review Agent プロンプト作成（`prompts/review.py`）
- [ ] プロンプト `__init__.py` 作成

## Phase 3: エージェント実装（TDD）

### 3.1 Math Coach Agent (#43)
- [ ] テスト作成: `test_math_coach.py`
- [ ] 実装: `math_coach.py`

### 3.2 Japanese Coach Agent (#44)
- [ ] テスト作成: `test_japanese_coach.py`
- [ ] 実装: `japanese_coach.py`

### 3.3 Encouragement Agent (#45)
- [ ] テスト作成: `test_encouragement.py`
- [ ] 実装: `encouragement.py`

### 3.4 Review Agent (#46)
- [ ] テスト作成: `test_review.py`
- [ ] 実装: `review.py`

### 3.5 Router Agent (#42)
- [ ] テスト作成: `test_router.py`
- [ ] 実装: `router.py`
- [ ] `agents/__init__.py` 作成

## Phase 4: 統合

- [ ] `runner_service.py` の変更（create_router_agent を使用）
- [ ] `runner_service.py` のテスト更新
- [ ] 既存エンドポイントとの後方互換性テスト

## Phase 5: 品質チェック

- [ ] `uv run ruff check .` パス
- [ ] `uv run mypy .` パス
- [ ] `uv run pytest tests/ -v` 全テストパス
- [ ] カバレッジ 80% 以上確認
- [ ] セルフコードレビュー
