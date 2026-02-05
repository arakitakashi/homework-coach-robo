# COMPLETED - Infrastructure Implementation

**完了日**: 2026-02-05

## 実装内容の要約

GCP上に宿題コーチロボットのインフラストラクチャを構築するためのTerraformモジュールとCloud Buildパイプラインを実装しました。

### 作成したファイル

#### Terraform Shared Configuration
- `infrastructure/terraform/shared/versions.tf` - Terraform/Provider バージョン制約
- `infrastructure/terraform/shared/providers.tf` - Google Cloud Provider設定

#### Terraform Modules (8モジュール)

| モジュール | 説明 | ファイル |
|-----------|------|----------|
| vpc | VPC Network + VPC Access Connector | main.tf, variables.tf, outputs.tf |
| iam | Service Accounts + IAM Roles | main.tf, variables.tf, outputs.tf |
| secret_manager | Secret定義 + IAM Bindings | main.tf, variables.tf, outputs.tf |
| firestore | Firestore Database + Indexes | main.tf, indexes.tf, variables.tf, outputs.tf |
| bigquery | Dataset + Tables (3テーブル) | main.tf, tables.tf, variables.tf, outputs.tf |
| redis | Memorystore for Redis | main.tf, variables.tf, outputs.tf |
| cloud_storage | Assets Bucket + CDN設定 | main.tf, variables.tf, outputs.tf |
| cloud_run | Backend/Frontend Services | main.tf, iam.tf, variables.tf, outputs.tf |

#### Development Environment
- `infrastructure/terraform/environments/dev/backend.tf` - GCS State Backend
- `infrastructure/terraform/environments/dev/main.tf` - Root Module
- `infrastructure/terraform/environments/dev/variables.tf` - 変数定義
- `infrastructure/terraform/environments/dev/outputs.tf` - 出力定義
- `infrastructure/terraform/environments/dev/terraform.tfvars` - 開発環境設定

#### Docker Files
- `infrastructure/docker/backend/Dockerfile` - FastAPI + uv
- `infrastructure/docker/frontend/Dockerfile` - Next.js + Bun

#### Cloud Build Pipelines
- `infrastructure/cloud-build/cloudbuild-backend.yaml` - Backend Build & Deploy
- `infrastructure/cloud-build/cloudbuild-frontend.yaml` - Frontend Build & Deploy
- `infrastructure/cloud-build/cloudbuild-infrastructure.yaml` - Terraform Apply

## 検証結果

| 検証項目 | 結果 |
|---------|------|
| terraform init | ✅ 成功 |
| terraform validate | ✅ 成功 |
| terraform fmt -check | ✅ 成功（自動フォーマット適用） |

## 主要な設計判断

### 1. Cloud Run設定

| Service | CPU | Memory | Min | Max | Timeout |
|---------|-----|--------|-----|-----|---------|
| Frontend | 1 | 512Mi | 0 (dev) | 10 | 60s |
| Backend | 2 | 1Gi | 0 (dev) | 20 | 300s |

### 2. データサービス

- **Firestore**: Native mode, asia-northeast1, 6つのComposite Index
- **BigQuery**: `homework_coach` dataset, 3テーブル（日付パーティション）
- **Redis**: BASIC tier (dev), 1GB, PRIVATE_SERVICE_ACCESS

### 3. セキュリティ

- 各サービス専用のService Account
- 最小権限の原則に基づくIAM設計
- Secret ManagerによるCredentials管理
- VPC Connector経由のRedisアクセス

## 発生した問題と解決方法

### 問題1: Firestore Index - 最低2フィールド必須

**エラー**: `At least 2 "fields" blocks are required`

**解決**: `dialogue_turns_by_timestamp` indexにroleフィールドを追加

```hcl
fields {
  field_path = "role"
  order      = "ASCENDING"
}
fields {
  field_path = "timestamp"
  order      = "ASCENDING"
}
```

## 次のステップ

1. **GCPプロジェクト作成**
   - 開発環境用プロジェクトを作成
   - `terraform.tfvars` の `project_id` を更新

2. **必要なAPIの有効化**
   - terraform applyで自動的に有効化される

3. **Terraform State Bucket作成**
   ```bash
   gsutil mb -l asia-northeast1 gs://homework-coach-terraform-state
   gsutil versioning set on gs://homework-coach-terraform-state
   ```

4. **インフラのデプロイ**
   ```bash
   cd infrastructure/terraform/environments/dev
   terraform init
   terraform plan
   terraform apply
   ```

5. **Secret値の設定**
   - Redis URL等のシークレット値を手動で設定

6. **CI/CDトリガーの設定**
   - Cloud Build トリガーをGitHubリポジトリに接続

## Lessons Learned

1. **Firestore Index制約**: Composite indexには最低2つのフィールドが必要
2. **モジュール分割**: サービスごとに分割することで、依存関係が明確になり管理しやすい
3. **lifecycle ignore_changes**: Cloud RunのimageはCI/CDで更新するため、Terraform管理から除外
4. **VPC Private Service Access**: RedisへのアクセスにはVPC Connectorと合わせて設定が必要
