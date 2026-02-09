# Task List - WebSocket Phase 2 メッセージハンドラ統合 (Issue #65)

## TDD順序（ボトムアップ）

### Step 1: voiceWebSocket テスト → 型 + 実装

- [x] `voiceWebSocket.test.ts` に AgentTransition テスト追加（3テスト）
- [x] `voiceWebSocket.test.ts` に EmotionUpdate テスト追加（3テスト）
- [x] `types.ts` に ADKAgentTransitionEvent, ADKEmotionUpdateEvent 型追加
- [x] `types.ts` の ADKEvent に agentTransition?, emotionUpdate? 追加
- [x] `types.ts` の VoiceWebSocketOptions に onAgentTransition?, onEmotionUpdate? 追加
- [x] `voiceWebSocket.ts` の processADKEvent に agentTransition ハンドリング追加
- [x] `voiceWebSocket.ts` の processADKEvent に emotionUpdate ハンドリング追加
- [x] テスト全パス確認

### Step 2: useVoiceStream テスト → 実装

- [x] `useVoiceStream.test.tsx` に onAgentTransition パススルーテスト追加
- [x] `useVoiceStream.test.tsx` に onEmotionUpdate パススルーテスト追加
- [x] `useVoiceStream.ts` の UseVoiceStreamOptions に onAgentTransition?, onEmotionUpdate? 追加
- [x] `useVoiceStream.ts` の connect() でコールバックパススルー追加
- [x] テスト全パス確認

### Step 3: SessionContent テスト → 実装

- [x] `SessionContent.test.tsx` の capturedVoiceStreamOptions にコールバック型追加
- [x] `SessionContent.test.tsx` に AgentTransition テスト追加（2テスト）
- [x] `SessionContent.test.tsx` に EmotionUpdate テスト追加（2テスト）
- [x] `SessionContent.tsx` に handleAgentTransition コールバック追加
- [x] `SessionContent.tsx` に handleEmotionUpdate コールバック追加
- [x] `SessionContent.tsx` の useVoiceStream に新コールバック追加
- [x] テスト全パス確認

### Step 4: 品質チェック

- [x] `bun lint` パス
- [x] `bun typecheck` パス（e2e/のみ既存エラー）
- [x] `bunx vitest run` 全テストパス（291テスト / 26ファイル）
- [ ] コミット
