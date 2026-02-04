"""宿題コーチロボット - バックエンドAPIエントリーポイント"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="宿題コーチロボット API",
    description="小学校低学年向けソクラテス式対話学習支援API",
    version="0.1.0",
)

# API v1 ルーターを登録
app.include_router(api_v1_router)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンド開発サーバー
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
