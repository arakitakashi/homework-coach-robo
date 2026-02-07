# Design - E2Eテスト実装

## アーキテクチャ概要

2層構造のE2Eテスト:
- **Tier 1 (Functional)**: Playwright route interception → フロントエンドUI検証
- **Tier 2 (Integration)**: Docker Compose + E2Eモードバックエンド → 通信検証

## ファイル構成

```
frontend/
  e2e/
    playwright.config.ts
    fixtures/base.ts
    helpers/selectors.ts
    helpers/sse-mock.ts
    tests/
      smoke/health-check.spec.ts
      smoke/navigation.spec.ts
      functional/home-page.spec.ts
      functional/session-creation.spec.ts
      functional/text-dialogue.spec.ts
      functional/voice-ui.spec.ts
      functional/session-cleanup.spec.ts
      integration/session-api.spec.ts
      integration/dialogue-stream.spec.ts
    global-setup.ts
    global-teardown.ts
  tsconfig.e2e.json

backend/
  app/testing/
    __init__.py
    mock_runner.py
    mock_voice.py

docker-compose.e2e.yml
.github/workflows/ci-e2e.yml
```

## 技術選定

- Playwright 1.48+ (routeWebSocket対応)
- Docker Compose (統合テスト用バックエンド起動)

## テスト戦略

### Functional テスト
- `page.route()` でREST/SSE APIをモック
- `page.routeWebSocket()` でWebSocketをモック
- フロントエンド単体のUI動作を検証

### Integration テスト
- Docker ComposeでバックエンドをE2Eモードで起動
- `E2E_MODE=true` でGemini APIをモックサービスに差し替え
- 実際のHTTP/SSE通信を検証
