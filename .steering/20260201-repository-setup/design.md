# Design - リポジトリセットアップ

## アーキテクチャ概要

モノレポ構成を採用し、フロントエンド・バックエンド・共通リソースを一元管理する。

```
homework-coach-robo/
├── frontend/          # Next.js 14+ (App Router) + Bun
├── backend/           # FastAPI + Python 3.10+ + uv
├── shared/            # 共通型定義・定数
├── infrastructure/    # Terraform, Cloud Build設定
├── scripts/           # プロジェクト全体スクリプト
├── docs/              # ドキュメント（既存）
├── poc/               # PoC成果物（既存）
└── .github/           # GitHub設定
```

## 技術選定

### フロントエンド

| 技術 | バージョン | 理由 |
|------|-----------|------|
| Next.js | 14+ | App Router、RSC対応 |
| Bun | latest | 高速なパッケージ管理、TypeScript直接実行 |
| TypeScript | 5.x | 型安全性 |
| Jotai | latest | 軽量な状態管理、Next.js親和性 |
| Rive | latest | リッチなキャラクターアニメーション |

### バックエンド

| 技術 | バージョン | 理由 |
|------|-----------|------|
| Python | 3.10+ | 型ヒント、async/await |
| FastAPI | 0.128+ | 高速、型安全、OpenAPI自動生成 |
| uv | latest | 高速なPythonパッケージ管理 |
| Pydantic | v2 | データバリデーション |
| pytest | latest | テストフレームワーク |

### 開発ツール

| ツール | 用途 |
|--------|------|
| ESLint | TypeScript linter |
| Prettier | コードフォーマッター |
| Black | Python formatter |
| isort | Python import整理 |
| mypy | Python型チェック |
| Vitest | フロントエンドテスト |

## ファイル構成

### フロントエンド（`frontend/`）

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/               # 認証グループルート
│   ├── (main)/               # メインアプリグループルート
│   ├── api/                  # API Routes
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/               # Reactコンポーネント
│   ├── ui/                   # 汎用UI
│   ├── features/             # 機能別
│   └── layouts/              # レイアウト
├── lib/                      # ユーティリティ
│   ├── api/                  # APIクライアント
│   ├── hooks/                # カスタムフック
│   └── utils/                # 汎用ヘルパー
├── store/                    # Jotai atoms
│   └── atoms/
├── types/                    # TypeScript型定義
├── public/                   # 静的ファイル
│   ├── characters/           # Riveキャラクター
│   └── animations/           # Riveアニメーション
├── tests/                    # テスト
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.local.example
├── .eslintrc.json
├── .prettierrc
├── next.config.js
├── package.json
├── tsconfig.json
└── Dockerfile
```

### バックエンド（`backend/`）

```
backend/
├── app/
│   ├── api/                  # APIエンドポイント
│   │   ├── v1/
│   │   └── deps.py
│   ├── core/                 # コア機能
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/               # データモデル
│   ├── schemas/              # APIスキーマ
│   ├── services/             # ビジネスロジック
│   │   └── adk/              # ADK関連
│   ├── db/                   # DB クライアント
│   ├── websocket/            # WebSocket管理
│   ├── utils/                # ユーティリティ
│   └── main.py               # エントリーポイント
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/                  # スクリプト
├── .env.example
├── .python-version
├── pyproject.toml
├── Dockerfile
└── README.md
```

### 共通リソース（`shared/`）

```
shared/
├── types/
│   ├── api.ts                # TypeScript用API型
│   └── models.py             # Python用モデル型
└── constants/
    ├── error_codes.ts
    └── error_codes.py
```

### GitHub設定（`.github/`）

```
.github/
├── workflows/
│   ├── ci-frontend.yml       # フロントエンドCI
│   └── ci-backend.yml        # バックエンドCI
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
└── PULL_REQUEST_TEMPLATE.md
```

## CI/CD設計

### フロントエンドCI (`ci-frontend.yml`)

トリガー:
- `frontend/**` への変更
- PRまたはmainへのプッシュ

ジョブ:
1. **lint**: ESLint実行
2. **typecheck**: TypeScript型チェック
3. **test**: Vitest実行
4. **build**: `next build` 実行

### バックエンドCI (`ci-backend.yml`)

トリガー:
- `backend/**` への変更
- PRまたはmainへのプッシュ

ジョブ:
1. **lint**: Black, isort, ruff
2. **typecheck**: mypy
3. **test**: pytest実行

## 依存関係

### フロントエンド主要依存

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "jotai": "^2.0.0",
    "@rive-app/react-canvas": "latest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "vitest": "latest",
    "@types/react": "^18.0.0",
    "@types/node": "^20.0.0"
  }
}
```

### バックエンド主要依存

```toml
[project]
dependencies = [
    "fastapi>=0.128.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.0.0",
    "google-adk>=0.1.0",
    "firebase-admin>=6.0.0",
    "google-cloud-firestore>=2.0.0",
    "redis>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
    "isort>=5.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]
```

## 環境変数設計

### フロントエンド (`.env.local.example`)

```bash
# API設定
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Firebase設定
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=

# アプリ設定
NEXT_PUBLIC_APP_ENV=development
```

### バックエンド (`.env.example`)

```bash
# アプリ設定
APP_ENV=development
PORT=8000
LOG_LEVEL=INFO

# Google Cloud設定
GCP_PROJECT_ID=
GCP_REGION=asia-northeast1

# Gemini API
GOOGLE_API_KEY=

# Redis
REDIS_URL=redis://localhost:6379
```

## セキュリティ考慮事項

1. **機密情報の除外**
   - `.gitignore` で環境変数ファイル、サービスアカウントキーを除外
   - テンプレートファイル（`.env.example`）のみをコミット

2. **依存関係の監査**
   - CIでdependabot設定
   - 脆弱性のある依存関係を検知

## 代替案と採用理由

### パッケージマネージャー

| 選択肢 | 採用 | 理由 |
|--------|------|------|
| npm | ❌ | 遅い |
| yarn | ❌ | Bunの方が高速 |
| pnpm | ❌ | Bunの方がシンプル |
| Bun | ✅ | 最速、TypeScript直接実行 |

### Python環境管理

| 選択肢 | 採用 | 理由 |
|--------|------|------|
| pip | ❌ | 遅い、依存解決が貧弱 |
| Poetry | ❌ | uvの方が高速 |
| uv | ✅ | 最速、Rustベース |
