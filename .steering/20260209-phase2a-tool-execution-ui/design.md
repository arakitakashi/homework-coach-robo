# Design - Phase 2a ツール実行状態UIコンポーネント

## アーキテクチャ概要

WebSocket → VoiceWebSocketClient → useVoiceStream → SessionContent → Jotai atoms → ToolExecutionDisplay

## ファイル構成

新規:
- components/features/ToolExecutionDisplay/ToolExecutionDisplay.tsx
- components/features/ToolExecutionDisplay/ToolExecutionDisplay.test.tsx
- components/features/ToolExecutionDisplay/index.ts

修正:
- lib/api/types.ts (ADKEvent, VoiceWebSocketOptions)
- lib/api/voiceWebSocket.ts (processADKEvent)
- lib/api/voiceWebSocket.test.ts
- lib/hooks/useVoiceStream.ts (onToolExecution)
- lib/hooks/useVoiceStream.test.ts
- src/app/session/SessionContent.tsx
- src/app/session/SessionContent.test.tsx
- components/features/index.ts

## 依存関係

既存のPhase 2型定義・atomsを再利用:
- types/phase2.ts: ToolExecution, ToolExecutionStatus, ToolName
- store/atoms/phase2.ts: activeToolExecutionsAtom, isToolRunningAtom
- types/websocket.ts: ToolExecutionMessage
