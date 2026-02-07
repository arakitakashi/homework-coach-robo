# Task List - Infrastructure Phase 2 Update

## Phase 1: API有効化

- [x] bootstrap/main.tf に discoveryengine.googleapis.com 追加
- [x] environments/dev/main.tf に discoveryengine.googleapis.com 追加

## Phase 2: モジュール更新

- [x] IAM: variables.tf に feature flag 追加
- [x] IAM: main.tf に条件付きIAMロール追加
- [x] Secret Manager: variables.tf に feature flag 追加
- [x] Secret Manager: main.tf に gemini-api-key シークレット追加
- [x] Secret Manager: outputs.tf に output 追加
- [x] Firestore: variables.tf に feature flag 追加
- [x] Firestore: indexes.tf に5インデックス追加
- [x] BigQuery: variables.tf に feature flag 追加
- [x] BigQuery: tables.tf に3テーブル追加
- [x] BigQuery: outputs.tf に output 追加
- [x] Cloud Run: variables.tf に env_vars 変数追加
- [x] Cloud Run: main.tf に dynamic env ブロック追加

## Phase 3: 環境レベル配線

- [x] environments/dev/variables.tf に feature flag 変数追加
- [x] environments/dev/main.tf にモジュール配線追加
- [x] environments/dev/outputs.tf に Phase 2 output 追加

## Phase 4: 検証

- [x] terraform validate 成功確認
- [ ] コミット
