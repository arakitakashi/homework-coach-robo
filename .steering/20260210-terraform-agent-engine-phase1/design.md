# Design - Terraform Agent Engine Phase 1

## アーキテクチャ概要

Phase 1では、Agent EngineのインフラをTerraformで管理する基盤を構築する。エージェント本体のデプロイは現行のPythonスクリプトを使用。

```
Terraform
├── API有効化（aiplatform.googleapis.com）
├── Cloud Run環境変数（プレースホルダー）
└── 将来の拡張ポイント（Phase 2）

Python スクリプト（現行）
└── Agent Engineへのエージェントデプロイ
```

---

## 技術選定

### 使用技術
- Terraform 1.5+
- Google Provider 5.0+
- `google_project_service` リソース（API有効化）
- `google_cloud_run_service` リソース（環境変数設定）

---

## 実装設計

### 1. API有効化

#### 変更ファイル
- `infrastructure/terraform/environments/dev/main.tf`

#### 実装
```hcl
resource "google_project_service" "required_apis" {
  for_each = toset([
    # 既存のAPI...
    "aiplatform.googleapis.com",  # 追加
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}
```

---

### 2. Cloud Run環境変数設定

#### 変更ファイル
- `infrastructure/terraform/modules/cloud_run/main.tf`
- `infrastructure/terraform/modules/cloud_run/variables.tf`

#### 実装

##### variables.tf（新規変数）
```hcl
variable "agent_engine_resource_name" {
  description = "Agent Engine リソース名（プレースホルダー）"
  type        = string
  default     = ""
}

variable "agent_engine_id" {
  description = "Agent Engine ID（プレースホルダー）"
  type        = string
  default     = ""
}
```

##### main.tf（環境変数追加）
```hcl
resource "google_cloud_run_service" "backend" {
  # 既存設定...

  template {
    spec {
      containers {
        # 既存環境変数...

        # Agent Engine環境変数（Phase 1）
        env {
          name  = "AGENT_ENGINE_RESOURCE_NAME"
          value = var.agent_engine_resource_name
        }

        env {
          name  = "AGENT_ENGINE_ID"
          value = var.agent_engine_id
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "GCP_LOCATION"
          value = var.location
        }
      }
    }
  }
}
```

##### environments/dev/main.tf（モジュール呼び出し更新）
```hcl
module "cloud_run" {
  source = "../../modules/cloud_run"

  # 既存パラメータ...

  # Agent Engine設定（Phase 1: プレースホルダー）
  agent_engine_resource_name = var.agent_engine_resource_name
  agent_engine_id            = var.agent_engine_id
}
```

---

### 3. 変数定義

#### environments/dev/variables.tf
```hcl
variable "agent_engine_resource_name" {
  description = "Agent Engine リソース名"
  type        = string
  default     = ""
}

variable "agent_engine_id" {
  description = "Agent Engine ID"
  type        = string
  default     = ""
}
```

#### environments/dev/terraform.tfvars（手動設定）
```hcl
# Phase 1: 空文字（Pythonスクリプトでデプロイ後に手動設定）
agent_engine_resource_name = ""
agent_engine_id            = ""
```

---

## ファイル構成

### 変更ファイル
```
infrastructure/terraform/
├── environments/dev/
│   ├── main.tf                    # API有効化追加、モジュール呼び出し更新
│   ├── variables.tf               # 新規変数追加
│   └── terraform.tfvars           # プレースホルダー値設定
└── modules/cloud_run/
    ├── main.tf                    # 環境変数追加
    └── variables.tf               # 新規変数追加
```

### 新規ファイル
なし（既存ファイルの修正のみ）

---

## 依存関係

### Terraform Providerバージョン
- `hashicorp/google`: ~> 5.0（既存）
- `hashicorp/google-beta`: ~> 5.0（既存）

### 新規依存なし
既存のProvider/Moduleで対応可能。

---

## エラーハンドリング

### 想定されるエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| API有効化エラー | 権限不足 | サービスアカウントに`roles/serviceusage.admin`を付与 |
| Cloud Run更新エラー | 環境変数の型不整合 | `type = string`を確認 |
| Plan時の差分検出 | 既存環境変数との競合 | 既存設定を確認、必要に応じて統合 |

---

## セキュリティ考慮事項

### 環境変数の扱い
- **プレースホルダー値**: 空文字（実際のリソース名は後から設定）
- **シークレット情報**: 含まない（リソース名はシークレットではない）
- **terraform.tfvars**: `.gitignore`で管理（既存設定）

---

## パフォーマンス考慮事項

### Terraform実行時間
- API有効化: 約30秒〜1分
- Cloud Run更新: 約1〜2分
- **合計**: 約2〜3分

### 影響範囲
- Cloud Run再デプロイが発生（環境変数追加時）
- ダウンタイム: 0秒（ローリングアップデート）

---

## テスト計画

### 1. Plan検証
```bash
terraform plan
# 期待: API追加、Cloud Run環境変数追加のみ
# 期待: 既存リソースの削除・再作成なし
```

### 2. Apply実行
```bash
terraform apply
```

### 3. 環境変数確認
```bash
gcloud run services describe homework-coach-backend \
  --region=asia-northeast1 \
  --format='value(spec.template.spec.containers[0].env)'
```

期待される出力：
```
AGENT_ENGINE_RESOURCE_NAME=
AGENT_ENGINE_ID=
GCP_PROJECT_ID=homework-coach-robo
GCP_LOCATION=us-central1
```

---

## Phase 2への移行パス

### Phase 2で実装予定
1. **Agent Engineモジュール作成**
   ```
   modules/agent_engine/
   ├── main.tf
   ├── variables.tf
   └── outputs.tf
   ```

2. **`google_vertex_ai_reasoning_engine`リソース使用**
   - エージェントコードのデプロイをTerraformで管理

3. **Terraform Data Sourceでリソース名取得**
   ```hcl
   data "google_vertex_ai_reasoning_engine" "existing" {
     name = "projects/.../agents/..."
   }
   ```

4. **CI/CD統合**
   - Cloud BuildでTerraform実行
   - エージェントコード変更時に自動apply

---

## 代替案と採用理由

### 代替案1: 完全Terraform化（Phase 2相当）
**メリット**: 完全なIaC
**デメリット**: 実装時間増、エージェントコードのシリアライゼーション課題

**不採用理由**: Phase 1はクイックウィン重視。基盤構築を優先。

### 代替案2: 現状維持（Pythonスクリプトのみ）
**メリット**: 変更なし
**デメリット**: 手動運用、再現性低い

**不採用理由**: IaCの恩恵を受けられない。

### 採用理由（ハイブリッドアプローチ）
- 短期間で基盤構築
- 段階的移行でリスク低減
- 将来のPhase 2へのスムーズな移行
