# Design - WebSocket Phase 2 メッセージハンドラ統合 (Issue #65)

## アーキテクチャ概要

既存のToolExecutionハンドラと同一のデータフローパターンに従う：

```
VoiceWebSocketClient.processADKEvent()
  → onAgentTransition / onEmotionUpdate コールバック
    → useVoiceStream パススルー
      → SessionContent ハンドラ
        → Jotai atoms 更新
          → UI コンポーネント（将来Issue）
```

## データ設計

### ADKEvent 拡張

```typescript
// lib/api/types.ts
interface ADKAgentTransitionEvent {
  fromAgent: string
  toAgent: string
  reason: string
}

interface ADKEmotionUpdateEvent {
  emotion: string
  frustrationLevel: number
  engagementLevel: number
}

interface ADKEvent {
  // ...existing
  agentTransition?: ADKAgentTransitionEvent
  emotionUpdate?: ADKEmotionUpdateEvent
}
```

### コールバック型

```typescript
// VoiceWebSocketOptions 拡張
onAgentTransition?: (fromAgent: string, toAgent: string, reason: string) => void
onEmotionUpdate?: (emotion: string, frustrationLevel: number, engagementLevel: number) => void

// UseVoiceStreamOptions 拡張（同一シグネチャ）
```

### SessionContent → Jotai atoms マッピング

| イベント | ハンドラ | 更新atom |
|---------|---------|---------|
| AgentTransition | handleAgentTransition | activeAgentAtom, agentTransitionHistoryAtom |
| EmotionUpdate | handleEmotionUpdate | emotionAnalysisAtom, emotionHistoryAtom |

## ファイル構成（変更対象）

| ファイル | 変更内容 |
|---------|---------|
| `frontend/lib/api/types.ts` | ADKEvent拡張、VoiceWebSocketOptions拡張 |
| `frontend/lib/api/voiceWebSocket.ts` | processADKEvent拡張 |
| `frontend/lib/api/voiceWebSocket.test.ts` | テスト追加（6テスト） |
| `frontend/lib/hooks/useVoiceStream.ts` | コールバックパススルー追加 |
| `frontend/lib/hooks/useVoiceStream.test.tsx` | テスト追加（2テスト） |
| `frontend/src/app/session/SessionContent.tsx` | ハンドラ追加、atoms接続 |
| `frontend/src/app/session/SessionContent.test.tsx` | テスト追加（4テスト） |

## 既存リソースの再利用

- `AgentType`, `ActiveAgent`, `AgentTransition` → `types/phase2.ts`
- `EmotionType`, `EmotionAnalysis` → `types/phase2.ts`
- `activeAgentAtom`, `agentTransitionHistoryAtom` → `store/atoms/phase2.ts`
- `emotionAnalysisAtom`, `emotionHistoryAtom` → `store/atoms/phase2.ts`
- `ADKToolExecutionEvent` パターン → `lib/api/types.ts`（テンプレート）
- ToolExecution テストパターン → 各テストファイル（テンプレート）
