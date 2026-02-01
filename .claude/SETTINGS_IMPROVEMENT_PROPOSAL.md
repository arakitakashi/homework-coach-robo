# Claude Code Settings Improvement Proposal

**Date**: 2026-02-02
**Author**: Claude Opus 4.5 + User

---

## 現状の設定スキーマ

現在の `.claude/settings.json` は以下の構造をサポート:

```json
{
  "commandPermissions": {
    "blocked": ["..."],        // 実行禁止コマンド
    "requireApproval": ["..."], // 承認必須コマンド
    "autoApprove": ["..."]      // 自動承認コマンド（Bashのみ）
  }
}
```

**制限**: `autoApprove` は **Bash コマンドのみ** に適用され、他のツール（Write, Read, Glob, Grep）には適用されない。

---

## 今回の改善（実施済み）

### commandPermissions.autoApprove に追加

```json
"uv run pytest*",
"uv run ruff*",
"uv run mypy*",
"uv sync*",
"pwd"
```

**効果**: バックエンド開発でのTDDサイクルが高速化

---

## 将来の改善提案

### 1. Write ツールの条件付き自動承認

**ユースケース**:
- テストファイル（`tests/**/*.py`）の作成・編集
- `__init__.py` の作成
- ステアリングドキュメント（`.steering/**/*.md`）の作成・編集

**提案スキーマ**:
```json
{
  "toolPermissions": {
    "Write": {
      "autoApprove": [
        "tests/**/*.py",
        "**/__init__.py",
        ".steering/**/*.md"
      ],
      "requireApproval": [
        "**/*.py",
        "**/*.ts",
        "**/*.tsx"
      ]
    }
  }
}
```

**期待効果**:
- TDD での Red-Green-Refactor サイクル高速化
- 定型ファイルの作成がスムーズに

### 2. Read/Glob/Grep ツールの自動承認

**現状**: これらのツールは読み取り専用で副作用がないが、都度承認が必要な場合がある。

**提案**:
```json
{
  "toolPermissions": {
    "Read": {
      "autoApprove": ["**/*"]
    },
    "Glob": {
      "autoApprove": ["**/*"]
    },
    "Grep": {
      "autoApprove": ["**/*"]
    }
  }
}
```

**期待効果**:
- コードベース探索の効率化
- コンテキスト収集の高速化

### 3. Edit ツールの条件付き自動承認

**提案**:
```json
{
  "toolPermissions": {
    "Edit": {
      "autoApprove": [
        "tests/**/*.py",
        ".steering/**/*.md"
      ]
    }
  }
}
```

---

## 優先度

| 提案 | 優先度 | 理由 |
|------|--------|------|
| Write for tests | 高 | TDDに必須 |
| Read/Glob/Grep | 中 | 読み取り専用で安全 |
| Edit for tests | 中 | リファクタリングに有用 |
| Write for prod code | 低 | レビューが必要 |

---

## フィードバック先

Claude Code の設定スキーマ改善について、以下でフィードバック可能:

- [Claude Code GitHub Issues](https://github.com/anthropics/claude-code/issues)

---

## 暫定対策

現在のスキーマでできる最大限の改善として、Bashコマンドの自動承認を充実させる（今回実施）。

ファイル操作については、ユーザーが慣れてきたら手動で承認を素早く行うワークフローで対応。
