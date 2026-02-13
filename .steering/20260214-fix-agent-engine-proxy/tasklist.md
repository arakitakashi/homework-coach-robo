# Task List - Agent Engine プロキシ修正

## Phase 1: 環境セットアップ

- [x] ブランチ作成（`fix/agent-engine-missing-methods`）
- [x] ステアリングディレクトリ作成（`.steering/20260214-fix-agent-engine-proxy/`）
- [x] 必須ドキュメント作成（requirements.md, design.md, tasklist.md）

## Phase 2: テスト実装（TDD）

### 2.1. `register_operations()` のテスト作成

- [x] `test_register_operations_returns_correct_format()` 作成
  - `register_operations()` が正しい形式（辞書）を返すこと
  - `""` キーに `["query", "create_session"]` が含まれること
  - `"stream"` キーに `["stream_query"]` が含まれること

### 2.2. `AgentEngineClient.create_session()` のテスト作成

- [x] `test_create_session_calls_correct_proxy_method()` 作成
  - プロキシの `create_session()` メソッドを呼び出すこと（`async_create_session` ではない）
  - 正しい引数（`user_id`）が渡されること
  - 戻り値が正しく返されること

### 2.3. `AgentEngineClient.stream_query()` のテスト作成

- [x] `test_stream_query_calls_correct_proxy_method()` 作成
  - プロキシの `stream_query()` メソッドを呼び出すこと（`async_stream_query` ではない）
  - 正しい引数（`user_id`, `session_id`, `message`）が渡されること
  - イベントストリームが正しく返されること

## Phase 3: 実装

### 3.1. `HomeworkCoachAgent.register_operations()` の実装

- [x] `register_operations()` メソッドを追加
  - Agent Engine ドキュメントに従った形式で実装
  - 同期メソッド（`query`, `create_session`）を `""` キーに登録
  - ストリーミングメソッド（`stream_query`）を `"stream"` キーに登録
- [x] テスト実行（Green確認）- 後で実行

### 3.2. `AgentEngineClient.create_session()` の修正

- [x] プロキシメソッド呼び出しを `async_create_session` → `create_session` に修正
- [x] `# type: ignore[attr-defined]` コメントの必要性を確認（必要に応じて保持）
- [x] テスト実行（Green確認）- 後で実行

### 3.3. `AgentEngineClient.stream_query()` の修正

- [x] プロキシメソッド呼び出しを `async_stream_query` → `stream_query` に修正
- [x] `# type: ignore[attr-defined]` コメントの必要性を確認（必要に応じて保持）
- [x] テスト実行（Green確認）- 後で実行

## Phase 4: 統合テスト

- [x] 全ユニットテストの実行（`uv run pytest tests/`）
- [x] カバレッジ確認（80%以上）

## Phase 5: 品質チェック

- [x] `/quality-check` スキルでサブエージェントに委譲
  - Ruff lint（`uv run ruff check .`）
  - mypy 型チェック（`uv run mypy .`）
  - pytest（`uv run pytest`）
  - カバレッジ確認
- [x] 品質チェック結果の確認・修正（必要に応じて）
  - テストの `hasattr()` チェック削除
  - async generator の型定義を `AsyncGenerator[Any, None]` に修正
  - `scripts/__init__.py` 作成（mypy モジュール名重複エラー解消）

## Phase 6: ドキュメント更新

- [x] `/update-docs` スキルでサブエージェントに委譲
  - `CLAUDE.md` の Development Context 確認（軽微な修正のため更新不要と判断）
  - `docs/implementation-status.md` の完了済み機能一覧に追記
  - `docs/implementation-status.md` のステアリングディレクトリ一覧に `.steering/20260214-fix-agent-engine-proxy/` 追加
  - 関連ドキュメント（`docs/agent-architecture.md`）の確認（変更なし）

## Phase 7: PR作成

- [ ] コミット作成
  - コミットメッセージ: `fix(backend): Agent Engineプロキシのregister_operations未定義 + asyncメソッド呼び出し修正 (#131)`
- [ ] プッシュ
- [ ] `/create-pr` スキルで PR 作成
  - タイトル: `fix(backend): Agent Engineプロキシのregister_operations未定義 + asyncメソッド呼び出し修正 (#131)`
  - 本文: 修正内容のサマリー、テスト結果、デプロイ手順
  - `closes #131` を含める

## Phase 8: デプロイ確認（PR マージ後）

- [ ] PR マージ後、CD パイプラインが Agent Engine を自動更新することを確認
- [ ] Cloud Run バックエンドログでエラーが出力されないことを確認
- [ ] フロントエンドからメッセージ送信が成功することを確認

## Notes

- TDD原則に従い、テスト→実装の順序で進める
- 各実装完了時、該当するテストが Green になることを確認
- `# type: ignore` コメントは、動的なプロキシオブジェクトの性質上、必要に応じて残す
