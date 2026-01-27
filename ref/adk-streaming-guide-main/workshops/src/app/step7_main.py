"""Step 7: Bidirectional audio - voice input and output."""

import asyncio
import json
import warnings
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

# Suppress noisy warnings
warnings.filterwarnings("ignore", message="Your application has authenticated using end user credentials")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

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
    print("Connection open")

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

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        while True:
            message = await websocket.receive()

            # Handle text messages (JSON)
            if "text" in message:
                json_message = json.loads(message["text"])

                if json_message.get("type") == "text":
                    user_text = json_message["text"]
                    print(f"[UPSTREAM] User text: {user_text}")

                    content = types.Content(
                        parts=[types.Part(text=user_text)]
                    )
                    live_request_queue.send_content(content)

            # Handle binary messages (audio)
            elif "bytes" in message:
                audio_data = message["bytes"]
                print(f"[UPSTREAM] Audio chunk: {len(audio_data)} bytes")

                # Create audio blob with correct format
                audio_blob = types.Blob(
                    mime_type="audio/pcm;rate=16000",  # 16kHz mono PCM
                    data=audio_data
                )

                # Stream audio (doesn't trigger response until VAD detects silence)
                live_request_queue.send_realtime(audio_blob)

    async def downstream_task() -> None:
        """Receives Events from run_live() and sends to WebSocket."""
        print("[DOWNSTREAM] Starting run_live()")

        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config,
        ):
            event_json = event.model_dump_json(exclude_none=True, by_alias=True)
            print(f"[DOWNSTREAM] Event: {event_json[:100]}...")
            await websocket.send_text(event_json)

        print("[DOWNSTREAM] run_live() completed")

    try:
        await asyncio.gather(upstream_task(), downstream_task())
    except (WebSocketDisconnect, RuntimeError):
        print("Client disconnected")
    finally:
        live_request_queue.close()
        print("Session terminated")
