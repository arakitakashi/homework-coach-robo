# Design - サブエージェントスキル

## アーキテクチャ概要

各スキルは「メインエージェントがスキルを読み込み → Task ツールでサブエージェントを起動 → サブエージェントが作業を完了 → 結果をメインに返却」というパターンで動作する。

```
Main Agent
  ├─ /update-docs → Task(general-purpose) → docs読み込み・更新・コミット
  ├─ /quality-check → Task(Bash) → mypy/ruff/pytest 実行・結果返却
  └─ /create-pr → Task(general-purpose) → git diff分析・PR作成
```

## スキル設計

### 1. /update-docs

- **目的**: CLAUDE.md と docs/implementation-status.md の更新を委譲
- **サブエージェントタイプ**: general-purpose
- **入力**: 作業サマリー（メインエージェントが引数として渡す）
- **出力**: 更新完了報告 + コミットハッシュ
- **コンテキスト削減効果**: ~1000行のドキュメント読み込みをメインから排除

### 2. /quality-check

- **目的**: mypy/ruff/pytest の一括実行と結果構造化
- **サブエージェントタイプ**: Bash
- **入力**: なし（カレントディレクトリのbackendを対象）
- **出力**: 各チェックの PASS/FAIL + エラー詳細
- **コンテキスト削減効果**: エラー出力（数百〜数千行）をメインから排除

### 3. /create-pr 拡張

- **目的**: git diff分析 → PR title/body生成 → gh pr create を一貫して委譲
- **サブエージェントタイプ**: general-purpose
- **入力**: なし（git状態から自動判定）
- **出力**: PR URL
- **コンテキスト削減効果**: git diff/log の出力をメインから排除

## ファイル構成

```
.claude/skills/
├── update-docs/
│   └── SKILL.md
├── quality-check/
│   └── SKILL.md
└── create-pr/
    └── SKILL.md  (既存を拡張)
```

## 代替案と採用理由

| 案 | 説明 | 採用 | 理由 |
|----|------|------|------|
| A: スキル内で直接実行 | スキルがメインエージェントに手順を指示 | ❌ | コンテキスト削減にならない |
| B: Task委譲パターン | スキルがサブエージェント起動を指示 | ✅ | メインのコンテキストを最小化 |
| C: 外部スクリプト | シェルスクリプトで自動化 | ❌ | 柔軟性が低い、LLM判断不要な固定処理のみ |
