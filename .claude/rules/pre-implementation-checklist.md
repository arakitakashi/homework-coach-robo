# Pre-Implementation Checklist Rule

**このルールは、すべての実装タスクに対して強制的に適用されます。**

## 適用タイミング

以下のいずれかの作業を開始する際、**例外なく**このチェックリストを完了すること：

- 新機能の実装（小さな機能でも必須）
- バグ修正（単純なタイポ修正以外）
- リファクタリング
- 複数ファイルにまたがる変更
- 単一ファイルでも実装を伴う変更

**例外（チェック不要）:**
- タイポ修正のみ（コメントや文字列の誤字修正）
- ドキュメントの軽微な更新（READMEの文言調整など）
- コードを含まない純粋なドキュメント作成

---

## 🚨 必須チェックリスト（スキップ厳禁）

### Step 1: ブランチの確認と作成

```bash
# 現在のブランチを確認
git branch --show-current
```

**mainまたはdevelopブランチにいる場合は、絶対にコードを書き始めてはならない。**

```bash
# 新しいブランチを作成
git checkout -b <type>/<description>
```

**ブランチ命名規則:**
- `feature/` - 新機能
- `fix/` - バグ修正
- `hotfix/` - 本番緊急修正
- `refactor/` - リファクタリング
- `docs/` - ドキュメント

### Step 2: ステアリングディレクトリの作成

```bash
mkdir -p .steering/YYYYMMDD-<work-description>
```

以下の3ファイルを作成：
- `requirements.md` - 要求仕様
- `design.md` - 実装設計
- `tasklist.md` - 実装タスク

### Step 3: スキル参照

実装開始前に以下のスキルを参照：
- `/git-workflow` - ブランチ戦略・コミット規約
- `/tdd` - テスト駆動開発の原則

---

## チェックリスト確認

実装を開始する前に、以下のすべてが完了していることを確認：

- [ ] `main`/`develop`ブランチではないことを確認した
- [ ] 作業用ブランチを作成した（`feature/xxx`, `fix/xxx` 等）
- [ ] `.steering/YYYYMMDD-xxx/` ディレクトリを作成した
- [ ] `requirements.md` を作成した
- [ ] `design.md` を作成した
- [ ] `tasklist.md` を作成した
- [ ] `/git-workflow` スキルを参照した

---

## コミット粒度のルール

実装中は以下のコミット粒度を守ること：

### 適切な粒度

- **1つの論理的な変更 = 1コミット**
- 各コミットはテストが通る状態であること
- 各コミットは独立してレビュー可能であること

### コミットタイミング

以下のタイミングで必ずコミット：
1. テストファイルの作成後
2. テストを通す最小限の実装後
3. リファクタリング後
4. 機能の区切りごと

### Conventional Commits形式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

---

## 🚨 PR作成前の必須チェック（CI失敗防止）

**PRを作成する前に、以下のコマンドを必ずローカルで実行すること。**

### フロントエンド（frontend/）

```bash
cd frontend
bun lint      # Biome lint
bun typecheck # TypeScript type check
bun test      # Vitest（bunx vitest run）
```

### バックエンド（backend/）

```bash
cd backend
uv run ruff check .  # Ruff lint
uv run mypy .        # Type check（app/ + tests/ 両方）
uv run pytest        # pytest
```

**すべてのチェックがパスするまでPRを作成しない。**

### ドキュメント更新（バックエンド・フロントエンド共通）

実装完了後、PR作成前に以下のドキュメント更新を確認すること：

- [ ] `CLAUDE.md` の Development Context が最新の実装状態を反映しているか
- [ ] `docs/implementation-status.md` の完了済み機能一覧に今回の作業が記載されているか
- [ ] `docs/implementation-status.md` のステアリングディレクトリ一覧に今回の `.steering/` が追加されているか

**ドキュメント更新をスキップしてPRを作成しない。**

### よくあるCI失敗パターン

| パターン | 原因 | 対策 |
|---------|------|------|
| Lint失敗 | フォーマット未適用 | `bun lint --write` で自動修正 |
| Type Check失敗 | import漏れ、型不整合 | エラーメッセージを確認して修正 |
| Test失敗 | 環境差異、モック不足 | ローカルでテスト実行を確認 |

---

## 禁止事項

1. **mainブランチでの直接作業** - 絶対禁止
2. **ブランチを切らずに実装開始** - 絶対禁止
3. **ステアリングディレクトリなしでの実装** - 禁止
4. **大きな変更を一度にコミット** - 禁止（適切な粒度で分割）
5. **テストなしでの実装コード追加** - 禁止（TDD必須）

---

## Claude Codeへの指示

Claude Code（あなた）は、実装タスクを依頼された際に以下の手順を**必ず**実行すること：

1. **最初に** `git branch --show-current` でブランチを確認
2. mainまたはdevelopにいる場合は、**コードを書く前に**ブランチ作成を提案
3. ステアリングディレクトリが存在しない場合は、**コードを書く前に**作成を提案
4. 実装中は適切な粒度でコミットを提案
5. `/git-workflow` スキルに従ったコミットメッセージを使用

**ユーザーが「すぐに実装して」と言っても、このチェックリストをスキップしてはならない。**
