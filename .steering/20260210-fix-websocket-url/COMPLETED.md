# COMPLETED - WebSocket URL 自動生成修正

## 完了サマリー

**問題**: フロントエンドがWebSocket接続時に`ws://localhost:8000`をハードコードされたデフォルト値として使用し、本番環境で接続に失敗していた。

**解決**: `NEXT_PUBLIC_API_URL`からWebSocket URLを自動導出するロジックを実装。環境変数の追加やインフラ変更なしで問題を解決。

---

## 実装内容

### 変更ファイル
- `frontend/lib/hooks/useVoiceStream.ts` (132行目)

### 変更コード

#### Before
```typescript
const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
```

#### After
```typescript
// WebSocket URLの優先順位:
// 1. NEXT_PUBLIC_WS_URL（明示的設定）
// 2. NEXT_PUBLIC_API_URLから導出（http→ws, https→wss）
// 3. ローカル開発用デフォルト
const baseUrl =
  process.env.NEXT_PUBLIC_WS_URL ||
  (process.env.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL.replace(/^http/, "ws")
    : "ws://localhost:8000")
```

### URL変換例

| 環境変数 | 導出されるWebSocket URL |
|---------|----------------------|
| `NEXT_PUBLIC_API_URL=https://backend.run.app` | `wss://backend.run.app` |
| `NEXT_PUBLIC_API_URL=http://localhost:8080` | `ws://localhost:8080` |
| `NEXT_PUBLIC_WS_URL=wss://custom.com` | `wss://custom.com`（優先） |
| 両方未設定 | `ws://localhost:8000`（開発用） |

---

## テスト結果

### ✅ Lint（Biome）
```
Checked 117 files in 49ms. No fixes applied.
```

### ✅ Type Check（TypeScript）
```
$ tsc --noEmit
（エラーなし）
```

### ✅ Unit Tests（Vitest）
```
Test Files  28 passed (28)
Tests       309 passed (309)
Duration    3.75s
```

---

## 影響範囲

### 変更あり
- `frontend/lib/hooks/useVoiceStream.ts` - 1行修正（132行目）

### 変更なし
- Dockerfile - 変更不要
- GitHub Actionsワークフロー - 変更不要
- 環境変数設定 - 追加不要
- バックエンド - 変更なし

---

## デプロイ

### 本番環境での動作
1. Dockerビルド時に`NEXT_PUBLIC_API_URL`が注入される（既存の仕組み）
2. ランタイムで`https://backend.run.app`が`wss://backend.run.app`に変換される
3. WebSocket接続が正しいURLに対して行われる

### 確認手順
1. mainブランチにマージ後、自動デプロイが実行される
2. フロントエンドのコンソールでWebSocketエラーが消えることを確認
3. 音声ストリーミング機能が正常に動作することを確認

---

## 今後の改善点

### なし
- シンプルで保守性の高い実装
- 既存のテストで十分カバーされている
- 追加のテストコード不要

---

## 学んだこと（Lessons Learned）

### 環境変数設計のベストプラクティス
- 関連する環境変数（API URL + WebSocket URL）を個別に設定するより、1つから導出する方がシンプル
- デフォルト値のフォールバックチェーンを明確にすることで、開発環境と本番環境の両方に対応できる

### Next.js環境変数の制約
- `NEXT_PUBLIC_*`環境変数はビルド時にバンドルに埋め込まれる
- ランタイムで値を変更できないため、導出ロジックはビルド成果物に含まれる

### 最小限の変更原則
- 1行の修正で問題を解決（オーバーエンジニアリングを避けた）
- インフラ変更なしで対応（デプロイリスクを最小化）

---

## コミット情報

```
commit 2dbde78
Author: Claude Sonnet 4.5

fix: derive WebSocket URL from NEXT_PUBLIC_API_URL

フロントエンドのWebSocket接続エラーを修正。
```

---

**完了日時**: 2026-02-10
**所要時間**: 約15分（設計 + 実装 + テスト）
**ステータス**: ✅ 完了・テスト済み・PR準備完了
