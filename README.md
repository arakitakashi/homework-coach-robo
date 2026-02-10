## 概要

開発を進めるうえで遵守すべき標準ルールを定義します。

## ローカル開発環境（Docker）

Dockerを使用してローカルでアプリケーションを起動する手順です。

### 前提条件

- Docker Desktop がインストールされていること
- Google Cloud 認証が設定されていること（Gemini APIを使用する場合）

### クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/arakitakashi/homework-coach-robo.git
cd homework-coach-robo

# 2. 環境変数ファイルを作成（オプション）
cp .env.example .env
# 必要に応じて .env を編集

# 3. Docker Compose で起動
docker compose up

# バックグラウンドで起動する場合
docker compose up -d
```

### アクセスURL

| サービス | URL | 説明 |
|----------|-----|------|
| Frontend | http://localhost:3000 | Next.js フロントエンド |
| Backend | http://localhost:8080 | FastAPI バックエンド |
| API Docs | http://localhost:8080/docs | Swagger UI |
| Health Check | http://localhost:8080/health | ヘルスチェック |

### よく使うコマンド

```bash
# 起動
docker compose up

# バックグラウンド起動
docker compose up -d

# 停止
docker compose down

# ログ確認
docker compose logs -f

# 特定サービスのログ
docker compose logs -f backend
docker compose logs -f frontend

# 再ビルド（依存関係変更時）
docker compose build --no-cache
docker compose up

# コンテナ内でコマンド実行
docker compose exec backend uv run pytest
docker compose exec frontend bun test
```

### 環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `GOOGLE_CLOUD_PROJECT` | `homework-coach-robo` | GCPプロジェクトID |
| `GOOGLE_CLOUD_LOCATION` | `asia-northeast1` | GCPリージョン |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8080` | バックエンドAPI URL |

### Google Cloud 認証（Gemini API使用時）

対話機能を使用する場合は、Google Cloud認証が必要です。

```bash
# 1. gcloud CLI で認証
gcloud auth application-default login

# 2. 環境変数を設定
export GOOGLE_CLOUD_PROJECT=your-project-id

# 3. Docker Compose で起動（認証情報をマウント）
docker compose -f docker-compose.yml -f docker-compose.gcloud.yml up
```

### トラブルシューティング

#### ポートが使用中の場合

```bash
# 使用中のポートを確認
lsof -i :3000
lsof -i :8080

# プロセスを終了するか、docker-compose.yml でポートを変更
```

#### 依存関係のキャッシュをクリアしたい場合

```bash
# ボリュームを削除して再起動
docker compose down -v
docker compose up --build
```

### Docker を使わない開発

Dockerを使わずにローカルで開発する場合は、以下を参照してください：

- **バックエンド**: `backend/README.md`
- **フロントエンド**: `frontend/README.md`

## プロジェクト構造

本リポジトリは、小学生の宿題コーチロボ専用のリポジトリです。

### ドキュメントの分類

#### 1. 永続的ドキュメント（`docs/`）

アプリケーション全体の「**何を作るか**」「**どう作るか**」を定義する恒久的なドキュメント。
アプリケーションの基本設計や方針が変わらない限り更新されません。

- **product-requirements.md** - プロダクト要求定義書
  - プロダクトビジョンと目的
  - ターゲットユーザーと課題・ニーズ
  - 主要な機能一覧
  - 成功の定義
  - ビジネス要件
  - ユーザーストーリー
  - 受け入れ条件
  - 機能要件
  - 非機能要件

- **functional-design.md** - 機能設計書
  - 機能ごとのアーキテクチャ
  - システム構成図
  - データモデル定義（ER図含む）
  - コンポーネント設計
  - ユースケース図、画面遷移図、ワイヤフレーム
  - API設計（将来的にバックエンドと連携する場合）

- **architecture.md** - 技術仕様書
  - テクノロジースタック
  - 開発ツールと手法
  - 技術的制約と要件
  - パフォーマンス要件

- **repository-structure.md** - リポジトリ構造定義書
  - フォルダ・ファイル構成
  - ディレクトリの役割
  - ファイル配置ルール

- **development-guidelines.md** - 開発ガイドライン
  - コーディング規約
  - 命名規則
  - スタイリング規約
  - テスト規約
  - Git規約

- **glossary.md** - ユビキタス言語定義
  - ドメイン用語の定義
  - ビジネス用語の定義
  - UI/UX用語の定義
  - 英語・日本語対応表
  - コード上の命名規則

