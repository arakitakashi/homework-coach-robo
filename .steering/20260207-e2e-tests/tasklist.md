# Task List - E2Eテスト実装

## Phase 1: インフラセットアップ

- [ ] `@playwright/test` インストール
- [ ] `frontend/e2e/playwright.config.ts` 作成
- [ ] `frontend/tsconfig.e2e.json` 作成
- [ ] `frontend/package.json` にe2eスクリプト追加
- [ ] 空テストで動作確認

## Phase 2: ヘルパー・フィクスチャ

- [ ] `helpers/selectors.ts`
- [ ] `helpers/sse-mock.ts`
- [ ] `fixtures/base.ts`

## Phase 3: スモークテスト

- [ ] `smoke/health-check.spec.ts`
- [ ] `smoke/navigation.spec.ts`

## Phase 4: ファンクショナルテスト

- [ ] `functional/home-page.spec.ts`
- [ ] `functional/session-creation.spec.ts`
- [ ] `functional/text-dialogue.spec.ts`
- [ ] `functional/voice-ui.spec.ts`
- [ ] `functional/session-cleanup.spec.ts`

## Phase 5: バックエンドE2Eモード

- [ ] `backend/app/testing/mock_runner.py`
- [ ] `backend/app/testing/mock_voice.py`
- [ ] `backend/app/main.py` に `E2E_MODE` 分岐追加
- [ ] `docker-compose.e2e.yml` 作成

## Phase 6: 統合テスト

- [ ] `global-setup.ts` / `global-teardown.ts`
- [ ] `integration/session-api.spec.ts`
- [ ] `integration/dialogue-stream.spec.ts`

## Phase 7: CI/CD・品質チェック

- [ ] `.github/workflows/ci-e2e.yml` 作成
- [ ] 全テスト実行確認
- [ ] CLAUDE.md更新
