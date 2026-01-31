"""
Gemini Live API PoC - FastAPI WebSocket Server
"""

import asyncio
import base64
import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import Blob, Content, Part
from starlette.websockets import WebSocketDisconnect

from tutor_agent.agent import root_agent

# 環境変数読み込み
load_dotenv()

# SSL証明書設定（Gemini Live API接続に必要）
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

# アプリ名
APP_NAME = "homework_coach_poc"

# セッションサービス（インメモリ）
session_service = InMemorySessionService()

# Runner
runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    print("Starting Homework Coach PoC Server...")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Homework Coach PoC",
    description="Gemini Live API技術検証サーバー",
    lifespan=lifespan,
)


def get_run_config() -> RunConfig:
    """RunConfigを生成"""
    return RunConfig(
        response_modalities=["AUDIO"],
    )


async def agent_to_client_messaging(websocket: WebSocket, user_id: str, session_id: str, live_request_queue: LiveRequestQueue):
    """エージェントからクライアントへのメッセージング"""
    run_config = get_run_config()
    print(f"Starting run_live for user={user_id}, session={session_id}")

    try:
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config,
        ):
            # デバッグログ
            content_info = "None"
            if event.content:
                role = getattr(event.content, 'role', 'no_role')
                parts_count = len(event.content.parts) if event.content.parts else 0
                has_audio = any(
                    p.inline_data and p.inline_data.mime_type.startswith("audio/")
                    for p in (event.content.parts or [])
                    if hasattr(p, 'inline_data') and p.inline_data
                )
                content_info = f"role={role}, parts={parts_count}, has_audio={has_audio}"
            print(f"Event: author={event.author}, partial={event.partial}, turn_complete={event.turn_complete}, content=[{content_info}]")

            try:
                message = {
                    "author": event.author or "agent",
                    "is_partial": event.partial or False,
                    "turn_complete": event.turn_complete or False,
                    "parts": [],
                    "input_transcription": None,
                    "output_transcription": None,
                }

                if not event.content:
                    if message["turn_complete"]:
                        await websocket.send_text(json.dumps(message))
                    continue

                # 文字起こしテキストを抽出
                transcription = "".join(
                    p.text for p in event.content.parts if p.text
                )

                role = getattr(event.content, "role", None)

                # ユーザー入力の文字起こし
                if role == "user":
                    if transcription:
                        message["input_transcription"] = {
                            "text": transcription,
                            "is_final": not event.partial,
                        }

                # エージェント応答の処理
                if role == "model" or (role is None and event.author and event.author != "user"):
                    if transcription:
                        message["output_transcription"] = {
                            "text": transcription,
                            "is_final": not event.partial,
                        }
                        message["parts"].append({"type": "text", "data": transcription})

                # 音声データの処理
                for part in event.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        if part.inline_data.mime_type and part.inline_data.mime_type.startswith("audio/"):
                            audio = base64.b64encode(part.inline_data.data).decode("ascii")
                            message["parts"].append({"type": "audio/pcm", "data": audio})
                            print(f"Sending audio: {len(part.inline_data.data)} bytes")
                    if hasattr(part, 'function_call') and part.function_call:
                        message["parts"].append({
                            "type": "function_call",
                            "data": {
                                "name": part.function_call.name,
                                "args": part.function_call.args or {},
                            },
                        })

                # メッセージ送信
                if (message["parts"] or message["turn_complete"] or
                    message["input_transcription"] or message["output_transcription"]):
                    await websocket.send_text(json.dumps(message))

            except Exception as e:
                print(f"Error processing event: {e}")

    except Exception as e:
        print(f"run_live error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("agent_to_client_messaging ended")


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """クライアントからエージェントへのメッセージング"""
    while True:
        try:
            msg = json.loads(await websocket.receive_text())
            mime = msg.get("mime_type", "")

            if mime == "text/plain":
                print(f"Received text: {msg['data'][:50]}...")
                content = Content(role="user", parts=[Part.from_text(text=msg["data"])])
                live_request_queue.send_content(content=content)
            elif mime == "audio/pcm":
                data = base64.b64decode(msg["data"])
                print(f"Received audio: {len(data)} bytes")
                live_request_queue.send_realtime(Blob(data=data, mime_type="audio/pcm;rate=16000"))
            elif mime == "image/jpeg":
                data = base64.b64decode(msg["data"])
                live_request_queue.send_realtime(Blob(data=data, mime_type=mime))

        except WebSocketDisconnect:
            print("Client disconnected")
            break
        except Exception as e:
            print(f"Error in client_to_agent: {e}")
            break


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocketエンドポイント"""
    await websocket.accept()
    print(f"Client connected: {user_id}")

    # 毎回新しいセッションIDを生成（タイムスタンプ付き）
    import time
    session_id = f"session_{user_id}_{int(time.time() * 1000)}"

    # 新しいセッションを作成
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    print(f"Created new session: {session_id}")

    # LiveRequestQueueを作成
    live_request_queue = LiveRequestQueue()

    try:
        # upstream/downstreamタスクを並行実行
        results = await asyncio.gather(
            agent_to_client_messaging(websocket, user_id, session_id, live_request_queue),
            client_to_agent_messaging(websocket, live_request_queue),
            return_exceptions=True,
        )
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i} exception: {result}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        live_request_queue.close()
        print(f"Client disconnected: {user_id}")


@app.get("/")
async def root():
    """ルートエンドポイント - テストページを返す"""
    return FileResponse("../client/index.html")


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "ok", "service": "homework-coach-poc"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
