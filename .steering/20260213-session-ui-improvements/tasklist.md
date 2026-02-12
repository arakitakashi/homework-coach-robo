# Task List - セッションUI改善とバグ修正

## Phase 1: 環境セットアップ

- [x] 作業ブランチ作成 (`fix/session-ui-improvements-115-120`)
- [x] ステアリングディレクトリ作成
- [x] requirements.md, design.md, tasklist.md 作成
- [ ] 関連ファイルの現状確認

## Phase 2: テスト実装（TDD）

### #120: characterパラメータバリデーション

- [ ] `src/app/session/page.tsx` の現状確認
- [ ] バリデーションロジックのテスト作成（Red）
- [ ] バリデーション実装（Green）

### #119: 404ページ日本語化

- [ ] `src/app/not-found.tsx` のテスト作成（Red）
- [ ] 404ページ実装（Green）

### #115: 対話履歴リセット

- [ ] 対話履歴リセット処理のテスト作成（Red）
- [ ] リセット処理実装（Green）

### #116: まほうつかい画像表示

- [ ] キャラクター画像表示のテスト作成（Red）
- [ ] 画像表示ロジック修正（Green）
- [ ] 必要な画像アセットの確認・追加

### #117: ストーリー説明文連動

- [ ] キャラクター名動的表示のテスト作成（Red）
- [ ] ストーリー説明文修正（Green）

### #118: 音声録音ボタン状態

- [ ] 音声録音ボタン状態のテスト作成（Red）
- [ ] WebSocket/マイク状態管理修正（Green）

## Phase 3: リファクタリング

- [ ] コードの整理・改善
- [ ] テストの整理・改善
- [ ] 不要なコメント削除

## Phase 4: 統合テスト

- [ ] すべての修正が統合されていることを確認
- [ ] 手動テストで各issueが解決されていることを確認
- [ ] クロスブラウザテスト（必要に応じて）

## Phase 5: 品質チェック

- [ ] `bun lint` - Biome lint
- [ ] `bun typecheck` - TypeScript型チェック
- [ ] `bunx vitest run` - Vitestテスト実行
- [ ] テストカバレッジ確認（80%以上）
- [ ] セキュリティレビュー（`/security-review` スキル）
- [ ] ドキュメント更新
  - [ ] `CLAUDE.md` の Development Context 更新
  - [ ] `docs/implementation-status.md` 更新
  - [ ] `.steering/20260213-session-ui-improvements/COMPLETED.md` 作成

## Phase 6: デプロイ準備

- [ ] コミットメッセージ作成（Conventional Commits形式）
- [ ] プッシュ
- [ ] PR作成（`/create-pr` スキル）
- [ ] issue #115-#120 をPR説明文でクローズ
