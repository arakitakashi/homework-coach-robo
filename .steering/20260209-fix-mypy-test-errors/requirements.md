# Requirements - Fix mypy Test Errors

## 背景・目的

Phase 2a〜2d の実装完了後、`uv run mypy .` が264エラーを報告。全てテストファイル内。CI安定化のために全エラーを解消する。

## 要求事項

### 機能要件
- テストファイルの mypy エラーを0にする
- 既存テスト526件が全パスを維持する

### 非機能要件
- ruff チェックもクリーンを維持
- テストカバレッジを低下させない

### 制約条件
- `app/` のコードは変更しない（既にクリーン）
- テストの振る舞いは変えない（型アノテーション追加のみ）

## 成功基準
- `uv run mypy .` → 0 errors
- `uv run ruff check .` → エラーなし
- `uv run pytest tests/ -v` → 全テスト通過
