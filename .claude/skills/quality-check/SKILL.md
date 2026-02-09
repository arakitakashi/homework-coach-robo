---
name: quality-check
description: Delegates quality checks (lint, type check, test) to a sub-agent and returns a structured pass/fail summary. Supports backend (mypy/ruff/pytest), frontend (Biome/TypeScript/Vitest), and infrastructure (Terraform). Use before creating a PR or when verifying code quality after changes.
allowed-tools: Task
---

# Quality Check

## Overview

このスキルは、品質チェック（lint, 型チェック, テスト）をサブエージェントに委譲し、メインエージェントのコンテキストにエラー出力が載ることを防ぎます。バックエンド・フロントエンド・インフラに対応しています。

## When to Use

- 実装完了後の品質チェック（Phase 5）
- PR作成前のローカルCIチェック
- エラー修正後の再確認

## Instructions

### Step 1: 対象を判定

変更したファイルに基づいて、チェック対象を判定してください：

| 変更対象 | チェック |
|---------|--------|
| `backend/` or `app/` or `tests/` | バックエンド |
| `frontend/` or `components/` or `src/` | フロントエンド |
| `infrastructure/` | インフラ |

複数の対象がある場合は、それぞれのサブエージェントを**並列で起動**してください。

### Step 2: サブエージェントを起動

対象ごとに Task ツールで `Bash` タイプのサブエージェントを起動してください。

---

#### バックエンド用プロンプト

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

---

#### フロントエンド用プロンプト

```
フロントエンドの品質チェックを実行し、結果を構造化して報告してください。

作業ディレクトリ: [frontendディレクトリの絶対パス]

以下の4つのチェックを順番に実行してください:

1. **リンター（Biome）**
   コマンド: cd [frontendディレクトリ] && bun lint

2. **型チェック（TypeScript）**
   コマンド: cd [frontendディレクトリ] && bun typecheck

3. **テスト（Vitest）**
   コマンド: cd [frontendディレクトリ] && bun test

4. **ビルド確認**
   コマンド: cd [frontendディレクトリ] && bun build

## 報告フォーマット

### 結果サマリー
- lint (Biome): PASS / FAIL (エラー数)
- typecheck (TypeScript): PASS / FAIL (エラー数)
- test (Vitest): PASS / FAIL (テスト数 passed, テスト数 failed)
- build: PASS / FAIL

### エラー詳細（FAILの場合のみ）
各エラーについて:
- ファイルパス:行番号
- エラーコード
- エラーメッセージ
- 修正案（可能な場合）
```

---

#### インフラ用プロンプト

```
インフラストラクチャの品質チェックを実行し、結果を構造化して報告してください。

作業ディレクトリ: [infrastructureディレクトリの絶対パス]

以下の2つのチェックを順番に実行してください:

1. **フォーマットチェック（Terraform）**
   コマンド: cd [infrastructureディレクトリ] && terraform fmt -check -recursive

2. **バリデーション（Terraform）**
   各環境ディレクトリで実行:
   コマンド: cd [infrastructureディレクトリ]/terraform/environments/dev && terraform validate

## 報告フォーマット

### 結果サマリー
- terraform fmt: PASS / FAIL
- terraform validate: PASS / FAIL (環境ごと)

### エラー詳細（FAILの場合のみ）
各エラーについて:
- ファイルパス
- エラーメッセージ
- 修正案（可能な場合）
```

---

### Step 3: 結果に基づいてアクション

サブエージェントの結果に基づいて：

- **全PASS**: PR作成に進む
- **FAILあり**: エラー詳細を確認し、修正を行う。修正後、再度このスキルを実行して確認

## Notes

- 複数対象がある場合、サブエージェントを並列起動するとチェック時間を短縮できます
- pytest/Vitest の出力が長い場合（数百テスト）、サブエージェントが要約してくれるためコンテキスト節約に効果的
- エラーが多い場合（10件以上）、修正自体も別のサブエージェントに委譲することを検討してください
