# Requirements - Infrastructure Implementation

## 背景・目的

宿題コーチロボットのバックエンド・フロントエンドをGCP上にデプロイするためのインフラストラクチャを構築する。Terraform によるIaC（Infrastructure as Code）とCloud Build によるCI/CDパイプラインを実装する。

## 要求事項

### 機能要件

1. **Terraform モジュール構成**
   - VPC + VPC Connector（Redis アクセス用）
   - IAM（サービスアカウント、ロール）
   - Secret Manager（秘密情報管理）
   - Firestore（Native mode）
   - BigQuery（分析用データ）
   - Memorystore for Redis（キャッシュ）
   - Cloud Storage（静的アセット）
   - Cloud Run（バックエンド/フロントエンド）

2. **Docker イメージ**
   - Backend: FastAPI + uv
   - Frontend: Next.js + Bun

3. **Cloud Build パイプライン**
   - バックエンドビルド＆デプロイ
   - フロントエンドビルド＆デプロイ
   - インフラ変更適用（Terraform）

### 非機能要件

1. **セキュリティ**
   - 最小権限の原則に基づくIAM設計
   - Secret Manager による秘密情報管理
   - VPC Connector によるプライベート通信

2. **可用性**
   - Cloud Run の自動スケーリング
   - Redis の高可用性構成（本番環境）

3. **コスト最適化**
   - 開発環境は min instances = 0
   - 本番環境のみ min instances = 1

### 制約条件

- GCPプロジェクトは事前に作成済みであること
- 必要なAPIは事前に有効化されていること
- asia-northeast1 リージョンを使用

## 対象範囲

### In Scope

- Terraform モジュール（全環境共通）
- 開発環境（dev）の設定
- Docker ファイル
- Cloud Build 設定

### Out of Scope

- staging/production 環境の terraform.tfvars（dev完了後に追加）
- DNS/ドメイン設定
- Monitoring/Alerting（Phase 2以降）
- VPN/Cloud Interconnect

## 成功基準

1. `terraform validate` が成功する
2. `terraform plan` がエラーなく完了する
3. Docker イメージがビルドできる
4. Cloud Build 設定が構文的に正しい
