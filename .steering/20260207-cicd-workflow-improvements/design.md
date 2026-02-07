# Design - CI/CD Workflow Improvements

## 変更概要

### 1. GitHub Secrets設定

| Secret | Value |
|--------|-------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/652907685934/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `github-actions@homework-coach-robo.iam.gserviceaccount.com` |

### 2. CDワークフロー改善

現状の問題:
- `push to main` で即座にデプロイ開始
- CIチェック（lint/typecheck/test）の結果を待たない

改善:
- CDワークフローの各deployジョブの中で、変更対象のCIチェック成功を確認してからデプロイ

### 3. マニュアルデプロイワークフロー (`deploy.yml`)

```yaml
workflow_dispatch:
  inputs:
    service:
      description: 'デプロイ対象'
      type: choice
      options: [backend, frontend, both]
    environment:
      description: '環境'
      type: choice
      options: [dev]
```

## ファイル構成

```
.github/workflows/
├── ci-backend.yml          # 既存（変更なし）
├── ci-frontend.yml         # 既存（変更なし）
├── cd.yml                  # 既存（CI依存追加）
└── deploy.yml              # 新規（マニュアルデプロイ）
```

## セキュリティ考慮事項

- WIF認証によりlong-lived credentialsを使用しない
- `workflow_dispatch`はリポジトリのwrite権限を持つユーザーのみ実行可能
- `allow-unauthenticated`はdev環境のみ（本番は別途検討）
