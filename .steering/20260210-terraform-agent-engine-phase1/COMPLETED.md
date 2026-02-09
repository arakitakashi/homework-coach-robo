# COMPLETED - Terraform Agent Engine Phase 1

**完了日**: 2026-02-10
**ブランチ**: `feature/terraform-agent-engine-phase1`

---

## 実装内容の要約

Phase 3のAgent EngineインフラをTerraformで管理する基盤を構築しました。エージェント本体のデプロイは引き続きPythonスクリプトを使用し、環境変数とAPI有効化をTerraformで管理します。

---

## 実装の詳細

### 変更ファイル

#### 1. `infrastructure/terraform/environments/dev/variables.tf`
**追加内容**:
- `agent_engine_resource_name`: Agent Engineリソース名（デフォルト: 空文字）
- `agent_engine_id`: Agent Engine ID（デフォルト: 空文字）
- `gcp_location`: GCPロケーション（デフォルト: us-central1）

```hcl
variable "agent_engine_resource_name" {
  description = "Agent Engine resource name (empty for local runner)"
  type        = string
  default     = ""
}

variable "agent_engine_id" {
  description = "Agent Engine ID (empty for local runner)"
  type        = string
  default     = ""
}

variable "gcp_location" {
  description = "GCP location for Agent Engine (default: us-central1)"
  type        = string
  default     = "us-central1"
}
```

#### 2. `infrastructure/terraform/environments/dev/main.tf`
**追加内容**:
- Cloud Run `backend_env_vars`にAgent Engine環境変数を追加
- 条件付きで環境変数を設定（`agent_engine_resource_name`が空文字でない場合のみ）

```hcl
# Phase 3: Agent Engine configuration
var.agent_engine_resource_name != "" ? {
  AGENT_ENGINE_RESOURCE_NAME = var.agent_engine_resource_name
  AGENT_ENGINE_ID            = var.agent_engine_id
  GCP_LOCATION               = var.gcp_location
} : {},
```

---

## API有効化

`aiplatform.googleapis.com`は**既に有効化済み**でした（`main.tf`の51行目）。追加の作業は不要です。

---

## テスト結果

### ✅ Terraform Format
```bash
terraform fmt .
```
→ 成功（フォーマット適用）

### ✅ Terraform Init
```bash
terraform init -backend=false
```
→ 成功（プロバイダー初期化完了）

### ✅ Terraform Validate
```bash
terraform validate
```
→ **Success! The configuration is valid.**

---

## デプロイフロー（Phase 1完了後の手順）

### Step 1: Terraform適用（既存環境）
```bash
cd infrastructure/terraform/environments/dev
terraform plan  # 環境変数追加のみ確認
terraform apply # Cloud Run更新
```

**期待される変更**:
- Cloud Run backend サービスに環境変数追加（値は空文字）
- 既存リソースの削除・再作成なし

### Step 2: Pythonスクリプトでエージェントデプロイ
```bash
cd backend
uv run python scripts/deploy_agent_engine.py \
  --project homework-coach-robo \
  --location us-central1 \
  --bucket homework-coach-assets-4592ba87
```

**出力例**:
```
Deployment successful!
  Resource name: projects/12345/locations/us-central1/reasoningEngines/67890
  Engine ID: 67890

Set the following environment variables:
  export AGENT_ENGINE_RESOURCE_NAME=projects/12345/locations/us-central1/reasoningEngines/67890
  export AGENT_ENGINE_ID=67890
```

### Step 3: Terraform変数を更新
```bash
cd infrastructure/terraform/environments/dev

# terraform.tfvars に実際の値を追記
cat >> terraform.tfvars <<EOF
# Phase 3: Agent Engine
agent_engine_resource_name = "projects/12345/locations/us-central1/reasoningEngines/67890"
agent_engine_id            = "67890"
gcp_location               = "us-central1"
EOF

# 再度適用
terraform plan   # 環境変数の値更新のみ
terraform apply
```

### Step 4: 動作確認
```bash
# バックエンド環境変数を確認
gcloud run services describe homework-coach-backend \
  --region=asia-northeast1 \
  --format='value(spec.template.spec.containers[0].env)' | \
  grep AGENT_ENGINE

# テストスクリプトで動作確認
cd backend
uv run python scripts/test_agent_engine.py \
  --resource-name projects/12345/locations/us-central1/reasoningEngines/67890
```

---

## 環境変数の動作

### デフォルト（Phase 1完了直後）
```hcl
agent_engine_resource_name = ""  # 空文字
agent_engine_id            = ""  # 空文字
```

→ Cloud Runに環境変数は**追加されない**（条件分岐により）
→ バックエンドは**ローカルRunner**を使用

### Pythonスクリプトでデプロイ後
```hcl
agent_engine_resource_name = "projects/.../reasoningEngines/..."
agent_engine_id            = "67890"
gcp_location               = "us-central1"
```

→ Cloud Runに環境変数が追加される
→ バックエンドは**Agent Engine経由**で実行

---

## 影響範囲

### 変更あり
- `infrastructure/terraform/environments/dev/variables.tf` - 3変数追加
- `infrastructure/terraform/environments/dev/main.tf` - `backend_env_vars`に条件付き環境変数追加

### 変更なし
- Cloud Runモジュール（`modules/cloud_run/`）- 既存の`backend_env_vars`を使用
- Dockerfile、GitHub Actions - 変更不要
- バックエンドコード - 変更不要

---

## Phase 2への移行パス

Phase 1完了後、以下を検討：

### Phase 2a: Terraformモジュール化
```
infrastructure/terraform/modules/agent_engine/
├── main.tf
├── variables.tf
└── outputs.tf
```

### Phase 2b: `google_vertex_ai_reasoning_engine`リソース使用
- エージェントコードのTerraformデプロイ
- cloudpickleシリアライゼーション自動化

### Phase 2c: CI/CD統合
- Cloud BuildでTerraform実行
- エージェントコード変更時に自動デプロイ

---

## 学んだこと（Lessons Learned）

### 1. 既存インフラの活用
`backend_env_vars`という汎用的な環境変数マップが既に存在していたため、新規変数を追加する必要がなく、シンプルに実装できた。

### 2. 条件付き環境変数
`var.agent_engine_resource_name != "" ?`の条件分岐により、Agent Engineを使用しない環境（ローカル開発）でも同じTerraform設定を使用できる。

### 3. 段階的移行の重要性
Phase 1（基盤構築）とPhase 2（完全Terraform化）を分離することで、リスクを低減しながら段階的に移行できる。

---

## コミット情報

```
commit [pending]

feat(terraform): add Agent Engine Phase 1 infrastructure

Terraformで Agent Engine 環境変数を管理する基盤を構築。

変更内容:
- Agent Engine関連の変数追加（resource_name, id, location）
- Cloud Run backend_env_varsに条件付き環境変数追加
- aiplatform.googleapis.com は既に有効化済み

テスト:
- terraform fmt: ✅
- terraform init: ✅
- terraform validate: ✅
```

---

**ステータス**: ✅ 完了・テスト済み・PR準備完了