#### 2. 作業単位のドキュメント（`.steering/[YYYYMMDD]-[開発タイトル]/`）

特定の開発作業における「**今回何をするか**」を定義する一時的なステアリングファイル。
作業完了後は参照用として保持されますが、新しい作業では新しいディレクトリを作成します。

- **requirements.md** - 今回の作業の要求内容
  - 変更・追加する機能の説明
  - ユーザーストーリー
  - 受け入れ条件
  - 制約事項

- **design.md** - 変更内容の設計
  - 実装アプローチ
  - 変更するコンポーネント
  - データ構造の変更
  - 影響範囲の分析

- **tasklist.md** - タスクリスト
  - 具体的な実装タスク
  - タスクの進捗状況
  - 完了条件

### ステアリングディレクトリの命名規則

```
.steering/[YYYYMMDD]-[開発タイトル]/
```

**例：**

- `.steering/20250103-initial-implementation/`
- `.steering/20250115-add-tag-feature/`
- `.steering/20250120-fix-filter-bug/`
- `.steering/20250201-improve-performance/`

## 開発プロセス

### 初回セットアップ時の手順

#### 1. フォルダ作成

```bash
mkdir -p docs
mkdir -p .steering
```

#### 2. 永続的ドキュメント作成（`docs/`）

アプリケーション全体の設計を定義します。
各ドキュメントを作成後、必ず確認・承認を得てから次に進みます。

1. `docs/product-requirements.md` - プロダクト要求定義書
2. `docs/functional-design.md` - 機能設計書
3. `docs/architecture.md` - 技術仕様書
4. `docs/repository-structure.md` - リポジトリ構造定義書
5. `docs/development-guidelines.md` - 開発ガイドライン
6. `docs/glossary.md` - ユビキタス言語定義

**重要：** 1ファイルごとに作成後、必ず確認・承認を得てから次のファイル作成を行う

#### 3. 初回実装用のステアリングファイル作成

初回実装用のディレクトリを作成し、実装に必要なドキュメントを配置します。

```bash
mkdir -p .steering/[YYYYMMDD]-initial-implementation
```

作成するドキュメント：

1. `.steering/[YYYYMMDD]-initial-implementation/requirements.md` - 初回実装の要求
2. `.steering/[YYYYMMDD]-initial-implementation/design.md` - 実装設計
3. `.steering/[YYYYMMDD]-initial-implementation/tasklist.md` - 実装タスク

#### 4. 環境セットアップ

#### 5. 実装開始

`.steering/[YYYYMMDD]-initial-implementation/tasklist.md` に基づいて実装を進めます。

#### 6. 品質チェック

### 機能追加・修正時の手順

#### 1. 影響分析

- 永続的ドキュメント（`docs/`）への影響を確認
- 変更が基本設計に影響する場合は `docs/` を更新

#### 2. ステアリングディレクトリ作成

新しい作業用のディレクトリを作成します。

```bash
mkdir -p .steering/[YYYYMMDD]-[開発タイトル]
```

**例：**

```bash
mkdir -p .steering/20250115-add-tag-feature
```

#### 3. 作業ドキュメント作成

作業単位のドキュメントを作成します。
各ドキュメント作成後、必ず確認・承認を得てから次に進みます。

1. `.steering/[YYYYMMDD]-[開発タイトル]/requirements.md` - 要求内容
2. `.steering/[YYYYMMDD]-[開発タイトル]/design.md` - 設計
3. `.steering/[YYYYMMDD]-[開発タイトル]/tasklist.md` - タスクリスト

**重要：** 1ファイルごとに作成後、必ず確認・承認を得てから次のファイル作成を行う

#### 4. 永続的ドキュメント更新（必要な場合のみ）

変更が基本設計に影響する場合、該当する `docs/` 内のドキュメントを更新します。

#### 5. 実装開始

`.steering/[YYYYMMDD]-[開発タイトル]/tasklist.md` に基づいて実装を進めます。

#### 6. 品質チェック

---

## デプロイ手順

このセクションでは、アプリケーションをGoogle Cloud Platform（GCP）にデプロイする手順を説明します。

### 前提条件

デプロイを開始する前に、以下の準備が必要です：

#### 1. 必要なツール

