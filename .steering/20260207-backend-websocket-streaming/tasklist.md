# Task List - Backend WebSocket Voice Streaming

## Phase 1: ステアリング & セットアップ

- [x] ステアリングディレクトリ作成
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成

## Phase 2: スキーマ実装（TDD）

- [x] `tests/unit/schemas/test_voice_stream.py` テスト作成（18テスト）
- [x] `app/schemas/voice_stream.py` 実装（ADKTranscription, ADKInlineData, ADKContentPart, ADKEventMessage, TextInputMessage）
- [x] テスト通過確認

## Phase 3: VoiceStreamingService実装（TDD）

- [x] `tests/unit/services/voice/__init__.py` 作成
- [x] `tests/unit/services/voice/test_streaming_service.py` テスト作成（16テスト）
- [x] `app/services/voice/__init__.py` 作成
- [x] `app/services/voice/streaming_service.py` 実装
- [x] テスト通過確認

## Phase 4: WebSocketエンドポイント実装（TDD）

- [x] `tests/unit/api/v1/test_voice_stream.py` テスト作成（9テスト）
- [x] `app/api/v1/voice_stream.py` 実装
- [x] テスト通過確認

## Phase 5: ルート登録 & 品質チェック

- [x] `app/main.py` にWebSocketルート登録
- [x] `uv run ruff check .` → All checks passed
- [x] `uv run mypy .` → No issues found
- [x] `uv run pytest tests/ -v --cov` → 352 passed, 96% coverage

## Phase 6: 完了

- [x] COMPLETED.md 作成
