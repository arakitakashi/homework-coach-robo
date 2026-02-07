# Design - Infrastructure Phase 2 Update

## アーキテクチャ概要

既存のTerraformモジュール構造を維持しつつ、Feature flagパターンで Phase 2 リソースを条件付き作成する。

## 技術選定

- **Feature Flag パターン**: `count = var.enable_xxx ? 1 : 0` で条件付きリソース作成
- **動的ブロック**: Cloud Run環境変数に `dynamic "env"` ブロック使用
- **既存モジュール拡張**: 新モジュール作成せず、variables.tf/main.tf への追加で対応

## ファイル構成

変更対象: 16ファイル（既存ファイルのみ）

| Module | Files | Changes |
|--------|-------|---------|
| bootstrap | main.tf | API追加 |
| environments/dev | main.tf, variables.tf, outputs.tf | 配線・flag・output |
| iam | main.tf, variables.tf | 条件付きIAMロール |
| secret_manager | main.tf, variables.tf, outputs.tf | Gemini APIキー |
| firestore | indexes.tf, variables.tf | 5インデックス |
| bigquery | tables.tf, variables.tf, outputs.tf | 3テーブル |
| cloud_run | main.tf, variables.tf | 動的env |

## セキュリティ考慮事項

- IAMロールは最小権限原則に従い、条件付きで追加
- Gemini APIキーはSecret Managerで管理
- Feature flagで不要なリソースは作成しない

## 代替案と採用理由

| 案 | 採否 | 理由 |
|----|------|------|
| 新モジュール作成 | ❌ | 既存モジュール拡張で十分 |
| 全リソース常時作成 | ❌ | 不要なコスト・権限が発生 |
| Feature flag + count | ✅ | 段階的有効化、後方互換性 |
