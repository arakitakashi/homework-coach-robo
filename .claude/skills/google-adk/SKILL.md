# Google ADK (Agent Development Kit) Skill

**Version**: 1.0
**Last Updated**: 2026-01-31
**Compliance**: Google Agent Development Kit (ADK) Python SDK, Gemini Live API

---

Production-tested patterns for building AI agents with Google ADK, Gemini Live API, real-time streaming, and FastAPI integration.

## Overview

Google Agent Development Kit (ADK) is a framework for building AI agents powered by Google's Gemini models. This skill focuses on:

- **Real-time conversation** with Gemini Live API
- **Bidirectional streaming** (WebSocket) for voice interactions
- **Tool integration** for extending agent capabilities
- **FastAPI integration** for production deployments
- **Voice processing** patterns for conversational AI

## Latest Versions

Based on the project's MVP Phase requirements:

- **Python**: 3.10+
- **Google ADK**: Latest Python SDK
- **Gemini Live API**: Latest version
- **FastAPI**: 0.128.0+
- **uv**: Package manager (recommended)

---

## Quick Start

### Project Setup with uv

```bash
# Add ADK dependencies
uv add google-adk google-genai

# For voice processing
uv add google-cloud-speech google-cloud-texttospeech

# For WebSocket support
uv add websockets

# Verify installation
uv run python -c "import google.genai; print('ADK installed successfully')"
```

### Environment Setup

```bash
# .env
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### Minimal Working Example

```python
# src/agent/basic_agent.py
import asyncio
from google import genai

async def main():
    # Initialize client
    client = genai.Client(api_key="YOUR_API_KEY")

    # Create a simple agent
    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents="こんにちは！算数の問題を教えてください。"
    )

    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Core Concepts

### 1. Agent Configuration

ADK agents are configured with model settings, system instructions, and tools.

```python
# src/agent/config.py
from google import genai
from typing import Optional

class AgentConfig:
    """Configuration for ADK agent"""

    MODEL_NAME = "gemini-2.0-flash-exp"

    # System instruction for Socratic dialogue
    SYSTEM_INSTRUCTION = """
    あなたは小学校低学年（1〜3年生）向けの宿題サポートロボットです。

    重要な原則：
    1. 答えを直接教えない - 質問で子供を導く（ソクラテス式対話）
    2. 子供の感情に適応する - 音声トーンからフラストレーションを検知
    3. プロセスを評価する - 正解/不正解ではなく、考えたプロセスを重視
    4. 対等な関係 - 「完璧な先生」ではなく「一緒に悩む仲間」として振る舞う

    3段階ヒントシステム：
    - レベル1: 問題理解の確認（「この問題、何を聞いてると思う？」）
    - レベル2: 既習事項の想起（「同じような問題、前にやったよね？」）
    - レベル3: 部分的支援（「じゃあ、最初の1ステップだけ一緒にやろう」）
    """

    # Generation config
    GENERATION_CONFIG = {
        "temperature": 0.8,  # Creative but controlled
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 500,
    }

    # Safety settings (for children)
    SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]

def create_agent_config() -> dict:
    """Create agent configuration"""
    return {
        "model": AgentConfig.MODEL_NAME,
        "system_instruction": AgentConfig.SYSTEM_INSTRUCTION,
        "generation_config": AgentConfig.GENERATION_CONFIG,
        "safety_settings": AgentConfig.SAFETY_SETTINGS,
    }
```

### 2. Tool Integration

Tools extend agent capabilities with custom functions.

