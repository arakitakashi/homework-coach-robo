"""音声ストリームWebSocketエンドポイント

双方向音声ストリーミング用WebSocketエンドポイント。
フロントエンドのVoiceWebSocketClientプロトコルに準拠。
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import Depends, WebSocket, WebSocketDisconnect

from app.services.adk.memory import FirestoreMemoryService
from app.services.adk.sessions import FirestoreSessionService
from app.services.voice.streaming_service import VoiceStreamingService

logger = logging.getLogger(__name__)

# デフォルトのアプリ名
DEFAULT_APP_NAME = "homework-coach"


def get_session_service() -> FirestoreSessionService:
    """FirestoreSessionServiceを取得する"""
    return FirestoreSessionService()


def get_memory_service() -> FirestoreMemoryService:
    """FirestoreMemoryServiceを取得する"""
    return FirestoreMemoryService()


async def _ensure_session_exists(
    session_service: FirestoreSessionService,
    user_id: str,
    session_id: str,
) -> None:
    """セッションが存在することを確認し、なければ作成する"""
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


async def _agent_to_client(
    websocket: WebSocket,
    service: VoiceStreamingService,
    user_id: str,
    session_id: str,
) -> None:
    """エージェントからクライアントへのイベント転送"""
    try:
        async for event in service.receive_events(
            user_id=user_id,
            session_id=session_id,
        ):
            json_str = event.model_dump_json(exclude_none=True, by_alias=True)
            await websocket.send_text(json_str)
    except Exception:
        logger.exception("Error in agent-to-client stream")


async def _client_to_agent(
    websocket: WebSocket,
    service: VoiceStreamingService,
) -> None:
    """クライアントからエージェントへのメッセージ転送"""
    while True:
        message = await websocket.receive()

        # WebSocket closeフレームの検出
        if message.get("type") == "websocket.disconnect":
            raise WebSocketDisconnect(code=message.get("code", 1000))

        if message.get("bytes"):
            # バイナリ音声データ
            service.send_audio(message["bytes"])
        elif message.get("text"):
            # JSONテキストメッセージ
            try:
                data: dict[str, Any] = json.loads(message["text"])
                if data.get("type") == "text" and data.get("text"):
                    service.send_text(data["text"])
                else:
                    logger.warning(f"Unknown message type: {data.get('type')}")
            except json.JSONDecodeError:
                logger.warning("Invalid JSON message received")


async def voice_stream_endpoint(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
    session_service: FirestoreSessionService = Depends(get_session_service),
    memory_service: FirestoreMemoryService = Depends(get_memory_service),
) -> None:
    """音声ストリームWebSocketエンドポイント

    双方向音声ストリーミングを提供する。

    Args:
        websocket: WebSocket接続
        user_id: ユーザーID
        session_id: セッションID
        session_service: セッション管理サービス
        memory_service: 記憶管理サービス
    """
    await websocket.accept()

    # セッションの確認/作成
    await _ensure_session_exists(session_service, user_id, session_id)

    # VoiceStreamingServiceの作成
    service = VoiceStreamingService(
        session_service=session_service,
        memory_service=memory_service,
    )

    try:
        # エージェントからのイベント転送を開始
        agent_task = asyncio.create_task(_agent_to_client(websocket, service, user_id, session_id))

        # クライアントからのメッセージ受信（メインループ）
        try:
            await _client_to_agent(websocket, service)
        except WebSocketDisconnect:
            logger.info(f"Client disconnected: {user_id}/{session_id}")
        finally:
            agent_task.cancel()

    except Exception:
        logger.exception("Error in voice stream WebSocket")
    finally:
        service.close()
