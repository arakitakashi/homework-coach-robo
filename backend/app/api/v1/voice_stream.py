"""音声ストリームWebSocketエンドポイント

双方向音声ストリーミング用WebSocketエンドポイント。
フロントエンドのVoiceWebSocketClientプロトコルに準拠。
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import Depends, WebSocket, WebSocketDisconnect
from google.adk.memory import BaseMemoryService

from app.services.adk.memory.memory_factory import create_memory_service
from app.services.adk.sessions import FirestoreSessionService
from app.services.voice.streaming_service import VoiceStreamingService

logger = logging.getLogger(__name__)

# デフォルトのアプリ名
DEFAULT_APP_NAME = "homework-coach"


def get_session_service() -> FirestoreSessionService:
    """FirestoreSessionServiceを取得する"""
    return FirestoreSessionService()


def get_memory_service() -> BaseMemoryService:
    """メモリサービスを取得する（環境変数ベースで切り替え）"""
    return create_memory_service()


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
        # エラーをクライアントに通知（デバッグ用）
        try:
            error_msg = json.dumps({"error": "AIとの接続でエラーが発生しました"})
            await websocket.send_text(error_msg)
        except Exception:
            logger.debug("Failed to send error message to client")


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
    memory_service: BaseMemoryService = Depends(get_memory_service),
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

    try:
        # セッションの確認/作成
        await _ensure_session_exists(session_service, user_id, session_id)
    except Exception:
        logger.exception(f"Failed to ensure session: {user_id}/{session_id}")
        error_msg = json.dumps({"error": "セッションの初期化に失敗しました"})
        await websocket.send_text(error_msg)
        await websocket.close(code=1011)
        return

    try:
        # VoiceStreamingServiceの作成
        service = VoiceStreamingService(
            session_service=session_service,
            memory_service=memory_service,
        )
    except Exception:
        logger.exception("Failed to create VoiceStreamingService")
        error_msg = json.dumps({"error": "音声サービスの初期化に失敗しました"})
        await websocket.send_text(error_msg)
        await websocket.close(code=1011)
        return

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
