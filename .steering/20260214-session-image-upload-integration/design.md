# Design - セッションページへの画像アップロード機能統合

## アーキテクチャ概要

SessionContentコンポーネントに入力モード選択UIと画像アップロードフローを統合する。Issue #153で実装したCameraInterfaceコンポーネントとIssue #152で実装したWebSocket画像イベントを組み合わせて、シームレスなユーザー体験を提供する。

### コンポーネント階層

```
SessionContent (既存)
  ├── InputModeSelector (新規)
  │     ├── VoiceModeButton
  │     └── ImageModeButton
  ├── CameraInterface (統合) ← セッション開始前の画像モード選択時に表示
  ├── VoiceInterface (既存)
  └── DialogueHistory (既存)
```

## 技術選定

### 状態管理

**Jotai atoms**を使用:
- `inputModeAtom`: 入力モード（'voice' | 'image' | null）
- `recognizedProblemTextAtom`: 画像認識結果

理由:
- 既存のSessionContentがJotaiを使用
- グローバル状態として他のコンポーネントからもアクセス可能
- シンプルで理解しやすいAPI

### WebSocket拡張

**VoiceWebSocketClientに新規メソッドを追加**:
- `sendImageStart()`: `start_with_image`イベント送信
- `onImageProblemConfirmed`: `image_problem_confirmed`イベント受信コールバック
- `onImageRecognitionError`: `image_recognition_error`イベント受信コールバック

理由:
- 既存のVoiceWebSocketClientを拡張することで、接続管理を統一
- 音声イベントと画像イベントを同じ接続で処理

## データ設計

### 型定義拡張

#### `types/session.ts` - WebSocket送信メッセージ型

```typescript
/** 画像問題開始イベント */
export interface StartWithImageMessage {
  type: "start_with_image"
  payload: {
    problem_text: string
    problem_type?: string
    image_url: string
    metadata?: Record<string, unknown>
  }
}

/** WebSocket送信メッセージ（拡張） */
export type WebSocketOutgoingMessage = VoiceTextMessage | StartWithImageMessage
```

#### `types/phase2.ts` - WebSocket受信イベント型（確認）

既存の型定義に以下が含まれているか確認（なければ追加）:

```typescript
/** 画像問題確認イベント */
export interface ImageProblemConfirmedEvent {
  type: "image_problem_confirmed"
  payload: {
    problem_id: string
    coach_response: string
  }
}

/** 画像認識エラーイベント */
export interface ImageRecognitionErrorEvent {
  type: "image_recognition_error"
  payload: {
    error: string
    code: string
  }
}

/** WebSocket受信イベント（拡張） */
export type WebSocketIncomingEvent =
  | ADKEvent
  | ImageProblemConfirmedEvent
  | ImageRecognitionErrorEvent
```

### Jotai Atoms

#### `store/atoms/camera.ts`（既存 - 確認）

```typescript
import { atom } from "jotai"

/** 入力モード */
export const inputModeAtom = atom<'voice' | 'image' | null>(null)

/** 画像認識結果 */
export const recognizedProblemTextAtom = atom<string | null>(null)
```

## API設計（該当する場合）

### VoiceWebSocketClient拡張

#### 新規メソッド

```typescript
class VoiceWebSocketClient {
  // 既存メソッド...

  /**
   * 画像問題開始イベントを送信
   * @param problemText - 認識された問題文
   * @param imageUrl - アップロード済み画像URL
   * @param problemType - 問題タイプ（optional）
   * @param metadata - 追加メタデータ（optional）
   */
  sendImageStart(
    problemText: string,
    imageUrl: string,
    problemType?: string,
    metadata?: Record<string, unknown>
  ): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: StartWithImageMessage = {
        type: "start_with_image",
        payload: {
          problem_text: problemText,
          image_url: imageUrl,
          problem_type: problemType,
          metadata,
        },
      }
      this.ws.send(JSON.stringify(message))
    }
  }
}
```

#### コールバック拡張

```typescript
export interface VoiceWebSocketOptions {
  // 既存コールバック...

  /** 画像問題確認コールバック */
  onImageProblemConfirmed?: (problemId: string, coachResponse: string) => void
  /** 画像認識エラーコールバック */
  onImageRecognitionError?: (error: string, code: string) => void
}
```

#### イベント処理拡張

```typescript
private processADKEvent(event: ADKEvent | WebSocketIncomingEvent): void {
  // 既存のADKイベント処理...

  // 画像問題確認イベント
  if ('type' in event && event.type === 'image_problem_confirmed') {
    this.options.onImageProblemConfirmed?.(
      event.payload.problem_id,
      event.payload.coach_response
    )
    return
  }

  // 画像認識エラーイベント
  if ('type' in event && event.type === 'image_recognition_error') {
    this.options.onImageRecognitionError?.(
      event.payload.error,
      event.payload.code
    )
    return
  }

  // 既存のADKイベント処理...
}
```

## ファイル構成

### 新規作成

```
frontend/
├── components/features/InputModeSelector/
│   ├── InputModeSelector.tsx         # 入力モード選択UI
│   ├── InputModeSelector.test.tsx    # テスト
│   └── index.ts                      # エクスポート
└── store/atoms/camera.ts             # カメラ関連atoms（存在確認）
```

### 変更ファイル

