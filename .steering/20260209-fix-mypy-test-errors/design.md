# Design - Fix mypy Test Errors

## アプローチ

テストファイルのみの修正。Write ツールでファイル全体を書き換え。

## エラー種別と対応方針

| エラー | 対応 |
|--------|------|
| `no-untyped-def` (215) | `-> None` 追加 |
| `index` (13) | `assert result is not None` |
| `arg-type` (11) | 型修正 / type: ignore |
| `call-arg` (7) | `# type: ignore[call-arg]` |
| `attr-defined` (6) | `# type: ignore[attr-defined]` |
| `union-attr` (4) | assert ガード |
| `operator` (3) | 型ナロイング |
| `comparison-overlap` (3) | `.value` 比較 |
