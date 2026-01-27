"""Step 4: Session initialization per connection."""

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables BEFORE importing agent
load_dotenv(Path(__file__).parent / ".env")

from my_agent.agent import agent  # noqa: E402

# ========================================
# Phase 1: Application Initialization
# ========================================

APP_NAME = "bidi-workshop"

app = FastAPI()
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)


@app.get("/")
async def root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
) -> None:
    """WebSocket endpoint with session initialization."""
    await websocket.accept()
    print(f"Client connected: user={user_id}, session={session_id}")

    # ========================================
    # Phase 2: Session Initialization
    # ========================================

    # Configure streaming behavior for native audio model
    # Native audio models ONLY support AUDIO response modality
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,  # Bidirectional streaming
        response_modalities=["AUDIO"],       # Native audio models require AUDIO
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    # Get or create session for conversation history
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        print(f"Created new session: {session_id}")
    else:
        print(f"Resumed existing session: {session_id}")

    # Create queue for sending input to the model
    live_request_queue = LiveRequestQueue()

    print(f"Session initialized with config: {run_config}")

    # ========================================
    # Phase 3: Active Session (coming next!)
    # ========================================

    try:
        while True:
            message = await websocket.receive()

            if "text" in message:
                text_data = message["text"]
                print(f"Received: {text_data}")

                # Placeholder - actual streaming will be added in Step 5 & 6
                response = {
                    "content": {
                        "parts": [{"text": "[Step 4 Complete] Session initialized. Proceed to Step 5 to enable model responses."}]
                    }
                }
                await websocket.send_text(json.dumps(response))
                await websocket.send_text(json.dumps({"turnComplete": True}))

    except (WebSocketDisconnect, RuntimeError):
        print("Client disconnected")
    finally:
        # ========================================
        # Phase 4: Termination
        # ========================================
        live_request_queue.close()
        print("LiveRequestQueue closed")