```python
# src/agent/tools.py
from google.genai import types

# Define a tool for hint generation
hint_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_hint",
            description="Generate a hint for the student based on their current level",
            parameters={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "The homework problem the student is working on"
                    },
                    "current_level": {
                        "type": "integer",
                        "description": "Current hint level (1, 2, or 3)",
                        "enum": [1, 2, 3]
                    },
                    "previous_attempts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Student's previous answers or attempts"
                    }
                },
                "required": ["problem", "current_level"]
            }
        )
    ]
)

# Tool for emotion detection
emotion_detection_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="analyze_emotion",
            description="Analyze student's emotional state from voice tone",
            parameters={
                "type": "object",
                "properties": {
                    "audio_features": {
                        "type": "object",
                        "description": "Audio features extracted from voice",
                        "properties": {
                            "pitch": {"type": "number"},
                            "energy": {"type": "number"},
                            "speaking_rate": {"type": "number"}
                        }
                    }
                },
                "required": ["audio_features"]
            }
        )
    ]
)

# Tool for progress tracking
progress_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="record_progress",
            description="Record student's progress on a problem",
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "problem_id": {"type": "string"},
                    "solved_independently": {"type": "boolean"},
                    "hints_used": {"type": "integer"},
                    "time_spent_seconds": {"type": "integer"}
                },
                "required": ["session_id", "problem_id", "solved_independently", "hints_used"]
            }
        )
    ]
)

# Combine tools
ALL_TOOLS = [hint_tool, emotion_detection_tool, progress_tool]
```

### 3. Tool Function Implementations

```python
# src/agent/tool_handlers.py
from typing import Dict, Any
import json

async def handle_generate_hint(args: Dict[str, Any]) -> str:
    """Handle hint generation tool call"""
    problem = args.get("problem")
    current_level = args.get("current_level")
    previous_attempts = args.get("previous_attempts", [])

    # Import hint system service
    from src.services.hint_system import HintSystem

    hint_system = HintSystem()
    hint = await hint_system.generate_hint({
        "problem": problem,
        "current_level": current_level,
        "previous_levels": list(range(1, current_level))
    })

    return json.dumps({
        "hint": hint.message,
        "level": hint.level,
        "type": hint.type
    })

async def handle_analyze_emotion(args: Dict[str, Any]) -> str:
    """Handle emotion analysis tool call"""
    audio_features = args.get("audio_features", {})

    # Import emotion detection service
    from src.services.emotion_detector import EmotionDetector

    detector = EmotionDetector()
    emotion = await detector.analyze(audio_features)

    return json.dumps({
        "emotion": emotion.state,
        "frustration_level": emotion.frustration_level,
        "recommendation": emotion.support_recommendation
    })

async def handle_record_progress(args: Dict[str, Any]) -> str:
    """Handle progress recording tool call"""
    from src.services.progress_tracker import ProgressTracker
    from google.cloud.firestore_v1 import AsyncClient
    from src.database import get_firestore_client

    db = get_firestore_client()
    tracker = ProgressTracker()

    await tracker.record(
        db=db,
        session_id=args["session_id"],
        problem_id=args["problem_id"],
        solved_independently=args["solved_independently"],
        hints_used=args["hints_used"],
        time_spent_seconds=args.get("time_spent_seconds", 0)
    )

    return json.dumps({"status": "recorded"})

# Tool dispatcher
TOOL_HANDLERS = {
    "generate_hint": handle_generate_hint,
    "analyze_emotion": handle_analyze_emotion,
    "record_progress": handle_record_progress,
}

async def dispatch_tool_call(function_name: str, args: Dict[str, Any]) -> str:
    """Dispatch tool call to appropriate handler"""
    handler = TOOL_HANDLERS.get(function_name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {function_name}"})

    try:
        return await handler(args)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

---

## Gemini Live API Integration

### Real-time Streaming Agent

```python
# src/agent/live_agent.py
import asyncio
from google import genai
from google.genai import types
from typing import AsyncGenerator, Optional
import json

from src.agent.config import create_agent_config
from src.agent.tools import ALL_TOOLS
from src.agent.tool_handlers import dispatch_tool_call

