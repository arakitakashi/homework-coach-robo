# Design - Session Content Integration

## アーキテクチャ概要

```
SessionContent (page)
├── useSession (セッション管理)
│   ├── sessionClient.createSession()
│   └── sessionAtom (Jotai)
├── useDialogue (対話管理)
│   ├── dialogueClient.run() (SSE)
│   ├── dialogueTurnsAtom
│   └── characterStateAtom
└── TextInput (新規) / VoiceInterface (既存)
```

## コンポーネント設計

### 1. SessionClient (`lib/api/sessionClient.ts`)

バックエンドのセッションAPIを呼び出すクライアント。

```typescript
interface CreateSessionRequest {
  problem: string
  childGrade: number
  characterType?: string
}

interface SessionResponse {
  sessionId: string
  problem: string
  currentHintLevel: number
  tone: string
  turnsCount: number
  createdAt: string
}

class SessionClient {
  async createSession(request: CreateSessionRequest): Promise<SessionResponse>
}
```

### 2. useSession (`lib/hooks/useSession.ts`)

セッション管理フック。

```typescript
interface UseSessionReturn {
  session: Session | null
  isCreating: boolean
  error: string | null
  createSession: (problem: string, childGrade: number) => Promise<void>
  clearSession: () => void
}

function useSession(options?: { baseUrl?: string }): UseSessionReturn
```

**動作:**
1. `createSession`呼び出しでバックエンドにセッション作成リクエスト
2. 成功時、`sessionAtom`にセッション情報を保存
3. `useDialogue`がセッション情報を参照して対話可能に

### 3. TextInput (`components/ui/TextInput`)

テキスト入力コンポーネント（MVP用）。

```typescript
interface TextInputProps {
  onSubmit: (text: string) => void
  disabled?: boolean
  placeholder?: string
}
```

### 4. SessionContent統合

```typescript
function SessionContent({ characterType }: SessionContentProps) {
  const { session, createSession, isCreating } = useSession()
  const { sendMessage, isLoading, error } = useDialogue()

  // 初期化時にセッション作成
  useEffect(() => {
    if (!session) {
      createSession("宿題を一緒にやろう", 1) // デフォルト問題
    }
  }, [])

  const handleSendMessage = (text: string) => {
    sendMessage(text)
  }

  return (
    // ...
    <TextInput onSubmit={handleSendMessage} disabled={isLoading} />
    // ...
  )
}
```

## データフロー

```
[ユーザー入力]
    ↓
TextInput.onSubmit(text)
    ↓
useDialogue.sendMessage(text)
    ↓
dialogueClient.run({ user_id, session_id, message })
    ↓ (SSE)
onText → robotResponseRef蓄積
    ↓
onDone → dialogueTurnsAtom更新
    ↓
[DialogueHistory表示更新]
```

## APIエンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| POST | /api/v1/dialogue/sessions | セッション作成 |
| POST | /api/v1/dialogue/run | 対話実行（SSE） |

## 型定義

既存の`types/session.ts`を拡張:

```typescript
interface Session {
  id: string
  userId: string
  problem?: string
  currentHintLevel?: number
  createdAt?: Date
}
```

## ファイル構成

```
frontend/lib/
├── api/
│   ├── index.ts              # エクスポート集約（更新）
│   ├── types.ts              # 型定義（更新）
│   ├── sessionClient.ts      # セッションAPI（新規）
│   └── sessionClient.test.ts # テスト（新規）
└── hooks/
    ├── index.ts              # エクスポート集約（更新）
    ├── useSession.ts         # セッションフック（新規）
    └── useSession.test.tsx   # テスト（新規）

frontend/components/ui/
├── TextInput/
│   ├── TextInput.tsx         # テキスト入力（新規）
│   ├── TextInput.test.tsx    # テスト（新規）
│   └── index.ts              # エクスポート（新規）
└── index.ts                  # エクスポート集約（更新）

frontend/src/app/session/
├── SessionContent.tsx        # 統合（更新）
└── SessionContent.test.tsx   # テスト（更新）
```

## エラーハンドリング

| エラー種別 | 対応 |
|-----------|------|
| セッション作成失敗 | ErrorMessageコンポーネントで表示、リトライボタン |
| 対話送信失敗 | useDialogue.errorで表示、clearErrorでクリア |
| ネットワークエラー | タイムアウト後に再試行を提案 |

## セキュリティ考慮事項

- ユーザーIDは仮実装（認証フェーズで正式実装）
- 入力のサニタイズはバックエンドで実施
- CORSはバックエンド設定に依存

## 代替案と採用理由

### 音声→テキスト変換をフロントエンドで実装？

**不採用理由:**
- Cloud Speech-to-Textの統合が必要で、MVPスコープ外
- 音声データをバックエンドに送信してバックエンドで変換する方が一貫性がある
- テキスト入力でMVPを完成させ、音声はフェーズ2で対応

### WebSocket vs SSE

**SSEを採用（既存実装維持）:**
- バックエンドがSSEで実装済み
- テキスト対話では片方向ストリーミングで十分
- 将来の音声対応時にWebSocket検討
