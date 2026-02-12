# Task List - GCS Permissions Fix for Agent Engine Deployment

## Phase 1: Terraform 修正

- [x] `modules/cloud_storage/variables.tf` に `github_actions_service_account_email` 変数追加
- [x] `modules/cloud_storage/main.tf` に IAM バインディング追加
- [x] `environments/dev/main.tf` に引数追加

## Phase 2: CD Workflow 修正

- [x] `.github/workflows/cd.yml` のバケット名取得を Secret 参照に変更

## Phase 3: 検証

- [x] `terraform init -backend=false && terraform validate` 成功確認

## Phase 4: 品質チェック

- [x] セルフコードレビュー
- [ ] ドキュメント更新確認
