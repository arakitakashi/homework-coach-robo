# Design - Voice Input Implementation

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ VoiceInterface│───▶│useVoiceStream│───▶│VoiceWebSocket│  │
│  │  (UI Component)│    │   (Hook)     │    │   (Client)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                   │                    │          │
│          ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ CharacterDisplay│  │PCMRecorder   │    │ AudioPlayer  │  │
│  │  (表情変化)    │    │ (AudioWorklet)│    │ (AudioWorklet)│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
                     WebSocket (Binary PCM)
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                                                              │
│  WebSocket /ws/{user_id}/{session_id}                       │
│       │                                                      │
│       ▼                                                      │
│  ADK LiveRequestQueue ──▶ Gemini Live API                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 技術選定

| コンポーネント | 技術 | 理由 |
|--------------|------|------|
| 音声録音 | AudioWorklet | 低レイテンシ、メインスレッド非ブロック |
| 音声再生 | AudioWorklet | 低レイテンシ、ストリーミング対応 |
| 通信 | WebSocket | 双方向リアルタイム通信、バイナリ対応 |
| 状態管理 | Jotai | 既存のアーキテクチャに準拠 |

## ファイル構成

```
frontend/
├── lib/
│   ├── api/
│   │   ├── voiceWebSocket.ts          # WebSocketクライアント（音声用）
│   │   ├── voiceWebSocket.test.ts
│   │   └── types.ts                   # 型定義追加
│   └── hooks/
│       ├── useVoiceStream.ts          # 音声ストリーミングフック
│       └── useVoiceStream.test.ts
├── components/
│   └── features/
│       └── VoiceInterface/
│           ├── VoiceInterface.tsx     # 拡張
│           └── VoiceInterface.test.tsx
└── public/
    └── worklets/
        ├── pcm-recorder-processor.js  # 録音用AudioWorklet
        └── pcm-player-processor.js    # 再生用AudioWorklet
```

## データ設計

### WebSocketメッセージ形式

**Client → Server:**
```typescript
// テキストメッセージ
{ type: "text", text: string }

// 音声データ（バイナリ）
ArrayBuffer (16kHz 16-bit PCM)
```

**Server → Client:**
```typescript
// ADK Event形式
{
  author?: string;
  turnComplete?: boolean;
  interrupted?: boolean;
  inputTranscription?: { text: string; finished: boolean };
  outputTranscription?: { text: string; finished: boolean };
  content?: {
    parts: Array<{
      text?: string;
      inlineData?: { mimeType: string; data: string };
    }>;
  };
}
```

### 状態管理（Jotai Atoms）

```typescript
// lib/api/atoms/voice.ts
export const voiceConnectionStateAtom = atom<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
export const isRecordingAtom = atom<boolean>(false);
export const isPlayingAtom = atom<boolean>(false);
export const audioLevelAtom = atom<number>(0);
```

## API設計

### VoiceWebSocketClient

```typescript
interface VoiceWebSocketOptions {
  baseUrl: string;
  userId: string;
  sessionId: string;
  onAudioData: (data: ArrayBuffer) => void;
  onTranscription: (text: string, isUser: boolean) => void;
  onTurnComplete: () => void;
  onError: (error: string) => void;
}

class VoiceWebSocketClient {
  constructor(options: VoiceWebSocketOptions);
  connect(): void;
  disconnect(): void;
  sendAudio(pcmData: ArrayBuffer): void;
  sendText(message: string): void;
  readonly isConnected: boolean;
}
```

### useVoiceStream Hook

```typescript
interface UseVoiceStreamReturn {
  // 状態
  isConnected: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  audioLevel: number;
  error: string | null;

  // アクション
  connect: (userId: string, sessionId: string) => void;
  disconnect: () => void;
  startRecording: () => Promise<void>;
  stopRecording: () => void;

  // イベント
  onTranscription: (handler: (text: string, isUser: boolean) => void) => void;
}
```

## AudioWorklet設計

### PCM Recorder Processor

```javascript
// public/worklets/pcm-recorder-processor.js
class PCMRecorderProcessor extends AudioWorkletProcessor {
  // 16kHz 16-bit PCMに変換
  // 一定サイズのバッファが溜まったらメインスレッドに送信
}
```

### PCM Player Processor

```javascript
// public/worklets/pcm-player-processor.js
class PCMPlayerProcessor extends AudioWorkletProcessor {
  // base64デコード済みPCMデータを受信
  // AudioContextのサンプルレートに変換して再生
}
```

## エラーハンドリング

| エラー | 原因 | 対処 |
|--------|------|------|
| `NotAllowedError` | マイク権限拒否 | ユーザーにわかりやすいエラーメッセージ表示 |
| WebSocket接続失敗 | ネットワークエラー | 自動再接続（5秒後） |
| AudioContext未サポート | ブラウザ非対応 | 対応ブラウザの案内 |

## セキュリティ考慮事項

1. WebSocket接続はHTTPSページではwss://を使用
2. ユーザーIDとセッションIDの検証はサーバー側で実施
3. マイク権限は明示的なユーザーアクションで要求

## パフォーマンス考慮事項

1. AudioWorkletでメインスレッドをブロックしない
2. PCMデータは圧縮せずバイナリで送信（低レイテンシ優先）
3. 音声バッファサイズは2048サンプル（約128ms @16kHz）

## 代替案と採用理由

| 選択肢 | 採用 | 理由 |
|--------|------|------|
| ScriptProcessorNode | × | 非推奨、メインスレッドブロック |
| AudioWorklet | ○ | 低レイテンシ、モダンAPI |
| MediaRecorder API | × | PCM出力が難しい |
| WebRTC | × | サーバー側の実装が複雑 |
