# Design - Infrastructure Implementation

## アーキテクチャ概要

```
┌──────────────────────────────────────────────────────────────────┐
│                          GCP Project                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐                      │
│  │   Cloud Run     │    │   Cloud Run     │                      │
│  │   (Frontend)    │    │   (Backend)     │                      │
│  └────────┬────────┘    └────────┬────────┘                      │
│           │                      │                                │
│           │     ┌────────────────┴────────────────┐              │
│           │     │         VPC Connector           │              │
│           │     └────────────────┬────────────────┘              │
│           │                      │                                │
│  ┌────────┴────────────────────┬─┴───────────────────────┐       │
│  │                             │                          │       │
│  │  ┌─────────────┐   ┌───────┴───────┐   ┌───────────┐ │       │
│  │  │  Firestore  │   │ Memorystore   │   │  BigQuery │ │       │
│  │  │  (Native)   │   │   (Redis)     │   │           │ │       │
│  │  └─────────────┘   └───────────────┘   └───────────┘ │       │
│  │                                                       │       │
│  └───────────────────────────────────────────────────────┘       │
│                                                                   │
│  ┌─────────────────┐   ┌─────────────────┐                       │
│  │ Secret Manager  │   │ Cloud Storage   │                       │
│  └─────────────────┘   └─────────────────┘                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 技術選定

| コンポーネント | 技術 | 理由 |
|--------------|------|------|
| IaC | Terraform | GCP公式サポート、モジュール再利用性 |
| CI/CD | Cloud Build | GCPネイティブ統合 |
| Container Registry | Artifact Registry | GCR後継、推奨 |
| Compute | Cloud Run | サーバーレス、自動スケール |
| Database | Firestore Native | リアルタイム、スケーラブル |
| Cache | Memorystore Redis | マネージド、低レイテンシ |
| Analytics | BigQuery | 大規模分析、コスト効率 |

## ファイル構成

```
infrastructure/
├── terraform/
│   ├── shared/
│   │   ├── versions.tf       # Terraform/Provider バージョン
│   │   └── providers.tf      # Google Provider 設定
│   │
│   ├── modules/
│   │   ├── vpc/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── iam/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── secret_manager/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── firestore/
│   │   │   ├── main.tf
│   │   │   ├── indexes.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── bigquery/
│   │   │   ├── main.tf
│   │   │   ├── tables.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── redis/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── cloud_storage/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   └── cloud_run/
│   │       ├── main.tf
│   │       ├── iam.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   └── environments/
│       └── dev/
│           ├── main.tf
│           ├── variables.tf
│           ├── outputs.tf
│           ├── terraform.tfvars
│           └── backend.tf
│
├── docker/
│   ├── backend/
│   │   └── Dockerfile
│   └── frontend/
│       └── Dockerfile
│
└── cloud-build/
    ├── cloudbuild-backend.yaml
    ├── cloudbuild-frontend.yaml
    └── cloudbuild-infrastructure.yaml
```

## データ設計

### Firestore (docs/firestore-design.md 参照)

Native mode, asia-northeast1 リージョン

### BigQuery

**Dataset**: `homework_coach`

**Tables**:
1. `dialogue_sessions` - 対話セッション分析用
2. `learning_history` - 学習履歴分析用

パーティション: `created_at` カラムで日付パーティション

## Cloud Run 設定

| 項目 | Frontend | Backend |
|------|----------|---------|
| CPU | 1 | 2 |
| Memory | 512Mi | 1Gi |
| Min Instances (dev) | 0 | 0 |
| Min Instances (prod) | 1 | 1 |
| Max Instances | 10 | 20 |
| Timeout | 60s | 300s |
| Concurrency | 80 | 100 |

## セキュリティ考慮事項

1. **最小権限の原則**
   - 各サービス専用のサービスアカウント
   - 必要なロールのみ付与

2. **秘密情報管理**
   - 全ての秘密は Secret Manager で管理
   - Cloud Run は Secret Manager アクセス権限のみ

3. **ネットワーク分離**
   - Redis は VPC 内のみアクセス可能
   - VPC Connector 経由でのみ接続

4. **認証**
   - Cloud Run は認証必須（--no-allow-unauthenticated）
   - API Gateway またはIAP で公開アクセス制御（将来）

## 環境変数・シークレット

### Environment Variables (非機密)

```
ENVIRONMENT=dev|staging|production
GCP_PROJECT_ID=project-id
GCP_REGION=asia-northeast1
```

### Secrets (Secret Manager)

```
GOOGLE_APPLICATION_CREDENTIALS  # サービスアカウントキー（本番のみ）
REDIS_URL                       # Redis接続URL
DATABASE_URL                    # Firestore接続（自動設定）
```

## 代替案と採用理由

| 検討項目 | 採用 | 代替案 | 理由 |
|---------|------|-------|------|
| Compute | Cloud Run | GKE, App Engine | シンプル、コスト効率、自動スケール |
| IaC | Terraform | Pulumi, CDK | チーム習熟度、GCP公式サポート |
| CI/CD | Cloud Build | GitHub Actions | GCPリソースへの直接アクセス |
| Cache | Memorystore | Cloud Functions + Memory | マネージド、永続性 |