class LiveAgent:
    """Agent for real-time conversation with Gemini Live API"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.config = create_agent_config()

    async def stream_conversation(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        session_id: str
    ) -> AsyncGenerator[dict, None]:
        """
        Stream conversation with audio input/output

        Args:
            audio_stream: Async generator yielding audio chunks
            session_id: User session ID

        Yields:
            Dict with response type and content
        """
        # Configure live session
        live_config = {
            "model": self.config["model"],
            "system_instruction": self.config["system_instruction"],
            "generation_config": self.config["generation_config"],
            "tools": ALL_TOOLS,
        }

        # Start live session
        async with self.client.aio.live.connect(
            model=live_config["model"],
            config=live_config
        ) as session:

            # Send audio chunks
            async def send_audio():
                async for chunk in audio_stream:
                    await session.send(chunk, end_of_turn=False)
                await session.send("", end_of_turn=True)

            # Receive responses
            async def receive_responses():
                async for response in session.receive():
                    # Handle different response types
                    if response.server_content:
                        # Text response
                        if response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if part.text:
                                    yield {
                                        "type": "text",
                                        "content": part.text
                                    }
                                elif part.inline_data:
                                    # Audio response
                                    yield {
                                        "type": "audio",
                                        "content": part.inline_data.data,
                                        "mime_type": part.inline_data.mime_type
                                    }

                    # Handle tool calls
                    if response.tool_call:
                        function_name = response.tool_call.name
                        args = json.loads(response.tool_call.args)

                        # Execute tool
                        result = await dispatch_tool_call(function_name, args)

                        # Send tool response back
                        await session.send(
                            types.LiveClientToolResponse(
                                function_responses=[
                                    types.FunctionResponse(
                                        name=function_name,
                                        response={"result": result}
                                    )
                                ]
                            )
                        )

                        yield {
                            "type": "tool_call",
                            "function": function_name,
                            "result": result
                        }

            # Run both tasks concurrently
            async with asyncio.TaskGroup() as group:
                group.create_task(send_audio())
                async for response in receive_responses():
                    yield response

    async def generate_text_response(self, prompt: str) -> str:
        """
        Generate a text-only response (non-streaming)

        Args:
            prompt: User's text input

        Returns:
            Agent's text response
        """
        response = await self.client.aio.models.generate_content(
            model=self.config["model"],
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.config["system_instruction"],
                temperature=self.config["generation_config"]["temperature"],
                tools=ALL_TOOLS,
            )
        )

        # Handle tool calls if any
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    # Execute tool
                    result = await dispatch_tool_call(
                        part.function_call.name,
                        json.loads(part.function_call.args)
                    )
                    # Continue conversation with tool result
                    # (simplified - production would need multi-turn handling)

        return response.text
```

---

## FastAPI Integration Patterns

### WebSocket Endpoint for Real-time Chat

```python
# src/api/routes/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from google.cloud.firestore_v1 import AsyncClient
import asyncio
import json
from typing import AsyncGenerator

from src.database import get_db
from src.agent.live_agent import LiveAgent
from src.auth.dependencies import get_current_user_ws
from src.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: AsyncClient = Depends(get_db)
):
    """
    WebSocket endpoint for real-time voice chat

    Message format (client -> server):
    {
        "type": "audio",
        "data": "base64-encoded-audio",
        "format": "audio/pcm"
    }

    Message format (server -> client):
    {
        "type": "audio" | "text" | "tool_call" | "error",
        "content": "...",
        "metadata": {...}
    }
    """
    await manager.connect(session_id, websocket)

    # Initialize agent
    agent = LiveAgent(api_key=settings.GOOGLE_API_KEY)

    try:
        # Audio stream generator
        async def audio_generator() -> AsyncGenerator[bytes, None]:
            while True:
                try:
                    message = await websocket.receive_json()

                    if message["type"] == "audio":
                        # Decode base64 audio
                        import base64
                        audio_bytes = base64.b64decode(message["data"])
                        yield audio_bytes

                    elif message["type"] == "end":
                        break

                except WebSocketDisconnect:
                    break

        # Stream conversation
        async for response in agent.stream_conversation(
            audio_stream=audio_generator(),
            session_id=session_id
        ):
            # Send response to client
            await manager.send_message(session_id, response)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error",
            "content": str(e)
        })
        manager.disconnect(session_id)

@router.post("/sessions/{session_id}/message")
async def send_text_message(
    session_id: str,
    message: str,
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """
    Send a text message (non-streaming alternative)
    """
    agent = LiveAgent(api_key=settings.GOOGLE_API_KEY)

    # Verify session ownership
    session_doc = await db.collection("sessions").document(session_id).get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_doc.to_dict()
    if session_data["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Generate response
    response_text = await agent.generate_text_response(message)

    # Save to Firestore
    await db.collection("sessions").document(session_id).collection("messages").add({
        "role": "user",
        "content": message,
        "timestamp": datetime.utcnow()
    })

    await db.collection("sessions").document(session_id).collection("messages").add({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.utcnow()
    })

    return {
        "response": response_text,
        "session_id": session_id
    }
```

### Session Management

```python
# src/api/routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1 import AsyncClient
from datetime import datetime
from pydantic import BaseModel

from src.database import get_db
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
    character: str  # robot, wizard, astronaut
    grade_level: int  # 1, 2, or 3

class SessionResponse(BaseModel):
    id: str
    user_id: str
    character: str
    grade_level: int
    status: str
    created_at: datetime

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_in: SessionCreate,
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """Create a new chat session"""
    doc_ref = db.collection("sessions").document()

    session_data = {
        "id": doc_ref.id,
        "user_id": user.id,
        "character": session_in.character,
        "grade_level": session_in.grade_level,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    await doc_ref.set(session_data)

    return SessionResponse(**session_data)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """Get session details"""
    doc = await db.collection("sessions").document(session_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = doc.to_dict()

    # Authorization check
    if session_data["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return SessionResponse(**session_data)

@router.patch("/{session_id}/end")
async def end_session(
    session_id: str,
    user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """End a chat session"""
    doc_ref = db.collection("sessions").document(session_id)
    doc = await doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = doc.to_dict()

    if session_data["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await doc_ref.update({
        "status": "completed",
        "ended_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return {"status": "completed", "session_id": session_id}
```

---

## Voice Processing Patterns

### Audio Input Processing

```python
# src/services/audio_processor.py
from google.cloud import speech_v1
from typing import AsyncGenerator
import io

class AudioProcessor:
    """Process audio input for ADK"""

    def __init__(self):
        self.client = speech_v1.SpeechAsyncClient()

    async def transcribe_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[str, None]:
        """
        Transcribe streaming audio to text

        Args:
            audio_stream: Generator yielding audio chunks

        Yields:
            Transcribed text chunks
        """
        # Configure recognition
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="ja-JP",
            enable_automatic_punctuation=True,
            model="default",
        )

        streaming_config = speech_v1.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )

        # Create request generator
        async def request_generator():
            yield speech_v1.StreamingRecognizeRequest(
                streaming_config=streaming_config
            )

            async for chunk in audio_stream:
                yield speech_v1.StreamingRecognizeRequest(audio_content=chunk)

        # Stream recognition
        responses = await self.client.streaming_recognize(
            requests=request_generator()
        )

        async for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if result.is_final:
                yield result.alternatives[0].transcript
```

### Audio Output Generation

```python
# src/services/tts_service.py
from google.cloud import texttospeech_v1
from typing import Optional

class TTSService:
    """Text-to-Speech service"""

    def __init__(self):
        self.client = texttospeech_v1.TextToSpeechAsyncClient()

    async def synthesize(
        self,
        text: str,
        voice_name: str = "ja-JP-Neural2-B",  # Child-friendly voice
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> bytes:
        """
        Convert text to speech

        Args:
            text: Text to synthesize
            voice_name: Google Cloud TTS voice name
            speaking_rate: Speech speed (0.25 to 4.0)
            pitch: Voice pitch (-20.0 to 20.0)

        Returns:
            Audio bytes (MP3 or WAV)
        """
        synthesis_input = texttospeech_v1.SynthesisInput(text=text)

        voice = texttospeech_v1.VoiceSelectionParams(
            language_code="ja-JP",
            name=voice_name,
        )

        audio_config = texttospeech_v1.AudioConfig(
            audio_encoding=texttospeech_v1.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        response = await self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        return response.audio_content
```

---

## Best Practices

### 1. Prompt Engineering for Children

```python
# Good: Age-appropriate, encouraging tone
SYSTEM_INSTRUCTION = """
あなたは小学校低学年の友達です。
一緒に宿題を考えましょう。