- **Google Cloud SDK (gcloud)** - [インストール](https://cloud.google.com/sdk/docs/install)
- **Terraform** >= 1.10.0 - [インストール](https://developer.hashicorp.com/terraform/downloads)
- **GitHub CLI (gh)** - [インストール](https://cli.github.com/)（CI/CD設定時）

```bash
# バージョン確認
gcloud --version
terraform --version
gh --version
```

#### 2. GCPアカウントとプロジェクト

- GCPアカウントを作成済みであること
- 請求先アカウントが有効化されていること
- プロジェクトID: `homework-coach-robo`（または任意のID）

```bash
# GCP認証
gcloud auth login
gcloud auth application-default login

# プロジェクト設定
export GCP_PROJECT_ID=homework-coach-robo
gcloud config set project $GCP_PROJECT_ID
```

#### 3. 必要なGCP APIの有効化

```bash
# 主要なAPIを有効化
gcloud services enable \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  storage-api.googleapis.com \
  aiplatform.googleapis.com \
  speech.googleapis.com \
  texttospeech.googleapis.com
```

---

### 初回デプロイ手順

初めてアプリケーションをデプロイする場合の手順です。

#### Step 1: Terraform Bootstrapの実行

まず、Terraformのstate管理用のGCSバケットを作成します。

```bash
cd infrastructure/terraform/bootstrap

# Terraform初期化
terraform init -backend=false

# 実行計画の確認
terraform plan

# 適用
terraform apply
```

これにより、以下のリソースが作成されます：
- Terraformステート保存用GCSバケット
- 必要なGCP APIの有効化

#### Step 2: 開発環境のインフラデプロイ

次に、アプリケーション実行に必要なインフラをデプロイします。

```bash
cd ../environments/dev

# Terraform初期化（リモートバックエンド設定）
terraform init

# 実行計画の確認
terraform plan

# 適用
terraform apply
```

これにより、以下のリソースが作成されます：
- VPC / サブネット
- Cloud Firestore データベース
- BigQuery データセット
- Cloud Storage バケット（アセット用）
- Cloud Run サービス（Backend / Frontend）
- Artifact Registry（Dockerイメージ用）
- IAM ロール / サービスアカウント
- Secret Manager（将来使用）
- GitHub Workload Identity Federation（CI/CD用）
- **Agent Engine（オプション、`enable_agent_engine = true` の場合）**

**Agent Engineを有効化する場合:**

```hcl
# environments/dev/terraform.tfvars
enable_agent_engine = true
```

Agent Engineを有効化すると、以下が追加で必要です：
1. エージェントのシリアライズ（`backend/scripts/serialize_agent.py`）
2. 依存関係のパッケージ化（`tar -czf dependencies.tar.gz app/`）
3. GCSへのアーティファクトアップロード

詳細は後述の「Agent Engineアーティファクトデプロイ」セクションを参照。

#### Step 3: 初回アプリケーションデプロイ（手動）

インフラが準備できたら、初回はDockerイメージをビルドしてデプロイします。

```bash
# リポジトリルートに戻る
cd ../../../../

# 環境変数設定
export GCP_PROJECT_ID=homework-coach-robo
export GCP_REGION=asia-northeast1
export ARTIFACT_REGISTRY=${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/homework-coach-docker

# Docker認証
gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev

# バックエンドイメージのビルド＆プッシュ
docker build \
  --platform linux/amd64 \
  -f infrastructure/docker/backend/Dockerfile \
  -t ${ARTIFACT_REGISTRY}/backend:latest \
  .
docker push ${ARTIFACT_REGISTRY}/backend:latest

# バックエンドデプロイ
gcloud run deploy homework-coach-backend \
  --image=${ARTIFACT_REGISTRY}/backend:latest \
  --region=${GCP_REGION} \
  --project=${GCP_PROJECT_ID} \
  --allow-unauthenticated

# バックエンドURLを取得
BACKEND_URL=$(gcloud run services describe homework-coach-backend \
  --region=${GCP_REGION} \
  --project=${GCP_PROJECT_ID} \
  --format='value(status.url)')

# フロントエンドイメージのビルド＆プッシュ
docker build \
  --platform linux/amd64 \
  -f infrastructure/docker/frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
  -t ${ARTIFACT_REGISTRY}/frontend:latest \
  .
docker push ${ARTIFACT_REGISTRY}/frontend:latest

# フロントエンドデプロイ
gcloud run deploy homework-coach-frontend \
  --image=${ARTIFACT_REGISTRY}/frontend:latest \
  --region=${GCP_REGION} \
  --project=${GCP_PROJECT_ID} \
  --allow-unauthenticated

# フロントエンドURLを取得
FRONTEND_URL=$(gcloud run services describe homework-coach-frontend \
  --region=${GCP_REGION} \
  --project=${GCP_PROJECT_ID} \
  --format='value(status.url)')

echo "Frontend URL: $FRONTEND_URL"
```

---

### 日常的なデプロイフロー（CI/CD自動化）

初回デプロイ後は、GitHubにコードをプッシュするだけで自動的にデプロイされます。

#### CI/CD パイプライン

GitHub Actionsによる自動デプロイが設定されています：

| ワークフロー | トリガー | 内容 |
|------------|---------|------|
| `ci-backend.yml` | PR作成、Push | バックエンドCI（lint, type check, test） |
| `ci-frontend.yml` | PR作成、Push | フロントエンドCI（lint, type check, test） |
| `ci-e2e.yml` | PR作成、Push | E2Eテスト（Docker Compose + Playwright） |
| `cd.yml` | Push to `main` | 自動デプロイ（Backend → Agent Engine → Frontend） |
| `deploy.yml` | 手動トリガー | マニュアルデプロイ（workflow_dispatch） |

#### 通常のデプロイフロー

```bash
# 1. フィーチャーブランチで開発
git checkout -b feature/new-feature

# 2. コード変更・コミット
git add .
git commit -m "feat: add new feature"

# 3. プッシュしてPR作成
git push -u origin feature/new-feature
gh pr create --title "feat: add new feature"

# 4. CI チェック（自動実行）
# - lint, type check, test がすべてパスすることを確認

# 5. PRマージ
gh pr merge --squash

# 6. main ブランチへのプッシュで自動デプロイ（cd.yml）
# - Backend: Dockerイメージビルド → Cloud Runデプロイ
# - Agent Engine: アーティファクトGCSアップロード（バックエンド変更時のみ）
# - Frontend: Dockerイメージビルド → Cloud Runデプロイ
```

#### バックエンド変更時の自動デプロイ

バックエンドコード（`backend/` ディレクトリ）を変更すると、以下が自動実行されます：

1. **Cloud Run バックエンドデプロイ**
   - Dockerイメージビルド
   - Artifact Registryにプッシュ
   - Cloud Runサービス更新

2. **Agent Engine アーティファクトデプロイ**（`deploy-agent-engine` ジョブ）
   - エージェントシリアライズ（`serialize_agent.py`）
   - 依存関係パッケージ化（`tar -czf dependencies.tar.gz app/`）
   - GCSアップロード:
     - `gs://.../agent-engine/pickle.pkl`
     - `gs://.../agent-engine/requirements.txt`
     - `gs://.../agent-engine/dependencies.tar.gz`

**注意**: Agent Engineリソース自体の再作成は手動で行う必要があります（後述）。

#### フロントエンドのみ変更時

フロントエンドコード（`frontend/` ディレクトリ）のみを変更した場合：
- Agent Engineアーティファクトデプロイはスキップされます
- CI/CD実行時間が短縮されます

---

### Agent Engineアーティファクトデプロイ

Agent Engineを使用する場合、以下のアーティファクトをGCSにアップロードする必要があります。

#### 自動デプロイ（推奨）

**バックエンドコードを変更して `main` にマージすると、CI/CDで自動的にアップロードされます。**

```bash
# 1. バックエンドコードを変更
# 例: backend/app/services/adk/agents/router.py を編集

# 2. コミット・プッシュ
git add backend/
git commit -m "feat: update router agent prompt"
git push

# 3. PR作成・マージ
gh pr create --title "feat: update router agent prompt"
gh pr merge --squash

# 4. cd.yml の deploy-agent-engine ジョブが自動実行
# - バックエンド変更検知
# - エージェントシリアライズ
# - GCSアップロード
```

#### 手動デプロイ（必要に応じて）

CI/CDを使わず、ローカルから手動でアップロードする場合：

```bash
# 1. バックエンドディレクトリに移動
cd backend

# 2. 依存関係インストール
uv sync

# 3. エージェントシリアライズ
uv run python scripts/serialize_agent.py
# → pickle.pkl が生成される

# 4. 依存関係パッケージ化
tar -czf dependencies.tar.gz app/

# 5. GCSバケット名取得
BUCKET_NAME=$(gcloud storage buckets list \
  --format="value(name)" \
  --filter="name:homework-coach-assets")

# 6. GCSアップロード
gcloud storage cp pickle.pkl "gs://${BUCKET_NAME}/agent-engine/"
gcloud storage cp agent_engine_requirements.txt "gs://${BUCKET_NAME}/agent-engine/requirements.txt"
gcloud storage cp dependencies.tar.gz "gs://${BUCKET_NAME}/agent-engine/"

# 7. アップロード確認
gcloud storage ls -l "gs://${BUCKET_NAME}/agent-engine/"
```

#### Agent Engineリソースの再作成（必要に応じて）

アーティファクトをアップロード後、Agent Engineリソース自体を再作成する必要がある場合：

```bash
cd infrastructure/terraform/environments/dev

# Agent Engineリソースをtaint（再作成マーク）
terraform taint 'module.agent_engine[0].google_vertex_ai_reasoning_engine.homework_coach_agent'

# 再作成（5-10分かかります）
terraform apply
```

**注意**: Agent Engine再作成は時間がかかるため、必要な場合のみ実行してください。
多くの場合、アーティファクトのアップロードのみで十分です。

---

### 手動デプロイ（トラブルシューティング時）

CI/CDが使えない場合や、手動でデプロイが必要な場合：

#### GitHub Actions の手動トリガー

```bash
# deploy.yml をGitHub UIから手動トリガー
# または gh CLI で:
gh workflow run deploy.yml
```

#### 完全手動デプロイ

```bash
# 環境変数設定
export GCP_PROJECT_ID=homework-coach-robo
export GCP_REGION=asia-northeast1
export ARTIFACT_REGISTRY=${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/homework-coach-docker

# バックエンドデプロイ
docker build -f infrastructure/docker/backend/Dockerfile -t ${ARTIFACT_REGISTRY}/backend:manual .
docker push ${ARTIFACT_REGISTRY}/backend:manual
gcloud run deploy homework-coach-backend \
  --image=${ARTIFACT_REGISTRY}/backend:manual \
  --region=${GCP_REGION}

# フロントエンドデプロイ
BACKEND_URL=$(gcloud run services describe homework-coach-backend \
  --region=${GCP_REGION} --format='value(status.url)')
docker build -f infrastructure/docker/frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
  -t ${ARTIFACT_REGISTRY}/frontend:manual .
docker push ${ARTIFACT_REGISTRY}/frontend:manual
gcloud run deploy homework-coach-frontend \
  --image=${ARTIFACT_REGISTRY}/frontend:manual \
  --region=${GCP_REGION}
```

---

### デプロイ確認

デプロイ後、以下のURLにアクセスして動作確認します：

```bash
# フロントエンドURL取得
gcloud run services describe homework-coach-frontend \
  --region=asia-northeast1 \
  --format='value(status.url)'

# バックエンドURL取得
gcloud run services describe homework-coach-backend \
  --region=asia-northeast1 \
  --format='value(status.url)'

# Health Check
curl https://your-backend-url/health
```

**確認項目:**
- [ ] フロントエンドが正常に表示される
- [ ] バックエンドAPIが応答する（`/health` エンドポイント）
- [ ] 音声入力が動作する
- [ ] 対話機能が動作する

---

### トラブルシューティング

#### デプロイが失敗する場合

**症状**: `terraform apply` が失敗する

```bash
# Terraformログ確認
terraform apply -no-color 2>&1 | tee terraform.log

# よくあるエラー:
# - API有効化されていない → bootstrap を先に実行
# - 権限不足 → IAMロールを確認
# - リソースクォータ超過 → GCPクォータ確認
```

**症状**: Cloud Runデプロイが失敗する

```bash
# Cloud Runログ確認
gcloud run services logs read homework-coach-backend \
  --region=asia-northeast1 \
  --limit=50

# よくあるエラー:
# - イメージがない → Artifact Registryにプッシュされているか確認
# - 環境変数不足 → Terraform変数を確認
# - 起動失敗 → アプリケーションログを確認
```

#### CI/CDが動かない場合

**症状**: GitHub Actionsが失敗する

```bash
# ワークフロー実行履歴確認
gh run list --workflow=cd.yml

# 最新の実行ログ確認
gh run view --log

# よくあるエラー:
# - Workload Identity Federation設定ミス → Terraformで再作成
# - シークレット未設定 → GitHub Settings > Secrets で確認
# - 権限不足 → サービスアカウントのIAMロール確認
```

#### Agent Engineが動かない場合

**症状**: Agent Engineがエラーを返す

```bash
# Agent Engineログ確認（現状、直接的なログ取得方法は限定的）
# 代わりに、バックエンドログを確認:
gcloud run services logs read homework-coach-backend \
  --region=asia-northeast1 \
  --limit=100

# アーティファクト確認
BUCKET_NAME=$(gcloud storage buckets list --format="value(name)" --filter="name:homework-coach-assets")
gcloud storage ls -l "gs://${BUCKET_NAME}/agent-engine/"

# よくあるエラー:
# - アーティファクトがない → GCSアップロード確認
# - シリアライズエラー → serialize_agent.py をローカルで実行して確認
# - 依存関係不足 → agent_engine_requirements.txt を確認
```

---

### 環境変数一覧

デプロイに必要な主要な環境変数:

#### バックエンド

| 変数名 | 設定場所 | 説明 |
|--------|---------|------|
| `GOOGLE_CLOUD_PROJECT` | Cloud Run環境変数 | GCPプロジェクトID |
| `GOOGLE_CLOUD_LOCATION` | Cloud Run環境変数 | GCPリージョン |
| `FIRESTORE_DATABASE_ID` | Cloud Run環境変数 | Firestoreデータベース名 |
| `AGENT_ENGINE_RESOURCE_NAME` | Cloud Run環境変数 | Agent EngineリソースURL（オプション） |

#### フロントエンド

| 変数名 | 設定場所 | 説明 |
|--------|---------|------|
| `NEXT_PUBLIC_API_URL` | ビルド引数 | バックエンドAPI URL |

#### CI/CD（GitHub Secrets）

| 変数名 | 説明 |
|--------|------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Federation プロバイダー |
| `GCP_SERVICE_ACCOUNT` | GitHub Actions用サービスアカウント |

詳細は `docs/implementation-status.md` の環境変数セクション（作成予定）を参照。

---

### 参考リンク

- **インフラ設計**: `docs/architecture.md`
- **Agent Engine詳細**: `infrastructure/terraform/modules/agent_engine/README.md`
- **実装ステータス**: `docs/implementation-status.md`
- **CI/CD設定**: `.github/workflows/cd.yml`
- **イシュー #101**: CI/CD Agent Engineアーティファクト自動デプロイ

---

## インフラストラクチャ

### Agent Engine デプロイ（Phase 3）

本プロジェクトは、Vertex AI Agent Engine を使用したスケーラブルなデプロイメントをサポートしています。

#### Terraform によるインフラ管理

Agent Engine のデプロイは Terraform で管理されています。

**モジュール構成**:
- `infrastructure/terraform/modules/agent_engine/` - Agent Engine リソース定義
- `infrastructure/terraform/environments/dev/` - 開発環境設定

**デプロイ手順**:

```bash
# 1. アーティファクト準備
cd backend
uv run python scripts/serialize_agent.py
tar -czf dependencies.tar.gz app/
gcloud storage cp pickle.pkl gs://homework-coach-assets-{suffix}/agent-engine/
gcloud storage cp agent_engine_requirements.txt gs://homework-coach-assets-{suffix}/agent-engine/requirements.txt
gcloud storage cp dependencies.tar.gz gs://homework-coach-assets-{suffix}/agent-engine/

# 2. Terraform デプロイ
cd ../infrastructure/terraform/environments/dev
terraform init -upgrade
terraform apply
```

詳細は以下を参照:
- **モジュール README**: `infrastructure/terraform/modules/agent_engine/README.md`
- **実装ドキュメント**: `docs/agent-architecture.md`
- **Issue #98**: Agent Engine を利用した内部完結型実装

### CI/CD

GitHub Actions による自動デプロイが設定されています。

- **CI パイプライン**: `.github/workflows/ci-*.yml`
- **CD パイプライン**: `.github/workflows/cd.yml`
- **認証**: Workload Identity Federation（Terraform管理）

## 利用可能なスキル

本プロジェクトでは、実装時に活用できるClaudeスキルが用意されています。
スキルを使用することで、ベストプラクティスに従った実装が可能になります。

### 開発プロセス

- **TDD Skill** (`/tdd`) - テスト駆動開発の完全ガイド（和田卓人の原則準拠）
- **使用タイミング**: 新機能実装開始時、テストファースト開発時

- **Git Workflow Skill** (`/git-workflow`) - Git Flow + Conventional Commits
- **使用タイミング**: ブランチ作成時、コミット時、PR作成時、レビュー時

### フロントエンド開発

- **Frontend Skill** (`/frontend`) - Next.js 14+ (App Router) + TypeScript + React
- **使用タイミング**: フロントエンド実装時、UI開発時、テスト作成時

### バックエンド開発

- **FastAPI Skill** (`/fastapi`) - FastAPI + Pydantic v2 + Firestore統合
- **使用タイミング**: バックエンドAPI実装時、Firestore連携時、認証実装時

- **Google ADK Basics Skill** (`/google-adk-basics`) - ADKの基礎とAgent構造
- **使用タイミング**: ADKプロジェクトのセットアップ時、Agent構造設計時

- **Google ADK Live Skill** (`/google-adk-live`) - Gemini Live API（リアルタイム音声・動画）
- **使用タイミング**: 音声対話エンジン実装時、リアルタイムAI構築時
- **前提**: `/google-adk-basics` の知識が必要

### 推奨される実装フロー

1. **機能設計** → `/tdd` で仕様をテストコードとして記述
2. **バックエンドAPI** → `/fastapi` でAPI実装
3. **フロントエンド** → `/frontend` でUI/UX実装（Next.js + React + TypeScript）
4. **AIエージェント基礎** → `/google-adk-basics` でAgent構造設計
5. **音声対話機能** → `/google-adk-live` でリアルタイム対話実装
6. **テスト実行** → `/tdd` のRed-Green-Refactorサイクルで品質確保
7. **コミット・PR** → `/git-workflow` でGit操作・レビュー

詳細は `CLAUDE.md` および `docs/development-guidelines.md` を参照してください。

## ドキュメント管理の原則

### 永続的ドキュメント（`docs/`）

- アプリケーションの基本設計を記述
- 頻繁に更新されない
- 大きな設計変更時のみ更新
- プロジェクト全体の「北極星」として機能

### 作業単位のドキュメント（`.steering/`）

- 特定の作業・変更に特化
- 作業ごとに新しいディレクトリを作成
- 作業完了後は履歴として保持
- 変更の意図と経緯を記録

## 図表・ダイアグラムの記載ルール

### 記載場所

設計図やダイアグラムは、関連する永続的ドキュメント内に直接記載します。
独立したdiagramsフォルダは作成せず、手間を最小限に抑えます。

**配置例：**

- ER図、データモデル図 → `functional-design.md` 内に記載
- ユースケース図 → `functional-design.md` または `product-requirements.md` 内に記載
- 画面遷移図、ワイヤフレーム → `functional-design.md` 内に記載
- システム構成図 → `functional-design.md` または `architecture.md` 内に記載

### 記述形式

1. **Mermaid記法（推奨）**
   - Markdownに直接埋め込める
   - バージョン管理が容易
   - ツール不要で編集可能

```mermaid
graph TD
    A[ユーザー] --> B[タスク作成]
    B --> C[タスク一覧]
    C --> D[タスク編集]
    C --> E[タスク削除]
```

2. **ASCII アート**
   - シンプルな図表に使用
   - テキストエディタで編集可能

```
┌─────────────┐
│   Header    │
└─────────────┘
       │
       ↓
┌─────────────┐
│  Task List  │
└─────────────┘
```

3. **画像ファイル（必要な場合のみ）**
   - 複雑なワイヤフレームやモックアップ
   - `docs/images/` フォルダに配置
   - PNG または SVG 形式を推奨

### 図表の更新

- 設計変更時は対応する図表も同時に更新
- 図表とコードの乖離を防ぐ

## 注意事項

- ドキュメントの作成・更新は段階的に行い、各段階で承認を得る
- `.steering/` のディレクトリ名は日付と開発タイトルで明確に識別できるようにする
- 永続的ドキュメントと作業単位のドキュメントを混同しない
- コード変更後は必ずリント・型チェックを実施する
- 共通のデザインシステム（Tailwind CSS）を使用して統一感を保つ
- セキュリティを考慮したコーディング（XSS対策、入力バリデーションなど）
- 図表は必要最小限に留め、メンテナンスコストを抑える
