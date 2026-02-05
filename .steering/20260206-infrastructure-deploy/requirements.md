# Requirements - Infrastructure Deploy

## 背景・目的

フロントエンド・バックエンドの実装が完了し、本番環境へのデプロイ準備が整った。
GCPプロジェクトにインフラをデプロイし、アプリケーションを動作可能な状態にする。

## 要求事項

### 機能要件

1. **Bootstrap実行**
   - Terraform State Bucket（GCS）の作成
   - 必要なGCP APIの有効化

2. **Dev環境デプロイ**
   - VPC + VPC Access Connector
   - Service Accounts + IAM Roles
   - Secret Manager Secrets
   - Firestore Database
   - BigQuery Dataset
   - Cloud Storage Bucket
   - Artifact Registry
   - Cloud Run Services（Backend/Frontend）

3. **Secret値の設定**
   - JWT Secret
   - Firebase Config（必要に応じて）

### 非機能要件

- リージョン: asia-northeast1（東京）
- 最小インスタンス: 0（コスト最適化）
- セキュリティ: 最小権限の原則を適用

### 制約条件

- GCPプロジェクトが存在すること
- gcloud CLI がインストールされていること
- Application Default Credentialsが設定されていること

## 対象範囲

### In Scope

- Bootstrap（State Bucket + API有効化）
- Dev環境のインフラデプロイ
- Secret値の設定
- 動作確認

### Out of Scope

- Staging/Production環境のデプロイ
- Cloud Buildパイプラインの設定
- 実際のアプリケーションイメージのデプロイ

## 成功基準

1. terraform applyが成功すること
2. Cloud Runサービスが作成されること
3. Firestoreデータベースが作成されること
4. Secret Managerにシークレットが作成されること
