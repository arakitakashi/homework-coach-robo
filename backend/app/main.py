"""宿題コーチロボット - バックエンドAPIエントリーポイント"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.api.v1.voice_stream import voice_stream_endpoint

app = FastAPI(
    title="宿題コーチロボット API",
    description="小学校低学年向けソクラテス式対話学習支援API",
    version="0.1.0",
)

# API v1 ルーターを登録
app.include_router(api_v1_router)

# WebSocketエンドポイントを登録
app.websocket("/ws/{user_id}/{session_id}")(voice_stream_endpoint)

# CORS設定
# 環境変数CORS_ORIGINSで追加のオリジンを指定可能（カンマ区切り）
cors_origins = [
    "http://localhost:3000",  # ローカル開発
    "https://homework-coach-frontend-652907685934.asia-northeast1.run.app",  # 本番
]
# 環境変数から追加のオリジンを取得
extra_origins = os.environ.get("CORS_ORIGINS", "")
if extra_origins:
    cors_origins.extend(origin.strip() for origin in extra_origins.split(",") if origin.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """ルートエンドポイント"""
    return {"message": "宿題コーチロボット API"}
