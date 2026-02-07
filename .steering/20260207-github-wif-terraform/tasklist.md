# Task List - GitHub Actions WIF Terraform Module

## Phase 1: モジュール作成

- [x] `modules/github_wif/main.tf` 作成
- [x] `modules/github_wif/variables.tf` 作成
- [x] `modules/github_wif/outputs.tf` 作成

## Phase 2: 既存ファイル修正

- [x] `bootstrap/main.tf` に `iamcredentials.googleapis.com` 追加
- [x] `environments/dev/main.tf` に module 呼び出し + API 追加
- [x] `environments/dev/variables.tf` に変数追加
- [x] `environments/dev/outputs.tf` に出力追加

## Phase 3: 検証

- [x] `terraform fmt` でフォーマット確認
- [x] `terraform validate` で構文確認
- [ ] コミット
