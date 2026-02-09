---
name: quality-check
description: Delegates backend quality checks (mypy, ruff, pytest) to a sub-agent and returns a structured pass/fail summary. Use before creating a PR or when verifying code quality after changes.
allowed-tools: Task
---

# Quality Check

## Overview

このスキルは、バックエンドの品質チェック（mypy, ruff, pytest）をサブエージェントに委譲し、メインエージェントのコンテキストにエラー出力が載ることを防ぎます。

## When to Use

- 実装完了後の品質チェック（Phase 5）
- PR作成前のローカルCIチェック
- エラー修正後の再確認

## Instructions

### Step 1: サブエージェントを起動

Task ツールで `Bash` タイプのサブエージェントを起動し、以下のプロンプトを使用してください。

```
バックエンドの品質チェックを実行し、結果を構造化して報告してください。

作業ディレクトリ: [backendディレクトリの絶対パス]

以下の3つのチェックを順番に実行してください:

1. **型チェック（mypy）**
   コマンド: cd [backendディレクトリ] && uv run mypy .

2. **リンター（ruff）**
   コマンド: cd [backendディレクトリ] && uv run ruff check .

3. **テスト（pytest）**
   コマンド: cd [backendディレクトリ] && uv run pytest tests/ -v

## 報告フォーマット

以下の形式で結果を報告してください:

### 結果サマリー
- mypy: PASS / FAIL (エラー数)
- ruff: PASS / FAIL (エラー数)
- pytest: PASS / FAIL (テスト数 passed, テスト数 failed)

### エラー詳細（FAILの場合のみ）
各エラーについて:
- ファイルパス:行番号
- エラーコード
- エラーメッセージ
- 修正案（可能な場合）
```

### Step 2: 結果に基づいてアクション

サブエージェントの結果に基づいて：

- **全PASS**: PR作成に進む
- **FAILあり**: エラー詳細を確認し、修正を行う。修正後、再度このスキルを実行して確認

## Notes

- pytest の出力が長い場合（数百テスト）、サブエージェントが要約してくれるためコンテキスト節約に効果的
- mypy エラーが多い場合（10件以上）、修正自体も別のサブエージェントに委譲することを検討してください
