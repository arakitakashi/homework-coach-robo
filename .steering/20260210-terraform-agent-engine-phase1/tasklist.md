# Task List - Terraform Agent Engine Phase 1

## Phase 1: 環境セットアップ

- [x] ブランチ作成（`feature/terraform-agent-engine-phase1`）
- [x] ステアリングディレクトリ作成（`.steering/20260210-terraform-agent-engine-phase1/`）
- [x] requirements.md作成
- [x] design.md作成
- [x] tasklist.md作成

## Phase 2: Terraform実装

### 2.1: API有効化
- [ ] `infrastructure/terraform/environments/dev/main.tf`を修正
  - [ ] `aiplatform.googleapis.com`を`required_apis`に追加

### 2.2: Cloud Runモジュール変数追加
- [ ] `infrastructure/terraform/modules/cloud_run/variables.tf`を修正
  - [ ] `agent_engine_resource_name`変数追加
  - [ ] `agent_engine_id`変数追加

### 2.3: Cloud Run環境変数追加
- [ ] `infrastructure/terraform/modules/cloud_run/main.tf`を修正
  - [ ] `AGENT_ENGINE_RESOURCE_NAME`環境変数追加
  - [ ] `AGENT_ENGINE_ID`環境変数追加
  - [ ] `GCP_PROJECT_ID`環境変数追加
  - [ ] `GCP_LOCATION`環境変数追加

### 2.4: 環境設定変数追加
- [ ] `infrastructure/terraform/environments/dev/variables.tf`を修正
  - [ ] `agent_engine_resource_name`変数追加
  - [ ] `agent_engine_id`変数追加

### 2.5: モジュール呼び出し更新
- [ ] `infrastructure/terraform/environments/dev/main.tf`を修正
  - [ ] `module.cloud_run`の呼び出しに新変数を追加

## Phase 3: Terraformテスト

- [ ] `terraform fmt`実行（フォーマット）
- [ ] `terraform validate`実行（構文チェック）
- [ ] `terraform init`実行（プロバイダー初期化）
- [ ] `terraform plan`実行（差分確認）
  - [ ] API追加のみ確認
  - [ ] Cloud Run環境変数追加のみ確認
  - [ ] 既存リソースの削除・再作成がないことを確認

## Phase 4: ドキュメント更新

- [ ] README更新（Agent Engineデプロイ手順追記）
- [ ] CLAUDE.md更新（Terraform管理の記述追加）

## Phase 5: コミット

- [ ] 変更をステージング
- [ ] コミット作成

## Phase 6: 完了

- [ ] COMPLETED.md作成

---

## 注意事項

- **terraform apply は実行しない**（Phase 1では plan のみ）
- 実際のapplyは本番環境で慎重に実行
- プレースホルダー値（空文字）を使用
