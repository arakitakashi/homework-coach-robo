# Task List - Frontend WebSocket Integration

## Phase 1: usePcmPlayer フック

- [x] `lib/hooks/usePcmPlayer.test.ts` テスト作成
- [x] `lib/hooks/usePcmPlayer.ts` 実装
- [x] `lib/hooks/index.ts` エクスポート追加

## Phase 2: useVoiceStream audioLevel追加

- [x] `lib/hooks/useVoiceStream.test.tsx` テスト追加
- [x] `lib/hooks/useVoiceStream.ts` audioLevel実装

## Phase 3: SessionContent統合

- [x] `tests/pages/Session.test.tsx` テスト追加
- [x] `src/app/session/SessionContent.tsx` WebSocket統合実装
- [x] `src/app/session/SessionContent.test.tsx` 既存テストのモック修正

## Phase 4: 品質チェック

- [x] `bun lint` パス
- [x] `bun typecheck` パス
- [x] `bun test` 全テストパス（194テスト、23ファイル）
