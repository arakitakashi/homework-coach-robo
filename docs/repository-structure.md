# 宿題コーチロボット - リポジトリ構造定義書

**Document Version**: 1.1
**Last Updated**: 2026-01-29
**Status**: MVP構造定義（Kubernetes削除）

---

## 目次

1. [概要](#1-概要)
2. [リポジトリ全体構造](#2-リポジトリ全体構造)
3. [ディレクトリ詳細](#3-ディレクトリ詳細)
4. [ファイル配置ルール](#4-ファイル配置ルール)
5. [命名規則](#5-命名規則)
6. [環境設定ファイル](#6-環境設定ファイル)
7. [セキュリティ考慮事項](#7-セキュリティ考慮事項)

---

## 1. 概要

本ドキュメントは、宿題コーチロボットプロジェクトのリポジトリ構造を定義します。

### 1.1 リポジトリタイプ

**モノレポ (Monorepo)** 構成を採用

**理由:**
- フロントエンド・バックエンドの依存関係を一元管理
- 共通型定義・ユーティリティの共有が容易
- CI/CDパイプラインの統一管理
- バージョン管理の一貫性

### 1.2 技術スタック（再掲）

- **フロントエンド**: Next.js 14+ (App Router) + Bun
- **バックエンド**: FastAPI + Python 3.10+ + uv
- **インフラ**: Google Cloud Run
- **データ**: Firestore, BigQuery, Redis
- **AI**: Google ADK + Gemini Live API

---

## 2. リポジトリ全体構造

```
homework-coach-robo/
├── .github/                      # GitHub設定
│   ├── workflows/                # GitHub Actions
│   │   ├── ci-frontend.yml       # フロントエンドCI
│   │   ├── ci-backend.yml        # バックエンドCI
│   │   ├── deploy-staging.yml    # ステージング環境デプロイ
│   │   └── deploy-production.yml # 本番環境デプロイ
│   ├── ISSUE_TEMPLATE/           # Issueテンプレート
│   └── PULL_REQUEST_TEMPLATE.md  # PRテンプレート
│
├── .vscode/                      # VS Code設定（オプション）
│   ├── settings.json             # ワークスペース設定
│   ├── extensions.json           # 推奨拡張機能
│   └── launch.json               # デバッグ設定
│
├── frontend/                     # フロントエンドアプリケーション
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/               # 認証グループルート
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (main)/               # メインアプリグループルート
│   │   │   ├── home/
│   │   │   ├── session/
│   │   │   └── result/
│   │   ├── api/                  # API Routes
│   │   │   ├── auth/
│   │   │   └── health/
│   │   ├── layout.tsx            # ルートレイアウト
│   │   ├── page.tsx              # ルートページ
│   │   └── globals.css           # グローバルスタイル
│   ├── components/               # Reactコンポーネント
│   │   ├── ui/                   # 汎用UIコンポーネント
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   ├── features/             # 機能別コンポーネント
│   │   │   ├── VoiceInterface/
│   │   │   │   ├── VoiceInterface.tsx
│   │   │   │   ├── AudioVisualizer.tsx
│   │   │   │   └── index.ts
│   │   │   ├── CharacterAvatar/
│   │   │   │   ├── CharacterAvatar.tsx
│   │   │   │   ├── useRiveAnimation.ts
│   │   │   │   └── index.ts
│   │   │   ├── CameraInterface/
│   │   │   │   ├── CameraInterface.tsx
│   │   │   │   ├── ImagePreview.tsx
│   │   │   │   └── index.ts
│   │   │   ├── HintBox/
│   │   │   └── ProgressTracker/
│   │   └── layouts/              # レイアウトコンポーネント
│   │       ├── Header.tsx
│   │       └── Footer.tsx
│   ├── lib/                      # ユーティリティ・ヘルパー
│   │   ├── api/                  # APIクライアント
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── session.ts
│   │   │   └── vision.ts
│   │   ├── hooks/                # カスタムフック
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useAudioRecorder.ts
│   │   │   ├── useSession.ts
│   │   │   └── useCamera.ts
│   │   ├── utils/                # 汎用ユーティリティ
│   │   │   ├── audio.ts
│   │   │   ├── format.ts
│   │   │   └── validation.ts
│   │   └── constants.ts          # 定数定義
│   ├── store/                    # Jotai atoms
│   │   ├── atoms/
│   │   │   ├── session.ts
│   │   │   ├── user.ts
│   │   │   ├── audio.ts
│   │   │   └── ui.ts
│   │   └── index.ts
│   ├── types/                    # TypeScript型定義
│   │   ├── api.ts
│   │   ├── session.ts
│   │   ├── user.ts
│   │   └── index.ts
│   ├── public/                   # 静的ファイル
│   │   ├── characters/           # Riveキャラクターファイル
│   │   │   ├── robot.riv
│   │   │   ├── wizard.riv
│   │   │   ├── astronaut.riv
│   │   │   └── animal.riv
│   │   ├── animations/           # Riveアニメーション
│   │   │   ├── treasure-chest.riv
│   │   │   └── sparkles.riv
│   │   ├── icons/                # アイコン
│   │   └── favicon.ico
│   ├── tests/                    # テスト
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── .env.local.example        # 環境変数テンプレート
│   ├── .eslintrc.json            # ESLint設定
│   ├── .prettierrc               # Prettier設定
│   ├── bun.lockb                 # Bun lockfile
│   ├── Dockerfile                # Docker設定
│   ├── next.config.js            # Next.js設定
│   ├── package.json              # パッケージ定義
│   ├── tsconfig.json             # TypeScript設定
│   └── README.md                 # フロントエンド説明
│
├── backend/                      # バックエンドアプリケーション
│   ├── app/                      # FastAPIアプリケーション
│   │   ├── api/                  # APIエンドポイント
│   │   │   ├── v1/               # API v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── sessions.py
│   │   │   │   ├── users.py
│   │   │   │   ├── problems.py
│   │   │   │   ├── vision.py
│   │   │   │   └── websocket.py
│   │   │   └── deps.py           # 依存性注入
│   │   ├── core/                 # コア機能
│   │   │   ├── config.py         # 設定管理
│   │   │   ├── security.py       # セキュリティ
│   │   │   └── logging.py        # ロギング設定
│   │   ├── models/               # データモデル（Pydantic）
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── problem.py
│   │   │   └── dialogue.py
│   │   ├── schemas/              # APIスキーマ
│   │   │   ├── auth.py
│   │   │   ├── session.py
│   │   │   ├── user.py
│   │   │   └── vision.py
│   │   ├── services/             # ビジネスロジック
│   │   │   ├── adk/              # Google ADK関連
│   │   │   │   ├── agent.py
│   │   │   │   ├── runner.py
│   │   │   │   ├── session_service.py
│   │   │   │   └── tools.py
│   │   │   ├── auth_service.py
│   │   │   ├── session_service.py
│   │   │   ├── dialogue_service.py
│   │   │   ├── vision_service.py
│   │   │   ├── tts_service.py
│   │   │   ├── stt_service.py
│   │   │   └── bigquery_service.py
│   │   ├── db/                   # データベース関連
│   │   │   ├── firestore.py      # Firestoreクライアント
│   │   │   ├── bigquery.py       # BigQueryクライアント
│   │   │   └── redis.py          # Redisクライアント
│   │   ├── websocket/            # WebSocket管理
│   │   │   ├── manager.py
│   │   │   ├── handlers.py
│   │   │   └── events.py
│   │   ├── utils/                # ユーティリティ
│   │   │   ├── audio.py
│   │   │   ├── image.py
│   │   │   └── validators.py
│   │   └── main.py               # FastAPIアプリケーションエントリーポイント
│   ├── tests/                    # テスト
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── scripts/                  # スクリプト
│   │   ├── init_firestore.py    # Firestore初期化
│   │   ├── seed_problems.py     # 問題データシード
│   │   └── migrate_bigquery.py  # BigQueryマイグレーション
│   ├── .env.example              # 環境変数テンプレート
│   ├── .python-version           # Pythonバージョン指定
│   ├── Dockerfile                # Docker設定
│   ├── pyproject.toml            # Python設定（Black, isort等）
│   ├── requirements.txt          # Python依存関係
│   ├── requirements-dev.txt      # 開発用依存関係
│   └── README.md                 # バックエンド説明
│
├── shared/                       # 共通リソース
│   ├── types/                    # 共通型定義
│   │   ├── api.ts                # API型（TypeScript）
│   │   ├── models.py             # モデル型（Python）
│   │   └── README.md
│   └── constants/                # 共通定数
│       ├── error_codes.ts
│       └── error_codes.py
│
├── infrastructure/               # インフラ設定
│   ├── terraform/                # Terraform（IaC）
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   ├── modules/
│   │   │   ├── cloud_run/
│   │   │   ├── firestore/
│   │   │   ├── bigquery/
│   │   │   └── redis/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── cloud-build/              # Cloud Build設定
│       ├── cloudbuild-frontend.yaml
│       └── cloudbuild-backend.yaml
│
├── scripts/                      # プロジェクト全体スクリプト
│   ├── setup.sh                  # 初回セットアップ
│   ├── dev.sh                    # 開発環境起動
│   ├── test.sh                   # 全テスト実行
│   ├── build.sh                  # 全ビルド
│   └── deploy.sh                 # デプロイ
│
├── docs/                         # ドキュメント
│   ├── product-requirements.md   # プロダクト要求仕様書
│   ├── functional-design.md      # 機能設計書
│   ├── architecture.md           # 技術仕様書
│   ├── repository-structure.md   # 本ドキュメント
│   ├── firestore-design.md       # Firestore設計
│   ├── cost-analysis.md          # コスト分析
│   ├── api/                      # API仕様書
│   │   ├── rest-api.md
│   │   └── websocket-api.md
│   ├── guides/                   # 開発ガイド
│   │   ├── getting-started.md
│   │   ├── contributing.md
│   │   └── deployment.md
│   └── images/                   # ドキュメント用画像
│
├── .gitignore                    # Git除外設定
├── .editorconfig                 # エディタ設定
├── CLAUDE.md                     # Claude Codeプロジェクト指示書
├── README.md                     # プロジェクト説明
├── LICENSE                       # ライセンス
└── CHANGELOG.md                  # 変更履歴
```

---

## 3. ディレクトリ詳細

### 3.1 フロントエンド (`frontend/`)

#### 3.1.1 `app/` - Next.js App Router

```
app/
├── (auth)/          # 認証関連ページグループ
├── (main)/          # メインアプリページグループ
├── api/             # API Routes（バックエンドプロキシ等）
├── layout.tsx       # ルートレイアウト
├── page.tsx         # ルートページ（リダイレクトまたはランディング）
└── globals.css      # グローバルスタイル
```

**ルートグループ規約:**
- `(auth)` - 認証が不要なページ
- `(main)` - 認証が必要なメインアプリ

#### 3.1.2 `components/` - Reactコンポーネント

```
components/
├── ui/              # 汎用UIコンポーネント（ボタン、カード等）
├── features/        # 機能別コンポーネント（大きな機能単位）
└── layouts/         # レイアウトコンポーネント
```

**配置ルール:**
- 1ファイル1コンポーネント原則
- 各フィーチャーディレクトリに `index.ts` でエクスポート集約
- テストファイルは同じディレクトリに `*.test.tsx`

#### 3.1.3 `lib/` - ユーティリティ

```
lib/
├── api/             # APIクライアント（バックエンド通信）
├── hooks/           # カスタムReact Hooks
├── utils/           # 汎用ヘルパー関数
└── constants.ts     # 定数定義
```

#### 3.1.4 `store/` - Jotai状態管理

```
store/
├── atoms/           # 個別Atom定義
│   ├── session.ts   # セッション関連atom
│   ├── user.ts      # ユーザー関連atom
│   ├── audio.ts     # 音声関連atom
│   └── ui.ts        # UI状態atom
└── index.ts         # atom集約エクスポート
```

**Atom命名規則:**
```typescript
// Primitive atom
export const sessionAtom = atom<Session | null>(null);

// Derived atom (読み取り専用)
export const isSessionActiveAtom = atom(
  (get) => get(sessionAtom) !== null
);

// Derived atom (読み書き)
export const sessionWithDefaultAtom = atom(
  (get) => get(sessionAtom) ?? DEFAULT_SESSION,
  (get, set, newSession: Session) => {
    set(sessionAtom, newSession);
  }
);
```

#### 3.1.5 `types/` - TypeScript型定義

```
types/
├── api.ts           # APIリクエスト・レスポンス型
├── session.ts       # セッション関連型
├── user.ts          # ユーザー関連型
├── problem.ts       # 問題関連型
└── index.ts         # 型集約エクスポート
```

#### 3.1.6 `public/` - 静的ファイル

```
public/
├── characters/      # Riveキャラクターファイル（.riv）
├── animations/      # Riveアニメーション（.riv）
├── icons/           # アイコン画像
└── favicon.ico
```

**配信方法:**
- Next.jsが自動的に `/` ルートから配信
- Riveファイルは `/characters/robot.riv` でアクセス可能

### 3.2 バックエンド (`backend/`)

#### 3.2.1 `app/api/` - APIエンドポイント

```
app/api/
├── v1/              # API Version 1
│   ├── auth.py      # 認証エンドポイント
│   ├── sessions.py  # セッション管理
│   ├── users.py     # ユーザー管理
│   ├── problems.py  # 問題管理
│   ├── vision.py    # 画像認識
│   └── websocket.py # WebSocket接続
└── deps.py          # 依存性注入（Firebase Auth等）
```

**エンドポイント命名:**
```python
# RESTful規約
GET    /api/v1/users/{user_id}
POST   /api/v1/sessions
PUT    /api/v1/sessions/{session_id}
DELETE /api/v1/sessions/{session_id}

# WebSocket
WS     /api/v1/ws/session/{session_id}
```

#### 3.2.2 `app/services/` - ビジネスロジック

```
app/services/
├── adk/                    # Google ADK関連
│   ├── agent.py            # エージェント定義
│   ├── runner.py           # ADK Runner
│   ├── session_service.py  # Firestoreセッションサービス
│   └── tools.py            # ADK Tools（ヒントシステム等）
├── auth_service.py         # 認証サービス
├── dialogue_service.py     # 対話管理サービス
├── vision_service.py       # 画像認識サービス
└── bigquery_service.py     # BigQuery連携
```

**サービス層の責務:**
- ビジネスロジックの実装
- 外部サービス（GCP APIs）との通信
- データベース操作の抽象化

#### 3.2.3 `app/models/` vs `app/schemas/`

**models/** - データモデル（内部表現）
```python
# models/session.py
from pydantic import BaseModel

class Session(BaseModel):
    id: str
    user_id: str
    start_time: datetime
    # Firestoreに保存する形式
```

**schemas/** - APIスキーマ（外部I/O）
```python
# schemas/session.py
from pydantic import BaseModel

class SessionCreateRequest(BaseModel):
    user_id: str
    character: str

class SessionResponse(BaseModel):
    id: str
    user_id: str
    status: str
    # クライアントに返す形式
```

#### 3.2.4 `app/db/` - データベースクライアント

```
app/db/
├── firestore.py     # Firestoreクライアント（シングルトン）
├── bigquery.py      # BigQueryクライアント
└── redis.py         # Redisクライアント
```

### 3.3 共通リソース (`shared/`)

```
shared/
├── types/           # 共通型定義
│   ├── api.ts       # TypeScript用API型
│   └── models.py    # Python用モデル型
└── constants/       # 共通定数
    ├── error_codes.ts
    └── error_codes.py
```

**使用例:**
```typescript
// frontend/lib/api/client.ts
import { ErrorCode } from '@/../../shared/constants/error_codes';
```

```python
# backend/app/api/v1/auth.py
from shared.constants.error_codes import ErrorCode
```

### 3.4 インフラストラクチャ (`infrastructure/`)

#### 3.4.1 `terraform/` - Infrastructure as Code

```
terraform/
├── environments/
│   ├── dev/         # 開発環境
│   ├── staging/     # ステージング環境
│   └── production/  # 本番環境
├── modules/
│   ├── cloud_run/   # Cloud Runモジュール
│   ├── firestore/   # Firestoreモジュール
│   └── bigquery/    # BigQueryモジュール
└── main.tf
```

**Terraform構成:**
```hcl
# environments/dev/main.tf
module "cloud_run_frontend" {
  source = "../../modules/cloud_run"

  service_name = "homework-coach-frontend-dev"
  image        = "gcr.io/project/frontend:latest"
  region       = "asia-northeast1"

  env_vars = {
    NODE_ENV = "development"
  }
}
```

### 3.5 ドキュメント (`docs/`)

```
docs/
├── *.md             # 設計ドキュメント
├── api/             # API仕様書
├── guides/          # 開発ガイド
└── images/          # ドキュメント用画像
```

---

## 4. ファイル配置ルール

### 4.1 フロントエンド

#### コンポーネント配置

```
components/features/VoiceInterface/
├── VoiceInterface.tsx          # メインコンポーネント
├── VoiceInterface.test.tsx     # テスト
├── AudioVisualizer.tsx         # サブコンポーネント
├── useVoiceRecorder.ts         # カスタムフック
├── VoiceInterface.module.css   # スタイル（必要に応じて）
└── index.ts                    # エクスポート集約
```

**index.ts パターン:**
```typescript
export { VoiceInterface } from './VoiceInterface';
export { AudioVisualizer } from './AudioVisualizer';
export { useVoiceRecorder } from './useVoiceRecorder';
```

#### API クライアント配置

```
lib/api/
├── client.ts        # 基底APIクライアント（axios設定等）
├── auth.ts          # 認証関連API
├── session.ts       # セッション関連API
└── vision.ts        # 画像認識API
```

**client.ts 例:**
```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 4.2 バックエンド

#### サービス層配置

```
app/services/
├── base_service.py          # 基底サービスクラス
├── auth_service.py
├── session_service.py
└── adk/
    ├── __init__.py
    ├── agent.py
    └── tools.py
```

**基底サービスパターン:**
```python
# base_service.py
class BaseService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

# auth_service.py
class AuthService(BaseService):
    def __init__(self, firestore_client):
        super().__init__()
        self.db = firestore_client
```

#### テスト配置

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_auth_service.py
│   │   └── test_session_service.py
│   └── api/
│       └── test_auth_endpoints.py
├── integration/
│   ├── test_session_flow.py
│   └── test_vision_integration.py
└── conftest.py              # Pytest fixtures
```

---

## 5. 命名規則

### 5.1 ディレクトリ命名

| タイプ | 規則 | 例 |
|--------|------|-----|
| **フロントエンド** | kebab-case | `voice-interface/`, `audio-visualizer/` |
| **バックエンド** | snake_case | `auth_service/`, `adk_tools/` |
| **Next.js ルート** | kebab-case | `login/`, `session/` |
| **ルートグループ** | (kebab-case) | `(auth)/`, `(main)/` |

### 5.2 ファイル命名

#### TypeScript/TSX

| ファイルタイプ | 規則 | 例 |
|--------------|------|-----|
| **コンポーネント** | PascalCase | `VoiceInterface.tsx` |
| **フック** | camelCase | `useWebSocket.ts` |
| **ユーティリティ** | camelCase | `formatDate.ts` |
| **型定義** | camelCase | `session.ts` |
| **定数** | camelCase | `constants.ts` |
| **テスト** | *.test.tsx | `VoiceInterface.test.tsx` |

#### Python

| ファイルタイプ | 規則 | 例 |
|--------------|------|-----|
| **モジュール** | snake_case | `auth_service.py` |
| **クラス** | PascalCase | `class AuthService:` |
| **関数** | snake_case | `def get_user():` |
| **定数** | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT = 3` |
| **テスト** | test_*.py | `test_auth_service.py` |

### 5.3 変数命名

#### TypeScript

```typescript
// 変数: camelCase
const sessionId = 'abc123';
const isRecording = false;

// 定数: UPPER_SNAKE_CASE
const MAX_AUDIO_LENGTH = 30000;
const API_BASE_URL = 'https://api.example.com';

// 型: PascalCase
type SessionData = {
  id: string;
  userId: string;
};

// インターフェース: PascalCase
interface VoiceInterfaceProps {
  onAudioData: (data: Blob) => void;
}

// Enum: PascalCase
enum CharacterType {
  Robot = 'robot',
  Wizard = 'wizard',
}
```

#### Python

```python
# 変数: snake_case
session_id = 'abc123'
is_recording = False

# 定数: UPPER_SNAKE_CASE
MAX_AUDIO_LENGTH = 30000
API_BASE_URL = 'https://api.example.com'

# クラス: PascalCase
class SessionService:
    pass

# 関数: snake_case
def create_session(user_id: str) -> Session:
    pass

# Private: _で始まる
def _internal_helper():
    pass
```

### 5.4 Jotai Atom 命名

```typescript
// Primitive atom: [name]Atom
export const sessionAtom = atom<Session | null>(null);
export const userAtom = atom<User | null>(null);

// Derived atom (read-only): [name]Atom
export const isSessionActiveAtom = atom(
  (get) => get(sessionAtom) !== null
);

// Derived atom (read-write): [name]Atom
export const sessionStatusAtom = atom(
  (get) => get(sessionAtom)?.status ?? 'idle',
  (get, set, newStatus: string) => {
    const session = get(sessionAtom);
    if (session) {
      set(sessionAtom, { ...session, status: newStatus });
    }
  }
);
```

---

## 6. 環境設定ファイル

### 6.1 フロントエンド環境変数

#### `.env.local.example`

```bash
# API設定
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Firebase設定
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id

# アプリ設定
NEXT_PUBLIC_APP_ENV=development
```

**命名規則:**
- クライアント側で使用: `NEXT_PUBLIC_*`
- サーバー側のみ: プレフィックスなし

### 6.2 バックエンド環境変数

#### `.env.example`

```bash
# アプリ設定
APP_ENV=development
PORT=8080
LOG_LEVEL=INFO

# Google Cloud設定
GCP_PROJECT_ID=your_project_id
GCP_REGION=asia-northeast1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Firestore
FIRESTORE_EMULATOR_HOST=localhost:8080  # 開発環境のみ

# BigQuery
BIGQUERY_DATASET=homework_coach

# Redis
REDIS_URL=redis://localhost:6379

# Firebase Auth
FIREBASE_SERVICE_ACCOUNT=/path/to/firebase-service-account.json
```

### 6.3 設定ファイル一覧

| ファイル | 用途 | 場所 |
|---------|------|------|
| `.gitignore` | Git除外設定 | ルート |
| `.editorconfig` | エディタ設定 | ルート |
| `tsconfig.json` | TypeScript設定 | frontend/ |
| `next.config.js` | Next.js設定 | frontend/ |
| `.eslintrc.json` | ESLint設定 | frontend/ |
| `.prettierrc` | Prettier設定 | frontend/ |
| `pyproject.toml` | Python設定 | backend/ |
| `.python-version` | Pythonバージョン | backend/ |
| `requirements.txt` | Python依存関係 | backend/ |
| `bun.lockb` | Bunロックファイル | frontend/ |

---

## 7. セキュリティ考慮事項

### 7.1 機密情報の管理

**絶対にGitにコミットしない:**
- `.env`, `.env.local` - 環境変数
- `*.key`, `*.pem` - 秘密鍵
- `*-service-account.json` - GCPサービスアカウント
- `firebase-adminsdk-*.json` - Firebaseサービスアカウント

**`.gitignore` 必須設定:**

```gitignore
# 環境変数
.env
.env.local
.env.*.local

# 秘密鍵
*.key
*.pem
*.p12

# サービスアカウント
*-service-account.json
firebase-adminsdk-*.json

# ビルド成果物
frontend/.next/
frontend/out/
backend/__pycache__/
backend/*.pyc

# 依存関係
frontend/node_modules/
backend/.venv/
backend/venv/

# IDE設定
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 7.2 Secret Manager使用

**本番環境では必ずSecret Managerを使用:**

```python
# backend/app/core/config.py
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    """Secret Managerから秘密情報を取得"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

### 7.3 ファイルパーミッション

```bash
# サービスアカウントキー
chmod 600 *-service-account.json

# 環境変数ファイル
chmod 600 .env .env.local
```

---

## 8. ファイル配置チェックリスト

### 8.1 新規コンポーネント追加時

- [ ] コンポーネントファイル作成（`*.tsx`）
- [ ] テストファイル作成（`*.test.tsx`）
- [ ] `index.ts` でエクスポート
- [ ] 型定義を `types/` に追加（必要に応じて）
- [ ] Storybookストーリー作成（UIコンポーネントの場合）

### 8.2 新規APIエンドポイント追加時

- [ ] エンドポイント実装（`app/api/v1/*.py`）
- [ ] スキーマ定義（`app/schemas/*.py`）
- [ ] サービス層実装（`app/services/*_service.py`）
- [ ] ユニットテスト作成（`tests/unit/`）
- [ ] API仕様書更新（`docs/api/rest-api.md`）

### 8.3 環境変数追加時

- [ ] `.env.example` に追加
- [ ] `.env.local.example` に追加（フロントエンド）
- [ ] `app/core/config.py` に設定項目追加（バックエンド）
- [ ] Secret Managerに登録（本番環境）
- [ ] ドキュメント更新

---

## 9. ディレクトリ作成コマンド

### 9.1 フロントエンド初期化

```bash
cd homework-coach-robo

# フロントエンド構造作成
mkdir -p frontend/{app,components/{ui,features,layouts},lib/{api,hooks,utils},store/atoms,types,public/{characters,animations,icons},tests/{unit,integration,e2e}}

# 必要なファイル作成
touch frontend/{.env.local.example,.eslintrc.json,.prettierrc,Dockerfile,next.config.js,tsconfig.json,README.md}
```

### 9.2 バックエンド初期化

```bash
# バックエンド構造作成
mkdir -p backend/{app/{api/v1,core,models,schemas,services/adk,db,websocket,utils},tests/{unit,integration},scripts}

# 必要なファイル作成
touch backend/{.env.example,.python-version,Dockerfile,pyproject.toml,requirements.txt,requirements-dev.txt,README.md}
touch backend/app/__init__.py
touch backend/app/main.py
```

### 9.3 その他ディレクトリ

```bash
# 共通リソース
mkdir -p shared/{types,constants}

# インフラ
mkdir -p infrastructure/{terraform/{environments/{dev,staging,production},modules/{cloud_run,firestore,bigquery}},cloud-build}

# スクリプト
mkdir -p scripts
touch scripts/{setup.sh,dev.sh,test.sh,build.sh,deploy.sh}
chmod +x scripts/*.sh

# ドキュメント
mkdir -p docs/{api,guides,images}
```

