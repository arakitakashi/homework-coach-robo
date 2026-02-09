# Requirements - サブエージェントスキル

## 背景・目的

メインエージェントのコンテキストウィンドウ肥大化を防ぐため、実装完了後の定型的なタスク（ドキュメント更新・品質チェック・PR作成）をサブエージェントに委譲するスキルを作成する。

## 要求事項

### 機能要件

1. `/update-docs` スキル: ドキュメント更新をサブエージェントに委譲
2. `/quality-check` スキル: 品質チェック（mypy/ruff/pytest）をサブエージェントに委譲
3. `/create-pr` スキル拡張: 差分分析からPR body作成までサブエージェントに委譲

### 非機能要件

- メインエージェントのコンテキスト消費を最小化
- 各スキルは Task ツールによるサブエージェント委譲パターンを使用

### 制約条件

- 既存のスキル構造（SKILL.md + skill.json）に準拠
- steering-workflow.md のワークフローと整合

## 対象範囲

### In Scope

- 3つのスキルファイル作成
- steering-workflow.md の更新（サブエージェント委譲の明示）
- CLAUDE.md のスキル一覧更新

### Out of Scope

- 既存スキルの内容変更（tdd, fastapi 等）
- CI/CD ワークフローの変更

## 成功基準

- `/update-docs`, `/quality-check` がスキルとして認識される
- `/create-pr` が差分分析を含む形に拡張される
- steering-workflow.md にサブエージェント委譲の手順が記載される