```
frontend/
├── src/app/session/SessionContent.tsx        # メインUI統合
├── src/app/session/SessionContent.test.tsx   # テスト更新
├── lib/api/voiceWebSocket.ts                 # WebSocketクライアント拡張
├── lib/api/voiceWebSocket.test.ts            # テスト更新
├── lib/api/types.ts                          # 型定義拡張
├── lib/hooks/useVoiceStream.ts               # フック拡張
├── lib/hooks/useVoiceStream.test.ts          # テスト更新
├── types/session.ts                          # 送信メッセージ型追加
├── types/phase2.ts                           # 受信イベント型追加（確認）
└── tests/pages/Session.test.tsx              # 統合テスト更新
```

## 実装フロー

### 1. セッション開始前（入力モード選択）

```
SessionContent
  ↓
InputModeSelector表示（セッション未作成時）
  ↓
ユーザーが「📷 写真で伝える」を選択
  ↓
inputModeAtom = 'image'
  ↓
CameraInterface表示
```

### 2. 画像アップロードと認識

```
CameraInterface
  ↓
画像をキャプチャ/アップロード
  ↓
VisionClient.analyzeImage() → Gemini Vision認識
  ↓
onProblemRecognized(recognizedText, result)
  ↓
recognizedProblemTextAtom = recognizedText
```

### 3. WebSocketイベント送信

```
onProblemRecognized()
  ↓
セッション作成（既存ロジック）
  ↓
WebSocket接続（useVoiceStream）
  ↓
VoiceWebSocketClient.sendImageStart(
  problemText,
  imageUrl,
  problemType,
  metadata
)
```

### 4. サーバーレスポンス処理

```
WebSocket受信: image_problem_confirmed
  ↓
onImageProblemConfirmed(problemId, coachResponse)
  ↓
対話履歴に追加: { speaker: 'robot', text: coachResponse }
  ↓
inputModeAtom = 'voice'（音声モードに切り替え）
  ↓
VoiceInterface表示
```

### エラーフロー

```
WebSocket受信: image_recognition_error
  ↓
onImageRecognitionError(error, code)
  ↓
エラーメッセージ表示
  ↓
CameraInterfaceの再表示（retryオプション）
```

## 依存関係

### 外部ライブラリ

- `jotai` (既存): 状態管理
- `framer-motion` (既存): モード切り替えアニメーション

### 内部依存

- `CameraInterface` (Issue #153で実装済み)
- `VoiceWebSocketClient` (既存、拡張対象)
- `useVoiceStream` (既存、拡張対象)
- `VisionClient` (Issue #150で実装済み)

## エラーハンドリング

### クライアント側エラー

| エラーケース | ハンドリング |
|------------|------------|
| カメラアクセス拒否 | CameraInterfaceのエラー状態表示 + ファイルアップロードフォールバック |
| 画像認識API失敗 | エラーメッセージ表示 + リトライボタン |
| WebSocket未接続 | エラーメッセージ表示 + 再接続ボタン |
| 画像アップロード失敗 | エラーメッセージ表示 + リトライボタン |

### サーバー側エラー（WebSocket経由）

| エラーコード | 意味 | ハンドリング |
|------------|------|------------|
| INVALID_PAYLOAD | ペイロード不正 | エラーメッセージ表示 + リトライ |
| AGENT_ERROR | エージェント転送失敗 | エラーメッセージ表示 + 音声モードにフォールバック |

## セキュリティ考慮事項

### 入力検証

- `problemText`: 最大長チェック（1000文字）
- `imageUrl`: gs://プレフィックス検証（Cloud Storage URLのみ許可）
- `problemType`: 許可リスト（"math", "japanese"）

### XSS対策

- `recognizedText`をDOMに表示する際は自動エスケープ（React default）
- `coachResponse`も同様にエスケープ

### プライバシー

- 画像URLはCloud Storageの署名付きURLを使用（一時的）
- セッション終了時に画像URLをクリア

## パフォーマンス考慮事項

### 画像アップロード最適化

- 画像サイズ制限: 最大5MB
- 画像圧縮: CameraInterface側で実施（80%品質JPEG）
- プログレス表示: アップロード中のUIフィードバック

### WebSocket最適化

- 既存の接続を再利用（音声と画像で同じ接続）
- バックエンドでのイベント処理は非同期

### UIパフォーマンス

- モード切り替えアニメーション: 300ms以内
- Framer Motionの`AnimatePresence`でスムーズな遷移

## 代替案と採用理由

### 代替案1: 別のWebSocket接続を使用

**検討**: 画像専用のWebSocket接続を作成

**却下理由**:
- 接続管理が複雑化
- セッション状態の同期が必要
- オーバーヘッド増加

### 代替案2: REST APIで画像問題を送信

**検討**: WebSocketではなくREST APIで画像問題を送信

**却下理由**:
- WebSocketでの統一的なイベント処理ができない
- リアルタイム応答が遅延
- サーバー側の実装が複雑化（Issue #152ですでにWebSocketで実装済み）

### 代替案3: セッション作成前にモード固定

**検討**: セッション作成時にモードを固定し、途中で切り替え不可

**却下理由**:
- ユーザビリティが低下
- 画像認識後の音声対話が自然でない
- 要件（画像認識完了後、自動的に音声モードに切り替え）に反する

## 採用した設計の利点

1. **統一されたWebSocket接続**: 音声と画像で同じ接続を使用し、管理が容易
2. **シームレスな切り替え**: 画像モード→音声モードの自動遷移でUX向上
3. **既存コードの再利用**: CameraInterface、VoiceWebSocketClientを拡張
4. **型安全性**: TypeScriptの型定義で実行時エラーを防止
5. **テスタビリティ**: Jotai atomsとコールバックでテストが容易
