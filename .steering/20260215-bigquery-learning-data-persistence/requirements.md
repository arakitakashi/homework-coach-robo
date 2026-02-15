# Requirements - BigQuery学習データ永続化機能の実装

## 背景・目的

### 背景

現在のシステムでは、セッション中の学習データはFirestoreにリアルタイムで保存されていますが、長期的な学習分析やダッシュボード表示のためのデータウェアハウスへの永続化機能が実装されていません。

- **インフラ（Terraform）**: BigQueryデータセット、6つのテーブル定義が完全実装済み
- **設計（ドキュメント）**: `docs/functional-design.md` に `BigQueryDataService` の詳細設計が存在
- **実装（バックエンドコード）**: 未実装（Issue #164）

### 目的

学習セッション終了時に、Firestoreの一時データをBigQueryに永続化し、以下を実現する：

1. **長期的な学習データの保存**: Firestoreはリアルタイムデータ、BigQueryは分析用データとして役割分担
2. **学習統計の集計基盤**: ユーザーの学習履歴、傾向分析、成長トラッキングを可能にする
3. **将来のダッシュボード機能**: 保護者向け・児童向けの学習レポート機能の基盤を構築
4. **データガバナンス**: パーティショニング・クラスタリングによる効率的なクエリと費用最適化

---

## 要求事項

### 機能要件

#### FR-1: BigQueryDataService の実装

**優先度**: P0（MVP必須）

BigQueryへのデータ保存を担当するサービスクラスを実装する。

- `save_session_data()`: セッション終了時のデータ保存
- `save_learning_history()`: 学習履歴の記録
- `save_learning_profile_snapshot()`: 学習プロファイルのスナップショット保存
- エラーハンドリング、リトライロジック
- Pydanticスキーマバリデーション

#### FR-2: セッション終了時の保存処理統合

**優先度**: P0（MVP必須）

WebSocketハンドラまたはセッション管理サービスにBigQuery保存処理を統合する。

- セッション終了イベントをトリガーにBigQuery保存
- Firestoreとの連携（セッション中はFirestore、終了後にBigQuery）
- 非同期処理による保存（セッション終了応答をブロックしない）

#### FR-3: 統計取得API（Phase 2以降）

**優先度**: P1（将来対応）

ユーザーの学習統計を取得するAPI。

- `get_user_stats()`: ユーザー学習統計取得（集計クエリ）
- ダッシュボード用データ集計API
- Firestoreキャッシング（BigQueryクエリ結果をキャッシュ）

#### FR-4: Phase 2テーブル統合（マルチエージェント導入後）

**優先度**: P2（将来対応）

Phase 2で導入されるマルチエージェント機能に対応したテーブルへの保存。

- `agent_metrics`: エージェントのパフォーマンス追跡
- `emotion_analysis`: 音声トーン分析による感情記録
- `rag_metrics`: RAG検索のパフォーマンス追跡

### 非機能要件

#### NFR-1: パフォーマンス

- BigQuery保存処理は非同期実行（セッション終了応答を500ms以内に返す）
- バッチインサート使用（`insert_rows_json()`）
- リトライロジック（指数バックオフ、最大3回）

#### NFR-2: データ整合性

- Firestore → BigQuery のデータ整合性保証
- トランザクション境界の明確化
- 保存失敗時のログ記録とアラート

#### NFR-3: セキュリティ

- BigQueryクライアント認証はService Accountを使用
- Secret Managerからの認証情報取得
- 個人情報（PII）のログ出力禁止

#### NFR-4: テストカバレッジ

- ユニットテストカバレッジ80%以上
- 統合テスト（BigQuery Emulator使用）
- E2Eテスト（セッション終了→BigQuery保存の確認）

### 制約条件

#### 技術的制約

- **BigQueryクォータ**: 1日あたりのインサート上限に注意（バッチインサート使用で緩和）
- **BigQuery Emulator**: 本番環境との機能差異がある（ストリーミングインサート未対応）
- **既存コードへの影響最小化**: FirestoreSessionServiceの動作を変更しない

#### スコープ制約

