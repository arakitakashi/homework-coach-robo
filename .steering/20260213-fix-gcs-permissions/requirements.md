# Requirements - GCS Permissions Fix for Agent Engine Deployment (#110)

## 背景・目的

CD パイプラインの `deploy-agent-engine` ジョブが GCS バケットリスト時に 403 エラーで失敗している。
GitHub Actions SA に GCS バケットへの適切な権限が付与されていないことが原因。

## 要求事項

### 機能要件

1. GitHub Actions SA が GCS バケットに Agent Engine アーティファクトをアップロードできること
2. CD パイプラインの `deploy-agent-engine` ジョブが正常に完了すること

### 非機能要件

- 最小権限の原則に従い、必要最小限の権限のみ付与
- バケット名の動的取得を廃止し、Secret で管理する安全な方法に変更

### 制約条件

- 既存の Terraform モジュール構成を維持
- 条件付きリソース作成パターン (`count`) を使用

## 対象範囲

### In Scope

- Terraform cloud_storage モジュールへの IAM バインディング追加
- CD ワークフローのバケット名取得方法の変更

### Out of Scope

- Agent Engine モジュール自体の変更
- 他の SA の権限変更

## 成功基準

- `terraform validate` が成功すること
- CD ワークフローが `GCS_ASSETS_BUCKET` Secret を使用してアーティファクトをアップロードできること
