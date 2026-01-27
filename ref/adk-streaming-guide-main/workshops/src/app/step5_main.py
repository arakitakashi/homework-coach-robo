"""Step 5: Upstream task - sending text to the model."""

import asyncio
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

load_dotenv(Path(__file__).parent / ".env")

from my_agent.agent import agent  # noqa: E402

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
    await websocket.accept()

    # Phase 2: Session Initialization
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"],
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

    live_request_queue = LiveRequestQueue()

    # ========================================
    # Phase 3: Upstream Task
    # ========================================

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        print("Upstream task started")

        while True:
            message = await websocket.receive()

            if "text" in message:
                text_data = message["text"]
                json_message = json.loads(text_data)

                if json_message.get("type") == "text":
                    user_text = json_message["text"]
                    print(f"User said: {user_text}")

                    # Create Content object and send to queue
                    content = types.Content(
                        parts=[types.Part(text=user_text)]
                    )
                    live_request_queue.send_content(content)
                    print("Sent to LiveRequestQueue")

            elif "bytes" in message:
                # Audio handling will come later
                print(f"Received audio: {len(message['bytes'])} bytes")

    async def downstream_task() -> None:
        """Placeholder - will receive events from run_live()."""
        print("Downstream task started (placeholder)")
        # Keep task alive
        while True:
            await asyncio.sleep(1)

    try:
        # Run both tasks concurrently
        await asyncio.gather(upstream_task(), downstream_task())
    except (WebSocketDisconnect, RuntimeError):
        print("Client disconnected")
    finally:
        live_request_queue.close()
        print("Session terminated")
