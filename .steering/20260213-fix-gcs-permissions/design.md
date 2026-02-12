# Design - GCS Permissions Fix for Agent Engine Deployment

## アーキテクチャ概要

2つの修正で構成:
1. **Terraform**: GitHub Actions SA に GCS バケットへの `objectAdmin` 権限を付与
2. **CD Workflow**: バケット名を Secret から直接取得（`buckets list` を廃止）

## 技術選定

- 既存の `count` パターンで条件付きリソース作成
- `roles/storage.objectAdmin` - オブジェクトの CRUD に必要十分な権限

## ファイル構成

| ファイル | 変更内容 |
|---------|---------|
| `modules/cloud_storage/variables.tf` | `github_actions_service_account_email` 変数追加 |
| `modules/cloud_storage/main.tf` | IAM バインディングリソース追加 |
| `environments/dev/main.tf` | モジュール引数追加 |
| `.github/workflows/cd.yml` | バケット名取得方法変更 |

## セキュリティ考慮事項

- `objectAdmin` はバケットレベルのバインディング（プロジェクトレベルではない）
- `storage.buckets.list` 権限が不要になり、権限スコープが縮小される
- バケット名は GitHub Secret で管理（コードにハードコードしない）

## 代替案と採用理由

| 案 | 採用 | 理由 |
|----|------|------|
| プロジェクトレベル storage.admin | ❌ | 権限過大 |
| バケットレベル objectAdmin + Secret | ✅ | 最小権限 + 安定した参照 |
| Terraform output をワークフローで取得 | ❌ | 追加の Terraform 操作が必要 |
