# Design - GitHub Actions WIF Terraform Module

## アーキテクチャ概要

新規モジュール `modules/github_wif/` を作成し、GitHub Actions ↔ GCP 間の Workload Identity Federation を管理する。

```
modules/github_wif/
├── main.tf        # リソース定義
├── variables.tf   # 入力変数
└── outputs.tf     # 出力値
```

## リソース構成

```
google_service_account.github_actions
├── google_project_iam_member.github_actions_artifact_registry  (artifactregistry.writer)
├── google_project_iam_member.github_actions_run_admin          (run.admin)
└── google_project_iam_member.github_actions_sa_user            (iam.serviceAccountUser)

google_iam_workload_identity_pool.github_pool
└── google_iam_workload_identity_pool_provider.github_provider  (OIDC)

google_service_account_iam_member.github_actions_wif  (SA ↔ Pool binding)
```

## 既存ファイル修正

| ファイル | 変更内容 |
|---------|---------|
| `environments/dev/main.tf` | `module "github_wif"` 追加、API 2つ追加 |
| `environments/dev/variables.tf` | `github_owner`, `github_repo` 追加 |
| `environments/dev/outputs.tf` | WIF provider, SA email 出力追加 |
| `bootstrap/main.tf` | `iamcredentials.googleapis.com` 追加 |

## セキュリティ考慮事項

- WIF プロバイダの attribute condition で `arakitakashi` オーナーのリポジトリに限定
- 最小権限の原則: デプロイに必要な3ロールのみ付与

## 代替案と採用理由

| 案 | 判断 | 理由 |
|----|------|------|
| 既存 `modules/iam/` に追加 | ❌ 不採用 | IAMモジュールは Cloud Run SA 専用、責務が異なる |
| 新規 `modules/github_wif/` | ✅ 採用 | ライフサイクル独立、既存パターンに合致 |
| gcloud CLI で手動作成 | ❌ 不採用 | IaC 管理外になる |
