"""Step 1: Minimal WebSocket server - echoes messages back."""

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Create FastAPI application
app = FastAPI()

# Serve static files (HTML, CSS, JS)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


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
    """WebSocket endpoint - currently just echoes messages."""
    await websocket.accept()
    print(f"Client connected: user={user_id}, session={session_id}")

    try:
        while True:
            # Receive message from client
            message = await websocket.receive()

            if "text" in message:
                text_data = message["text"]
                print(f"Received text: {text_data}")

                # Echo back a simple response (content first, then turnComplete)
                import json
                response = {
                    "content": {
                        "parts": [{"text": f"Echo: {text_data}"}]
                    }
                }
                await websocket.send_text(json.dumps(response))
                await websocket.send_text(json.dumps({"turnComplete": True}))

            elif "bytes" in message:
                print(f"Received binary: {len(message['bytes'])} bytes")
                # Ignore binary for now

    except (WebSocketDisconnect, RuntimeError):
        print("Client disconnected")
