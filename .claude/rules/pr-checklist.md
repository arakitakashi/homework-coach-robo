# PR Checklist Rule

**このルールは、Pull Request作成前に実行すべきローカルチェックを定義します。**

---

## 背景

CIで初めてエラーが発覚すると、以下の無駄が発生します：

1. 修正コードの作成
2. コミット・プッシュ
3. CI再実行の待機（数分）
4. 結果確認

**ローカルで同じチェックを実行すれば、即座にフィードバックを得られます。**

---

## PR作成前チェックリスト

### Backend（Python / FastAPI）

```bash
cd backend

# 1. Lint（Ruff）
uv run ruff check app tests

# 2. 型チェック（mypy）
uv run mypy .

# 3. テスト（pytest）
uv run pytest tests/ -v

# 4. カバレッジ確認（80%以上）
uv run pytest tests/ --cov=app --cov-report=term-missing
```

### Frontend（TypeScript / Next.js）

```bash
cd frontend

# 1. Lint（Biome）
bun lint

# 2. 型チェック（TypeScript）
bun typecheck

# 3. テスト（Vitest）
bun test

# 4. ビルド確認
bun build
```

---

## チェックリスト確認

PR作成前に以下のすべてが完了していることを確認：

### Backend

- [ ] `uv run ruff check app tests` → エラーなし
- [ ] `uv run mypy .` → エラーなし（`app/` + `tests/` 両方）
- [ ] `uv run pytest tests/` → 全テスト通過
- [ ] カバレッジ80%以上

### Frontend

- [ ] `bun lint` → エラーなし
- [ ] `bun typecheck` → エラーなし
- [ ] `bun test` → 全テスト通過
- [ ] `bun build` → ビルド成功

### ドキュメント

- [ ] `CLAUDE.md` の Development Context が最新か（新機能・アーキテクチャ変更時）
- [ ] `docs/implementation-status.md` の完了済み機能一覧に今回の作業が記載されているか
- [ ] `docs/implementation-status.md` のステアリングディレクトリ一覧が最新か
- [ ] その他、変更内容に関連する `docs/` 配下のドキュメントが最新か

---

## よくあるCI失敗パターンと対策

### 1. mypy型エラー

**症状**: `union-attr`、`arg-type`エラー

**原因**: `Optional`型（`T | None`）に対するNoneチェック漏れ

**対策**:
```python
# ❌ エラー
context = store.get_session(session_id)
return context.problem  # contextがNoneの可能性

# ✅ 修正（ユーザー入力由来）
if context is None:
    raise HTTPException(status_code=404, ...)
return context.problem

# ✅ 修正（内部ロジックで保証）
assert context is not None
return context.problem
```

### 2. Ruff未使用インポート

**症状**: `F401 imported but unused`

**原因**: auto-formatで削除されたインポートを再追加し忘れ

**対策**: `auto-format-hooks.md`ルールに従う

### 3. Ruff未使用引数

**症状**: `ARG002 Unused method argument`

**原因**: 将来使用予定の引数を定義

**対策**:
```python
def func(
    used_arg: str,
    future_arg: int,  # noqa: ARG002 - 将来のフェーズで使用予定
) -> str:
    return used_arg
```

---

## 一括チェックスクリプト

以下のコマンドで全チェックを一括実行できます：

### Backend

```bash
cd backend && \
uv run ruff check app tests && \
uv run mypy . && \
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd frontend && \
bun lint && \
bun typecheck && \
bun test && \
bun build
```

---

## Claude Codeへの指示

Claude Code（あなた）は、PR作成前に以下を**必ず**実行すること：

1. **該当するチェックリストをすべて実行**
2. **エラーがあれば修正してから再実行**
3. **全チェックがパスしてからPRを作成**

**「CIで確認すればいい」というアプローチは避けること。**
**ローカルで確認できるものはローカルで確認する。**
