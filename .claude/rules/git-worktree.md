# Git Worktree Rule

**このルールは、git worktreeを使った並列開発における安全性を保証するために強制的に適用されます。**

---

## 背景

このプロジェクトでは **git worktree** を活用した並列開発を行っています。
各worktreeは `.tree/` 配下に配置され、異なるブランチの作業を同時に進めることができます。

```
homework-coach-robo/          # メインworktree（現在のディレクトリ）
└── .tree/
    ├── backend/              # バックエンド作業用worktree
    ├── frontend/             # フロントエンド作業用worktree
    └── ...                   # 必要に応じて追加
```

---

## 絶対遵守事項

### 1. 他のworktreeのファイルに触れない

**自分が作業しているworktree以外のファイルを読み取り・編集・削除してはならない。**

```
# ✅ 正しい: メインworktreeで作業中
/Users/.../homework-coach-robo/frontend/src/...
/Users/.../homework-coach-robo/backend/app/...

# ❌ 禁止: 他のworktreeのファイルに触れる
/Users/.../homework-coach-robo/.tree/backend/...
/Users/.../homework-coach-robo/.tree/frontend/...
```

### 2. worktreeの識別

作業開始時に、自分がどのworktreeで作業しているかを確認する：

```bash
git worktree list
```

**カレントディレクトリがどのworktreeに属するか**を常に意識すること。

### 3. worktree間の依存を避ける

- 他のworktreeの状態に依存する操作を行わない
- 他のworktreeのブランチに対して `git merge` や `git rebase` を行わない（メインworktreeで行う）
- 共有リソース（`.claude/`, `docs/`, `CLAUDE.md`）の編集はメインworktreeで行う

---

## worktreeの作成・削除

### 新規worktree作成

```bash
# .tree/ 配下に作成
git worktree add .tree/<name> <branch>

# 例: featureブランチ用のworktreeを作成
git worktree add .tree/feature-auth feature/auth-implementation
```

### worktree削除

```bash
# worktreeを削除
git worktree remove .tree/<name>

# 不要なworktree情報をクリーンアップ
git worktree prune
```

---

## ファイルパスの注意点

### 相対パスの罠

worktree内で相対パスを使う場合、意図しないworktreeのファイルを参照しないよう注意：

```bash
# ❌ 危険: 相対パスで上位に遡ると別worktreeに到達する可能性
cd .tree/backend && cat ../../frontend/src/...  # メインworktreeのfrontendを参照してしまう

# ✅ 安全: 絶対パスまたはworktreeルートからの相対パスを使用
```

### 共有される `.git` ディレクトリ

すべてのworktreeは同じ `.git` ディレクトリを共有しています。
以下は全worktreeに影響するため、慎重に操作すること：

- `git stash` - 全worktreeで共有される
- `git config` - リポジトリレベルの設定は全worktreeに影響
- `.gitignore` - メインworktreeのものが適用される

---

## Claude Codeへの指示

Claude Code（あなた）は、以下を**必ず**実行すること：

1. **ファイル操作前に、パスが `.tree/` を含んでいないことを確認**
2. **`.tree/` 配下のファイルを Read / Edit / Write / Grep / Glob の対象にしない**
3. **ユーザーが明示的に `.tree/` 内の作業を指示した場合のみ、そのworktree内で作業**
4. **worktree間でファイルをコピー・移動しない**（ユーザーが明示的に指示した場合を除く）

**「ちょっと確認するだけ」でも `.tree/` 配下のファイルにアクセスしてはならない。**
