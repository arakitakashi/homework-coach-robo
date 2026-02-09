# Task List - Phase 3: セッション管理の移行 (#54)

## Phase 1: 環境セットアップ

- [ ] 依存パッケージの確認（`google-cloud-aiplatform[agent_engines]`は既にインストール済み）
- [ ] 環境変数の確認（`AGENT_ENGINE_ID`, `GCP_PROJECT_ID`, `GCP_LOCATION`）
- [ ] 必要なディレクトリの作成（`scripts/`, `docs/`, `tests/integration/`）

## Phase 2: セッションファクトリ拡張（TDD）

### 2.1 テスト作成

- [ ] `tests/unit/services/adk/sessions/test_session_factory_migration.py` 作成
  - [ ] `test_should_use_managed_session_no_agent_engine_id()`: `AGENT_ENGINE_ID`未設定 → False
  - [ ] `test_should_use_managed_session_migrated_user()`: `MIGRATED_USER_IDS`に含まれる → True
  - [ ] `test_should_use_managed_session_percentage_below()`: ハッシュ < パーセンテージ → True
  - [ ] `test_should_use_managed_session_percentage_above()`: ハッシュ >= パーセンテージ → False
  - [ ] `test_should_use_managed_session_invalid_percentage()`: 不正値 → False
  - [ ] `test_create_session_service_with_user_id()`: ユーザーID指定でファクトリ動作確認

### 2.2 実装

- [ ] `app/services/adk/sessions/session_factory.py` 拡張
  - [ ] `should_use_managed_session(user_id)` 関数追加
  - [ ] `create_session_service(user_id)` のシグネチャ変更
  - [ ] `_create_vertex_ai_session_service()` ヘルパー関数追加
- [ ] `app/services/adk/sessions/__init__.py` にエクスポート追加

### 2.3 品質チェック

- [ ] ruff / mypy チェック通過
- [ ] 既存テスト回帰なし

## Phase 3: データ移行スクリプト（TDD）

### 3.1 FirestoreSessionService拡張（ヘルパーメソッド）

- [ ] テスト作成: `tests/unit/services/adk/sessions/test_firestore_session_service_helpers.py`
  - [ ] `test_list_all_session_ids()`: 全セッションID取得
- [ ] 実装: `FirestoreSessionService.list_all_session_ids()` 追加

### 3.2 移行スクリプトテスト

- [ ] テスト作成: `tests/integration/test_session_migration.py`
  - [ ] `test_migrate_sessions_success()`: 正常移行フロー
  - [ ] `test_migrate_sessions_dry_run()`: dry-run モード
  - [ ] `test_migrate_sessions_skip_missing()`: 存在しないセッションをスキップ
  - [ ] `test_migrate_sessions_retry_on_failure()`: 失敗時のリトライ

### 3.3 移行スクリプト実装

- [ ] `scripts/migrate_sessions.py` 作成
  - [ ] `migrate_sessions(dry_run)` 関数
  - [ ] 並列処理（`asyncio.gather()`、最大10並列）
  - [ ] エラーハンドリング（リトライ、ログ記録）
  - [ ] 進捗ログ出力（1000セッションごと）
  - [ ] CLI引数解析（`--dry-run`, `--verbose`）

### 3.4 品質チェック

- [ ] ruff / mypy チェック通過
- [ ] 統合テスト通過

## Phase 4: データ検証ツール（TDD）

### 4.1 テスト作成

- [ ] テスト作成: `tests/integration/test_session_validation.py`
  - [ ] `test_validate_sessions_all_matched()`: 全一致ケース
  - [ ] `test_validate_sessions_mismatch()`: 不一致検出
  - [ ] `test_sessions_match_function()`: `_sessions_match()`のロジック確認

### 4.2 検証ツール実装

- [ ] `scripts/validate_sessions.py` 作成
  - [ ] `validate_sessions()` 関数
  - [ ] `_sessions_match(firestore_data, vertex_data)` 比較ロジック
  - [ ] スコープ区切りの差分考慮（`{"app:": {...}}` vs `{"app:key": "value"}`）
  - [ ] レポート出力（JSON/Markdown形式）

### 4.3 品質チェック

- [ ] ruff / mypy チェック通過
- [ ] 統合テスト通過

## Phase 5: ロールバック手順書作成

- [ ] `docs/session-migration-rollback.md` 作成
  - [ ] 緊急ロールバック手順（5分以内で実行可能）
  - [ ] 環境変数削除 → サービス再起動 → 検証
  - [ ] データバックアップ手順
  - [ ] トラブルシューティングガイド

## Phase 6: エンドポイント統合（オプショナル）

### 6.1 dialogue_runner.py の user_id 伝搬

- [ ] テスト更新: `tests/unit/api/v1/test_dialogue_runner.py`
  - [ ] `user_id` がセッションファクトリに渡されることを確認
- [ ] 実装: `dialogue_runner.py` で `create_session_service(user_id)` 呼び出し

### 6.2 品質チェック

- [ ] ruff / mypy チェック通過
- [ ] 既存テスト回帰なし

## Phase 7: 統合テスト

- [ ] E2Eテスト: 段階的移行シナリオ
  - [ ] 0% → 既存動作維持
  - [ ] 10% → 10%のユーザーがマネージドセッション使用
  - [ ] 100% → 全ユーザーがマネージドセッション使用
- [ ] ロールバックテスト
  - [ ] 環境変数削除 → Firestoreにフォールバック確認

## Phase 8: 品質チェック

- [ ] コードレビュー（セルフレビュー）
- [ ] セキュリティレビュー（`/security-review` スキル使用）
- [ ] 全テスト通過: `uv run pytest tests/ -v`
- [ ] Lint通過: `uv run ruff check .`
- [ ] 型チェック通過: `uv run mypy .`
- [ ] テストカバレッジ確認（80%以上）: `uv run pytest tests/ --cov=app --cov-report=term-missing`
- [ ] ドキュメント更新
  - [ ] `CLAUDE.md` の Development Context 更新
  - [ ] `docs/implementation-status.md` の完了済み機能一覧に追加
  - [ ] `docs/agent-architecture.md` にセッション管理移行を追記

## Phase 9: デプロイ準備（本番前）

- [ ] 開発環境で移行スクリプト実行（`--dry-run`）
- [ ] データ検証ツールで整合性確認
- [ ] ロールバック手順のリハーサル
- [ ] デプロイ計画書の作成
  - [ ] Phase 1: 1% ロールアウト（1日監視）
  - [ ] Phase 2: 10% ロールアウト（1週間監視）
  - [ ] Phase 3: 50% ロールアウト（1週間監視）
  - [ ] Phase 4: 100% ロールアウト（本番移行完了）

## Phase 10: 完了サマリー

- [ ] `COMPLETED.md` 作成
  - [ ] 実装内容の要約
  - [ ] 発生した問題と解決方法
  - [ ] 今後の改善点
  - [ ] 学んだこと（Lessons Learned）
