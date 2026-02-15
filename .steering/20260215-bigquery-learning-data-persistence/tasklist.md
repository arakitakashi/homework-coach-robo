# Task List - BigQuery学習データ永続化機能の実装

このタスクリストは、TDD原則（Red-Green-Refactor）に従って段階的に進めます。

---

## Phase 1: 環境セットアップ

### 1.1 依存関係の追加

- [ ] `backend/pyproject.toml` に `google-cloud-bigquery>=3.10.0` を追加
- [ ] `uv sync` で依存関係を更新
- [ ] 依存関係が正しくインストールされたことを確認

### 1.2 ディレクトリ構成の作成

- [ ] `backend/app/schemas/bigquery.py` ファイル作成（空ファイル）
- [ ] `backend/app/services/bigquery/` ディレクトリ作成
- [ ] `backend/app/services/bigquery/__init__.py` ファイル作成
- [ ] `backend/app/services/bigquery/bigquery_service.py` ファイル作成（空ファイル）
- [ ] `tests/unit/schemas/` ディレクトリ作成（存在しない場合）
- [ ] `tests/unit/services/bigquery/` ディレクトリ作成
- [ ] `tests/unit/services/bigquery/__init__.py` ファイル作成
- [ ] `tests/integration/` ディレクトリ確認（存在確認）

### 1.3 環境変数の確認

- [ ] `.env.example` にBigQuery関連の環境変数を追加（必要に応じて）
- [ ] ローカル開発用のService Accountキーファイル確認

---

## Phase 2: テスト実装（TDD - Red）

### 2.1 Pydanticスキーマのテスト作成

- [ ] `tests/unit/schemas/test_bigquery.py` 作成
  - [ ] `DialogueTurnBQ` バリデーションテスト
  - [ ] `DialogueSessionBQ` バリデーションテスト
  - [ ] `LearningHistoryBQ` バリデーションテスト
  - [ ] `SubjectUnderstandingBQ` バリデーションテスト
  - [ ] `LearningProfileSnapshotBQ` バリデーションテスト
  - [ ] 日時フィールドのシリアライゼーションテスト
  - [ ] `model_dump(mode="json")` の動作確認テスト

### 2.2 BigQueryDataService のテスト作成

- [ ] `tests/unit/services/bigquery/test_bigquery_service.py` 作成
  - [ ] `test_save_session_data_success` - 成功ケース
  - [ ] `test_save_session_data_failure` - 失敗時のエラーハンドリング
  - [ ] `test_save_session_data_retry` - リトライロジック
  - [ ] `test_save_learning_history_success` - 成功ケース
  - [ ] `test_save_learning_history_failure` - 失敗時のエラーハンドリング
  - [ ] `test_save_learning_profile_snapshot_success` - 成功ケース
  - [ ] `test_save_learning_profile_snapshot_failure` - 失敗時のエラーハンドリング
  - [ ] `test_save_all_success` - 一括保存の成功ケース
  - [ ] `test_save_all_partial_failure` - 一部失敗時の挙動

### 2.3 テスト実行（Red確認）

- [ ] `uv run pytest tests/unit/schemas/test_bigquery.py -v` 実行 → 失敗確認
- [ ] `uv run pytest tests/unit/services/bigquery/test_bigquery_service.py -v` 実行 → 失敗確認

---

## Phase 3: 実装（TDD - Green & Refactor）

### 3.1 Pydanticスキーマの実装

- [ ] `backend/app/schemas/bigquery.py` 実装
  - [ ] `DialogueTurnBQ` クラス
  - [ ] `DialogueSessionBQ` クラス
  - [ ] `LearningHistoryBQ` クラス
  - [ ] `SubjectUnderstandingBQ` クラス
  - [ ] `LearningProfileSnapshotBQ` クラス
  - [ ] 日時フィールドのシリアライゼーション設定

### 3.2 スキーマテスト実行（Green確認）

- [ ] `uv run pytest tests/unit/schemas/test_bigquery.py -v` 実行 → 全テスト通過確認

### 3.3 BigQueryDataService の実装

- [ ] `backend/app/services/bigquery/bigquery_service.py` 実装
  - [ ] `BigQueryDataService` クラス定義
  - [ ] `__init__()` メソッド（クライアント初期化）
  - [ ] `save_session_data()` メソッド（リトライデコレーター含む）
  - [ ] `save_learning_history()` メソッド（リトライデコレーター含む）
  - [ ] `save_learning_profile_snapshot()` メソッド（リトライデコレーター含む）
  - [ ] `save_all()` メソッド（一括保存）
  - [ ] エラーハンドリング、ログ出力