大切なこと：
- やさしい言葉を使う
- 答えを教えない、質問で導く
- 頑張ったことを褒める
- 間違えても大丈夫だと伝える
"""

# Bad: Too formal, adult-oriented
SYSTEM_INSTRUCTION = """
You are an educational AI assistant designed to facilitate
learning outcomes through guided inquiry methodology.
"""
```

### 2. Error Handling

```python
# Always handle API errors gracefully
try:
    response = await agent.generate_text_response(prompt)
except Exception as e:
    # Log error
    logger.error(f"Agent error: {e}")

    # Return child-friendly error message
    return {
        "response": "ごめんね、今ちょっと考えがまとまらなくて...もう一度言ってくれる？",
        "error": True
    }
```

### 3. Rate Limiting and Quotas

```python
# Implement rate limiting for API calls
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    async def check_limit(self, user_id: str) -> bool:
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True

# Use in endpoint
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)

@router.post("/message")
async def send_message(message: str, user=Depends(get_current_user)):
    if not await rate_limiter.check_limit(user.id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Process message
    ...
```

### 4. Context Management

```python
# Manage conversation context efficiently
class ConversationContext:
    """Manage conversation history"""

    MAX_HISTORY = 10  # Keep last 10 turns

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: list[dict] = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

        # Trim history
        if len(self.history) > self.MAX_HISTORY * 2:  # 2 messages per turn
            self.history = self.history[-self.MAX_HISTORY * 2:]

    def get_context(self) -> list[dict]:
        return self.history
```

### 5. Safety and Content Filtering

```python
# Always use safety settings for children
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# Apply to all agent configurations
config = {
    "safety_settings": SAFETY_SETTINGS,
    # ... other config
}
```

---

## Common Issues & Solutions

### Issue #1: WebSocket Connection Drops

**Problem**: WebSocket disconnects unexpectedly during streaming

**Solution**:
```python
# Implement heartbeat/ping-pong
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)

    async def heartbeat():
        while True:
            try:
                await websocket.send_json({"type": "ping"})
                await asyncio.sleep(30)  # Every 30 seconds
            except:
                break

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        # Main logic
        ...
    finally:
        heartbeat_task.cancel()
        manager.disconnect(session_id)
```

### Issue #2: Tool Call Errors

**Problem**: Tool calls fail silently or return errors

**Solution**:
```python
# Add comprehensive error handling
async def dispatch_tool_call(function_name: str, args: Dict[str, Any]) -> str:
    handler = TOOL_HANDLERS.get(function_name)
    if not handler:
        logger.error(f"Unknown tool: {function_name}")
        return json.dumps({
            "error": f"Unknown tool: {function_name}",
            "fallback": "I'm not sure how to help with that. Let's try something else."
        })

    try:
        return await handler(args)
    except Exception as e:
        logger.error(f"Tool call failed: {function_name}, error: {e}", exc_info=True)
        return json.dumps({
            "error": str(e),
            "fallback": "Sorry, I had trouble with that. Can we try again?"
        })
```

### Issue #3: Audio Format Mismatches

**Problem**: Audio input/output format incompatibility

**Solution**:
```python
# Standardize audio format
AUDIO_CONFIG = {
    "encoding": "LINEAR16",  # PCM 16-bit
    "sample_rate": 16000,    # 16kHz
    "channels": 1,           # Mono
}

# Convert if needed
import audioop

def convert_audio(audio_bytes: bytes, from_rate: int, to_rate: int) -> bytes:
    """Convert audio sample rate"""
    return audioop.ratecv(audio_bytes, 2, 1, from_rate, to_rate, None)[0]
```

### Issue #4: High Latency

**Problem**: Slow response times in real-time chat

**Solutions**:

1. **Use streaming**: Stream responses as they're generated
2. **Optimize prompts**: Shorter system instructions
3. **Reduce tool calls**: Only use essential tools
4. **Cache common responses**: Cache hint templates
5. **Use faster model**: Consider `gemini-2.0-flash-exp` over larger models

```python
# Enable streaming for faster perceived response
async def stream_response(prompt: str):
    async for chunk in agent.stream_text(prompt):
        yield chunk  # Send immediately, don't wait for full response
```

---

## Testing Patterns

### Unit Testing Agent Logic

```python
# tests/test_agent.py
import pytest
from src.agent.live_agent import LiveAgent
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_generate_text_response():
    """Test text response generation"""
    agent = LiveAgent(api_key="test-key")

    with patch.object(agent.client.aio.models, 'generate_content') as mock_generate:
        # Mock response
        mock_generate.return_value = AsyncMock(text="こんにちは！")

        response = await agent.generate_text_response("こんにちは")

        assert response == "こんにちは！"
        mock_generate.assert_called_once()

@pytest.mark.asyncio
async def test_tool_call_handling():
    """Test tool call execution"""
    from src.agent.tool_handlers import dispatch_tool_call

    result = await dispatch_tool_call("generate_hint", {
        "problem": "3 + 5 = ?",
        "current_level": 1
    })

    assert "hint" in result
    assert "level" in result
```

### Integration Testing WebSocket

```python
# tests/test_websocket.py
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection"""
    client = TestClient(app)

    with client.websocket_connect("/chat/ws/test-session-123") as websocket:
        # Send audio data
        websocket.send_json({
            "type": "audio",
            "data": "...",  # base64 encoded
            "format": "audio/pcm"
        })

        # Receive response
        response = websocket.receive_json()

        assert response["type"] in ["text", "audio", "tool_call"]
