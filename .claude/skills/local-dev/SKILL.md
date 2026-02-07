# Local Development Skill

**Version**: 1.1
**Last Updated**: 2026-02-07

---

ローカル開発環境の起動・管理に関するガイドです。Docker Compose を使った起動方法と、Docker を使わない直接起動の両方をカバーします。

## 前提条件

- Docker Desktop がインストールされていること（Docker起動の場合）
- uv がインストールされていること（バックエンド直接起動の場合）
- Bun がインストールされていること（フロントエンド直接起動の場合）
- Google Cloud 認証が設定されていること（Gemini API を使用する場合）

---

## Claude Code への指示（起動手順）

**Claude Code（あなた）は、ローカル起動を支援する際に以下のプリフライトチェックを順番に実行すること。**
質問は最小限にとどめ、自動で解決できるものは自動で対処する。

### Step 1: Docker 接続確認

```bash
docker info --format '{{.ServerVersion}}' 2>/dev/null || echo "NOT_CONNECTED"
```

- `NOT_CONNECTED` の場合 → ユーザーに Docker Desktop の起動を依頼
- Docker Desktop 起動直後は接続に時間がかかることがある。5秒間隔で最大3回リトライ
- 3回リトライしても接続できない場合 → ユーザーに以下を確認：
  - Docker Desktop の左下ステータスが「Engine running」（緑色）か
  - `docker ps` がターミナルで実行できるか

### Step 2: `.env` ファイルの準備

```bash
# .env の存在確認
ls .env 2>/dev/null || echo "NOT_FOUND"
```

- `NOT_FOUND` の場合 → `.env.example` からコピーして作成
- **重要**: `.env.example` の `GOOGLE_CLOUD_PROJECT` はプレースホルダー（`your-project-id`）なので、
  コピー後に必ず `homework-coach-robo` に置換する

```bash
cp .env.example .env
sed -i '' 's/GOOGLE_CLOUD_PROJECT=your-project-id/GOOGLE_CLOUD_PROJECT=homework-coach-robo/' .env
```

- 既に `.env` が存在する場合 → `GOOGLE_CLOUD_PROJECT` の値を確認し、
  `your-project-id` のままであれば `homework-coach-robo` に修正

### Step 3: ポート競合チェック

```bash
lsof -i :3000 -t 2>/dev/null && echo "PORT_3000_IN_USE" || echo "PORT_3000_FREE"
lsof -i :8080 -t 2>/dev/null && echo "PORT_8080_IN_USE" || echo "PORT_8080_FREE"
```

- ポートが使用中の場合 → プロセス詳細を表示してユーザーに確認
  ```bash
  lsof -i :3000 -P | head -5
  ```
- ユーザーの許可を得てから `kill` する（勝手に kill しない）

### Step 4: GCloud 認証確認（Gemini API 使用時）

```bash
ls ~/.config/gcloud/application_default_credentials.json 2>/dev/null || echo "NOT_FOUND"
```

- `NOT_FOUND` の場合 → ユーザーに `gcloud auth application-default login` の実行を依頼

### Step 5: 起動

- Gemini API 使用時:
  ```bash
  docker compose -f docker-compose.yml -f docker-compose.gcloud.yml up -d
  ```
- Gemini API 不使用時:
  ```bash
  docker compose up -d
  ```

### Step 6: ヘルスチェック

起動後 10 秒待ってから確認：

```bash
curl -s http://localhost:8080/health
curl -s http://localhost:3000 -o /dev/null -w "%{http_code}"
```

- Backend: `{"status":"healthy"}` が返ればOK
- Frontend: HTTP 200 が返ればOK
- 失敗した場合 → `docker compose logs <service>` でエラーを確認

---

## 方法1: Docker Compose で起動（推奨）

### クイックスタート

```bash
# プロジェクトルートに移動
cd /Users/arakitakashi/git/indie-dev/homework-coach-robo/.tree/backend

# 1. 環境変数ファイルを作成（初回のみ）
cp .env.example .env
# ⚠️ GOOGLE_CLOUD_PROJECT を必ず homework-coach-robo に変更すること

# 2. 起動
docker compose up

# バックグラウンドで起動する場合
docker compose up -d
```

### Google Cloud 認証付き起動（Gemini API 使用時）

対話機能（Gemini Live API）を使用する場合は、GCloud 認証情報のマウントが必要です。

```bash
# 1. gcloud CLI で認証（初回 or 期限切れ時）
gcloud auth application-default login

# 2. GCloud認証付きで起動
docker compose -f docker-compose.yml -f docker-compose.gcloud.yml up
```

### アクセス URL

| サービス | URL | 説明 |
|----------|-----|------|
| Frontend | http://localhost:3000 | Next.js フロントエンド |
| Backend | http://localhost:8080 | FastAPI バックエンド |
| API Docs | http://localhost:8080/docs | Swagger UI |
| Health Check | http://localhost:8080/health | ヘルスチェック |

### よく使うコマンド

