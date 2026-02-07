# Design - Backend WebSocket Voice Streaming

## アーキテクチャ概要

```
Frontend (VoiceWebSocketClient)
    ↕ WebSocket (ws://.../ws/{user_id}/{session_id})
    │  ↓ Binary PCM (16kHz 16-bit) or JSON {"type":"text","text":"..."}
    │  ↑ JSON ADKEvent
Backend (voice_stream.py)
    ↕ VoiceStreamingService
    │  Uses LiveRequestQueue + Runner.run_live()
ADK Runner
    ↕ Gemini Live API (gemini-2.5-flash-native-audio-preview-12-2025)
```

## 技術選定

- **ADK Runner.run_live()**: 双方向ストリーミング対応
- **LiveRequestQueue**: 音声/テキスト入力のキューイング
- **RunConfig(response_modalities=["AUDIO"])**: 音声応答モード
- **asyncio.create_task**: agent→client と client→agent の並行処理

## データ設計

### Server→Client (ADKEventMessage)

```json
{
  "author": "agent",
  "turnComplete": true,
  "interrupted": false,
  "inputTranscription": { "text": "...", "finished": true },
  "outputTranscription": { "text": "...", "finished": true },
  "content": {
    "parts": [
      { "inlineData": { "mimeType": "audio/pcm", "data": "<base64>" } }
    ]
  }
}
```

### Client→Server

1. Binary: Raw PCM audio bytes
2. JSON: `{"type": "text", "text": "..."}`

## ファイル構成

```
app/schemas/voice_stream.py          # Pydanticスキーマ
app/services/voice/__init__.py       # パッケージ
app/services/voice/streaming_service.py  # VoiceStreamingService
app/api/v1/voice_stream.py          # WebSocketエンドポイント
tests/unit/schemas/test_voice_stream.py
tests/unit/services/voice/__init__.py
tests/unit/services/voice/test_streaming_service.py
tests/unit/api/v1/test_voice_stream.py
```

## 依存関係

- google-adk (Runner, LiveRequestQueue, RunConfig)
- google-genai (types.Blob, types.Content, types.Part)
- FastAPI (WebSocket, Depends)
- Pydantic (BaseModel)

## エラーハンドリング

- WebSocket切断: `WebSocketDisconnect` でgraceful cleanup
- agent→client エラー: ログ出力、タスクキャンセル
- 不正なJSONメッセージ: ログ警告、スキップ

## セキュリティ考慮事項

- user_id/session_idはURLパスパラメータ（バリデーション済み）
- 入力JSONは`json.loads`でパース、型チェック済み

## 代替案と採用理由

- **WebSocket route on APIRouter vs direct app.websocket()**: FastAPIのWebSocketはDependsを使う場合、直接`app.websocket()`で登録する方が安定。APIRouterでもWebSocketは動作するが、直接登録の方がシンプル。
