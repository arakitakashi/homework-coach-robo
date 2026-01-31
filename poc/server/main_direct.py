"""
Gemini Live API PoC - 直接API使用版
ADKを使わず、google-genaiを直接使用
"""

import asyncio
import base64
import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from google import genai
from starlette.websockets import WebSocketDisconnect

# 環境変数読み込み
load_dotenv()

# SSL証明書設定
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

# Gemini クライアント
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# モデル名
MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

# システムプロンプト
SYSTEM_INSTRUCTION = """あなたは「宿題コーチロボ」です。小学校低学年（1〜3年生）の子供の宿題をサポートします。

## 基本原則
- 答えを直接教えない。質問で子供を導く（ソクラテス式対話）
- 優しく、励ましながら対話する
- 日本語で会話する
- 短く、わかりやすい言葉を使う

## 対話パターン
1. まず子供の話を聞く
2. 「どこがわからないかな？」と確認
3. ヒントを出して考えさせる
4. 正解したら褒める
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Homework Coach PoC Server (Direct API)...")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Homework Coach PoC (Direct)",
    description="Gemini Live API直接使用版",
    lifespan=lifespan,
)


async def handle_session(websocket: WebSocket, session):
    """Geminiセッションとの双方向通信を処理"""

    async def receive_from_gemini():
        """Geminiからの応答を受信してクライアントに送信"""
        try:
            async for response in session.receive():
                if response.server_content:
                    message = {
                        "type": "response",
                        "parts": [],
                        "turn_complete": response.server_content.turn_complete or False,
                    }

                    if response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            # テキスト（思考含む）
                            if hasattr(part, 'text') and part.text:
                                thought = getattr(part, 'thought', False)
                                if not thought:  # 思考以外のテキストのみ送信
                                    message["parts"].append({
                                        "type": "text",
                                        "data": part.text
                                    })
                                    message["output_transcription"] = {
                                        "text": part.text,
                                        "is_final": True
                                    }

                            # 音声
                            if hasattr(part, 'inline_data') and part.inline_data:
                                audio_base64 = base64.b64encode(part.inline_data.data).decode('ascii')
                                message["parts"].append({
                                    "type": "audio/pcm",
                                    "data": audio_base64
                                })

                    if message["parts"] or message["turn_complete"]:
                        await websocket.send_text(json.dumps(message))

        except Exception as e:
            print(f"Gemini receive error: {e}")

    async def receive_from_client():
        """クライアントからの入力を受信してGeminiに送信"""
        try:
            while True:
                msg = json.loads(await websocket.receive_text())
                mime = msg.get("mime_type", "")

                if mime == "audio/pcm":
                    data = base64.b64decode(msg["data"])
                    print(f"Received audio: {len(data)} bytes")
                    await session.send_realtime_input(
                        audio={"data": data, "mime_type": "audio/pcm;rate=16000"}
                    )

                elif mime == "text/plain":
                    text = msg.get("data", "")
                    print(f"Received text: {text[:50]}...")
                    await session.send_client_content(
                        turns={"role": "user", "parts": [{"text": text}]},
                        turn_complete=True
                    )

        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print(f"Client receive error: {e}")

    # 両方のタスクを並行実行
    await asyncio.gather(
        receive_from_gemini(),
        receive_from_client(),
        return_exceptions=True
    )


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocketエンドポイント"""
    await websocket.accept()
    print(f"Client connected: {user_id}")

    try:
        config = {
            "response_modalities": ["AUDIO"],
            "system_instruction": SYSTEM_INSTRUCTION,
        }

        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print(f"Gemini Live session started for {user_id}")
            await handle_session(websocket, session)

    except Exception as e:
        print(f"Session error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"Client disconnected: {user_id}")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return FileResponse("../client/index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "homework-coach-poc-direct"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
