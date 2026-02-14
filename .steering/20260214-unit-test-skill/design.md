# Design - Unit Test Skill

## アーキテクチャ概要

```
User → Claude (Main Agent)
         ↓ Skill invocation
         ↓ /unit-test frontend tests/example.test.tsx
         ↓
         Task tool (subagent_type: general-purpose)
         ↓
         Sub-agent
         ├─ cd frontend && bun test tests/example.test.tsx
         ├─ 詳細ログ受信（数百行）
         ├─ サマリー抽出
         └─ 構造化された結果返却（10行以内）
         ↓
         Main Agent
         └─ ✅ 8 tests passed (0.5s) のみ受信
```

## 技術選定

### スキルインターフェース

```markdown
# Skill: unit-test

## Invocation

/unit-test <environment> <test-path> [test-name]

## Parameters
- environment: "frontend" | "backend"
- test-path: (optional) Path to test file or directory
- test-name: (optional) Specific test name to run

## Examples
/unit-test frontend
/unit-test frontend components/VoiceInterface.test.tsx
/unit-test backend tests/unit/services/test_auth_service.py
/unit-test backend tests/unit/services/ test_create_session
```

### サブエージェントタイプ

**選択: `general-purpose`**

理由:
- テスト実行は Bash ツールで実行可能
- 複雑なロジック不要
- 専用エージェントを作る必要はない

### テスト実行コマンド

#### Frontend (Vitest)

```bash
cd frontend

# 全テスト
bun test

# 特定ファイル
bun test components/VoiceInterface.test.tsx

# 特定テスト名
bun test -t "should start recording"
```

#### Backend (pytest)

```bash
cd backend

# 全テスト
uv run pytest tests/

# 特定ファイル
uv run pytest tests/unit/services/test_auth_service.py

# 特定テスト名
uv run pytest -k "test_create_session"
```

### 出力パース戦略

#### Vitest 出力例

```
✓ tests/components/VoiceInterface.test.tsx (8)
✓ tests/hooks/useWebSocket.test.ts (5)

Test Files  2 passed (2)
     Tests  13 passed (13)
  Start at  10:30:00
  Duration  0.5s
```

**抽出情報:**
- Test Files: 2 passed
- Tests: 13 passed
- Duration: 0.5s

#### pytest 出力例

```
==================== test session starts ====================
collected 15 items

tests/unit/services/test_auth_service.py .......... [ 66%]
tests/unit/services/test_session_service.py ..... [100%]

==================== 15 passed in 0.50s ====================
```

**抽出情報:**
- collected: 15 items
- passed: 15
- Duration: 0.50s

#### 失敗時の例（Vitest）

```
✓ tests/components/VoiceInterface.test.tsx (7)
❌ tests/components/VoiceInterface.test.tsx (1)
  ✓ should render
  ❌ should start recording
    Expected: true
    Received: false

Test Files  1 passed, 1 failed (2)
     Tests  7 passed, 1 failed (8)
```

**抽出情報:**
- Tests: 7 passed, 1 failed
- Failed test: "should start recording"
- Error: Expected: true, Received: false

## データ設計

### 返却フォーマット（構造化）

```typescript
interface UnitTestResult {
  status: 'pass' | 'fail';
  summary: {
    total: number;
    passed: number;
    failed: number;
    skipped?: number;
    duration: string;
  };
  failures?: Array<{
    testName: string;
    errorMessage: string;
  }>;
}
```

### 実際の返却例

**成功時:**
```
✅ Unit Test Result: PASS

Summary:
- Total: 13 tests
- Passed: 13
- Failed: 0
- Duration: 0.5s
```

**失敗時:**
```
❌ Unit Test Result: FAIL

Summary:
- Total: 8 tests
- Passed: 7
- Failed: 1
- Duration: 0.3s

Failures:
1. "should start recording"
   Expected: true
   Received: false
```

## ファイル構成

```
.claude/skills/
└── unit-test.md        # スキル定義（新規作成）
```

## 依存関係

### 既存スキルとの関係

| スキル | 用途 | 実行タイミング | 出力 |
|--------|------|---------------|------|
| `/unit-test` | TDDサイクル中のテスト実行 | Red/Greenフェーズ | サマリーのみ |
| `/quality-check` | 実装完了後の全チェック | PR作成前 | Lint+Type+Test+Coverage |
| `/analyze-errors` | エラー分析と修正提案 | エラー発生時 | 分析結果 |

### 使い分け

```
TDDサイクル中:
  テスト書く → /unit-test → 失敗確認（RED）
  実装書く → /unit-test → 成功確認（GREEN）
  リファクタ → /unit-test → 継続成功確認

実装完了後:
  /quality-check → 全品質チェック（lint/type/test/coverage）
```

## エラーハンドリング

### 1. テストコマンド実行失敗

```
❌ Error: Failed to run tests

Reason: Command 'bun test' not found
Suggestion: Ensure you are in the correct directory (frontend/)
```

### 2. 全テスト失敗

```
❌ Unit Test Result: FAIL

Summary:
- Total: 50 tests
- Passed: 0
- Failed: 50
- Duration: 2.3s

Note: All tests failed. This may indicate a setup issue.
Suggestion: Check test environment configuration.
```

### 3. タイムアウト

サブエージェントのタイムアウトはデフォルト設定に従う（通常は十分）。

## セキュリティ考慮事項

- テスト実行はサンドボックス内で実行される（Bashツールのデフォルト動作）
- 環境変数へのアクセスは既存のテスト環境と同じ
- 特別な権限昇格は不要

## パフォーマンス考慮事項

### オーバーヘッド分析

```
従来（メインエージェントで実行）:
  テスト実行: 0.5s
  ログ処理: 0.1s
  コンテキスト: 数百行
  Total: 0.6s

新方式（サブエージェント委譲）:
  サブエージェント起動: 1.0s
  テスト実行: 0.5s
  サマリー抽出: 0.1s
  結果返却: 0.1s
  コンテキスト: 10行以内
  Total: 1.7s
```

**トレードオフ:**
- +1.1秒の待機時間
- -数百行のコンテキスト消費

**判断:** コンテキスト節約のメリットが大きいため、許容可能。

## 代替案と採用理由

### 代替案1: Bashツールで`tail`を使う

```bash
bun test 2>&1 | tail -n 10
```

**メリット:** サブエージェント不要、即座に結果
**デメリット:** それでもある程度のログは出力される

**不採用理由:** コンテキストを完全に削減できない

### 代替案2: `/quality-check` スキルを拡張

```
/quality-check --test-only <path>
```

**メリット:** 既存スキルの再利用
**デメリット:** 責務が広がりすぎる

**不採用理由:** 単一責任の原則に反する

### 採用案: 専用の `/unit-test` スキル

**メリット:**
- 単一責任（テスト実行のみ）
- TDDフローに最適化
- コンテキスト完全削減

**理由:** 最も要求に適合する
