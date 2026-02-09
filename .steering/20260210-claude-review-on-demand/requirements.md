# Requirements - Claude Code Review オンデマンド化

## 背景・目的

GitHub Actions での Claude 使用量が多い。原因は `claude-code-review.yml` が全PRで自動実行されていること。レビューは明示的に求められた時のみ実行するように変更する。

## 要求事項

### 機能要件

- Claude Code Review は PR にラベル `claude-review` が付与された時のみ実行される
- `claude.yml`（@claude メンション対応）は現状維持

### 非機能要件

- 既存の CI ワークフロー（ci-backend, ci-frontend, ci-e2e, cd, deploy）に影響を与えない

## 成功基準

- PR 作成時に自動で Claude Code Review が実行されない
- `claude-review` ラベル付与時のみ実行される
