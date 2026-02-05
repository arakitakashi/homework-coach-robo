# Task List - ADK Runner統合

## Phase 1: 環境セットアップ

- [x] ディレクトリ構造の作成（`backend/app/services/adk/runner/`）
- [x] テストディレクトリの作成（`backend/tests/unit/services/adk/runner/`）
- [x] ADK Runner APIの確認

## Phase 2: SocraticDialogueAgent実装（TDD）

### 2.1 システムプロンプト

- [x] テスト作成: `test_agent.py`
  - [x] システムプロンプトに3段階ヒントシステムの原則が含まれる
  - [x] 答えを直接教えないルールが含まれる
  - [x] 小学校低学年向けの言葉遣い指示が含まれる
- [x] 実装: `agent.py`
  - [x] `SOCRATIC_SYSTEM_PROMPT`定数
  - [x] `create_socratic_agent()`関数

### 2.2 Agent作成

- [x] テスト作成: Agent生成テスト
  - [x] 正しいモデル名が設定される
  - [x] 正しい名前・説明が設定される
  - [x] システムプロンプトが設定される
- [x] 実装: Agent生成ロジック

## Phase 3: AgentRunnerService実装（TDD）

### 3.1 初期化

- [x] テスト作成: `test_runner_service.py::test_init_*`
  - [x] SessionServiceが注入される
  - [x] MemoryServiceが注入される
  - [x] Runnerが正しく初期化される
- [x] 実装: `__init__()`メソッド

### 3.2 run メソッド

- [x] テスト作成: `test_run_*`
  - [x] ユーザーメッセージを送信できる
  - [x] イベントをストリームで受け取れる
  - [x] テキストレスポンスを取得できる
- [x] 実装: `run()`メソッド

### 3.3 セッション管理

- [x] テスト作成: `test_extract_text_*`
  - [x] イベントからテキスト抽出
  - [x] コンテンツなしの処理
- [x] 実装: extract_text()メソッド

## Phase 4: 統合テスト

- [ ] InMemoryServicesを使った統合テスト（将来のフェーズで実装）
  - [ ] Agent + Runner + Services の連携確認
  - [ ] イベントフロー確認

## Phase 5: 品質チェック

- [x] コードレビュー（セルフレビュー）
  - [x] ADK Runnerの契約を満たしているか
  - [x] 既存コンポーネントとの互換性
  - [x] エラーハンドリングは適切か
- [x] テストカバレッジ確認（291テスト全てパス）
- [x] リンター・型チェック実行
  - [x] `uv run ruff check app/services/adk/runner` → All checks passed
  - [x] `uv run mypy app/services/adk/runner` → Success: no issues found

## Phase 6: ドキュメント更新

- [x] `__init__.py` エクスポート設定
- [x] CLAUDE.md の更新
- [x] COMPLETED.md の作成

---

## 実装サマリー

### 実装ファイル

| ファイル | 内容 |
|---------|------|
| `agent.py` | SOCRATIC_SYSTEM_PROMPT, create_socratic_agent() |
| `runner_service.py` | AgentRunnerService（Runner統合） |
| `__init__.py` | モジュールエクスポート |

### テストファイル

| ファイル | テスト数 |
|---------|---------|
| `test_agent.py` | 12テスト |
| `test_runner_service.py` | 12テスト |
| **合計** | **24テスト** |

### ADK Runner統合の主要機能

1. `create_socratic_agent()`: ソクラテス式対話エージェント作成 ✅
2. `AgentRunnerService.run()`: エージェント実行・イベントストリーム ✅
3. `AgentRunnerService.extract_text()`: イベントからテキスト抽出 ✅
