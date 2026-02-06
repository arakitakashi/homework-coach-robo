# GCP Workload Identity Federation Setup

GitHub ActionsからGCPに安全に認証するための設定手順。

## 前提条件

- GCP プロジェクト: `homework-coach-robo`
- gcloud CLI がインストール済み
- プロジェクトのオーナー権限

## 設定手順

### 1. 必要なAPIを有効化

```bash
gcloud services enable \
  iamcredentials.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --project=homework-coach-robo
```

### 2. Service Accountを作成

```bash
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --description="Service account for GitHub Actions CI/CD" \
  --project=homework-coach-robo
```

### 3. Service Accountに権限を付与

```bash
# Artifact Registry Writer（Docker push）
gcloud projects add-iam-policy-binding homework-coach-robo \
  --member="serviceAccount:github-actions@homework-coach-robo.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Cloud Run Admin（デプロイ）
gcloud projects add-iam-policy-binding homework-coach-robo \
  --member="serviceAccount:github-actions@homework-coach-robo.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Service Account User（Cloud Runのサービスアカウントとして実行）
gcloud projects add-iam-policy-binding homework-coach-robo \
  --member="serviceAccount:github-actions@homework-coach-robo.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### 4. Workload Identity Poolを作成

```bash
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --description="Workload Identity Pool for GitHub Actions" \
  --project=homework-coach-robo
```

### 5. Workload Identity Providerを作成

```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == 'arakitakashi'" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project=homework-coach-robo
```

### 6. Service AccountとWorkload Identity Poolを紐付け

```bash
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@homework-coach-robo.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/652907685934/locations/global/workloadIdentityPools/github-pool/attribute.repository/arakitakashi/homework-coach-robo" \
  --project=homework-coach-robo
```

### 7. Workload Identity Provider名を取得

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --project=homework-coach-robo \
  --format="value(name)"
```

出力例:
```
projects/652907685934/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

## GitHub Secretsの設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定：

| Secret Name | Value |
|-------------|-------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/652907685934/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `github-actions@homework-coach-robo.iam.gserviceaccount.com` |

## 確認

設定完了後、PRを作成してCIが動作することを確認。
mainにマージしてCDが動作することを確認。

## トラブルシューティング

### 認証エラー

```
Error: google-github-actions/auth failed with: the audience was not valid
```

→ Workload Identity Provider の設定を確認

### 権限エラー

```
Error: Permission denied on resource
```

→ Service Account の権限を確認
