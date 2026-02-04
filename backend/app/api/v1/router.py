"""API v1 ルーター集約"""

from fastapi import APIRouter

from app.api.v1.dialogue import router as dialogue_router

router = APIRouter(prefix="/api/v1")

router.include_router(dialogue_router)
