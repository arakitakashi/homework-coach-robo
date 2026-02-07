"""対話ランナーAPIエンドポイント

ADK RunnerベースのストリーミングAPIエンドポイント。
"""

import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.dialogue_runner import (
    DoneEvent,
    ErrorEvent,
    RunDialogueRequest,
    TextEvent,
)
from app.services.adk.memory import FirestoreMemoryService
from app.services.adk.runner import AgentRunnerService
from app.services.adk.sessions import FirestoreSessionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dialogue", tags=["dialogue"])

# デフォルトのアプリ名（runner_service.pyと同じ）
DEFAULT_APP_NAME = "homework-coach"


def get_session_service() -> FirestoreSessionService:
    """FirestoreSessionServiceを取得する"""
    return FirestoreSessionService()


def get_memory_service() -> FirestoreMemoryService:
    """FirestoreMemoryServiceを取得する"""
    return FirestoreMemoryService()


def get_agent_runner_service(
    session_service: FirestoreSessionService = Depends(get_session_service),
    memory_service: FirestoreMemoryService = Depends(get_memory_service),
) -> AgentRunnerService:
    """AgentRunnerServiceを取得する"""
    return AgentRunnerService(
        session_service=session_service,
        memory_service=memory_service,
    )


async def ensure_session_exists(
    session_service: FirestoreSessionService,
    user_id: str,
    session_id: str,
) -> None:
    """セッションが存在することを確認し、なければ作成する

    Args:
        session_service: セッションサービス
        user_id: ユーザーID
        session_id: セッションID
    """
    existing = await session_service.get_session(
        app_name=DEFAULT_APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if existing is None:
        logger.info(f"Creating new session: {session_id} for user: {user_id}")
        await session_service.create_session(
            app_name=DEFAULT_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )


async def event_generator(
    runner: AgentRunnerService,
    session_service: FirestoreSessionService,
    user_id: str,
    session_id: str,
    message: str,
) -> AsyncIterator[str]:
    """SSEイベントを生成する

    Args:
        runner: AgentRunnerService
        session_service: セッションサービス
        user_id: ユーザーID
        session_id: セッションID
        message: ユーザーメッセージ

    Yields:
        SSE形式のイベント文字列
    """
    try:
        # セッションが存在しない場合は作成
        await ensure_session_exists(session_service, user_id, session_id)

        async for event in runner.run(user_id, session_id, message):
            text = runner.extract_text(event)
            if text:
                text_event = TextEvent(text=text)
                yield f"event: text\ndata: {text_event.model_dump_json()}\n\n"

        done_event = DoneEvent(session_id=session_id)
        yield f"event: done\ndata: {done_event.model_dump_json()}\n\n"

    except Exception as e:
        logger.exception("Error during dialogue run")
        error_event = ErrorEvent(error=str(e), code="INTERNAL_ERROR")
        yield f"event: error\ndata: {error_event.model_dump_json()}\n\n"


@router.post(
    "/run",
    summary="対話を実行する（ストリーミング）",
    description="ADK Runnerを使用して対話を実行し、SSE形式でレスポンスをストリームします。",
)
async def run_dialogue(
    request: RunDialogueRequest,
    runner: AgentRunnerService = Depends(get_agent_runner_service),
    session_service: FirestoreSessionService = Depends(get_session_service),
) -> StreamingResponse:
    """対話を実行する（ストリーミング）

    SSE (Server-Sent Events) 形式でレスポンスをストリームします。

    イベントタイプ:
    - `text`: テキストチャンク（{"text": "..."}）
    - `error`: エラー（{"error": "...", "code": "..."}）
    - `done`: 完了（{"session_id": "..."}）
    """
    return StreamingResponse(
        event_generator(
            runner=runner,
            session_service=session_service,
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message,
        ),
        media_type="text/event-stream",
    )
