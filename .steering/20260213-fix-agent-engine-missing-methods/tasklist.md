# Task List - AgentEngine ラッパーメソッド追加

## Phase 1: 実装

- [x] `HomeworkCoachAgent` に `create_session()` メソッドを追加
- [x] `HomeworkCoachAgent` に `stream_query()` メソッドを追加
- [x] 既存コードに型注釈を追加（`__init__`, `_get_runner`, `query` 内部関数）

## Phase 2: 品質チェック

- [x] `uv run ruff check backend/scripts/serialize_agent.py` → PASS
- [x] `uv run mypy backend/scripts/serialize_agent.py` → PASS
- [x] バックエンド全体品質チェック → ruff PASS, pytest PASS (590), mypy pre-existing error only

## Phase 3: ドキュメント・PR

- [ ] ドキュメント更新
- [ ] コミット・プッシュ・PR作成
