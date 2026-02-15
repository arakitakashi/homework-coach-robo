---
name: unit-test
description: Delegates unit test execution to a sub-agent and returns only a structured pass/fail summary. Avoids polluting the main agent's context with verbose test output during TDD cycles.
allowed-tools: Task
---

# Unit Test

## Overview

このスキルは、ユニットテスト実行をサブエージェントに委譲し、メインエージェントのコンテキストにテスト出力が載ることを防ぎます。TDDサイクル（Red-Green-Refactor）で繰り返し使用することを想定しています。

## When to Use

- **RED phase**: テストが失敗することを確認
- **GREEN phase**: テストが通ることを確認
- **Quick verification**: 特定のテストの成否をすばやく確認
- **TDD cycle**: Red-Green-Refactorサイクルで繰り返し使用

**Do NOT use for:**
- PR前の全品質チェック（`/quality-check` を使用）
- カバレッジレポート（`/quality-check` を使用）
- lint / 型チェック（`/quality-check` を使用）

## Invocation

```
/unit-test <environment> [test-path] [test-name]
```

### Parameters

| Parameter | Required | Description | Examples |
|-----------|----------|-------------|----------|
| `environment` | Yes | テスト環境 | `frontend`, `backend` |
| `test-path` | No | テストファイルまたはディレクトリのパス | `components/VoiceInterface.test.tsx`, `tests/unit/services/` |
| `test-name` | No | 特定のテスト名 | `"should start recording"`, `test_create_session` |

**Note:** `test-path` を省略すると、全テストが実行されます。

## Instructions

### Step 1: パラメータを解析

ユーザーの入力からパラメータを抽出してください：

- `environment`: `frontend` または `backend`
- `test-path`: テストファイルまたはディレクトリのパス（省略時は全テスト）
- `test-name`: 特定のテスト名（省略可）

### Step 2: サブエージェントを起動

Task ツールで `Bash` タイプのサブエージェントを起動してください。

---

#### フロントエンド用プロンプト

```
ユニットテストを実行し、結果を構造化して報告してください。

作業ディレクトリ: [frontendディレクトリの絶対パス]

## 実行コマンド

cd [frontendディレクトリ] && bunx vitest run [test-path] [-t "test-name"]

※ test-pathが未指定の場合: cd [frontendディレクトリ] && bunx vitest run
※ test-nameが指定されている場合: -t "test-name" を追加

## 報告フォーマット（厳守）

### テスト成功時

✅ Unit Test Result: PASS

Environment: frontend
Path: [test-path or "all"]

Summary:
- Total: N tests
- Passed: N
- Failed: 0
- Duration: X.Xs

### テスト失敗時

❌ Unit Test Result: FAIL

Environment: frontend
Path: [test-path or "all"]

Summary:
- Total: N tests
- Passed: N
- Failed: N
- Duration: X.Xs

Failures:
1. "テスト名"
   エラータイプ: エラーメッセージ（1行）

2. "テスト名"
   Expected: 期待値
   Received: 実際の値

### コマンドエラー時

❌ Unit Test Execution Error

Environment: frontend
Path: [test-path]

Error: エラーメッセージ
Suggestion: 修正の提案

## 重要な制約

- verbose なテストランナー出力をそのまま返さない
- スタックトレースの全文を含めない
- 各失敗は最大3行に収める
- 報告全体を20行以内に収める
```

---

#### バックエンド用プロンプト

```
ユニットテストを実行し、結果を構造化して報告してください。

作業ディレクトリ: [backendディレクトリの絶対パス]

## 実行コマンド

cd [backendディレクトリ] && uv run pytest [test-path] [-k "test-name"] -v

※ test-pathが未指定の場合: cd [backendディレクトリ] && uv run pytest tests/ -v
※ test-nameが指定されている場合: -k "test-name" を追加

## 報告フォーマット（厳守）

### テスト成功時

✅ Unit Test Result: PASS

Environment: backend
Path: [test-path or "all"]

Summary:
- Total: N tests
- Passed: N
- Failed: 0
- Duration: X.Xs

### テスト失敗時

❌ Unit Test Result: FAIL

Environment: backend
Path: [test-path or "all"]

Summary:
- Total: N tests
- Passed: N
- Failed: N
- Duration: X.Xs

Failures:
1. "テスト名"
   エラータイプ: エラーメッセージ（1行）

2. "テスト名"
   Expected: 期待値
   Received: 実際の値

### コマンドエラー時

❌ Unit Test Execution Error

Environment: backend
Path: [test-path]

Error: エラーメッセージ
Suggestion: 修正の提案

## 重要な制約

- verbose なテストランナー出力をそのまま返さない
- スタックトレースの全文を含めない
- 各失敗は最大3行に収める
- 報告全体を20行以内に収める
```

---

### Step 3: 結果をユーザーに報告

サブエージェントから返された結果をそのまま報告してください。追加のコメントは不要です。

- **PASS**: TDDサイクルの次のステップに進む
- **FAIL（RED phase）**: 期待通り。実装に進む
- **FAIL（GREEN phase）**: 実装を修正し、再度 `/unit-test` で確認

## Relationship to Other Skills

| Skill | Purpose | When to Use | Output |
|-------|---------|-------------|--------|
| `/unit-test` | TDD中の高速テスト実行 | RED/GREEN phases | Pass/Fail summary only |
| `/quality-check` | PR前の全品質チェック | Phase 5 / PR作成前 | Lint + Type + Test + Build |
| `/analyze-errors` | エラー分析と修正提案 | エラーが多い場合 | Error categorization + fixes |

## Notes

- TDDワークフローに最適化されたスキルです
- 詳細なテスト出力よりも**速度とコンテキスト効率**を優先します
- 包括的なテスト分析が必要な場合は `/quality-check` を使用してください
- サブエージェントが verbose ログを内部で処理し、サマリーのみを返却します
