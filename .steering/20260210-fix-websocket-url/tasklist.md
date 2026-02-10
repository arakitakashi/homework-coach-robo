# Task List - WebSocket URL 自動生成修正

## Phase 1: 環境セットアップ

- [x] ブランチ作成（`fix/websocket-url-from-api-url`）
- [x] ステアリングディレクトリ作成（`.steering/20260210-fix-websocket-url/`）
- [x] requirements.md作成
- [x] design.md作成
- [x] tasklist.md作成

## Phase 2: 実装

- [ ] `frontend/lib/hooks/useVoiceStream.ts`の132行目を修正
- [ ] コード変更をコミット

## Phase 3: テスト

- [ ] Lintチェック（`cd frontend && bun lint`）
- [ ] 型チェック（`cd frontend && bun typecheck`）
- [ ] ユニットテスト（`cd frontend && bun test`）
- [ ] 必要に応じてテスト修正

## Phase 4: 品質チェック

- [ ] すべてのチェックがパスすることを確認
- [ ] 変更内容をレビュー

## Phase 5: 完了

- [ ] COMPLETED.mdを作成（変更サマリー）
- [ ] PR作成準備完了

---

## 注意事項

- TDD原則は適用しない（既存コードの軽微な修正のため）
- 既存テストが全てパスすることで品質を担保
- 新規テストコードの追加は不要
