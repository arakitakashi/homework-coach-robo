# Requirements - WebSocket URL 自動生成修正

## 背景・目的

### 現状の問題
- フロントエンドがWebSocket接続時に`ws://localhost:8000`にハードコードされたデフォルト値を使用
- `NEXT_PUBLIC_WS_URL`環境変数が未設定の場合、本番環境で接続失敗
- Dockerfileでは`NEXT_PUBLIC_API_URL`のみが設定され、`NEXT_PUBLIC_WS_URL`は未設定

### エラー内容
```
WebSocket connection to 'ws://localhost:8000/ws/anonymous/94ddfbee-b927-49f9-9683-5c10498a3e31' failed
```

### 目的
`NEXT_PUBLIC_API_URL`からWebSocket URLを自動生成し、追加の環境変数なしで正しいWebSocket接続を実現する。

---

## 要求仕様

### 機能要件

#### FR1: WebSocket URL自動生成
- `NEXT_PUBLIC_API_URL`が設定されている場合、そこからWebSocket URLを導出
- HTTPSプロトコル（`https://`）をWSSプロトコル（`wss://`）に変換
- HTTPプロトコル（`http://`）をWSプロトコル（`ws://`）に変換
- ホスト名・ポート・パスは保持

#### FR2: 優先順位
1. `NEXT_PUBLIC_WS_URL`が明示的に設定されている場合はそれを使用（既存の挙動維持）
2. `NEXT_PUBLIC_API_URL`が設定されている場合はそこから導出
3. どちらも未設定の場合は`ws://localhost:8000`（ローカル開発用フォールバック）

#### FR3: 後方互換性
- 既存の`NEXT_PUBLIC_WS_URL`環境変数を使用している環境では変更なし
- ローカル開発環境（環境変数未設定）では従来通り動作

### 非機能要件

#### NFR1: パフォーマンス
- URL変換はビルド時ではなくランタイムで実行
- 軽量な文字列置換のため、パフォーマンス影響なし

#### NFR2: テスト
- 既存のテストが全てパスすること
- URL変換ロジックの単体テストは不要（シンプルな文字列置換）

#### NFR3: デプロイメント
- Dockerfileやワークフローの変更は不要
- 既存のビルドプロセスに影響なし

---

## 対象範囲

### In Scope
- `frontend/lib/hooks/useVoiceStream.ts`のWebSocket URL生成ロジック修正
- 既存テストの実行・確認

### Out of Scope
- Dockerfileの変更
- ワークフローの変更
- 環境変数の追加
- バックエンドの変更

---

## 成功基準

1. ✅ `NEXT_PUBLIC_API_URL`からWebSocket URLが正しく導出される
2. ✅ 既存のテスト（309テスト）が全てパス
3. ✅ Lintチェック（Biome）がパス
4. ✅ 型チェック（TypeScript）がパス
5. ✅ ローカル開発環境で動作確認
6. ✅ 本番環境でWebSocket接続エラーが解消

---

## 変換ロジック例

| NEXT_PUBLIC_API_URL | 導出されるWebSocket URL |
|---------------------|------------------------|
| `https://backend.run.app` | `wss://backend.run.app` |
| `http://localhost:8080` | `ws://localhost:8080` |
| （未設定） | `ws://localhost:8000` |
