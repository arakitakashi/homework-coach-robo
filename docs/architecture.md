# 宿題コーチロボット - 技術仕様書

**Document Version**: 1.3
**Last Updated**: 2026-02-08
**Status**: MVP設計完了 + Phase 2 エージェントアーキテクチャ追加（ADK 1.23.0+）

---

## 目次

1. [テクノロジースタック](#1-テクノロジースタック)
2. [開発ツールと手法](#2-開発ツールと手法)
3. [技術的制約と要件](#3-技術的制約と要件)
4. [パフォーマンス要件](#4-パフォーマンス要件)
5. [セキュリティとプライバシー](#5-セキュリティとプライバシー)
6. [スケーラビリティ設計](#6-スケーラビリティ設計)
7. [コスト見積もり](#7-コスト見積もり)

---

## 1. テクノロジースタック

### 1.1 フロントエンド

#### フレームワーク・ランタイム

| 技術 | バージョン | 用途 |
|------|-----------|------|
| **Next.js** | 16+ | フロントエンドフレームワーク（App Router使用） |
| **Bun** | 1.0+ | JavaScriptランタイム（高速・All-in-one） |
| **TypeScript** | 5.0+ | 型安全な開発 |
| **React** | 18+ | UIライブラリ（Next.jsに含まれる） |

**Bun採用理由:**
- 高速な起動時間とパッケージインストール（npm比3-4倍高速）
- ビルトインテストランナー・バンドラー
- TypeScriptネイティブサポート
- Next.js 14+と完全互換

#### 主要ライブラリ

```json
{
  "dependencies": {
    "@rive-app/react-canvas": "^4.0.0",
    "jotai": "^2.6.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@types/bun": "^1.0.0",
    "@types/react": "^18.0.0",
    "@biomejs/biome": "^2.0.0"
  }
}
```

#### 音声・画像処理

- **Web Audio API**: PCM 16kHz音声処理
- **Navigator.mediaDevices API**: カメラアクセス（背面カメラ優先）
- **Canvas API**: 画像キャプチャとプレビュー
- **WebSocket**: リアルタイム双方向通信

#### アニメーション

- **Rive** (https://rive.app/): インタラクティブアニメーション
  - ステートマシンによる状態遷移
  - 音声レベルに応じたリップシンク
  - ファイルサイズ: 50-200KB/キャラクター

#### 状態管理

- **Jotai**: Atomic状態管理ライブラリ
  - グローバル状態: ユーザー情報、セッション状態
  - Atomic Design: 小さな単位で状態を管理
  - TypeScript完全サポート
  - React Server Components対応
  - DevTools統合

**Jotai採用理由:**
- Next.js App Routerとの親和性が高い
- ボイラープレートコードが少ない
- テストが容易
- 状態の依存関係を明示的に定義可能

**実装例:**
```typescript
// atoms/session.ts
import { atom } from 'jotai';

export const sessionAtom = atom<Session | null>(null);
export const isRecordingAtom = atom(false);
export const audioLevelAtom = atom(0);

// 派生atom
export const isSessionActiveAtom = atom(
  (get) => get(sessionAtom) !== null
);
```

### 1.2 バックエンド

#### フレームワーク・ランタイム

| 技術 | バージョン | 用途 |
|------|-----------|------|
| **Python** | 3.10+ | バックエンド開発言語 |
| **FastAPI** | 0.115.0+ | Webフレームワーク（REST + WebSocket） |
| **Google ADK** | 1.23.0+ | Agent Development Kit（対話エージェント） |

#### 主要ライブラリ

```python
# requirements.txt
google-adk>=1.23.0
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
websockets>=12.0
google-cloud-speech>=2.20.0
google-cloud-texttospeech>=2.14.0
google-cloud-firestore>=2.11.0
google-cloud-bigquery>=3.10.0
google-cloud-storage>=2.10.0
google-cloud-vision>=3.5.0
firebase-admin>=6.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

#### WebSocket実装

```python
from fastapi import WebSocket

class WebSocketManager:
    """
    双方向ストリーミング通信の管理
    - 音声チャンクの受信・送信
    - セッション状態の同期
    - リアルタイムイベント配信
    """
    pass
```

### 1.3 AI/MLサービス（Google Cloud）

#### Google ADK + Gemini Live API

```python
{
  "model": "gemini-2.5-flash-native-audio-preview",
  "multimodal": ["audio", "image", "text"],
  "streaming": true,
  "latency": "~1000ms (target)",
  "sdk": "google-adk>=1.23.0"
}
```

**主要機能:**
- ネイティブ音声処理（STT/TTS統合）
- マルチモーダル対応（音声 + 画像 + テキスト）
- ストリーミングレスポンス
- 4フェーズライフサイクル（App Init → Session Init → Streaming → Termination）

#### Cloud Speech-to-Text API

```python
{
  "model": "default",
  "language_code": "ja-JP",
  "sample_rate_hertz": 16000,
  "encoding": "LINEAR16",
  "enable_automatic_punctuation": true,
  "model_adaptation": "child_voice_optimized"  # 児童音声最適化
}
```

#### Cloud Text-to-Speech API

```python
{
  "voice": {
    "language_code": "ja-JP",
    "name": "ja-JP-Wavenet-A",  # 自然な音声
    "ssml_gender": "NEUTRAL"
  },
  "audio_config": {
    "audio_encoding": "LINEAR16",
    "sample_rate_hertz": 24000,
    "speaking_rate": 0.9,  # 少しゆっくり（子供向け）
    "pitch": 2.0,  # 少し高め（親しみやすさ）
    "volume_gain_db": 0.0
  }
}
```

**カスタム声質設定:**
| トーン | speaking_rate | pitch | 用途 |
|--------|--------------|-------|------|
| **励まし** | 1.0 | +3.0 | 正解時、達成時 |
| **説明** | 0.85 | +1.0 | 問題説明、ヒント提供 |
| **共感** | 0.9 | +2.0 | 困っている時、励ます時 |
| **考え中** | 0.8 | 0.0 | AIが考えている演出 |

#### Gemini Vision + Cloud Vision API

```python
{
  "model": "gemini-2.0-flash-exp",
  "features": [
    "OCR (handwriting + print)",
    "equation_recognition",
    "diagram_detection",
    "problem_extraction"
  ],
  "confidence_threshold": 0.7,
  "image_format": "JPEG",
  "max_image_size": "1920x1080"
}
```

**画像認識ワークフロー:**
1. 画像キャプチャ（JPEG 90%品質）
2. Gemini Visionで問題文抽出
3. Cloud Vision APIでOCR補完（低信頼度の場合）
4. 数式はLaTeX形式に変換
5. 信頼度 < 0.7の場合はユーザーに確認

### 1.4 データ層（Google Cloud）

#### Cloud Firestore

```javascript
// データ構造
{
  "users": {
    "userId": {
      "name": "string",
      "gradeLevel": "1-3",
      "settings": {
        "preferredCharacter": "robot|wizard|astronaut|animal",
        "voiceSpeed": "number",
        "volumeLevel": "number"
      }
    }
  },
  "sessions": {
    "sessionId": {
      "userId": "string",
      "startTime": "timestamp",
      "endTime": "timestamp?",
      "currentProblemId": "string?",
      "dialogueTurns": "array",  // セッション中のみ保持
      "emotionalState": "string",
      "hintLevel": "0-3"
    }
  },
  "problems": {
    "problemId": {
      "grade": "1-3",
      "subject": "math|reading|writing",
      "text": "string",
      "difficulty": "1-5",
      "hints": ["string[]"]
    }
  }
}
```

**用途:**
- リアルタイムセッション管理
- ユーザープロフィール
- 問題バンク
- 通知・リアルタイム進捗

#### BigQuery

```sql
-- dialogue_sessions テーブル
CREATE TABLE homework_coach.dialogue_sessions (
  session_id STRING NOT NULL,
  user_id STRING NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  problem_ids ARRAY<STRING>,
  total_hints_used INT64,
  self_solved_count INT64,
  total_points INT64,
  dialogue_turns ARRAY<STRUCT<
    turn_id STRING,
    speaker STRING,
    content STRING,
    timestamp TIMESTAMP,
    emotion STRING
  >>,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(start_time)
CLUSTER BY user_id;

-- learning_history テーブル
CREATE TABLE homework_coach.learning_history (
  user_id STRING NOT NULL,
  problem_id STRING NOT NULL,
  attempted_at TIMESTAMP NOT NULL,
  solved_independently BOOLEAN,
  hints_used INT64,
  time_spent_seconds INT64,
  points_earned INT64
)
PARTITION BY DATE(attempted_at)
CLUSTER BY user_id, problem_id;
```

**用途:**
- セッション完了後の対話履歴保存
- 学習進捗の長期分析
- 習熟度レポート生成
- つまずきポイント分析

### 1.5 認証・セキュリティ

#### Firebase Authentication

```javascript
{
  "providers": [
    "email/password",  // 保護者アカウント
    "anonymous"        // 子供アカウント（保護者アカウント配下）
  ],
  "custom_claims": {
    "role": "parent | child",
    "parent_id": "string"  // 子供アカウントの場合
  }
}
```

#### Secret Manager

```bash
# 環境変数の管理
GEMINI_API_KEY=secret:gemini-api-key
FIREBASE_SERVICE_ACCOUNT=secret:firebase-service-account
DATABASE_URL=secret:database-url
```

### 1.6 インフラストラクチャ

#### Cloud Run

**フロントエンド:**
```yaml
service: homework-coach-frontend
runtime: container
image: gcr.io/PROJECT_ID/frontend:latest
resources:
  cpu: 1
  memory: 512Mi
scaling:
  min_instances: 0  # コスト最適化
  max_instances: 10
  target_cpu_utilization: 70
environment_variables:
  NODE_ENV: production
  NEXT_PUBLIC_API_URL: https://api.homework-coach.com
```

**バックエンド:**
```yaml
service: homework-coach-backend
runtime: container
image: gcr.io/PROJECT_ID/backend:latest
resources:
  cpu: 2
  memory: 1Gi
scaling:
  min_instances: 0  # 開発環境: 0、本番環境: 1
  max_instances: 20
  target_cpu_utilization: 70
timeout: 300s  # WebSocket長時間接続用
environment_variables:
  PYTHON_ENV: production
  PORT: 8080
```

**コールドスタート対策:**
- Cloud Scheduler: 5分間隔でwarmupエンドポイントにリクエスト（$0/月）
- Dockerイメージ最適化: マルチステージビルド
- CPU Boost: 起動時のCPU性能向上
- 目標起動時間: 0.5-1.5秒

#### Cloud Storage + Cloud CDN

```yaml
bucket: homework-coach-assets
location: asia-northeast1 (Tokyo)
storage_class: STANDARD
contents:
  - /characters/*.riv       # Riveアニメーションファイル
  - /animations/*.riv       # 宝箱などの演出
  - /audio/common/*.mp3     # よく使う音声（事前生成）
  - /images/icons/*.png     # UIアイコン
  - /agent-engine/          # Agent Engine デプロイアーティファクト（Phase 3）
    - pickle.pkl            # シリアライズされた Router Agent
    - requirements.txt      # Python 依存関係
    - dependencies.tar.gz   # アプリケーションコード（app/）
cdn:
  enabled: true
  cache_ttl: 86400  # 24時間
```

#### Vertex AI Agent Engine（Phase 3）

```yaml
service: homework-coach-agent-engine
region: us-central1
agent_framework: google-adk
python_version: "3.10"
package_spec:
  pickle_object_gcs_uri: gs://homework-coach-assets-{suffix}/agent-engine/pickle.pkl
  requirements_gcs_uri: gs://homework-coach-assets-{suffix}/agent-engine/requirements.txt
  dependency_files_gcs_uri: gs://homework-coach-assets-{suffix}/agent-engine/dependencies.tar.gz
deployment:
  method: Terraform
  module: infrastructure/terraform/modules/agent_engine/
integration:
  - Cloud Run 環境変数に AGENT_ENGINE_RESOURCE_NAME 設定
  - Cloud Run 環境変数に AGENT_ENGINE_ID 設定
  - テキスト対話（/api/v1/dialogue/run）が Agent Engine 経由に切り替え可能
  - フォールバック: ローカル Runner（Cloud Run内実行）
```

**Terraform によるインフラ管理:**

Agent Engine は Terraform モジュールで管理され、`enable_agent_engine` フラグで有効化/無効化可能。

```hcl
# infrastructure/terraform/environments/dev/terraform.tfvars
enable_agent_engine = true
gcp_location        = "us-central1"
```

詳細は `infrastructure/terraform/modules/agent_engine/README.md` および `.steering/20260211-agent-engine-terraform/` を参照。

---

## 2. 開発ツールと手法

### 2.1 開発環境

#### 言語・ランタイムバージョン

```bash
# フロントエンド
bun --version   # v1.0.0+

# バックエンド
python --version  # Python 3.10.0+
uv --version      # uv 0.1.0+
```

#### パッケージ管理

**フロントエンド: Bun（決定）**
```bash
# パッケージインストール
bun install

# 開発サーバー起動
bun run dev

# プロダクションビルド
bun run build

# テスト実行
bun test

# 依存関係の追加
bun add <package>
bun add -d <dev-package>
```

**Bunの利点:**
- インストール速度: npm比3-4倍高速
- ビルトインテストランナー（Jest互換）
- ビルトインバンドラー（Webpackの代替）
- TypeScript/JSX直接実行
- package.json互換（npm/yarnからの移行が容易）

**バックエンド: uv（決定）**
```bash
# uvインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# パッケージインストール
uv pip install -r requirements.txt

# 依存関係の同期（lockファイル使用）
uv pip sync requirements.txt

# 仮想環境作成
uv venv

# パッケージ追加
uv pip install <package>
```

**uvの利点:**
- インストール速度: pip比10-100倍高速
- Rust実装で高速・安全
- pip完全互換
- requirements.txtロック機能
- メモリ効率が良い

### 2.2 開発ツール

#### IDE・エディタ

| ツール | 推奨プラグイン |
|--------|--------------|
| **VS Code** | Biome, Python, Pylance, Ruff, Docker |
| **Cursor** | 上記 + AI code completion |

#### コード品質管理

**フロントエンド:**
```json
{
  "scripts": {
    "lint": "biome lint .",
    "format": "biome format --write .",
    "check": "biome check .",
    "type-check": "tsc --noEmit"
  }
}
```

**バックエンド:**
```bash
# Linting & Formatting (Ruff - Black/isort/flake8の統合代替)
ruff check .             # リンター
ruff format .            # コードフォーマット
mypy .                   # 型チェック
```

#### テストフレームワーク

**フロントエンド:**
```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "vitest": "^1.0.0"
  }
}
```

**バックエンド:**
```bash
pytest                   # ユニットテスト
pytest-asyncio           # 非同期テスト
pytest-cov               # カバレッジ
```

### 2.3 CI/CDパイプライン

#### 前提条件: Workload Identity Federation (WIF)

GitHub ActionsからGCPへの認証にはWorkload Identity Federationを使用する。
CDおよびマニュアルデプロイが動作するために、以下の設定が必須。

**GCP側の設定:**

| リソース | 値 |
|----------|-----|
| Service Account | `github-actions@homework-coach-robo.iam.gserviceaccount.com` |
| Workload Identity Pool | `github-pool`（global） |
| Workload Identity Provider | `github-provider`（OIDC） |
| OIDC Issuer URI | `https://token.actions.githubusercontent.com` |
| Attribute Condition | `assertion.repository_owner == 'arakitakashi'` |

Service Accountに必要なロール:
- `roles/artifactregistry.writer` — Docker Push
- `roles/run.admin` — Cloud Runデプロイ
- `roles/iam.serviceAccountUser` — Service Account実行
- `roles/storage.objectAdmin` — GCS バケットへのオブジェクト読み書き（Agent Engine アーティファクトアップロード）

**GitHub Secrets:**

| Secret名 | 値 |
|-----------|-----|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/652907685934/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `github-actions@homework-coach-robo.iam.gserviceaccount.com` |
| `GCS_ASSETS_BUCKET` | GCS アセットバケット名（Agent Engine アーティファクトアップロード先） |

セットアップ手順の詳細は `.steering/20260206-github-actions-cicd/gcp-wif-setup.md` を参照。

#### GitHub Actions ワークフロー構成

| ワークフロー | ファイル | トリガー | 用途 |
|-------------|---------|---------|------|
| Backend CI | `ci-backend.yml` | push/PR to main, workflow_call | Lint, TypeCheck, Test |
| Frontend CI | `ci-frontend.yml` | push/PR to main, workflow_call | Lint, TypeCheck, Test, Build |
| CD | `cd.yml` | push to main | CI実行後、自動デプロイ |
| Deploy (Manual) | `deploy.yml` | workflow_dispatch | CI実行後、手動デプロイ |

#### CI → CD フロー（自動デプロイ）

```
push to main
  └── CD workflow
        ├── CI Backend (lint → typecheck → test)
        ├── CI Frontend (lint → typecheck → test → build)
        ├── Deploy Backend (CI Backend通過後)
        │     ├── Docker Build → Artifact Registry Push
        │     └── Cloud Run Deploy
        └── Deploy Frontend (CI Frontend + Deploy Backend通過後)
              ├── Backend URL取得
              ├── Docker Build (NEXT_PUBLIC_API_URL注入) → Artifact Registry Push
              └── Cloud Run Deploy
```

#### マニュアルデプロイ

GitHub UI の **Actions > "Deploy (Manual)" > "Run workflow"** から実行可能。

- **デプロイ対象**: `backend` / `frontend` / `both` を選択
- **環境**: `dev`（将来的にstaging/prodを追加予定）
- CIチェック通過後にのみデプロイが実行される
- デプロイ後にヘルスチェックで自動検証

#### Cloud Build（代替デプロイ手段）

`infrastructure/cloud-build/` にCloud Buildパイプラインも用意されている。
GitHub Actions以外のデプロイ手段として使用可能。

| 設定ファイル | 用途 |
|-------------|------|
| `cloudbuild-backend.yaml` | バックエンドのビルド・デプロイ |
| `cloudbuild-frontend.yaml` | フロントエンドのビルド・デプロイ |
| `cloudbuild-infrastructure.yaml` | Terraformによるインフラ管理 |

### 2.4 開発手法

#### アジャイル・スクラム

- **スプリント期間**: 2週間
- **デイリースタンドアップ**: 毎朝15分
- **スプリントレビュー**: スプリント終了時
- **レトロスペクティブ**: スプリント終了後

#### ブランチ戦略（Git Flow）

```
main (本番環境)
  ↑
develop (開発環境)
  ↑
feature/xxx (機能開発)
hotfix/xxx (緊急修正)
```

#### コミットメッセージ規約

```bash
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードフォーマット
refactor: リファクタリング
test: テスト追加
chore: ビルド・設定変更

# 例:
git commit -m "feat: CameraInterface component for image recognition"
git commit -m "fix: resolve cold start issue in Cloud Run"
```

### 2.5 モニタリング・ロギング

#### Cloud Logging

```python
import logging
from google.cloud import logging as cloud_logging

# Cloud Logging設定
client = cloud_logging.Client()
client.setup_logging()

logger = logging.getLogger(__name__)

# 構造化ログ
logger.info(
    "Session started",
    extra={
        "session_id": session_id,
        "user_id": user_id,
        "character": character_type
    }
)
```

#### Cloud Monitoring

```yaml
# アラート設定
alerts:
  - name: "High Error Rate"
    condition: error_rate > 5%
    duration: 5m
    notification: email, slack

  - name: "High Latency"
    condition: p95_latency > 3000ms
    duration: 5m
    notification: email, slack

  - name: "Low Memory"
    condition: memory_usage > 80%
    duration: 5m
    notification: email
```

#### Cloud Trace

- エンドツーエンドのリクエスト追跡
- レイテンシ分析
- ボトルネック特定

---

## 3. 技術的制約と要件

### 3.1 ブラウザ要件

#### サポートブラウザ

| ブラウザ | 最小バージョン | 備考 |
|---------|--------------|------|
| **Chrome** | 90+ | 推奨ブラウザ |
| **Safari** | 14+ | iOS/macOS |
| **Edge** | 90+ | Chromiumベース |
| **Firefox** | 88+ | 基本サポート |

#### 必須Web API

```javascript
// 必須機能のチェック
const requiredAPIs = {
  webAudio: 'AudioContext' in window,
  webSocket: 'WebSocket' in window,
  mediaDevices: navigator.mediaDevices && navigator.mediaDevices.getUserMedia,
  canvas: 'HTMLCanvasElement' in window,
  localStorage: 'localStorage' in window
};

if (!Object.values(requiredAPIs).every(Boolean)) {
  console.error('Required APIs not supported');
}
```

### 3.2 ネットワーク要件

#### 帯域幅

| 用途 | 最小帯域幅 | 推奨帯域幅 |
|------|-----------|-----------|
| **音声ストリーミング** | 64 kbps | 128 kbps |
| **画像アップロード** | 512 kbps | 1 Mbps |
| **WebSocket通信** | 128 kbps | 256 kbps |
| **合計** | **1 Mbps** | **3 Mbps** |

#### レイテンシ

- **RTT (Round Trip Time)**: < 200ms
- **パケットロス**: < 1%

### 3.3 デバイス要件

#### クライアントデバイス

**最小スペック:**
- CPU: デュアルコア 1.5GHz+
- RAM: 2GB+
- マイク: 内蔵 or 外付け
- カメラ: 2MP+ (オプション)

**推奨スペック:**
- CPU: クアッドコア 2.0GHz+
- RAM: 4GB+
- マイク: ノイズキャンセリング対応
- カメラ: 5MP+ 背面カメラ

### 3.4 データ保護要件（GDPR/個人情報保護法）

#### データ分類

| データタイプ | 保持期間 | 暗号化 | アクセス制御 |
|------------|---------|-------|------------|
| **ユーザープロフィール** | アカウント削除まで | ✅ | 厳密 |
| **セッション音声** | 保存しない | N/A | N/A |
| **対話履歴（テキスト）** | 1年間 | ✅ | 厳密 |
| **学習進捗データ** | 3年間 | ✅ | 中程度 |
| **匿名化された集計データ** | 無期限 | ❌ | 緩い |

#### データ削除ポリシー

```python
async def delete_user_data(user_id: str):
    """
    ユーザーデータの完全削除（GDPR Right to be Forgotten）
    """
    # Firestoreから削除
    await firestore.collection('users').document(user_id).delete()
    await firestore.collection('sessions').where('userId', '==', user_id).delete()

    # BigQueryから削除（論理削除）
    await bigquery.query(f"""
        UPDATE homework_coach.dialogue_sessions
        SET user_id = 'DELETED', anonymized = TRUE
        WHERE user_id = '{user_id}'
    """)
```

### 3.5 音声処理制約

#### 入力音声フォーマット

```javascript
{
  "encoding": "PCM_16",
  "sampleRate": 16000,  // 16kHz
  "channels": 1,        // モノラル
  "bitDepth": 16        // 16-bit
}
```

#### 音声品質要件

- **SNR (Signal-to-Noise Ratio)**: > 20dB
- **周波数応答**: 100Hz - 8kHz
- **最大音声長**: 30秒/ターン

### 3.6 画像処理制約

#### 入力画像フォーマット

```javascript
{
  "format": "JPEG",
  "quality": 90,
  "maxResolution": "1920x1080",
  "maxFileSize": "5MB",
  "colorSpace": "RGB"
}
```

#### 画像認識要件

- **最小文字サイズ**: 12pt
- **最小コントラスト**: 4.5:1
- **明るさ**: 適度な照明環境

---

## 4. パフォーマンス要件

### 4.1 レイテンシ目標

```typescript
interface LatencyTargets {
  stt: {
    target: 200,      // ms
    maximum: 500      // ms
  };

  llm: {
    target: 1000,     // ms
    maximum: 2000     // ms
  };

  tts: {
    target: 300,      // ms
    maximum: 500      // ms
  };

  vision: {
    target: 2000,     // ms（画像認識）
    maximum: 5000     // ms
  };

  endToEnd: {
    target: 1500,     // ms（音声入力完了から応答音声開始まで）
    maximum: 3000     // ms
  };
}
```

### 4.2 スループット目標

| メトリクス | 目標値 |
|-----------|--------|
| **同時接続数** | 100+ |
| **リクエスト/秒** | 50+ |
| **WebSocket接続数** | 100+ |

### 4.3 最適化戦略

#### 4.3.1 音声ストリーミング最適化

```typescript
class AudioOptimizer {
  // チャンク化して逐次送信
  streamAudio(audioData: ArrayBuffer): void {
    const chunkSize = 4096; // bytes
    const chunks = this.splitIntoChunks(audioData, chunkSize);

    chunks.forEach((chunk, index) => {
      this.sendChunk(chunk, index);
    });
  }

  // 音声圧縮
  compressAudio(audio: ArrayBuffer): ArrayBuffer {
    return opus.encode(audio, {
      bitrate: 24000,  // 24kbps
      sampleRate: 16000 // 16kHz
    });
  }
}
```

#### 4.3.2 LLM応答の最適化

```python
class LLMOptimizer:
    async def generate_response(self, prompt: str):
        """ストリーミングレスポンスで低レイテンシ"""
        stream = await self.llm.stream_completion(prompt)
        async for chunk in stream:
            yield chunk

    async def get_cached_response(self, context: DialogueContext):
        """頻出パターンのキャッシング"""
        cache_key = self.generate_cache_key(context)
        return await self.cache.get(cache_key)
```

#### 4.3.3 TTS事前生成

```python
class TTSOptimizer:
    def pre_generate_common_phrases(self):
        """よく使うフレーズを事前生成してキャッシュ"""
        common_phrases = [
            'すごいね！',
            'いい感じだよ',
            'もう一回言ってくれる？',
            'ゆっくり考えてみよう'
        ]

        for phrase in common_phrases:
            audio = await self.tts.synthesize(phrase)
            await self.cache.set(f"tts:{phrase}", audio, ttl=86400)
```

#### 4.3.4 画像処理最適化

```typescript
class ImageOptimizer {
  // 画像圧縮
  compressImage(canvas: HTMLCanvasElement): string {
    return canvas.toDataURL('image/jpeg', 0.9); // 90%品質
  }

  // プログレッシブ処理
  async processImage(imageData: string) {
    // 1. 低解像度でクイックプレビュー
    const preview = await this.quickRecognition(imageData);
    this.showPreview(preview);

    // 2. 高精度で最終認識
    const final = await this.fullRecognition(imageData);
    this.showFinalResult(final);
  }
}
```

### 4.4 リソース使用量目標

#### メモリ使用量

| コンポーネント | 最大メモリ |
|--------------|-----------|
| **フロントエンド** | 512 Mi |
| **バックエンド** | 1 Gi |

#### CPU使用率

- **平常時**: < 30%
- **ピーク時**: < 70%

---

## 5. セキュリティとプライバシー

### 5.1 認証・認可

```python
from fastapi import Depends, HTTPException
from firebase_admin import auth

async def verify_token(token: str):
    """Firebase IDトークン検証"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/sessions/{session_id}")
async def get_session(
    session_id: str,
    user = Depends(verify_token)
):
    # ユーザーは自分のセッションのみアクセス可能
    if session.user_id != user['uid']:
        raise HTTPException(status_code=403, detail="Forbidden")
    return session
```

### 5.2 データ暗号化

- **転送中**: TLS 1.3
- **保存時**: Google Cloud Storage Encryption

### 5.3 APIレート制限

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/vision/recognize")
@limiter.limit("10/minute")  # 1分間に10リクエストまで
async def recognize_image(request: VisionRequest):
    pass
```

---

## 6. スケーラビリティ設計

### 6.1 水平スケーリング

```yaml
# Cloud Run Auto-scaling
min_instances: 0
max_instances: 20
target_cpu_utilization: 70
target_concurrency: 80  # 1インスタンスあたり80並行リクエスト
```

### 6.2 データベーススケーリング

- **Firestore**: 自動スケール（最大10,000 writes/秒）
- **BigQuery**: ペタバイト級スケール対応

---

## 7. コスト見積もり

### 7.1 月間コスト見積もり（100ユーザー想定）

| サービス | 使用量 | 月額費用 |
|---------|-------|---------|
| **Cloud Run (Frontend)** | 10GB-hours | $2 |
| **Cloud Run (Backend)** | 50GB-hours | $10 |
| **Firestore** | 10GB storage, 1M reads | $3 |
| **BigQuery** | 10GB storage, 1TB queries | $6 |
| **Cloud Storage** | 5GB | $0.10 |
| **Cloud CDN** | 10GB transfer | $1 |
| **Gemini API** | 10K requests | $20 |
| **Cloud Speech-to-Text** | 100時間 | $14 |
| **Cloud Text-to-Speech** | 100時間 | $40 |
| **合計** | - | **$96.10** |

### 7.2 コスト最適化戦略

1. **最小インスタンス0**: 低トラフィック時のコスト削減
2. **TTSキャッシング**: 同じフレーズの再生成を回避
3. **CDN活用**: 静的アセットの配信コスト削減
4. **BigQueryパーティショニング**: クエリコスト削減

---

## 付録

### A. 参考資料

- [Google ADK Documentation](https://cloud.google.com/agent-development-kit)
- [Gemini Live API Guide](https://cloud.google.com/gemini/docs/live-api)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Rive Documentation](https://rive.app/community/doc/)

### B. 用語集

- **ADK**: Agent Development Kit（エージェント開発キット）
- **STT**: Speech-to-Text（音声テキスト変換）
- **TTS**: Text-to-Speech（テキスト音声変換）
- **OCR**: Optical Character Recognition（光学文字認識）
- **RTT**: Round Trip Time（往復遅延時間）
- **MVP**: Minimum Viable Product（実用最小限の製品）

