# Task List - Infrastructure Deploy

## Phase 1: 前提条件の確認

- [x] GCPプロジェクトの確認
- [x] gcloud CLI認証の確認
- [x] terraform.tfvarsのプロジェクトID確認・更新

## Phase 2: Bootstrap実行

- [x] bootstrap/ディレクトリでterraform init
- [x] terraform plan確認
- [x] terraform apply実行
- [x] 出力値（state_bucket_name, enabled_apis）確認

## Phase 3: Dev環境デプロイ

- [x] environments/dev/ディレクトリでterraform init
- [x] terraform plan確認
- [x] terraform apply実行（既存リソースで変更なし）
- [x] 出力値確認（backend_url, frontend_url等）

## Phase 4: Secret値の設定

- [x] JWT Secretの生成と設定（既に設定済み）
- [x] Firebase Config（未設定だが現時点では任意）

## Phase 5: 動作確認

- [x] Cloud Runサービスの確認
- [x] Firestoreデータベースの確認
- [x] BigQueryデータセットの確認
- [x] Secret Managerの確認

## Phase 6: ドキュメント更新

- [x] COMPLETED.mdの作成
- [ ] CLAUDE.mdの更新（不要 - インフラ状態は既に最新）
