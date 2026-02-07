"""宿題コーチロボット - バックエンドAPIエントリーポイント"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.api.v1.voice_stream import voice_stream_endpoint

logger = logging.getLogger(__name__)

app = FastAPI(
    title="宿題コーチロボット API",
    description="小学校低学年向けソクラテス式対話学習支援API",
    version="0.1.0",
)

# API v1 ルーターを登録
app.include_router(api_v1_router)

# WebSocketエンドポイントを登録
app.websocket("/ws/{user_id}/{session_id}")(voice_stream_endpoint)

# E2Eテストモード: モックサービスでDI overrideする
if os.environ.get("E2E_MODE", "").lower() == "true":
    # InMemorySessionService (Firestoreなし)
    from google.adk.sessions import InMemorySessionService

    from app.api.v1.dialogue_runner import (
        get_agent_runner_service,
    )
    from app.api.v1.dialogue_runner import (
        get_memory_service as get_dialogue_memory_service,
    )
    from app.api.v1.dialogue_runner import (
        get_session_service as get_dialogue_session_service,
    )
    from app.api.v1.voice_stream import (
        get_memory_service as get_voice_memory_service,
    )
    from app.api.v1.voice_stream import (
        get_session_service as get_voice_session_service,
    )
    from app.testing.mock_runner import MockAgentRunnerService

    _e2e_session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
    _e2e_mock_runner = MockAgentRunnerService()

    app.dependency_overrides[get_dialogue_session_service] = lambda: _e2e_session_service
    app.dependency_overrides[get_dialogue_memory_service] = lambda: None
    app.dependency_overrides[get_agent_runner_service] = lambda: _e2e_mock_runner
    app.dependency_overrides[get_voice_session_service] = lambda: _e2e_session_service
    app.dependency_overrides[get_voice_memory_service] = lambda: None

    logger.warning("E2E_MODE enabled: using mock services")

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
