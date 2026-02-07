# Requirements - GitHub Actions WIF Terraform Module

## 背景・目的

GitHub Actions の CI/CD で使用する Workload Identity Federation (WIF) リソースが GCP に存在しないため認証エラーが発生している。セットアップ手順書（gcloud CLI）は `.steering/20260206-github-actions-cicd/gcp-wif-setup.md` に存在するが未実行。手動作成ではなく Terraform で IaC 管理する。

## 要求事項

### 機能要件

1. GitHub Actions から GCP への keyless 認証を可能にする WIF リソースを Terraform で作成
2. 必要なリソース:
   - Service Account (`github-actions`)
   - Workload Identity Pool (`github-pool`)
   - Workload Identity Provider (`github-provider`, OIDC)
   - SA ↔ Pool のバインド
   - IAM ロール付与（artifactregistry.writer, run.admin, iam.serviceAccountUser）

### 非機能要件

- 既存の Terraform モジュールパターンに合致すること
- `terraform plan` で差分が WIF リソース作成のみであること

### 制約条件

- 既存 `modules/iam/` には追加しない（責務分離）
- OIDC issuer: `https://token.actions.githubusercontent.com`
- リポジトリオーナー制限: `arakitakashi`

## 対象範囲

### In Scope

- `modules/github_wif/` モジュール新規作成
- `environments/dev/` からのモジュール呼び出し
- `bootstrap/main.tf` への API 追加

### Out of Scope

- GitHub Secrets の自動設定（手動で設定）
- CD ワークフローの修正

## 成功基準

- `terraform apply` 後、GitHub Actions ワークフローで認証が成功すること
