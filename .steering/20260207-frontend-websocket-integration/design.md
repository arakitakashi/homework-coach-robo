# Design - Frontend WebSocket Integration

## アーキテクチャ概要

```
SessionContent
├── useVoiceStream (WebSocket管理)
│   ├── onAudioData → feedAudio() + characterState="speaking"
│   ├── onTranscription → DialogueTurn追加
│   ├── onTurnComplete → characterState="idle"
│   └── onInterrupted → stopPlayback() + characterState="listening"
├── usePcmPlayer (PCM再生)
│   └── AudioContext(24kHz) + pcm-player-processor.js
└── useDialogue (SSEテキスト対話 - 既存)
```

## usePcmPlayer設計

### API

```typescript
interface UsePcmPlayerReturn {
  isPlaying: boolean
  feedAudio: (pcmData: ArrayBuffer) => void
  stop: () => void
  initialize: () => Promise<void>
  cleanup: () => void
}
```

### 内部動作

- `initialize()`: AudioContext(24kHz)作成、pcm-player-processor.jsロード、WorkletNode作成
- `feedAudio()`: worklet portへpostMessage、isPlaying=true、300msタイムアウトでisPlaying=false
- `stop()`: endOfAudioコマンド送信、タイムアウトクリア、isPlaying=false
- `cleanup()`: AudioContext/WorkletNode解放

## useVoiceStream audioLevel設計

- `UseVoiceStreamReturn`に`audioLevel: number`追加（0-1の範囲）
- `startRecording()`内のworklet `onmessage`でFloat32ArrayからRMS計算
- `stopRecordingInternal()`で`audioLevel`を0にリセット

## SessionContentコールバック設計

| コールバック | 処理 |
|------------|------|
| `onAudioData` | `feedAudio(data)` + `setCharacterState("speaking")` |
| `onTranscription` | `finished=true`のみDialogueTurn追加 |
| `onTurnComplete` | `setCharacterState("idle")` |
| `onInterrupted` | `stop()` + `setCharacterState("listening")` |

## ライフサイクル

- セッション作成完了時: `initPlayer()` + `voiceConnect(userId, sessionId)`
- セッション終了時: `voiceDisconnect()` + `cleanupPlayer()`
- 録音開始: `setCharacterState("listening")`
- 録音停止: `setCharacterState("thinking")`