### 3.4 BigQueryDataService エクスポート

- [ ] `backend/app/services/bigquery/__init__.py` 実装
  - [ ] `BigQueryDataService` のエクスポート

### 3.5 BigQueryDataService テスト実行（Green確認）

- [ ] `uv run pytest tests/unit/services/bigquery/test_bigquery_service.py -v` 実行 → 全テスト通過確認

### 3.6 リファクタリング

- [ ] コード整理（重複排除、可読性向上）
- [ ] ログメッセージの統一
- [ ] 型ヒントの確認
- [ ] Docstringの追加・修正

### 3.7 リファクタリング後のテスト実行

- [ ] `uv run pytest tests/unit/services/bigquery/ -v` 実行 → 全テスト通過確認

---

## Phase 4: セッション終了時の統合

### 4.1 セッション終了フックのテスト作成

- [ ] `tests/unit/api/v1/test_dialogue_runner.py` にBigQuery保存テスト追加
  - [ ] `test_save_session_to_bigquery_success` - 成功ケース
  - [ ] `test_save_session_to_bigquery_session_not_found` - セッション未存在
  - [ ] `test_save_session_to_bigquery_failure` - 保存失敗時のログ確認
  - [ ] `test_save_session_to_bigquery_async` - 非同期処理の確認

### 4.2 セッション終了フックの実装

- [ ] `backend/app/api/v1/dialogue_runner.py` 修正
  - [ ] `BigQueryDataService` のインポート
  - [ ] `_save_session_to_bigquery()` メソッド実装
    - [ ] Firestoreからセッションデータ取得
    - [ ] BigQueryスキーマへの変換ロジック
    - [ ] `bigquery_service.save_all()` 呼び出し
    - [ ] エラーハンドリング
  - [ ] WebSocketハンドラの `finally` ブロックに統合
    - [ ] `asyncio.create_task()` で非同期実行

### 4.3 データ変換ロジックのテスト作成

- [ ] `tests/unit/converters/test_bigquery_converters.py` 作成（必要に応じて）
  - [ ] Firestore → BigQuery 変換ロジックのテスト
  - [ ] 対話ターンの変換テスト
  - [ ] タイムスタンプ変換テスト

### 4.4 データ変換ロジックの実装

- [ ] `backend/app/converters/bigquery_converters.py` 実装（必要に応じて）
  - [ ] `firestore_to_bigquery_session()` 関数
  - [ ] `firestore_to_bigquery_history()` 関数
  - [ ] `firestore_to_bigquery_snapshot()` 関数

### 4.5 統合テスト実行

- [ ] `uv run pytest tests/unit/api/v1/test_dialogue_runner.py -v` 実行 → 全テスト通過確認

---

## Phase 5: 統合テスト（BigQuery Emulator）

### 5.1 BigQuery Emulator セットアップ

- [ ] `docker-compose.yml` にBigQuery Emulator追加（必要に応じて）
- [ ] テスト用のデータセット・テーブル作成スクリプト

### 5.2 統合テストの作成

- [ ] `tests/integration/test_bigquery_integration.py` 作成
  - [ ] `test_save_session_data_e2e` - エンドツーエンドの保存・取得
  - [ ] `test_save_learning_history_e2e` - 学習履歴の保存・取得
  - [ ] `test_save_learning_profile_snapshot_e2e` - プロファイルの保存・取得
  - [ ] `test_query_with_partition` - パーティション活用クエリ
  - [ ] `test_query_with_clustering` - クラスタリング活用クエリ

### 5.3 統合テスト実行

- [ ] Docker Compose起動 → BigQuery Emulator起動確認
- [ ] `uv run pytest tests/integration/test_bigquery_integration.py -v` 実行 → 全テスト通過確認

---

## Phase 6: 品質チェック

### 6.1 リンター・フォーマッター

- [ ] `uv run ruff check app tests` 実行 → エラーなし確認
- [ ] `uv run ruff format app tests` 実行 → フォーマット適用

### 6.2 型チェック

- [ ] `uv run mypy .` 実行 → エラーなし確認
  - [ ] `app/` 配下の型エラー確認
  - [ ] `tests/` 配下の型エラー確認

### 6.3 テストカバレッジ

