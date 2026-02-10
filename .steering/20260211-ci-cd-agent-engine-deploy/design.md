# Design - CI/CD Agent Engine Artifact Deployment

## アーキテクチャ概要

現在の `.github/workflows/cd.yml` に新しいジョブ `deploy-agent-engine` を追加し、バックエンド変更時にAgent Engineアーティファクトを自動的にGCSにアップロードする。

### 全体フロー

```
┌─────────────┐
│ Push to main│
└──────┬──────┘
       │
       ├─────────────────┬────────────────┐
       │                 │                │
       ▼                 ▼                ▼
 ┌──────────┐     ┌──────────┐    ┌───────────────┐
 │ci-backend│     │ci-frontend│   │Check changes  │
 └────┬─────┘     └────┬─────┘    │(backend/*)    │
      │                │           └───────┬───────┘
      │                │                   │
      ▼                │                   │
 ┌──────────────┐      │                   │
 │deploy-backend│      │                   │
 └──────┬───────┘      │                   │
        │              │                   │
        │              │                   ▼
        │              │           ┌───────────────────┐
        │              │           │deploy-agent-engine│
        │              │           │(conditional)      │
        │              │           │                   │
        │              │           │1. Serialize agent │
        │              │           │2. Package deps    │
        │              │           │3. Upload to GCS   │
        │              │           └───────────────────┘
        │              │
        ├──────────────┼──────────────────┐
        │              │                  │
        ▼              ▼                  ▼
    ┌─────────────────────────────────────┐
    │deploy-frontend                      │
    │(needs: [ci-frontend, deploy-backend,│
    │        deploy-agent-engine])        │
    └─────────────────────────────────────┘
```

---

## 技術選定

### CI/CD環境

- **GitHub Actions** - 既存のワークフロー `.github/workflows/cd.yml` を拡張
- **Ubuntu latest runner** - 既存ジョブと同じ環境

### 認証

- **Workload Identity Federation** - 既存の `google-github-actions/auth@v2` を利用
- **GCP Service Account** - 既存のシークレット `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`

### Python環境

- **uv** - バックエンドで使用しているPythonパッケージマネージャー
- **Python 3.12** - uvの推奨バージョン

### GCSアップロード

- **gcloud CLI** - 既存の `google-github-actions/setup-gcloud@v2` を利用

---

## データ設計

### GCSバケット構成

```
gs://homework-coach-assets-XXXXXXXX/
└── agent-engine/
    ├── pickle.pkl                  # シリアライズされたエージェント
    ├── requirements.txt            # Agent Engine 依存関係
    └── dependencies.tar.gz         # backend/app/ のソースコード
```

**バケット名取得:**
```bash
BUCKET_NAME=$(gcloud storage buckets list \
  --format="value(name)" \
  --filter="name:homework-coach-assets")
```

---

## ワークフロー設計

### 新しいジョブ: `deploy-agent-engine`

