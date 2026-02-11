# Issue: Agent Engine RESOURCE_NAME 環境変数の値が不正

## 問題の概要

Cloud Run Backend の環境変数 `AGENT_ENGINE_RESOURCE_NAME` に設定されている値が不正で、Agent Engine クライアントの初期化に失敗しています。

## 現状

### 環境変数の値（誤り）

```
AGENT_ENGINE_RESOURCE_NAME=5984689068984762368
```

この値は **ID のみ** で、`google_vertex_ai_reasoning_engine` リソースの `.name` プロパティから取得されています。

### 必要な形式（正しい）

```
AGENT_ENGINE_RESOURCE_NAME=projects/homework-coach-robo/locations/us-central1/reasoningEngines/5984689068984762368
```

完全なリソース名が必要です。これは `.id` プロパティから取得できます。

## 根本原因

Google Provider の `google_vertex_ai_reasoning_engine` リソースでは：
- `.name` プロパティ = **ID のみ**（例: `5984689068984762368`）
- `.id` プロパティ = **完全なリソース名**（例: `projects/.../locations/.../reasoningEngines/...`）

`modules/agent_engine/outputs.tf` で `.name` を使用していたため、ID のみが返され環境変数に設定されていました。

## エラーの症状

`dialogue_runner.py:60` の `get_agent_engine_client` で以下のエラーが発生：

```python
agent_engines.get(resource_name)  # resource_name="598468906898476236  8" (ID のみ)
```

`agent_engines.get()` は完全なリソース名を期待しているため、エラーが発生し、ローカル Runner にフォールバックします。しかし、ローカル Runner も Vertex AI 認証情報が不足しているため失敗：

```
ValueError: Missing key inputs argument!
To use the Google AI API, provide (`api_key`) arguments.
To use the Google Cloud API, provide (`vertexai`, `project` & `location`) arguments.
```

## 実施済みの修正

### 1. modules/agent_engine/outputs.tf

**修正内容**: `.name` → `.id` に変更

```diff
 output "resource_name" {
   description = "The full resource name of the Agent Engine"
-  value       = google_vertex_ai_reasoning_engine.homework_coach_agent.name
+  value       = google_vertex_ai_reasoning_engine.homework_coach_agent.id
 }
```

### 2. environments/dev/outputs.tf

**追加内容**: Agent Engine の outputs を追加

```hcl
# Phase 3: Agent Engine outputs
output "agent_engine_resource_name" {
  description = "The full resource name of the Agent Engine (if created)"
  value       = var.enable_agent_engine ? module.agent_engine[0].resource_name : null
}

output "agent_engine_id" {
  description = "The ID of the Agent Engine (if created)"
  value       = var.enable_agent_engine ? module.agent_engine[0].engine_id : null
}

output "agent_engine_display_name" {
  description = "The display name of the Agent Engine (if created)"
  value       = var.enable_agent_engine ? module.agent_engine[0].display_name : null
}
```

**summary にも追加**:

```hcl
# Phase 3: Agent Engine
agent_engine_enabled = var.enable_agent_engine
```

## 残りの作業

### Cloud Run Backend の環境変数を更新

**問題**: 上記の修正だけでは Cloud Run の環境変数は更新されません。Terraform は outputs の変更だけでは plan/apply で変更を検出しないためです。

**解決方法**: Cloud Run backend リソースを強制的に更新して、正しい環境変数値を反映させる必要があります。

#### オプション 1: terraform apply -replace（推奨）

```bash
cd infrastructure/terraform/environments/dev
terraform apply -replace="module.cloud_run.google_cloud_run_v2_service.backend"
```

**影響**:
- Cloud Run backend サービスが再作成される
- 数分間のダウンタイムが発生する可能性がある
- 環境変数が正しい値に更新される

#### オプション 2: main.tf で完全なリソース名を構築

`main.tf` の `backend_env_vars` で、完全なリソース名を構築する：

```hcl
backend_env_vars = merge(
  {
    // ... 既存の環境変数 ...
  },
  var.enable_agent_engine ? {
    AGENT_ENGINE_RESOURCE_NAME = "projects/${var.project_id}/locations/${var.gcp_location}/reasoningEngines/${module.agent_engine[0].engine_id}"
    AGENT_ENGINE_ID            = module.agent_engine[0].engine_id
    GCP_LOCATION               = var.gcp_location
  } : {},
)
```

この方法なら、terraform plan で変更が検出され、Cloud Run backend が更新されます。

## 検証方法

修正後、以下で確認：

```bash
# 環境変数の確認
gcloud run services describe homework-coach-backend \
  --region=asia-northeast1 \
  --format=json | jq -r '.spec.template.spec.containers[0].env[] | select(.name == "AGENT_ENGINE_RESOURCE_NAME") | "AGENT_ENGINE_RESOURCE_NAME=\(.value)"'

# 期待される出力
AGENT_ENGINE_RESOURCE_NAME=projects/homework-coach-robo/locations/us-central1/reasoningEngines/5984689068984762368
```

本番ログで Agent Engine が正常に動作していることを確認：

```bash
gcloud run services logs read homework-coach-backend \
  --region=asia-northeast1 \
  --limit=50 | grep -E "(Agent Engine|AGENT_ENGINE|dialogue_runner)"
```

## 関連ファイル

- `infrastructure/terraform/modules/agent_engine/outputs.tf` - ✅ 修正済み（`.name` → `.id`）
- `infrastructure/terraform/environments/dev/outputs.tf` - ✅ 修正済み（Agent Engine outputs 追加）
- `infrastructure/terraform/environments/dev/main.tf` - ⏳ 要確認（backend_env_vars の修正が必要な場合）
- `backend/app/api/v1/dialogue_runner.py` - 確認済み（問題なし）
- `backend/app/services/adk/runner/agent_engine_client.py` - 確認済み（問題なし）

## Priority

🔴 P0 - Critical

Agent Engine が完全に動作していない状態です。早急な修正が必要です。
