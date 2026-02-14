"""API v1 ルーター集約"""

from fastapi import APIRouter

from app.api.v1.dialogue import router as dialogue_router
from app.api.v1.dialogue_runner import router as dialogue_runner_router
from app.api.v1.vision import router as vision_router

router = APIRouter(prefix="/api/v1")

router.include_router(dialogue_router)
router.include_router(dialogue_runner_router)
router.include_router(vision_router)
