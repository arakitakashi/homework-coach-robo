"""Step 3: Application initialization with ADK components."""

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Load environment variables BEFORE importing agent
load_dotenv(Path(__file__).parent / ".env")

# Import agent after loading environment
from my_agent.agent import agent  # noqa: E402

# ========================================
# Phase 1: Application Initialization (once at startup)
# ========================================

APP_NAME = "bidi-workshop"

app = FastAPI()

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create session service - stores conversation history
session_service = InMemorySessionService()

# Create runner - orchestrates agent execution
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service,
)

print(f"Application initialized with model: {agent.model}")


@app.get("/")
async def root():
    """Serve the index.html page."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
) -> None:
    """WebSocket endpoint - still echoing, but ADK is ready."""
    await websocket.accept()
    print(f"Client connected: user={user_id}, session={session_id}")

    try:
        while True:
            message = await websocket.receive()

            if "text" in message:
                text_data = message["text"]
                print(f"Received: {text_data}")

                # Still echoing for now - we'll add ADK in next step
                response = {
                    "content": {
                        "parts": [{"text": f"ADK Ready! Model: {agent.model}"}]
                    }
                }
                await websocket.send_text(json.dumps(response))
                await websocket.send_text(json.dumps({"turnComplete": True}))

    except (WebSocketDisconnect, RuntimeError):
        print("Client disconnected")
