# COMPLETED - Backend WebSocket Voice Streaming

## 完了日

2026-02-07

## 実装内容の要約

フロントエンドの `VoiceWebSocketClient` と Gemini Live API を接続するバックエンドWebSocketエンドポイントを実装しました。

### 新規作成ファイル

| ファイル | 説明 |
|---------|------|
| `app/schemas/voice_stream.py` | Pydanticスキーマ（ADKEventMessage等） |
| `app/services/voice/__init__.py` | パッケージ初期化 |
| `app/services/voice/streaming_service.py` | VoiceStreamingService |
| `app/api/v1/voice_stream.py` | WebSocketエンドポイント |
| `tests/unit/schemas/test_voice_stream.py` | スキーマテスト（18テスト） |
| `tests/unit/services/voice/__init__.py` | テストパッケージ |
| `tests/unit/services/voice/test_streaming_service.py` | サービステスト（16テスト） |
| `tests/unit/api/v1/test_voice_stream.py` | エンドポイントテスト（9テスト） |

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `app/main.py` | WebSocketルート `/ws/{user_id}/{session_id}` 登録 |

### テスト結果

- **全352テスト通過**（既存309 + 新規43）
- **カバレッジ96%**
- ruff: All checks passed
- mypy: No issues found

## 発生した問題と解決方法

### 1. LiveRequestQueueのモック

**問題**: `LiveRequestQueue` のメソッドは実際の関数であり、MagicMockの `assert_called_once()` が使えない。

**解決**: `@patch("...LiveRequestQueue")` でクラスレベルでモックし、`mock_queue_cls.return_value = mock_queue` で戻り値を制御。

### 2. ADK型のmypyエラー

**問題**: ADK/google-genaiライブラリが完全に型付けされておらず、`no-untyped-call`、`attr-defined` エラー。

**解決**: 該当箇所に `# type: ignore[no-untyped-call]`、`# type: ignore[attr-defined]` を追加。

### 3. モック関数のパラメータ名不一致（テストハング）

**問題**: ruff ARG001修正でモック関数のパラメータ名を `user_id` → `_user_id` にリネームしたところ、`service.receive_events(user_id=..., session_id=...)` のキーワード引数とマッチせず `TypeError` が発生。エラーが `_agent_to_client` の `except Exception` で握りつぶされ、テストが無限にハングした。

**解決**: パラメータ名を `user_id`/`session_id` に戻し、`# noqa: ARG001` で ruff警告を抑制。

## 学んだこと（Lessons Learned）

1. **Pythonのキーワード引数マッチング**: パラメータ名をリネームすると、キーワード引数による呼び出しが壊れる。モック関数では元のパラメータ名を維持し、`# noqa` で未使用警告を抑制するのが安全。

2. **テストハングの原因特定**: asyncio並行タスクで一方のタスクがサイレントに失敗し、もう一方が永遠にブロックするパターン。エラーログを確認するか、タイムアウト付きでテストを実行して早期発見する。

3. **FastAPI WebSocketのDI**: WebSocketエンドポイントでも `Depends()` が使える。ただし `app.websocket()` で直接登録する方がAPIRouterより安定。
