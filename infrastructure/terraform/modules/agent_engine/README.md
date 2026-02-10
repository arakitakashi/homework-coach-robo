# Agent Engine Terraform Module

このモジュールは、Vertex AI Agent Engine（Reasoning Engine）をデプロイするためのTerraform設定を提供します。

## 概要

Agent Engineは、ADK（Agent Development Kit）で開発したエージェントを本番環境にデプロイ・管理・スケーリングするためのマネージドプラットフォームです。

## 前提条件

### GCS アーティファクト

デプロイ前に以下のファイルをGCSにアップロードする必要があります：

1. **pickle.pkl**: シリアライズされたエージェント
   ```bash
   cd backend
   uv run python scripts/serialize_agent.py
   gcloud storage cp pickle.pkl gs://homework-coach-assets-{suffix}/agent-engine/
   ```

2. **requirements.txt**: Pythonパッケージ依存関係
   ```bash
   cd backend
   gcloud storage cp agent_engine_requirements.txt gs://homework-coach-assets-{suffix}/agent-engine/requirements.txt
   ```

3. **dependencies.tar.gz**: カスタムコードパッケージ（app/ディレクトリ）
   ```bash
   cd backend
   tar -czf dependencies.tar.gz app/
   gcloud storage cp dependencies.tar.gz gs://homework-coach-assets-{suffix}/agent-engine/
   ```

### Terraform Provider

Agent Engineリソース（`google_vertex_ai_reasoning_engine`）は、Google Provider >= 7.13.0 が必要です。

## 使用方法

### モジュールの呼び出し

```hcl
module "agent_engine" {
  source = "../../modules/agent_engine"
  count  = var.enable_agent_engine ? 1 : 0

  project_id           = var.project_id
  region               = var.gcp_location
  pickle_gcs_uri       = "gs://your-bucket/agent-engine/pickle.pkl"
  requirements_gcs_uri = "gs://your-bucket/agent-engine/requirements.txt"
  dependencies_gcs_uri = "gs://your-bucket/agent-engine/dependencies.tar.gz"

  depends_on = [google_project_service.required_apis, module.cloud_storage]
}
```

### 変数

| 変数名 | 説明 | 型 | デフォルト |
|--------|------|-----|-----------|
| `project_id` | GCP プロジェクト ID | string | - |
| `region` | Agent Engine のロケーション | string | "us-central1" |
| `display_name` | Agent Engine の表示名 | string | "homework-coach-router-agent" |
| `description` | Agent Engine の説明 | string | "宿題コーチロボット - Router Agent (Phase 3)" |
| `pickle_gcs_uri` | pickle.pkl の GCS URI | string | - |
| `requirements_gcs_uri` | requirements.txt の GCS URI | string | - |
| `dependencies_gcs_uri` | dependencies.tar.gz の GCS URI | string | - |
| `python_version` | Python バージョン | string | "3.10" |

### 出力

| 出力名 | 説明 |
|--------|------|
| `resource_name` | Agent Engine のフルリソース名（例: projects/xxx/locations/xxx/reasoningEngines/xxx） |
| `engine_id` | Agent Engine の ID |
| `display_name` | Agent Engine の表示名 |
| `region` | Agent Engine のリージョン |

## デプロイ手順

### 1. アーティファクトの準備

```bash
# 1. エージェントをシリアライズ
cd backend
uv run python scripts/serialize_agent.py

# 2. 依存関係をパッケージ化
tar -czf dependencies.tar.gz app/

# 3. GCSにアップロード
BUCKET_NAME=$(terraform -chdir=../infrastructure/terraform/environments/dev output -raw assets_bucket_name)
gcloud storage cp pickle.pkl gs://${BUCKET_NAME}/agent-engine/
gcloud storage cp agent_engine_requirements.txt gs://${BUCKET_NAME}/agent-engine/requirements.txt
gcloud storage cp dependencies.tar.gz gs://${BUCKET_NAME}/agent-engine/
```

### 2. Terraform デプロイ

```bash
cd infrastructure/terraform/environments/dev

# 変数を設定（terraform.tfvars）
# enable_agent_engine = true
# gcp_location = "us-central1"

# デプロイ
terraform init -upgrade  # Provider バージョンアップデート
terraform plan
terraform apply
```

### 3. デプロイ確認

```bash
# Agent Engine のリソース名を取得
RESOURCE_NAME=$(terraform output -raw agent_engine_resource_name 2>/dev/null || \
  gcloud ai reasoning-engines list --location=us-central1 --format="value(name)" --limit=1)

# ログ確認
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit=10 \
  --format=json
```

## 更新とデプロイ

### エージェントコードの更新

エージェントコード（pickle.pkl）を更新する場合：

```bash
# 1. 再シリアライズ
cd backend
uv run python scripts/serialize_agent.py

# 2. GCSにアップロード（上書き）
gcloud storage cp pickle.pkl gs://${BUCKET_NAME}/agent-engine/

# 3. Agent Engine を再作成
cd ../../infrastructure/terraform/environments/dev
terraform taint 'module.agent_engine[0].google_vertex_ai_reasoning_engine.homework_coach_agent'
terraform apply
```

### セッションのクリーンアップ

Agent Engine を削除する前にセッションをクリーンアップする必要がある場合：

```bash
# API経由で強制削除
TOKEN=$(gcloud auth print-access-token)
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/${RESOURCE_NAME}?force=true"
```

## トラブルシューティング

### エラー: Provider version not supported

**症状**: `google_vertex_ai_reasoning_engine` リソースが認識されない

**解決策**: Provider バージョンを >= 7.13.0 にアップグレード
```bash
terraform init -upgrade
```

### エラー: ModuleNotFoundError during execution

**症状**: Agent Engine 実行時に `ModuleNotFoundError: No module named 'app.services'`

**原因**: dependencies.tar.gz が空、または正しくパッケージ化されていない

**解決策**:
```bash
cd backend
tar -czf dependencies.tar.gz app/
# サイズを確認（数十KB以上あるべき）
ls -lh dependencies.tar.gz
gcloud storage cp dependencies.tar.gz gs://${BUCKET_NAME}/agent-engine/
```

### エラー: Child resources must be deleted

**症状**: `The ReasoningEngine contains child resources: sessions`

**解決策**: 強制削除フラグを使用
```bash
TOKEN=$(gcloud auth print-access-token)
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  "https://us-central1-aiplatform.googleapis.com/v1beta1/${RESOURCE_NAME}?force=true"
```

## 制限事項と今後の対応

### 現在の制限

1. **セッション管理**: Agent Engine の内蔵セッション管理機能を使用するには、バックエンドコードの修正が必要（Issue #98）
2. **Runner依存**: 現在のシリアライゼーションは `Runner` を使用しており、外部サービス依存がある
3. **ステートレス化**: 完全な自己完結型エージェントにするには、Firestoreセッション管理からの移行が必要

### 今後の対応

詳細は [Issue #98](https://github.com/arakitakashi/homework-coach-robo/issues/98) を参照。

## 参考資料

- [Agent Engine 概要](https://docs.cloud.google.com/agent-builder/agent-engine/overview?hl=ja)
- [ADK ドキュメント](https://google.github.io/adk-docs/)
- [Vertex AI Reasoning Engine リソース](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vertex_ai_reasoning_engine)
