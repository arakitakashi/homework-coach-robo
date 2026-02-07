# Design - GitHub Actions CI/CD

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  CI (PR)    │    │ CD (main)   │    │ CD (main)   │     │
│  │             │    │ Frontend    │    │ Backend     │     │
│  │ - lint      │    │             │    │             │     │
│  │ - typecheck │    │ - build     │    │ - build     │     │
│  │ - test      │    │ - push      │    │ - push      │     │
│  │             │    │ - deploy    │    │ - deploy    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                              │                  │           │
└──────────────────────────────┼──────────────────┼───────────┘
                               │                  │
                               ▼                  ▼
                    ┌──────────────────────────────────┐
                    │      Google Cloud Platform        │
                    │                                   │
                    │  ┌─────────────┐  ┌───────────┐  │
                    │  │  Artifact   │  │ Cloud Run │  │
                    │  │  Registry   │──▶│           │  │
                    │  └─────────────┘  └───────────┘  │
                    └──────────────────────────────────┘
```

## ワークフロー設計

### 1. CI ワークフロー (`ci.yml`)

**トリガー**: Pull Request（opened, synchronize, reopened）

**ジョブ構成**:

```yaml
jobs:
  frontend-ci:
    - Checkout
    - Setup Bun
    - Install dependencies (cached)
    - Lint (biome)
    - Type check (tsc)
    - Test (vitest)

  backend-ci:
    - Checkout
    - Setup Python + uv
    - Install dependencies (cached)
    - Lint (ruff)
    - Type check (mypy)
    - Test (pytest)
```

### 2. CD ワークフロー (`cd.yml`)

**トリガー**: Push to main branch

**ジョブ構成**:

```yaml
jobs:
  deploy-backend:
    - Checkout
    - Authenticate to GCP (Workload Identity)
    - Build Docker image (amd64)
    - Push to Artifact Registry
    - Deploy to Cloud Run

  deploy-frontend:
    - Checkout
    - Authenticate to GCP (Workload Identity)
    - Build Docker image (amd64)
    - Push to Artifact Registry
    - Deploy to Cloud Run
```

## GCP認証

### Workload Identity Federation

GitHub ActionsからGCPに認証するため、Workload Identity Federationを使用。

**必要なGCP設定**:
1. Workload Identity Pool作成
2. Workload Identity Provider作成（GitHub OIDC）
3. Service Account作成
4. Service Accountへの権限付与
5. Workload Identity PoolとService Accountの紐付け

**GitHub Secrets**:
- `GCP_PROJECT_ID`: homework-coach-robo
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: projects/XXX/locations/global/workloadIdentityPools/github-pool/providers/github-provider
- `GCP_SERVICE_ACCOUNT`: github-actions@homework-coach-robo.iam.gserviceaccount.com

## ファイル構成

```
.github/
└── workflows/
    ├── ci.yml          # CI（PR時）
    └── cd.yml          # CD（mainマージ時）
```

## キャッシュ戦略

### Frontend
- `~/.bun/install/cache`: Bunの依存関係キャッシュ
- `node_modules`: インストール済みモジュール

### Backend
- `~/.cache/uv`: uvの依存関係キャッシュ
- `.venv`: 仮想環境

## エラーハンドリング

- ジョブ失敗時はGitHub UI上で確認可能
- CDジョブ失敗時は前回のCloud Run revisionが維持される

## セキュリティ考慮事項

- Workload Identity Federationで短期トークンを使用（長期認証情報を保存しない）
- Service Accountは最小権限（Artifact Registry Writer, Cloud Run Admin）
- Secretsは暗号化されて保存