```

---

## Performance Optimization

### 1. Connection Pooling

```python
# Reuse client instances
from functools import lru_cache

@lru_cache(maxsize=1)
def get_genai_client():
    """Cached client instance"""
    return genai.Client(api_key=settings.GOOGLE_API_KEY)
```

### 2. Async Batch Processing

```python
# Process multiple requests concurrently
async def process_batch(prompts: list[str]) -> list[str]:
    """Process multiple prompts in parallel"""
    agent = LiveAgent(api_key=settings.GOOGLE_API_KEY)

    tasks = [agent.generate_text_response(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)

    return results
```

### 3. Response Caching

```python
# Cache common responses
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
async def get_cached_hint(problem_hash: str, level: int) -> str:
    """Cache hint responses"""
    # Generate hint
    ...

# Use hash for cache key
problem_hash = hashlib.md5(problem.encode()).hexdigest()
hint = await get_cached_hint(problem_hash, level)
```

---

## References

- [Google AI Python SDK Documentation](https://ai.google.dev/api/python)
- [Gemini Live API Guide](https://ai.google.dev/gemini-api/docs/live)
- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text/docs)
- [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech/docs)

---

## Project-Specific Implementation Checklist

When implementing ADK for 宿題コーチロボット:

- [ ] Configure Socratic dialogue system instruction
- [ ] Implement 3-tier hint system tools
- [ ] Set up emotion detection from voice tone
- [ ] Configure safety settings for children (age 6-9)
- [ ] Implement progress tracking and gamification points
- [ ] Test WebSocket real-time streaming
- [ ] Integrate with Firestore for session/progress storage
- [ ] Set up voice character customization (robot/wizard/astronaut)
- [ ] Implement rate limiting (prevent API overuse)
- [ ] Add fallback responses for API failures
- [ ] Test with actual elementary school homework problems
- [ ] Optimize latency for real-time conversation feel

---

**最終更新**: 2026-01-31
**次回レビュー**: MVP実装開始時
