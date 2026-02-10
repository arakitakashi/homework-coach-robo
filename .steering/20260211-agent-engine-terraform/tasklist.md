# Task List - Agent Engine Terraform インフラ整備

## Phase 1: Terraform モジュール作成

- [x] agent_engine モジュールディレクトリ作成
- [x] main.tf - google_vertex_ai_reasoning_engine リソース定義
- [x] variables.tf - 変数定義（project_id, region, GCS URIs）
- [x] outputs.tf - 出力値定義（resource_name, engine_id）
- [x] README.md - モジュールドキュメント作成

## Phase 2: 環境統合

- [x] dev/main.tf - agent_engine モジュール追加
- [x] dev/main.tf - Cloud Run env vars に Agent Engine 出力値追加
- [x] dev/variables.tf - enable_agent_engine 変数追加
- [x] dev/variables.tf - 古い agent_engine_resource_name/id 変数削除
- [x] dev/terraform.tfvars - enable_agent_engine = true 設定
- [x] dev/terraform.tfvars - gcp_location = "us-central1" 設定

## Phase 3: Provider バージョンアップグレード

- [x] dev/main.tf - google provider >= 7.13.0 に更新
- [x] dev/main.tf - google-beta provider >= 7.13.0 に更新

## Phase 4: ドキュメント整備

- [x] modules/agent_engine/README.md - 完全なドキュメント作成
  - [x] 概要セクション
  - [x] 前提条件（GCS アーティファクト）
  - [x] 使用方法（変数・出力）
  - [x] デプロイ手順
  - [x] 更新手順
  - [x] トラブルシューティング
  - [x] 制限事項と今後の対応
  - [x] 参考資料リンク

- [x] steering/requirements.md - 要求仕様作成
- [x] steering/design.md - 設計ドキュメント作成
- [x] steering/tasklist.md - タスクリスト作成

## Phase 5: 実装状況更新

- [x] docs/implementation-status.md - 完了済み機能に追加
- [x] docs/implementation-status.md - ステアリングディレクトリ一覧に追加

## Phase 6: Git コミット

- [x] ファイルをステージング
- [x] コミットメッセージ作成
- [x] プッシュ

## Phase 7: Issue #98 作成

- [x] GitHub Issue #98 作成
  - [x] 背景説明
  - [x] 実装タスク（Phase 1-5）
  - [x] 技術調査項目
  - [x] 成功基準
  - [x] 参考資料

## Phase 8: 確認と検証

- [ ] terraform plan で構文エラーがないことを確認
- [ ] terraform apply でデプロイ成功を確認
- [ ] Cloud Run 環境変数が正しく設定されていることを確認
- [ ] Agent Engine ログが正常であることを確認

## 完了条件

- [x] すべての Terraform ファイルが作成・更新されている
- [x] ドキュメントが完備されている
- [x] Issue #98 がバックエンド実装の指針として利用可能
- [x] Git にコミット・プッシュされている
- [ ] terraform apply で正常にデプロイできる（検証待ち）
