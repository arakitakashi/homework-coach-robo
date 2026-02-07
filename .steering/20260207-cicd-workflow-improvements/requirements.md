# Requirements - CI/CD Workflow Improvements

## 背景・目的

CDワークフロー（`.github/workflows/cd.yml`）がGitHub Secrets未設定のため失敗している。
また、マニュアル操作でデプロイを実行できるワークフローが存在しない。

## 要求事項

### 機能要件

1. **GitHub Secrets設定**: WIF認証用のSecretsをリポジトリに登録
2. **CDワークフロー改善**: CIチェック成功後にデプロイを実行するよう修正
3. **マニュアルデプロイワークフロー**: `workflow_dispatch`でBackend/Frontendを個別にデプロイ可能

### 非機能要件

- デプロイの安全性: CIチェック未通過のコードがデプロイされない
- 操作性: GitHub UIからワンクリックでデプロイ可能

### 制約条件

- 既存のGCP WIF設定を使用（`gcp-wif-setup.md`に記載済み）
- Artifact Registry + Cloud Runの既存アーキテクチャを維持

## 対象範囲

### In Scope

- GitHub Secretsの設定
- CDワークフローの改善（CI依存追加）
- マニュアルデプロイワークフロー新規作成

### Out of Scope

- GCP側WIFリソースの変更
- Terraformへの移行
- ステージング/プロダクション環境の分離

## 成功基準

- CDワークフローがmainへのpush時に正常にデプロイされる
- マニュアルデプロイがGitHub UIから正常に実行できる
