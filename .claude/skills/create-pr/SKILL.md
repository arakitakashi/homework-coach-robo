---
name: create-pr
description: Creates GitHub pull requests by delegating diff analysis and PR body generation to a sub-agent. Use when creating PRs, submitting changes for review, or when the user says /pr or asks to create a pull request.
allowed-tools: Task, Bash(git:*), Bash(gh:*)
---

# Create Pull Request

GitHub PR を作成します。差分分析と PR body 生成をサブエージェントに委譲し、メインエージェントのコンテキスト消費を最小化します。

## PR Title Format

```
<type>(<scope>): <summary>
```

### Types

| Type       | Description                    |
|------------|--------------------------------|
| `feat`     | 新機能                          |
| `fix`      | バグ修正                        |
| `perf`     | パフォーマンス改善                |
| `test`     | テスト追加/修正                  |
| `docs`     | ドキュメントのみ                  |
| `refactor` | リファクタリング                  |
| `build`    | ビルドシステム/依存関係            |
| `ci`       | CI設定                          |
| `chore`    | メンテナンス                     |

### Summary Rules

- 命令形で記述: "Add" not "Added"
- 英語の場合、最初の文字を大文字
- 末尾にピリオドを付けない
- 70文字以内

## Instructions

### Step 1: プッシュ確認

リモートにプッシュされていなければプッシュする:
```bash
git push -u origin HEAD
```

### Step 2: サブエージェントで差分分析 + PR作成

Task ツールで `general-purpose` サブエージェントを起動し、以下のプロンプトを使用してください。

```
GitHub PRを作成してください。

## 手順

### 1. 現在の状態を確認
以下のコマンドを実行:
- `git status`（未コミットの変更がないか確認）
- `git log origin/main..HEAD --oneline`（コミット一覧）
- `git diff origin/main...HEAD --stat`（変更ファイル一覧）

### 2. 変更内容を分析
コミットログと変更ファイルから:
- PRのtype（feat/fix/docs/refactor/test/chore等）を判定
- 変更の要約を作成（1〜3文）
- テストプランを箇条書きで作成

### 3. PRを作成
gh CLIで作成:

gh pr create --title "<type>: <Summary>" --body "## Summary
<変更内容の箇条書き>

## Test plan
<テストプランの箇条書き>

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

PRのURLを返してください。
```

### Step 3: 結果確認

サブエージェントが返すPR URLを確認し、ユーザーに伝えてください。

## Notes

- `git diff` や `git log` の出力（数百〜数千行になりうる）がメインエージェントのコンテキストに載ることを避けられます
- サブエージェントが `gh pr create` を実行するため、`dangerouslyDisableSandbox: true` が必要になる場合があります
