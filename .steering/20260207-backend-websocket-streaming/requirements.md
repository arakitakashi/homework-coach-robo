# Requirements - Backend WebSocket Voice Streaming

## 背景・目的

フロントエンドの `VoiceWebSocketClient` が期待するプロトコルに準拠した、バックエンドWebSocketエンドポイントを実装する。PoCで検証済みの ADK `Runner.run_live()` + `LiveRequestQueue` パターンを本番バックエンドに移植する。

## 要求事項

### 機能要件

1. WebSocketエンドポイント `/ws/{user_id}/{session_id}` を提供
2. クライアントからバイナリPCM音声データ（16kHz 16-bit）を受信し、Gemini Live APIに転送
3. クライアントからJSONテキストメッセージ `{"type":"text","text":"..."}` を受信し、転送
4. Gemini Live APIからのイベントをフロントエンド互換のADKEvent JSON形式で返送
5. セッションが存在しない場合は自動作成

### 非機能要件

- テストカバレッジ80%以上
- ruff、mypy、pytestがすべてパス

### 制約条件

- フロントエンドの `VoiceWebSocketClient` プロトコルに準拠
- ADK `Runner.run_live()` を使用
- Live APIモデル: `gemini-2.5-flash-native-audio-preview-12-2025`

## 対象範囲

### In Scope

- Pydanticスキーマ（ADKEventMessage, ADKTranscription, etc.）
- VoiceStreamingService（Runner + LiveRequestQueue ラッパー）
- WebSocketエンドポイント（双方向ストリーミング）
- ルート登録（main.py）
- ユニットテスト

### Out of Scope

- E2Eテスト
- デプロイ
- フロントエンドの変更

## 成功基準

- 全テスト通過（352テスト）
- カバレッジ96%
- ruff/mypy エラーなし
