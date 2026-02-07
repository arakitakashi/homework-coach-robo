# Task List - E2Eテスト実装

## Phase 1: インフラセットアップ

- [x] `@playwright/test` インストール
- [x] `frontend/e2e/playwright.config.ts` 作成
- [x] `frontend/tsconfig.e2e.json` 作成
- [x] `frontend/package.json` にe2eスクリプト追加
- [x] 空テストで動作確認

## Phase 2: ヘルパー・フィクスチャ

- [x] `helpers/selectors.ts`
- [x] `helpers/sse-mock.ts`
- [x] `fixtures/base.ts`

## Phase 3: スモークテスト

- [x] `smoke/health-check.spec.ts`
- [x] `smoke/navigation.spec.ts`

## Phase 4: ファンクショナルテスト

- [x] `functional/home-page.spec.ts`
- [x] `functional/session-creation.spec.ts`
- [x] `functional/text-dialogue.spec.ts`
- [x] `functional/voice-ui.spec.ts`
- [x] `functional/session-cleanup.spec.ts`

## Phase 5: バックエンドE2Eモード

- [x] `backend/app/testing/mock_runner.py`
- [x] `backend/app/testing/mock_voice.py`
- [x] `backend/app/main.py` に `E2E_MODE` 分岐追加
- [x] `docker-compose.e2e.yml` 作成

## Phase 6: 統合テスト

- [x] `global-setup.ts` / `global-teardown.ts`
- [x] `integration/session-api.spec.ts`
- [x] `integration/dialogue-stream.spec.ts`

## Phase 7: CI/CD・品質チェック

- [x] `.github/workflows/ci-e2e.yml` 作成
- [x] 全テスト実行確認
- [x] CLAUDE.md更新
