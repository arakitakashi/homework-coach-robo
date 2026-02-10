# Design - Agent Engine Terraform インフラ整備

## アーキテクチャ概要

Agent Engine を Terraform で管理し、バックエンドが Agent Engine 内蔵のセッション管理を利用できるようにインフラを整備する。

```
┌─────────────────────────────────────────────┐
│ Terraform (dev環境)                          │
│                                             │
│ ┌─────────────────────┐                    │
│ │ module.agent_engine │                    │
│ │                     │                    │
│ │ ┌─────────────────┐ │                    │
│ │ │ Reasoning       │ │                    │
│ │ │ Engine          │ │                    │
│ │ │ (pickle.pkl)    │ │                    │
│ │ └─────────────────┘ │                    │
│ │                     │                    │
│ │ GCS Artifacts:      │                    │
│ │ - pickle.pkl        │                    │
│ │ - requirements.txt  │                    │
│ │ - dependencies.tar  │                    │
│ └─────────────────────┘                    │
│           │                                 │
│           │ outputs                         │
│           ↓                                 │
│ ┌─────────────────────┐                    │
│ │ module.cloud_run    │                    │
│ │ (backend)           │                    │
│ │                     │                    │
│ │ env:                │                    │
│ │ - AGENT_ENGINE_     │                    │
│ │   RESOURCE_NAME     │                    │
│ │ - AGENT_ENGINE_ID   │                    │
│ │ - GCP_LOCATION      │                    │
│ └─────────────────────┘                    │
└─────────────────────────────────────────────┘
```

## 技術選定

### Terraform Provider

- **google**: >= 7.13.0（google_vertex_ai_reasoning_engine サポート）
- **google-beta**: >= 7.13.0（ベータ機能アクセス）

### Agent Engine 設定

- **リージョン**: us-central1（Agent Engine 利用可能リージョン）
- **Python バージョン**: 3.10
- **フレームワーク**: google-adk

## モジュール構成

### agent_engine モジュール

**ファイル**: `infrastructure/terraform/modules/agent_engine/`

#### main.tf
```hcl
resource "google_vertex_ai_reasoning_engine" "homework_coach_agent" {
  provider = google-beta

  display_name = var.display_name
  description  = var.description
  region       = var.region
  project      = var.project_id

  spec {
    agent_framework = "google-adk"

    package_spec {
      pickle_object_gcs_uri    = var.pickle_gcs_uri
      requirements_gcs_uri     = var.requirements_gcs_uri
      dependency_files_gcs_uri = var.dependencies_gcs_uri
      python_version           = var.python_version
    }
  }
}
```

#### outputs.tf
- `resource_name`: フルリソース名
- `engine_id`: エージェント ID
- `display_name`: 表示名
- `region`: リージョン

#### variables.tf
- `project_id`: プロジェクト ID
- `region`: デプロイ先リージョン
- `display_name`: 表示名
- `description`: 説明
- `pickle_gcs_uri`: pickle ファイルの GCS URI
- `requirements_gcs_uri`: requirements.txt の GCS URI
- `dependencies_gcs_uri`: dependencies.tar.gz の GCS URI
- `python_version`: Python バージョン

## 環境統合

### dev/main.tf

```hcl
module "agent_engine" {
  source = "../../modules/agent_engine"
  count  = var.enable_agent_engine ? 1 : 0

  project_id           = var.project_id
  region               = var.gcp_location
  pickle_gcs_uri       = "gs://homework-coach-assets-{suffix}/agent-engine/pickle.pkl"
  requirements_gcs_uri = "gs://homework-coach-assets-{suffix}/agent-engine/requirements.txt"
  dependencies_gcs_uri = "gs://homework-coach-assets-{suffix}/agent-engine/dependencies.tar.gz"

  depends_on = [google_project_service.required_apis, module.cloud_storage]
}
```

### Cloud Run 環境変数統合

```hcl
backend_env_vars = merge(
  # ... 既存の env vars ...
  var.enable_agent_engine ? {
    AGENT_ENGINE_RESOURCE_NAME = module.agent_engine[0].resource_name
    AGENT_ENGINE_ID            = module.agent_engine[0].engine_id
    GCP_LOCATION               = var.gcp_location
  } : {},
)
```

### variables.tf

```hcl
variable "enable_agent_engine" {
  description = "Enable Agent Engine deployment via Terraform"
  type        = bool
  default     = false
}
```

### terraform.tfvars

```hcl
enable_agent_engine = true
gcp_location        = "us-central1"
```

## デプロイフロー

```
1. アーティファクト準備
   ├─ backend/scripts/serialize_agent.py
   │  └─ pickle.pkl 生成
   ├─ tar -czf dependencies.tar.gz app/
   └─ gcloud storage cp ... (GCS アップロード)

2. Terraform デプロイ
   ├─ terraform init -upgrade (Provider 更新)
   ├─ terraform plan
   └─ terraform apply
      ├─ Agent Engine 作成
      └─ Cloud Run 環境変数更新

3. 確認
   ├─ gcloud logging read (ログ確認)
   └─ curl (API テスト)
```

## エラーハンドリング

### セッション削除エラー

**問題**: Agent Engine 削除時に子リソース（sessions）が存在
**対策**: force=true フラグで API 経由削除

```bash
curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/${RESOURCE_NAME}?force=true"
```

### Provider バージョンエラー

**問題**: google_vertex_ai_reasoning_engine リソースが認識されない
**対策**: Provider >= 7.13.0 にアップグレード

```bash
terraform init -upgrade
```

## セキュリティ考慮事項

1. **GCS アクセス権限**
   - Agent Engine は既存の assets バケットにアクセス
   - Backend service account が読み取り権限を持つ

2. **環境変数**
   - AGENT_ENGINE_RESOURCE_NAME は公開情報（セキュリティリスクなし）
   - 実行時認証は GCP IAM で制御

3. **依存関係**
   - dependencies.tar.gz にアプリケーションコードを含む
   - 機密情報は含まない（環境変数・Secret Manager で管理）

## パフォーマンス考慮事項

- Agent Engine はマネージドサービスで自動スケーリング
- コールドスタート対策は不要（常時稼働）
- セッション管理は Agent Engine 内蔵機能を利用（Firestore より高速）

## 代替案と採用理由

### 代替案1: Python SDK で動的デプロイ

```python
from vertexai import agent_engines
agent_engines.create(...)
```

**不採用理由**:
- IaC 原則に反する
- 手動デプロイが必要
- 状態管理が困難

### 採用案: Terraform モジュール

**採用理由**:
- ✅ IaC 原則に準拠
- ✅ 宣言的な設定
- ✅ 状態管理が容易
- ✅ バージョン管理可能
- ✅ CI/CD 統合が容易

## 今後の拡張

1. **本番環境対応**
   - prod 環境設定の追加
   - 本番用 GCS バケット

2. **マルチリージョン対応**
   - リージョン変数の柔軟化
   - フェイルオーバー構成

3. **モニタリング統合**
   - Cloud Monitoring アラート
   - ログベース メトリクス
