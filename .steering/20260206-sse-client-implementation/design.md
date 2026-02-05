# Design - SSE Client Implementation

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                     SessionPage                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  useDialogue                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │ dialogueAtom│  │ characterAt │  │ sessionAtom │  │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │    │
│  │         │                │                │         │    │
│  │         └────────────────┼────────────────┘         │    │
│  │                          │                          │    │
│  │                 ┌────────▼────────┐                 │    │
│  │                 │ DialogueClient  │                 │    │
│  │                 │   (SSE接続)     │                 │    │
│  │                 └────────┬────────┘                 │    │
│  └──────────────────────────┼──────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              ▼
              POST /api/v1/dialogue/run
              Content-Type: application/json
              Accept: text/event-stream
```

## 技術選定

| 項目 | 選定 | 理由 |
|------|------|------|
| SSE接続 | fetch + ReadableStream | ブラウザ標準API、EventSourceはPOST非対応 |
| 状態管理 | Jotai atoms | プロジェクト標準 |
| 型定義 | Zod + TypeScript | バリデーション付き型安全性 |

## データ設計

### SSEイベント型

```typescript
// lib/api/types.ts

/** SSEイベントタイプ */
export type SSEEventType = "text" | "done" | "error"

/** テキストイベント */
export interface TextEvent {
  text: string
}

/** 完了イベント */
export interface DoneEvent {
  session_id: string
}

/** エラーイベント */
export interface ErrorEvent {
  error: string
  code: string
}

/** 対話リクエスト */
export interface RunDialogueRequest {
  user_id: string
  session_id: string
  message: string
}
```

### Jotai Atoms（既存）

- `dialogueHistoryAtom`: 対話履歴
- `characterStateAtom`: キャラクター状態
- `sessionAtom`: セッション情報

## API設計

### DialogueClient

```typescript
// lib/api/dialogueClient.ts

export interface DialogueClientOptions {
  baseUrl: string
  onText: (text: string) => void
  onDone: (sessionId: string) => void
  onError: (error: string, code: string) => void
}

export class DialogueClient {
  constructor(options: DialogueClientOptions)

  /** 対話を実行（SSEストリーミング） */
  async run(request: RunDialogueRequest): Promise<void>

  /** 接続を中断 */
  abort(): void
}
```

### useDialogue フック

```typescript
// lib/hooks/useDialogue.ts

export interface UseDialogueOptions {
  baseUrl?: string
}

export interface UseDialogueReturn {
  /** メッセージを送信 */
  sendMessage: (message: string) => Promise<void>
  /** 送信中かどうか */
  isLoading: boolean
  /** エラー */
  error: string | null
  /** エラーをクリア */
  clearError: () => void
}

export function useDialogue(options?: UseDialogueOptions): UseDialogueReturn
```

## ファイル構成

```
frontend/
├── lib/
│   ├── api/
│   │   ├── index.ts              # エクスポート集約
│   │   ├── types.ts              # SSEイベント型定義
│   │   ├── dialogueClient.ts     # SSEクライアント
│   │   └── dialogueClient.test.ts
│   └── hooks/
│       ├── useDialogue.ts        # 対話フック
│       └── useDialogue.test.ts
└── types/
    └── api.ts                    # API関連型（追加）
```

## エラーハンドリング

| エラー種別 | 検出方法 | 対応 |
|-----------|---------|------|
| ネットワークエラー | fetch throws | onError呼び出し、リトライ可能状態に |
| HTTPエラー | response.ok === false | onError呼び出し |
| SSEエラーイベント | event: error | onError呼び出し |
| タイムアウト | AbortSignal.timeout | onError呼び出し |
| パースエラー | JSON.parse throws | ログ出力、イベント無視 |

## セキュリティ考慮事項

- XSS対策: レスポンステキストはReactが自動エスケープ
- CORS: バックエンドで設定済み
- 認証: 将来的にJWTヘッダー追加（現時点では未実装）

## パフォーマンス考慮事項

- ストリーミング: チャンクごとに即座にUI更新
- メモリ: AbortControllerで不要な接続を即座に中断
- 再接続: 自動再接続は実装しない（ユーザー操作に委ねる）

## 代替案と採用理由

### EventSource vs fetch + ReadableStream

| 観点 | EventSource | fetch + ReadableStream |
|------|------------|----------------------|
| POST対応 | ❌ GETのみ | ✅ 対応 |
| ヘッダー追加 | ❌ 不可 | ✅ 可能 |
| 実装複雑度 | 低い | やや高い |

**採用理由**: バックエンドがPOSTメソッドを使用しているため、fetch + ReadableStreamを採用。
