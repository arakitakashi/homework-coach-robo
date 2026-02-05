# Task List - SSE Client Implementation

## Phase 1: 環境セットアップ

- [x] `/frontend` スキルを参照
- [x] 既存のJotai atomsを確認

## Phase 2: 型定義（TDD）

- [x] SSEイベント型のテスト作成
- [x] SSEイベント型の実装（`lib/api/types.ts`）

## Phase 3: SSEクライアント実装（TDD）

- [x] DialogueClientのテスト作成
- [x] DialogueClientの実装（`lib/api/dialogueClient.ts`）
- [x] エクスポート集約の更新（`lib/api/index.ts`）

## Phase 4: useDialogueフック実装（TDD）

- [x] useDialogueのテスト作成
- [x] useDialogueの実装（`lib/hooks/useDialogue.ts`）
- [x] エクスポート集約の更新（`lib/hooks/index.ts`）

## Phase 5: 品質チェック

- [x] `bun lint` パス
- [x] `bun typecheck` パス
- [x] `bun run test` パス（99テスト通過）
- [x] テストカバレッジ確認

## Phase 6: ドキュメント・コミット

- [x] COMPLETED.md 作成
- [x] コミット作成