```yaml
deploy-agent-engine:
  name: Deploy Agent Engine Artifacts
  runs-on: ubuntu-latest
  needs: ci-backend
  permissions:
    contents: read
    id-token: write

  steps:
    # 1. 変更検知
    - name: Checkout
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # 全履歴取得（git diffに必要）

    - name: Check backend changes
      id: backend_changes
      run: |
        # git diff でバックエンド変更を検知
        if git diff --name-only ${{ github.event.before }} ${{ github.sha }} | grep -q '^backend/'; then
          echo "changed=true" >> $GITHUB_OUTPUT
          echo "✓ Backend changes detected"
        else
          echo "changed=false" >> $GITHUB_OUTPUT
          echo "✓ No backend changes, skipping Agent Engine deployment"
        fi

    # 2. Python環境セットアップ（条件付き）
    - name: Set up Python
      if: steps.backend_changes.outputs.changed == 'true'
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install uv
      if: steps.backend_changes.outputs.changed == 'true'
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Install backend dependencies
      if: steps.backend_changes.outputs.changed == 'true'
      working-directory: backend
      run: |
        uv sync

    # 3. エージェントシリアライズ（条件付き）
    - name: Serialize Agent
      if: steps.backend_changes.outputs.changed == 'true'
      working-directory: backend
      run: |
        echo "Serializing Router Agent..."
        uv run python scripts/serialize_agent.py
        if [ ! -f pickle.pkl ]; then
          echo "✗ Error: pickle.pkl not generated"
          exit 1
        fi
        echo "✓ Serialized successfully ($(stat -f%z pickle.pkl) bytes)"

    # 4. 依存関係パッケージ化（条件付き）
    - name: Package dependencies
      if: steps.backend_changes.outputs.changed == 'true'
      working-directory: backend
      run: |
        echo "Packaging dependencies..."
        tar -czf dependencies.tar.gz app/
        if [ ! -f dependencies.tar.gz ]; then
          echo "✗ Error: dependencies.tar.gz not generated"
          exit 1
        fi
        echo "✓ Packaged successfully ($(stat -f%z dependencies.tar.gz) bytes)"

    # 5. GCS認証・アップロード（条件付き）
    - name: Authenticate to Google Cloud
      if: steps.backend_changes.outputs.changed == 'true'
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
        service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}

    - name: Set up Cloud SDK
      if: steps.backend_changes.outputs.changed == 'true'
      uses: google-github-actions/setup-gcloud@v2

    - name: Upload artifacts to GCS
      if: steps.backend_changes.outputs.changed == 'true'
      working-directory: backend
      run: |
        echo "Finding GCS bucket..."
        BUCKET_NAME=$(gcloud storage buckets list \
          --format="value(name)" \
          --filter="name:homework-coach-assets")

        if [ -z "$BUCKET_NAME" ]; then
          echo "✗ Error: No GCS bucket found matching 'homework-coach-assets'"
          exit 1
        fi

        echo "Found bucket: $BUCKET_NAME"
        echo "Uploading artifacts..."

        gcloud storage cp pickle.pkl "gs://${BUCKET_NAME}/agent-engine/" || exit 1
        gcloud storage cp agent_engine_requirements.txt "gs://${BUCKET_NAME}/agent-engine/requirements.txt" || exit 1
        gcloud storage cp dependencies.tar.gz "gs://${BUCKET_NAME}/agent-engine/" || exit 1

        echo "✓ All artifacts uploaded successfully"
        echo "  - gs://${BUCKET_NAME}/agent-engine/pickle.pkl"
        echo "  - gs://${BUCKET_NAME}/agent-engine/requirements.txt"
        echo "  - gs://${BUCKET_NAME}/agent-engine/dependencies.tar.gz"
```

### `deploy-frontend` ジョブの依存関係更新

```yaml
deploy-frontend:
  name: Deploy Frontend
  runs-on: ubuntu-latest
  needs: [ci-frontend, deploy-backend, deploy-agent-engine]  # ← 追加
  # ...
```

**理由:**
- `deploy-agent-engine` の完了を待ってからフロントエンドをデプロイ
- 全デプロイが完了してから一貫性のあるシステムを提供

---

## ファイル構成

### 変更ファイル

```
.github/workflows/
└── cd.yml  # ← 変更: deploy-agent-engine ジョブ追加

backend/
├── scripts/
│   └── serialize_agent.py  # ← 既存（変更なし）
└── agent_engine_requirements.txt  # ← 既存（変更なし）
```

---

## 依存関係

### GitHub Actions

- `actions/checkout@v4` - リポジトリチェックアウト（既存）
- `actions/setup-python@v5` - Python 3.12セットアップ
- `google-github-actions/auth@v2` - Workload Identity Federation認証（既存）
- `google-github-actions/setup-gcloud@v2` - gcloud CLIセットアップ（既存）

### Python

- `uv` - Pythonパッケージマネージャー
- `cloudpickle` - エージェントシリアライズ
- `google-adk` - ADKエージェント
- `backend/app/` - エージェント定義、ツール

### GCP

- **GCS Bucket** - `homework-coach-assets-XXXXXXXX`
- **Service Account** - `github-actions@homework-coach-robo.iam.gserviceaccount.com`
  - 必要な権限: `storage.objects.create`, `storage.objects.get`

---

## エラーハンドリング

### 1. バックエンド変更検知失敗

**原因:**
- `git diff` が失敗（shallow clone等）
- `github.event.before` が空（初回プッシュ等）

**対策:**
```yaml
- name: Check backend changes
  run: |
    if [ -z "${{ github.event.before }}" ]; then
      echo "changed=true" >> $GITHUB_OUTPUT
      echo "⚠ No previous commit (initial push), assuming backend changed"
      exit 0
    fi
    # 通常の git diff ロジック
```

