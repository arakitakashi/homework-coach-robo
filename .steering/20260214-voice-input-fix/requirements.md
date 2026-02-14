# Requirements - 音声入力が応答しない問題の修正

## 背景・目的

デプロイ済みアプリで「話しかける」ボタンを押して音声入力しても応答がない。
音量メーターは動いている（=マイク取得・AudioWorklet・WebSocket接続は成功）が、
AIからの応答が返ってこない。

## 要求事項

### 機能要件

- 音声入力後、AIが応答すること（音声+トランスクリプション）
- エラー発生時にフロントエンドにエラーが通知されること

### 非機能要件

- Cloud Run バックエンドで Gemini Live API が正常に動作すること

### 制約条件

- Gemini Live APIモデルはus-central1リージョンで利用可能（Cloud Runはasia-northeast1）

## 対象範囲

### In Scope

1. Cloud Run バックエンドに genai 環境変数を追加（Terraform）
2. WebSocket エラーハンドリング改善（バックエンド→フロントエンドへのエラー通知）

### Out of Scope

- 認証・認可の実装
- WebSocket URLの別設定（NEXT_PUBLIC_WS_URL）
- Cloud Runのタイムアウト延長（別issueで対応）

## 成功基準

- デプロイ後、音声入力に対してAIが応答を返す
- エラー発生時にフロントエンドにエラーメッセージが表示される