```bash
# 停止
docker compose down

# ログ確認（全サービス）
docker compose logs -f

# 特定サービスのログ
docker compose logs -f backend
docker compose logs -f frontend

# 再ビルド（依存関係変更時）
docker compose build --no-cache
docker compose up

# コンテナ内でテスト実行
docker compose exec backend uv run pytest
docker compose exec frontend bun test

# ボリュームを含めてクリーンアップ（キャッシュクリア）
docker compose down -v
docker compose up --build
```

### 環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `GOOGLE_CLOUD_PROJECT` | **要設定** | GCP プロジェクト ID（`homework-coach-robo`） |
| `GOOGLE_CLOUD_LOCATION` | `asia-northeast1` | GCP リージョン |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8080` | バックエンド API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8080` | WebSocket URL |
| `ENVIRONMENT` | `development` | 実行環境 |
| `LOG_LEVEL` | `DEBUG` | ログレベル |
| `CORS_ORIGINS` | `http://localhost:3000,...` | CORS 許可オリジン |

---

## 方法2: Docker を使わない直接起動

### バックエンド（FastAPI）

```bash
cd /Users/arakitakashi/git/indie-dev/homework-coach-robo/.tree/backend/backend

# 1. 依存関係のインストール
uv sync

# 2. 環境変数を設定
export GOOGLE_CLOUD_PROJECT=homework-coach-robo
export GOOGLE_CLOUD_LOCATION=asia-northeast1
export GOOGLE_GENAI_USE_VERTEXAI=true

# 3. GCloud認証（Gemini API使用時）
gcloud auth application-default login

# 4. 起動（ホットリロード付き）
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### フロントエンド（Next.js）

```bash
cd /Users/arakitakashi/git/indie-dev/homework-coach-robo/.tree/backend/frontend

# 1. 依存関係のインストール
bun install

# 2. 環境変数を設定（.env.local）
echo 'NEXT_PUBLIC_API_URL=http://localhost:8080' > .env.local
echo 'NEXT_PUBLIC_WS_URL=ws://localhost:8080' >> .env.local

# 3. 起動（ホットリロード付き）
bun run dev
```

### テスト・品質チェック

```bash
# バックエンド
cd backend
uv run pytest tests/ -v                              # テスト
uv run pytest tests/ --cov=app --cov-report=term-missing  # カバレッジ
uv run ruff check .                                   # Lint
uv run mypy .                                         # 型チェック

# フロントエンド
cd frontend
bun test                                              # テスト
bun lint                                              # Lint
bun typecheck                                         # 型チェック
bun build                                             # ビルド確認
```

---

## トラブルシューティング

### Docker CLI が接続できない

Docker Desktop が起動していても CLI から接続できないことがある。

```bash
# 症状
$ docker ps
Cannot connect to the Docker daemon at unix:///Users/<user>/.docker/run/docker.sock.
```

**対処法:**
1. Docker Desktop のステータスバーが「Engine running」（緑色）か確認
2. 起動直後の場合は 10〜30 秒待ってリトライ
3. それでもダメな場合は Docker Desktop を再起動

### ポートが使用中の場合

```bash
# 使用中のプロセスを確認
lsof -i :3000 -P
lsof -i :8080 -P

# プロセスを終了（PID を確認してから）
kill <PID>
```

**よくある原因:**
- 前回の `bun run dev` や `next dev` が残っている
- 別のターミナルで開発サーバーが動いている

### Firestore API エラー（`SERVICE_DISABLED`）

```
Cloud Firestore API has not been used in project your-project-id before or it is disabled.
```

**原因:** `.env` の `GOOGLE_CLOUD_PROJECT` がプレースホルダーのまま。

**対処法:**
```bash
# .env を確認
grep GOOGLE_CLOUD_PROJECT .env

# your-project-id のままなら修正
sed -i '' 's/GOOGLE_CLOUD_PROJECT=your-project-id/GOOGLE_CLOUD_PROJECT=homework-coach-robo/' .env

# バックエンドコンテナを再起動
docker compose up -d backend
```

### 依存関係のキャッシュをクリアしたい場合

```bash
# Docker: ボリュームを削除して再起動
docker compose down -v
docker compose up --build

# バックエンド（直接起動）: .venv を削除
cd backend && rm -rf .venv && uv sync

# フロントエンド（直接起動）: node_modules を削除
cd frontend && rm -rf node_modules && bun install
```

### Docker コンテナが起動しない場合

```bash
# コンテナの状態を確認
docker compose ps

# エラーログを確認
docker compose logs backend
docker compose logs frontend

# イメージを再ビルド
docker compose build --no-cache
```

### GCloud 認証エラーの場合

```bash
# 認証情報の確認
gcloud auth application-default print-access-token

# 認証情報の再取得
gcloud auth application-default login

# 認証ファイルの存在確認
ls ~/.config/gcloud/application_default_credentials.json
```

---

## Docker 構成の詳細

### docker-compose.yml

| サービス | ベースイメージ | ポート | ボリューム |
|---------|--------------|--------|-----------|
| backend | python:3.10-slim + uv | 8080:8080 | `./backend:/app` |
| frontend | oven/bun:1 | 3000:3000 | `./frontend:/app` |

### docker-compose.gcloud.yml（オーバーライド）

GCloud 認証情報を backend コンテナにマウントします。

```
~/.config/gcloud → /root/.config/gcloud (read-only)
```