- [ ] `uv run pytest tests/ --cov=app --cov-report=term-missing` 実行
- [ ] カバレッジ80%以上を確認
- [ ] 未カバレッジ部分の確認と対応（必要に応じて）

### 6.4 セキュリティレビュー

- [ ] `/security-review` スキルを参照
- [ ] 個人情報（PII）のログ出力がないことを確認
- [ ] 認証情報のハードコードがないことを確認
- [ ] BigQueryクライアントのIAMロール確認

### 6.5 ドキュメント更新

- [ ] `/update-docs` スキルを使用してドキュメント更新
  - [ ] `CLAUDE.md` の Development Context 更新
  - [ ] `docs/implementation-status.md` の完了済み機能一覧に追記
  - [ ] `docs/implementation-status.md` のステアリングディレクトリ一覧に追記
  - [ ] `docs/functional-design.md` のBigQueryDataService実装済みマーク

---

## Phase 7: デプロイ準備（該当する場合）

### 7.1 環境変数の確認

- [ ] 本番環境のSecret Managerに認証情報が設定されていることを確認
- [ ] Cloud Runサービスアカウントの権限確認
  - [ ] `roles/bigquery.dataEditor` ロールが付与されていることを確認

### 7.2 デプロイ手順書の作成

- [ ] `.steering/20260215-bigquery-learning-data-persistence/DEPLOYMENT.md` 作成（必要に応じて）
  - [ ] デプロイ前チェックリスト
  - [ ] デプロイ手順
  - [ ] ロールバック手順
  - [ ] 動作確認手順

### 7.3 E2Eテスト（本番想定）

- [ ] ステージング環境でのE2Eテスト実行
- [ ] BigQueryコンソールでデータ確認
- [ ] ログ確認（Cloud Logging）

---

## Phase 8: 完了サマリー作成

### 8.1 COMPLETED.md 作成

- [ ] `.steering/20260215-bigquery-learning-data-persistence/COMPLETED.md` 作成
  - [ ] 実装内容の要約
  - [ ] 発生した問題と解決方法
  - [ ] 今後の改善点
  - [ ] 学んだこと（Lessons Learned）

### 8.2 PR作成

- [ ] `/create-pr` スキルを使用してPR作成
  - [ ] PR本文に Issue #164 へのリンク
  - [ ] `closes #164` を含める（マージ時に自動クローズ）
  - [ ] 実装内容のサマリー
  - [ ] テスト結果のサマリー

---

## チェックポイント

各Phaseの完了時に以下を確認：

### Phase 1 完了時

- [ ] 依存関係が正しくインストールされている
- [ ] ディレクトリ構成が作成されている

### Phase 2 完了時

- [ ] 全テストが失敗している（Red確認）
- [ ] テストコードが仕様を正しく表現している

### Phase 3 完了時

- [ ] 全テストが通過している（Green確認）
- [ ] リファクタリング後もテストが通過している

### Phase 4 完了時

- [ ] セッション終了時にBigQuery保存が実行される
- [ ] 非同期処理が正しく動作している

### Phase 5 完了時

- [ ] BigQuery Emulatorでのテストが通過している
- [ ] パーティション・クラスタリングが正しく動作している

### Phase 6 完了時

- [ ] リンター・型チェックがパスしている
- [ ] テストカバレッジ80%以上
- [ ] ドキュメントが最新

---

## 参考スキル

実装時に参照すべきスキル：

- `/tdd` - テスト駆動開発の原則
- `/fastapi` - FastAPIベストプラクティス
- `/security-review` - セキュリティチェック
- `/unit-test` - ユニットテスト実行（サブエージェント委譲）
- `/quality-check` - 品質チェック（サブエージェント委譲）
- `/update-docs` - ドキュメント更新（サブエージェント委譲）
- `/create-pr` - PR作成（サブエージェント委譲）

---

## 進捗管理

- **Phase 1**: 0/11 完了
- **Phase 2**: 0/16 完了
- **Phase 3**: 0/15 完了
- **Phase 4**: 0/10 完了
- **Phase 5**: 0/7 完了
- **Phase 6**: 0/10 完了
- **Phase 7**: 0/5 完了
- **Phase 8**: 0/2 完了

**全体進捗**: 0/76 完了 (0%)

---

## 承認

- **作成者**: Claude Code
- **作成日**: 2026-02-15
- **レビュー者**: （ユーザー承認）
- **承認日**: （未承認）
