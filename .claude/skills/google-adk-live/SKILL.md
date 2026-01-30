# Google ADK Live - Gemini Live API (Bidi-streaming)

**Version**: 1.0 | **Last Updated**: 2026-01-31 | **For**: ADK + Gemini Live API

---

## Overview

Gemini Live API enables low-latency, bidirectional voice and video interactions.

**Use Cases:** Real-time tutors, live support, accessibility tools, interactive assistants

**Requirements:**
- ADK basics (use `/google-adk-basics`)
- Model: `gemini-live-2.5-flash-preview-native-audio`
- SSL: `export SSL_CERT_FILE=$(python -m certifi)`

**Supported Models:** Only `gemini-live-2.5-flash-preview-native-audio` (check [docs](https://ai.google.dev/gemini-api/docs/models#live-api))

---

## Complete Example (FastAPI + WebSocket)

**Production sample: `realtime-conversational-agent`**

### Project Structure

```
server/
├── main.py              # FastAPI + WebSocket
├── example_agent/
│   ├── __init__.py      # from . import agent
│   ├── agent.py         # root_agent
│   └── prompts.py
├── .env
└── pyproject.toml
```

### Agent Definition

```python
# example_agent/agent.py
from google.adk.agents import Agent

root_agent = Agent(
    name="live_agent",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="Real-time voice assistant",
    instruction="You are helpful. Keep responses concise.",
)
```

### Main Server (main.py)

```python
import asyncio
import base64
import json
from fastapi import FastAPI, WebSocket
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.genai.types import Blob, Content, Part
from starlette.websockets import WebSocketDisconnect
from example_agent.agent import root_agent

async def start_agent_session(user_id: str):
    runner = InMemoryRunner(app_name="my_app", agent=root_agent)
    session = await runner.session_service.create_session(
        app_name="my_app", user_id=user_id
    )
    live_request_queue = LiveRequestQueue()
    
    run_config = RunConfig(
        streaming_mode="bidi",
        session_resumption=types.SessionResumptionConfig(transparent=True),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
                end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
            )
        ),
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            ),
            language_code="en-US",
        ),
        output_audio_transcription={},
        input_audio_transcription={},
    )
    
    live_events = runner.run_live(session, live_request_queue, run_config)
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket: WebSocket, live_events):
    async for event in live_events:
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
            
            transcription = "".join(p.text for p in event.content.parts if p.text)
            
            if hasattr(event.content, "role") and event.content.role == "user":
                if transcription:
                    message["input_transcription"] = {
                        "text": transcription, "is_final": not event.partial
                    }
            
            elif hasattr(event.content, "role") and event.content.role == "model":
                if transcription:
                    message["output_transcription"] = {
                        "text": transcription, "is_final": not event.partial
                    }
                    message["parts"].append({"type": "text", "data": transcription})
                
                for part in event.content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                        audio = base64.b64encode(part.inline_data.data).decode("ascii")
                        message["parts"].append({"type": "audio/pcm", "data": audio})
                    elif part.function_call:
                        message["parts"].append({
                            "type": "function_call",
                            "data": {"name": part.function_call.name, 
                                   "args": part.function_call.args or {}}
                        })
            
            if message["parts"] or message["turn_complete"] or message["input_transcription"] or message["output_transcription"]:
                await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error: {e}")


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    while True:
        try:
            msg = json.loads(await websocket.receive_text())
            mime = msg["mime_type"]
            
            if mime == "text/plain":
                content = Content(role="user", parts=[Part.from_text(text=msg["data"])])
                live_request_queue.send_content(content=content)
            elif mime == "audio/pcm":
                data = base64.b64decode(msg["data"])
                live_request_queue.send_realtime(Blob(data=data, mime_type=mime))
            elif mime == "image/jpeg":
                data = base64.b64decode(msg["data"])
                live_request_queue.send_realtime(Blob(data=data, mime_type=mime))
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(f"Error: {e}")


app = FastAPI()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    live_events, live_request_queue = await start_agent_session(user_id)
    
    tasks = [
        asyncio.create_task(agent_to_client_messaging(websocket, live_events)),
        asyncio.create_task(client_to_agent_messaging(websocket, live_request_queue))
    ]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    live_request_queue.close()
```

**Run:** `export SSL_CERT_FILE=$(python -m certifi) && uvicorn main:app --reload`

---

## RunConfig Options

```python
from google.genai import types

run_config = RunConfig(
    streaming_mode="bidi",  # REQUIRED
    session_resumption=types.SessionResumptionConfig(transparent=True),  # Maintain context
    
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
        )
    ),
    
    response_modalities=["AUDIO"],  # or ["TEXT"] or ["AUDIO", "TEXT"]
    
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"  # Aoede, Charon, Fenrir, Kore, Puck
            )
        ),
        language_code="en-US",  # or ja-JP
    ),
    
    output_audio_transcription={},  # Enable transcriptions
    input_audio_transcription={},
)
```

---

## LiveRequestQueue Methods

```python
# Send text
content = Content(role="user", parts=[Part.from_text(text="Hello")])
live_request_queue.send_content(content=content)

# Send audio
audio_blob = Blob(data=audio_bytes, mime_type="audio/pcm")
live_request_queue.send_realtime(audio_blob)

# Send image/video
image_blob = Blob(data=image_bytes, mime_type="image/jpeg")
live_request_queue.send_realtime(image_blob)

# Close
live_request_queue.close()
```

---

## Event Processing

### Event Structure

```python
event.author          # "user" or "agent"
event.partial         # True if intermediate
event.turn_complete   # True if finished
event.interrupted     # True if interrupted
event.content         # Content with parts
```

### Content Parts

```python
part.text                      # Text
part.inline_data.data          # Audio bytes
part.inline_data.mime_type     # "audio/pcm"
part.function_call.name        # Function name
part.function_call.args        # Arguments
```

---

## Session Resumption

```python
run_config = RunConfig(
    streaming_mode="bidi",
    session_resumption=types.SessionResumptionConfig(transparent=True),
)

# Reuse session across connections
session = await runner.session_service.get_session(session_id="existing-id")
```

---

## Best Practices

### 1. SSL Certificate (REQUIRED)

```bash
export SSL_CERT_FILE=$(python -m certifi)
```

### 2. Error Handling

```python
try:
    async for event in live_events:
        await websocket.send_text(json.dumps(event))
except WebSocketDisconnect:
    live_request_queue.close()
except Exception as e:
    print(f"Error: {e}")
    live_request_queue.close()
```

### 3. Heartbeat

```python
async def heartbeat(websocket: WebSocket):
    while True:
        try:
            await websocket.send_json({"type": "ping"})
            await asyncio.sleep(30)
        except:
            break

asyncio.create_task(heartbeat(websocket))
```

### 4. Voice Selection

```python
# Voices: Aoede (warm), Charon (deep), Fenrir (energetic), Kore (calm), Puck (playful)
voice_name="Puck"  # Choose based on use case
language_code="ja-JP"  # Set language
```

---

## Common Issues

### Issue #1: SSL Error

**Solution:** `export SSL_CERT_FILE=$(python -m certifi)`

### Issue #2: WebSocket Disconnects

**Solution:** Implement heartbeat (see Best Practices #3)

### Issue #3: High Latency

**Solutions:**
- Use `response_modalities=["AUDIO"]`
- Reduce instruction length
- Minimize tools
- Check network

### Issue #4: Audio Format

**Solution:** Standardize
```python
AUDIO = {"encoding": "LINEAR16", "sample_rate": 16000, "channels": 1}
```

---

## Testing

### Unit

```python
import pytest
from example_agent.agent import root_agent

@pytest.mark.asyncio
async def test_live_agent():
    assert root_agent.model == "gemini-live-2.5-flash-preview-native-audio"
```

### Integration

```python
from fastapi.testclient import TestClient
from server.main import app

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws/test") as ws:
        ws.send_json({"mime_type": "text/plain", "data": "Hi"})
        response = ws.receive_json()
        assert "parts" in response or "output_transcription" in response
```

---

## Checklist

### Live API
- [ ] Install: `uv pip install google-adk google-genai fastapi uvicorn`
- [ ] Model: `gemini-live-2.5-flash-preview-native-audio`
- [ ] SSL: `export SSL_CERT_FILE=$(python -m certifi)`
- [ ] Queue: `LiveRequestQueue()`
- [ ] Config: `RunConfig(streaming_mode="bidi")`
- [ ] Start: `runner.run_live()`
- [ ] WebSocket: Implement bidi messaging
- [ ] Cleanup: `live_request_queue.close()`

### Production
- [ ] Error handling
- [ ] Heartbeat
- [ ] Session resumption
- [ ] Rate limiting
- [ ] Monitoring

---

## References

- [Bidi-streaming Guide](https://google.github.io/adk-docs/streaming/dev-guide/part1/)
- [Quickstart](https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/)
- [Sample](https://github.com/google/adk-samples/tree/main/python/agents/realtime-conversational-agent)
- [Live API](https://ai.google.dev/gemini-api/docs/live)
- **Prerequisites:** `/google-adk-basics`

---

**Version 1.0** | **Requires:** `/google-adk-basics` for fundamentals