### 2. エージェントシリアライズ失敗

**原因:**
- 依存関係のインストール失敗
- エージェント定義のインポートエラー
- cloudpickleのシリアライズエラー

**対策:**
```bash
uv run python scripts/serialize_agent.py
if [ ! -f pickle.pkl ]; then
  echo "✗ Error: pickle.pkl not generated"
  exit 1
fi
```

### 3. GCSアップロード失敗

**原因:**
- バケットが見つからない
- 権限不足
- ネットワークエラー

**対策:**
```bash
BUCKET_NAME=$(gcloud storage buckets list ...)
if [ -z "$BUCKET_NAME" ]; then
  echo "✗ Error: No GCS bucket found"
  exit 1
fi

gcloud storage cp ... || exit 1
```

---

## セキュリティ考慮事項

### 1. Workload Identity Federation

- **利点**: サービスアカウントキーを使用しない
- **既存実装**: `google-github-actions/auth@v2` で設定済み
- **追加作業**: なし

### 2. アーティファクトの内容検証

- **pickle.pkl**: cloudpickleで安全にシリアライズされたエージェント
- **dependencies.tar.gz**: `backend/app/` のみを含む（`.env`, `.venv` は除外）
- **requirements.txt**: 固定されたバージョン指定

### 3. GCSバケットアクセス

- **読み取り**: Agent Engineサービスアカウントのみ
- **書き込み**: GitHub Actionsサービスアカウントのみ
- **公開アクセス**: 無効

---

## パフォーマンス考慮事項

### 1. 条件付き実行

- バックエンド変更がない場合、Agent Engineステップは完全にスキップ
- フロントエンドのみの変更時、実行時間に影響なし

### 2. キャッシュ戦略（将来の最適化）

- **現時点**: キャッシュなし（依存関係は毎回インストール）
- **将来**: `actions/cache` で `uv` のキャッシュを追加可能

### 3. 並列実行

- `deploy-agent-engine` は `deploy-backend` と並列実行可能
- ただし、`deploy-frontend` は両方の完了を待つ

---

## 代替案と採用理由

### 代替案1: `deploy-backend` ジョブに統合

**メリット:**
- ジョブ数が増えない
- バックエンドデプロイと一緒に実行

**デメリット:**
- Cloud RunデプロイとAgent Engineデプロイの責務が混在
- 保守性が低下
- 条件分岐が複雑化

**採用理由（別ジョブ）:**
- 責務の分離（Cloud Run vs Agent Engine）
- 条件分岐が明確
- 将来の拡張（Agent Engine自動再作成）に対応しやすい

### 代替案2: Terraformでアーティファクトもビルド

**メリット:**
- インフラ定義とアーティファクトビルドが統一

**デメリット:**
- Terraformの `local-exec` プロビジョナーは推奨されない
- CI/CDの責務（ビルド）とTerraformの責務（リソース定義）が混在
- Terraform実行環境にPython依存関係が必要

**採用理由（CI/CD）:**
- Terraformはリソース定義のみに専念
- CI/CDでビルド・デプロイを行う方が一般的
- 既存の設計思想（`lifecycle { ignore_changes = [image] }`）と整合

### 代替案3: Agent Engine自動再作成を含める

**メリット:**
- 完全自動化（手動操作不要）

**デメリット:**
- Agent Engine再作成に5-10分かかる
- CI/CDの実行時間が大幅に増加
- デプロイ失敗のリスク

**採用理由（アーティファクトのみ）:**
- Phase 1: アーティファクトのアップロードのみ自動化
- Phase 2（将来）: Agent Engine再作成を検討
- 実行時間の短縮とリスク低減

---

## 将来の拡張

### Phase 2: Agent Engine自動再作成

```yaml
- name: Recreate Agent Engine (optional)
  if: steps.backend_changes.outputs.changed == 'true'
  run: |
    cd infrastructure/terraform/environments/dev
    terraform taint 'module.agent_engine[0].google_vertex_ai_reasoning_engine.homework_coach_agent'
    terraform apply -auto-approve
```

**検討事項:**
- 実行時間の増加（5-10分）
- Terraform Cloud/Enterprise利用時のAPI認証
- 失敗時のロールバック戦略
