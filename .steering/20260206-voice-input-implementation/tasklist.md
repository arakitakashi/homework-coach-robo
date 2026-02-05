# Task List - Voice Input Implementation

## Phase 1: 環境セットアップ

- [x] `/frontend` スキルを参照
- [x] リファレンス実装（`ref/adk-streaming-guide-main/workshops/`）を確認
- [x] ステアリングドキュメント作成

## Phase 2: AudioWorklet Processor実装

- [x] PCM Recorder Processor の実装（`public/worklets/pcm-recorder-processor.js`）
- [x] PCM Player Processor の実装（`public/worklets/pcm-player-processor.js`）

Note: AudioWorkletはWorkerコンテキストで実行されるため、ユニットテストは困難。統合テストで検証。

## Phase 3: WebSocketクライアント実装（TDD）

- [x] VoiceWebSocketClient の型定義（`lib/api/types.ts`）
- [x] VoiceWebSocketClient のテスト作成（`lib/api/voiceWebSocket.test.ts` - 17テスト）
- [x] VoiceWebSocketClient の実装（`lib/api/voiceWebSocket.ts`）
- [x] エクスポート集約の更新（`lib/api/index.ts`）

## Phase 4: useVoiceStreamフック実装（TDD）

- [x] useVoiceStream のテスト作成（`lib/hooks/useVoiceStream.test.tsx` - 10テスト）
- [x] useVoiceStream の実装（`lib/hooks/useVoiceStream.ts`）
- [x] エクスポート集約の更新（`lib/hooks/index.ts`）

## Phase 5: VoiceInterface拡張

- [x] VoiceInterface のテスト更新（プレゼンテーションコンポーネント化 - 10テスト）
- [x] VoiceInterface の実装拡張（プロップベースに変更）
- [x] SessionContent との統合（useVoiceStream接続）

## Phase 6: 品質チェック

- [x] `bun lint` パス
- [x] `bun typecheck` パス
- [x] `bun run test run` パス（172テスト全通過）
- [x] テストカバレッジ確認（80%以上）- Statements: 89.35%, Lines: 90.01%, Functions: 90.99%

## Phase 7: ドキュメント・コミット

- [x] COMPLETED.md 作成
- [x] CLAUDE.md 更新
- [ ] コミット作成
- [ ] PR作成