- **Phase 1（MVP）**: 基本的な3テーブル（`dialogue_sessions`, `learning_history`, `learning_profile_snapshots`）のみ
- **Phase 2以降**: 統計取得API、Phase 2テーブル（`agent_metrics`, `emotion_analysis`, `rag_metrics`）は将来対応

---

## 対象範囲

### In Scope（Phase 1 - MVP）

- ✅ `google-cloud-bigquery` 依存関係の追加
- ✅ `BigQueryDataService` クラスの実装
  - `save_session_data()`
  - `save_learning_history()`
  - `save_learning_profile_snapshot()`
- ✅ セッション終了時のBigQuery保存統合（`dialogue_runner.py`）
- ✅ Pydanticスキーマバリデーション
- ✅ エラーハンドリング、リトライロジック
- ✅ ユニットテスト、統合テスト、E2Eテスト

### Out of Scope（Phase 2以降）

- ❌ 統計取得API（`get_user_stats()`）
- ❌ RESTエンドポイント（`GET /api/v1/users/{user_id}/stats`）
- ❌ Firestoreキャッシング
- ❌ Phase 2テーブル（`agent_metrics`, `emotion_analysis`, `rag_metrics`）への保存
- ❌ ダッシュボードUI

---

## 成功基準

### 必須（Must Have）

1. ✅ **セッション終了時にBigQueryに保存される**
   - `dialogue_sessions` テーブルにセッションデータが保存される
   - `learning_history` テーブルに学習履歴が保存される
   - `learning_profile_snapshots` テーブルにプロファイルスナップショットが保存される

2. ✅ **テストカバレッジ80%以上**
   - ユニットテスト（BigQueryDataService）
   - 統合テスト（BigQuery Emulator）
   - E2Eテスト（セッション終了フロー）

3. ✅ **エラーハンドリングが適切**
   - BigQuery保存失敗時のログ記録
   - リトライロジック（指数バックオフ）
   - セッション終了応答はブロックしない（非同期処理）

### 推奨（Should Have）

4. ✅ **パフォーマンス要件を満たす**
   - セッション終了応答が500ms以内
   - バッチインサート使用

5. ✅ **データ整合性が保証される**
   - Firestore → BigQuery のデータ整合性検証
   - トランザクション境界が明確

### オプション（Nice to Have）

6. ❌ **統計取得API（Phase 2）**
   - ユーザー学習統計取得
   - Firestoreキャッシング

---

## 参考資料

- **Issue**: [#164 BigQuery学習データ永続化機能の実装](https://github.com/arakitakashi/homework-coach-robo/issues/164)
- **設計書**: `docs/functional-design.md` セクション2.2.2（BigQueryDataService）
- **スキーマ**: `infrastructure/terraform/modules/bigquery/tables.tf`
- **既存実装**: `backend/app/services/adk/sessions/firestore_session_service.py`（参考パターン）
- **統合ポイント**: `backend/app/api/v1/dialogue_runner.py`（セッション終了フック）

---

## リスクと対策

| リスク | 影響度 | 発生確率 | 対策 |
|-------|--------|---------|------|
| BigQueryクォータ超過 | 高 | 中 | バッチインサート、エラーリトライ、ログ監視 |
| Firestore ↔ BigQuery 整合性 | 高 | 中 | トランザクション境界の明確化、リトライロジック |
| セッション終了検知のタイミング | 中 | 低 | WebSocket切断とセッション終了を区別 |
| BigQuery Emulator の制限 | 低 | 高 | 本番環境での動作確認、統合テストの充実 |

---

## スケジュール（目安）

| フェーズ | 期間 | 主要タスク |
|---------|------|-----------|
| Phase 1: 環境セットアップ | 0.5日 | 依存関係追加、ディレクトリ作成 |
| Phase 2: テスト実装（TDD） | 1日 | BigQueryDataServiceのテスト作成 |
| Phase 3: 実装 | 1.5日 | BigQueryDataService実装、セッション統合 |
| Phase 4: 統合テスト | 0.5日 | E2Eテスト実装・実行 |
| Phase 5: 品質チェック | 0.5日 | Lint、Type Check、カバレッジ確認 |

**合計**: 約4日

---

## 承認

- **作成者**: Claude Code
- **作成日**: 2026-02-15
- **レビュー者**: （ユーザー承認）
- **承認日**: （未承認）
