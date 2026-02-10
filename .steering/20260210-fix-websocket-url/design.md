# Design - WebSocket URL 自動生成修正

## アーキテクチャ概要

シンプルな文字列置換により、`NEXT_PUBLIC_API_URL`からWebSocket URLを導出する。

```
環境変数 → URL導出ロジック → VoiceWebSocketClient
```

---

## 技術選定

### 変更対象ファイル
- `frontend/lib/hooks/useVoiceStream.ts` - WebSocket URL生成ロジック

### 使用技術
- TypeScript文字列メソッド（`replace`, `||` 演算子）
- Next.js環境変数（`process.env.NEXT_PUBLIC_*`）

---

## 実装設計

### URL導出ロジック

#### 現状コード（132行目）
```typescript
const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
```

#### 修正後コード
```typescript
const baseUrl =
  process.env.NEXT_PUBLIC_WS_URL ||
  (process.env.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL.replace(/^http/, 'ws')
    : "ws://localhost:8000")
```

#### 動作フロー
1. `NEXT_PUBLIC_WS_URL`が設定されている → そのまま使用
2. `NEXT_PUBLIC_WS_URL`未設定 && `NEXT_PUBLIC_API_URL`設定あり → プロトコル変換
3. 両方未設定 → デフォルト値`ws://localhost:8000`

---

## プロトコル変換ロジック

### 正規表現: `/^http/`

| 入力 | `replace(/^http/, 'ws')` | 出力 |
|------|-------------------------|------|
| `https://backend.run.app` | `wss://backend.run.app` | ✅ |
| `http://localhost:8080` | `ws://localhost:8080` | ✅ |
| `https://backend.run.app/path` | `wss://backend.run.app/path` | ✅ |
| `ws://already-ws` | `ws://already-ws` | ✅（変更なし） |

**正規表現の動作**:
- `^http` - 文字列の先頭が`http`で始まる場合のみマッチ
- `https://` → `wss://` （`http`を`ws`に置換）
- `http://` → `ws://` （`http`を`ws`に置換）

---

## ファイル構成

変更なし。既存ファイルの1行のみ修正。

```
frontend/lib/hooks/
└── useVoiceStream.ts (132行目を修正)
```

---

## 依存関係

**変更なし**。新規依存パッケージの追加はなし。

---

## エラーハンドリング

### 想定されるエッジケース

| ケース | 挙動 |
|--------|------|
| `NEXT_PUBLIC_API_URL`が不正な形式 | 文字列置換は常に実行されるため、結果的に不正なWS URLが生成される可能性があるが、WebSocket接続時にエラーとなるため、既存のエラーハンドリングで対応可能 |
| 両環境変数が未設定 | デフォルト値`ws://localhost:8000`を使用（ローカル開発環境） |

**結論**: 新たなエラーハンドリングは不要。既存のWebSocket接続エラーハンドリングで対応可能。

---

## セキュリティ考慮事項

- 環境変数の値はビルド時にNext.jsによってバンドルされる（ランタイム変更不可）
- 変更なし：既存のセキュリティモデルを維持

---

## パフォーマンス考慮事項

- 文字列置換（`replace`）は軽量な操作（O(n)、nは文字列長）
- WebSocket接続は1セッションあたり1回のみ実行
- **影響**: 無視できるレベル

---

## 代替案と採用理由

### 代替案1: Dockerfileで環境変数を追加
**メリット**: 明示的な設定
**デメリット**: インフラ変更が必要、環境変数が増える

### 代替案2: ヘルパー関数を作成
```typescript
function deriveWebSocketUrl(apiUrl: string): string {
  return apiUrl.replace(/^http/, 'ws')
}
```
**メリット**: テスト可能、再利用可能
**デメリット**: オーバーエンジニアリング（シンプルな文字列置換のため）

### 採用理由（インライン実装）
- 最もシンプル
- 追加ファイル不要
- テストコード不要（既存テストでカバー）
- 読みやすい（ロジックが1箇所に集約）
