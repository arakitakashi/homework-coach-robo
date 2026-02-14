# Task List - WebSocket画像イベント（start_with_image）

## Phase 1: テスト実装（TDD - Red）

- [ ] テストファイル `test_ws_image.py` 作成
  - [ ] `start_with_image` 成功ケースのテスト
  - [ ] `image_problem_confirmed` レスポンスのテスト
  - [ ] payload欠落時のエラーテスト
  - [ ] `problem_text` 空文字時のエラーテスト
  - [ ] エージェント転送失敗時のエラーテスト

## Phase 2: スキーマ実装（Green）

- [ ] `voice_stream.py` にスキーマ追加
  - [ ] `StartWithImagePayload`
  - [ ] `ImageProblemConfirmedMessage`
  - [ ] `ImageRecognitionErrorMessage`

## Phase 3: ハンドラ実装（Green）

- [ ] `_handle_start_with_image` 関数追加
- [ ] `_client_to_agent` に `start_with_image` ケース追加

## Phase 4: 品質チェック

- [ ] ruff check
- [ ] mypy
- [ ] pytest
