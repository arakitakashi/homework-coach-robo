# Requirements - GitHub Actions CI/CD

## 背景・目的

現在、手動でDocker buildとCloud Runデプロイを実行している。GitHub Actionsを使用してCI/CDパイプラインを自動化し、コード品質の担保とデプロイの効率化を実現する。

## 要求事項

### 機能要件

1. **CI（Continuous Integration）**
   - PRに対してlint、型チェック、テストを自動実行
   - Frontend: Biome lint, TypeScript check, Vitest
   - Backend: Ruff lint, mypy, pytest
   - 全チェックがパスしないとマージ不可

2. **CD（Continuous Deployment）**
   - mainブランチへのマージ時に自動デプロイ
   - Docker イメージのビルド（linux/amd64）
   - Artifact Registryへのプッシュ
   - Cloud Runへのデプロイ

### 非機能要件

- CI実行時間: 5分以内
- シークレット管理: GitHub Secretsを使用
- キャッシュ活用: 依存関係のキャッシュで高速化

### 制約条件

- GCPプロジェクト: homework-coach-robo
- リージョン: asia-northeast1
- Workload Identity Federation（WIF）を使用してGCP認証

## 対象範囲

### In Scope

- CI ワークフロー（PR時）
- CD ワークフロー（mainマージ時）
- Workload Identity Federation設定ドキュメント

### Out of Scope

- ステージング環境へのデプロイ
- ロールバック自動化
- Slack通知

## 成功基準

- [ ] PRに対してCI自動実行
- [ ] mainマージで自動デプロイ
- [ ] 手動デプロイ不要
