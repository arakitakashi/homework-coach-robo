# Completed - E2Eテスト実装

## 実装内容の要約

Playwrightを使用した2層構造のE2Eテストを実装した。

### テスト数

| カテゴリ | テスト数 |
|---------|---------|
| Smoke Tests | 5 |
| Functional Tests | 21 |
| Integration Tests | 8 |
| **合計** | **34** |

### Tier 1: Functional Tests（route interception）

- **ホームページ**: タイトル表示、キャラクター選択、aria-pressed、URL遷移
- **セッション作成**: ローディング表示、エラー表示、リトライ、戻るボタン
- **テキスト対話**: ウェルカムメッセージ、テキスト入力、SSEレスポンス、対話履歴
- **音声UI**: 録音ボタン表示、ステータステキスト、aria属性
- **セッション終了**: ホーム復帰、DELETE API呼び出し、新セッション開始

### Tier 2: Integration Tests（Docker Compose + E2Eモード）

- **セッションAPI**: CRUD操作、404エラー
- **対話ストリーム**: SSEイベント検証、ソクラテス式応答、フルUIフロー

### バックエンドE2Eモード

- `E2E_MODE=true` 環境変数でモックサービスに切り替え
- `MockAgentRunnerService`: 定型ソクラテス式レスポンス
- `MockVoiceStreamingService`: テキスト入出力のモック
- `InMemorySessionService`: Firestoreなしのセッション管理

## ファイル構成

```
frontend/e2e/
├── playwright.config.ts
├── fixtures/base.ts          # MockAPIクラス
├── helpers/
│   ├── selectors.ts          # 日本語UIテキスト定数
│   └── sse-mock.ts           # SSEレスポンス生成
├── global-setup.ts           # Docker Compose起動
├── global-teardown.ts        # Docker Compose停止
└── tests/
    ├── smoke/                # 5テスト
    ├── functional/           # 21テスト
    └── integration/          # 8テスト

backend/app/testing/
├── __init__.py
├── mock_runner.py            # MockAgentRunnerService
└── mock_voice.py             # MockVoiceStreamingService

docker-compose.e2e.yml
.github/workflows/ci-e2e.yml
```

## 実行方法

```bash
# Functional Tests（バックエンドモック）
cd frontend && bun run e2e:functional

# Integration Tests（Docker Compose）
docker compose -f docker-compose.e2e.yml up -d backend
cd frontend && bun run e2e:integration
docker compose -f docker-compose.e2e.yml down

# 全テスト
cd frontend && bun run e2e
```

## Lessons Learned

1. Playwright の `globalSetup`/`globalTeardown` はプロジェクトレベルではなくconfig レベルの設定
2. Biome は `.gitignore` を参照するため、`playwright-report/` を `.gitignore` に追加が必要
3. TypeScript の `Promise` コンストラクタ内での変数代入はクロージャの型推論に注意（deferred パターンで解決）
4. `bun test --run` と `bunx vitest run` の動作が異なる場合がある
