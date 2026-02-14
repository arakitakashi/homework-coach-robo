# Design - WebSocket画像イベント（start_with_image）

## アーキテクチャ概要

既存のWebSocket `_client_to_agent` 関数に `start_with_image` イベントタイプを追加。
受信時に問題テキストをエージェントへ `send_text()` で転送し、確認レスポンスをクライアントに返す。
コーチの応答は既存の `_agent_to_client` ストリーム経由で自然に返却される。

## メッセージフロー

```
Client                    Server                    Agent
  |                         |                         |
  |-- start_with_image ---->|                         |
  |                         |-- send_text(problem) -->|
  |<-- image_problem_confirmed --|                    |
  |                         |<--- ADK events ---------|
  |<--- ADK events ---------|                         |
```

## データ設計

### クライアント → サーバー

```json
{
  "type": "start_with_image",
  "payload": {
    "problem_text": "3 + 5 = ?",
    "problem_type": "math",
    "image_url": "gs://...",
    "metadata": {}
  }
}
```

### サーバー → クライアント（成功）

```json
{
  "type": "image_problem_confirmed",
  "payload": {
    "problem_id": "uuid",
    "coach_response": "画像から問題を読み取りました！一緒に考えよう！"
  }
}
```

### サーバー → クライアント（エラー）

```json
{
  "type": "image_recognition_error",
  "payload": {
    "error": "エラーメッセージ",
    "code": "INVALID_PAYLOAD"
  }
}
```

## ファイル構成

### 変更ファイル

- `backend/app/schemas/voice_stream.py` - スキーマ追加
- `backend/app/api/v1/voice_stream.py` - ハンドラ追加

### 新規ファイル

- `backend/tests/unit/api/v1/test_ws_image.py` - テスト

## エラーハンドリング

- `problem_text` が空の場合 → `image_recognition_error` (code: INVALID_PAYLOAD)
- `payload` が欠落の場合 → `image_recognition_error` (code: INVALID_PAYLOAD)
- エージェントへの転送失敗時 → `image_recognition_error` (code: AGENT_ERROR)
