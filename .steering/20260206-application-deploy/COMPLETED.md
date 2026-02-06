# COMPLETED - Application Deploy

**完了日**: 2026-02-06

---

## 実装内容の要約

アプリケーション（Backend + Frontend）をCloud Runにデプロイしました。

### デプロイ済みサービス

| サービス | URL | 状態 |
|---------|-----|------|
| **Backend** | https://homework-coach-backend-652907685934.asia-northeast1.run.app | ✅ 稼働中 |
| **Frontend** | https://homework-coach-frontend-652907685934.asia-northeast1.run.app | ✅ 稼働中 |

### ヘルスチェック結果

- Backend `/health`: `{"status":"healthy"}`
- Frontend `/api/health`: `{"status":"ok"}`

---

## 実行したステップ

### 1. フロントエンド設定変更

- `next.config.ts`: `output: "standalone"` を追加
- `/api/health/route.ts`: ヘルスチェックエンドポイントを作成

### 2. Dockerイメージビルド（amd64）

```bash
# Backend
docker buildx build --platform linux/amd64 \
  -f infrastructure/docker/backend/Dockerfile \
  -t asia-northeast1-docker.pkg.dev/homework-coach-robo/homework-coach-docker/backend:latest \
  --load .

# Frontend
docker buildx build --platform linux/amd64 \
  -f infrastructure/docker/frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=https://homework-coach-backend-652907685934.asia-northeast1.run.app \
  -t asia-northeast1-docker.pkg.dev/homework-coach-robo/homework-coach-docker/frontend:latest \
  --load .
```

### 3. Artifact Registryへのプッシュ

```bash
export PATH="/Users/arakitakashi/google-cloud-sdk/bin:$PATH"
docker push asia-northeast1-docker.pkg.dev/homework-coach-robo/homework-coach-docker/backend:latest
docker push asia-northeast1-docker.pkg.dev/homework-coach-robo/homework-coach-docker/frontend:latest
```

### 4. Cloud Runへのデプロイ

```bash
gcloud run deploy homework-coach-backend \
  --image=asia-northeast1-docker.pkg.dev/homework-coach-robo/homework-coach-docker/backend:latest \
  --region=asia-northeast1 \
  --project=homework-coach-robo

gcloud run deploy homework-coach-frontend \
  --image=asia-northeast1-docker.pkg.dev/homework-coach-robo/homework-coach-docker/frontend:latest \
  --region=asia-northeast1 \
  --project=homework-coach-robo
```

---

## 発生した問題と解決方法

### 1. ARM64イメージでCloud Runデプロイ失敗

**問題**: Apple Silicon（M1/M2）でビルドしたイメージがARM64だったため、Cloud Runで拒否された

**エラー**: `Container manifest type must support amd64/linux`

**解決**: `docker buildx build --platform linux/amd64` でamd64イメージをビルド

### 2. Docker認証の問題

**問題**: `docker-credential-gcloud`がPATHに含まれていなかったため、Artifact Registryへのプッシュが失敗

**解決**: `export PATH="/Users/arakitakashi/google-cloud-sdk/bin:$PATH"` でgcloud SDKのbinディレクトリをPATHに追加

---

## ファイル変更

- `frontend/next.config.ts`: standalone出力を有効化
- `frontend/src/app/api/health/route.ts`: ヘルスチェックエンドポイント追加

---

## 今後のステップ

1. **E2Eテスト**: フロントエンドからバックエンドへの接続テスト
2. **CI/CDパイプライン**: Cloud Buildトリガーの設定
3. **カスタムドメイン**: Cloud Runサービスへのドメイン設定
