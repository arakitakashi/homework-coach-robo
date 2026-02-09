# Requirements - Terraform Agent Engine Phase 1

## 背景・目的

### 現状の問題
- Agent EngineへのエージェントデプロイがPythonスクリプト（`deploy_agent_engine.py`）による手動実行
- 環境変数（`AGENT_ENGINE_RESOURCE_NAME`、`AGENT_ENGINE_ID`）が手動設定
- インフラとしてコード管理（IaC）されていない
- デプロイ状態がTerraform stateで管理されていない

### 目的
Agent EngineのインフラをTerraformで管理し、以下を実現する：
- インフラストラクチャとしてコード管理（IaC）
- 環境変数の自動設定
- デプロイ状態の追跡
- 再現可能なインフラ構築

---

## 要求仕様

### 機能要件

#### FR1: Agent Engine API有効化
- `aiplatform.googleapis.com`をTerraformで有効化
- 既存のAPI有効化リスト（`google_project_service.required_apis`）に追加

#### FR2: Cloud Run環境変数管理
- `AGENT_ENGINE_RESOURCE_NAME`（プレースホルダー値）
- `AGENT_ENGINE_ID`（プレースホルダー値）
- `GCP_PROJECT_ID`、`GCP_LOCATION`
- Cloud Runサービス（`homework-coach-backend`）に環境変数を追加

#### FR3: 段階的移行（Phase 1）
- ✅ API有効化とCloud Run環境変数設定
- ⚠️ エージェントデプロイは現行のPythonスクリプトを使用
- 🚧 完全Terraform化は将来（Phase 2）に実施

### 非機能要件

#### NFR1: 後方互換性
- 既存のTerraform構成を破壊しない
- `terraform plan`で意図しないリソース削除が発生しない

#### NFR2: ドキュメント
- README更新（Agent Engineデプロイ手順）
- Terraform変数のドキュメント化

#### NFR3: セキュリティ
- 環境変数にシークレット情報を含めない
- プレースホルダー値を使用（実際のリソース名は後から手動設定）

---

## 対象範囲

### In Scope（Phase 1）
- `infrastructure/terraform/environments/dev/main.tf`修正
  - Agent Engine API追加
  - Cloud Run環境変数追加（プレースホルダー）
- ドキュメント更新
  - README: Agent Engineデプロイ手順
  - CLAUDE.md: Terraform管理の記述追加

### Out of Scope（Phase 2以降）
- Terraformによるエージェントコードのデプロイ
- Cloud BuildとのCI/CD連携
- エージェントコード変更時の自動デプロイ
- Terraform Moduleの作成（`modules/agent_engine/`）

---

## 成功基準

1. ✅ `terraform plan`が成功する
2. ✅ Agent Engine API（`aiplatform.googleapis.com`）が有効化される
3. ✅ Cloud Run環境変数が設定される（プレースホルダー値）
4. ✅ 既存インフラに影響がない（意図しないリソース変更なし）
5. ✅ ドキュメントが更新される

---

## デプロイフロー（Phase 1完了後）

### Step 1: Terraform適用
```bash
cd infrastructure/terraform/environments/dev
terraform plan
terraform apply
```

### Step 2: Pythonスクリプトでエージェントデプロイ
```bash
cd backend
uv run python scripts/deploy_agent_engine.py \
  --project homework-coach-robo \
  --location us-central1 \
  --bucket homework-coach-assets-4592ba87
```

### Step 3: 環境変数更新（Terraformで反映）
```bash
# terraform.tfvars に実際の値を設定
echo 'agent_engine_resource_name = "projects/.../agents/..."' >> terraform.tfvars
echo 'agent_engine_id = "..."' >> terraform.tfvars

terraform apply
```

---

## 環境変数管理戦略

### プレースホルダー値（Phase 1）
```hcl
env {
  name  = "AGENT_ENGINE_RESOURCE_NAME"
  value = "" # 空文字（未設定）
}
env {
  name  = "AGENT_ENGINE_ID"
  value = "" # 空文字（未設定）
}
```

### 実際の値設定（Phase 1完了後）
- Pythonスクリプトでデプロイ後、手動で`terraform.tfvars`に追記
- `terraform apply`で反映

### 将来（Phase 2）
- Terraform Data Sourceで既存Agent Engineを参照
- または、Terraformで直接デプロイ

---

## Phase 2への移行パス

Phase 1完了後、以下を検討：
1. `modules/agent_engine/`モジュール作成
2. `google_vertex_ai_reasoning_engine`リソース使用
3. Cloud Buildと連携したCI/CD
4. エージェントコード変更時の自動デプロイ
