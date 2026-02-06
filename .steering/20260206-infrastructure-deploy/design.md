# Design - Infrastructure Deploy

## アーキテクチャ概要

```
GCP Project: homework-coach-robo (dev)
Region: asia-northeast1 (Tokyo)

┌─────────────────────────────────────────────────────────────┐
│ VPC Network                                                   │
│  ┌──────────────────┐    ┌──────────────────┐                │
│  │ VPC Connector    │    │ Private Service  │                │
│  │ (10.9.0.0/28)    │    │ Connection       │                │
│  └──────────────────┘    └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Cloud Run Services                                            │
│  ┌──────────────────┐    ┌──────────────────┐                │
│  │ Backend Service  │    │ Frontend Service │                │
│  │ - FastAPI + ADK  │    │ - Next.js 16     │                │
│  │ - CPU: 2, Mem: 1G│    │ - CPU: 1, Mem: 512M │             │
│  │ - Max: 20        │    │ - Max: 10        │                │
│  └──────────────────┘    └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Data Services                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                │
│  │ Firestore        │    │ BigQuery         │                │
│  │ - Sessions       │    │ - Analytics      │                │
│  │ - Memories       │    │ - Metrics        │                │
│  │ - App/User State │    │                  │                │
│  └──────────────────┘    └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Supporting Services                                           │
│  ┌──────────────────┐    ┌──────────────────┐                │
│  │ Secret Manager   │    │ Cloud Storage    │                │
│  │ - JWT Secret     │    │ - Assets Bucket  │                │
│  │ - Firebase Config│    │                  │                │
│  └──────────────────┘    └──────────────────┘                │
│  ┌──────────────────┐                                        │
│  │ Artifact Registry│                                        │
│  │ - Docker Images  │                                        │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

## デプロイ手順

### Phase 1: 前提条件の確認

1. GCPプロジェクトの確認
2. gcloud CLI認証の確認
3. terraform.tfvarsのプロジェクトID更新

### Phase 2: Bootstrap実行

```bash
cd infrastructure/terraform/bootstrap
terraform init
terraform plan
terraform apply
```

出力:
- state_bucket_name
- enabled_apis

### Phase 3: Dev環境デプロイ

```bash
cd ../environments/dev
terraform init  # GCS backendを使用
terraform plan
terraform apply
```

出力:
- backend_url
- frontend_url
- firestore_database_name
- bigquery_dataset_id
- assets_bucket_name

### Phase 4: Secret値の設定

```bash
# JWT Secret
gcloud secrets versions add homework-coach-jwt-secret \
  --data-file=<(openssl rand -base64 32)

# Firebase Config（必要に応じて）
gcloud secrets versions add homework-coach-firebase-config \
  --data-file=firebase-config.json
```

## 依存関係

```
Bootstrap (State Bucket + APIs)
    ↓
google_project_service (required_apis)
    ↓
    ├── module.vpc
    ├── module.iam
    ├── module.firestore
    └── module.bigquery
         ↓
    module.secret_manager
         ↓
    module.cloud_storage
         ↓
    module.cloud_run
```

## エラーハンドリング

| エラー | 対策 |
|--------|------|
| Firestore already exists | `terraform import` を実行 |
| API not enabled | Bootstrap を再実行 |
| Permission denied | IAM 権限を確認 |
| Quota exceeded | プロジェクト割り当てを確認 |

## セキュリティ考慮事項

- Service Accountは最小権限の原則に従う
- Secretの値はコードにハードコードしない
- Dev環境でもHTTPSを強制
