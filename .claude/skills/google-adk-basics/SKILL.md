# Google ADK Basics - Agent Development Fundamentals

**Version**: 2.0 | **Last Updated**: 2026-02-02 | **For**: ADK Python SDK v1.0+

---

## Overview

Google Agent Development Kit (ADK) is a code-first framework for building AI agents with Gemini models.

**Key Features:** Code-first Python, multi-agent systems, rich tools, session & memory management, deploy anywhere

**Requirements:** Python 3.10+, `uv` package manager, Google AI Studio OR Vertex AI

---

## Quick Start

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create Project

```bash
uv venv --python "python3.10" ".venv"
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install google-adk google-genai
```

### 3. Environment Setup

```bash
# .env - Option 1: Google AI Studio (simplest)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key

# Option 2: Vertex AI (production)
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Agent Structure Convention

**CRITICAL**: All agents MUST follow this structure for ADK CLI to work:

```
my_agent/
├── __init__.py     # MUST contain: from . import agent
└── agent.py        # MUST define: root_agent OR app
```

**Why**: ADK CLI (`adk web`, `adk run`) auto-discovers agents using this convention.

---

## Simple Agent Pattern

Use for basic agents without plugins or advanced features.

```python
# my_agent/__init__.py
from . import agent

# my_agent/agent.py
from google.adk.agents import Agent

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    description="An assistant that can help with tasks.",
)
```

**Run:** `adk web my_agent` or `adk run my_agent`

---

## LlmAgent Pattern (Recommended)

Use `LlmAgent` for production agents with tools and callbacks.

```python
from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

root_agent = LlmAgent(
    name="homework_coach",
    model="gemini-2.5-flash",
    description="Homework coaching agent",
    instruction="""
        You are a helpful tutor for elementary school students.
        Use the Socratic method to guide students.
        Never give direct answers.
    """,
    tools=[PreloadMemoryTool(), google_search_tool],
    output_key="coach_response",  # Store output in session state
    after_agent_callback=save_to_memory,  # Callback after execution
)
```

---

## Session & Memory Management

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    ADK Runner                        │
│  ┌─────────────────┐    ┌─────────────────────────┐ │
│  │ SessionService  │    │   MemoryBankService     │ │
│  │ (short-term)    │    │   (long-term)           │ │
│  │                 │    │                         │ │
│  │ - conversation  │    │ - user preferences      │ │
│  │ - session state │    │ - learned facts         │ │
│  │ - current turn  │    │ - historical context    │ │
│  └─────────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### SessionService (Short-term Memory)

Manages conversation context within a session.

```python
# Development: InMemorySessionService
from google.adk.sessions import InMemorySessionService
session_service = InMemorySessionService()

# Production: VertexAiSessionService
from google.adk.sessions import VertexAiSessionService
session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

# Create session
session = await session_service.create_session(
    app_name="homework_coach",
    user_id="user123",
)

# Get existing session
session = await session_service.get_session(
    app_name="homework_coach",
    user_id="user123",
    session_id="existing-session-id",
)
```

### session.state (Custom State)

Store custom data in session state:

```python
# Store custom state
session.state = {
    "current_phase": 2,
    "problem": "3 + 5 = ?",
    "attempts_count": 1,
    "hint_level": 1,
}

# Access in agent instruction
instruction = """
Current phase: {current_phase}
Problem: {problem}
"""
```

### MemoryBankService (Long-term Memory)

Persists important information across sessions.

```python
# Production: VertexAiMemoryBankService
from google.adk.memory import VertexAiMemoryBankService

memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

# Save session to memory (in callback)
await memory_service.add_session_to_memory(session)
```

### PreloadMemoryTool

Automatically loads relevant memories into context:

```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

root_agent = LlmAgent(
    name="coach",
    tools=[PreloadMemoryTool()],  # Add to tools
    instruction="Use memory to personalize responses.",
)
```

---

## Runner Configuration

### Complete Runner Setup

```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService

# Initialize services
session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

# Create runner
runner = Runner(
    app_name="homework_coach",
    agent=root_agent,
    session_service=session_service,
    memory_service=memory_service,
)

# Run agent
async def call_agent(user_id: str, session_id: str, message: str):
    session = await session_service.get_session(
        app_name="homework_coach",
        user_id=user_id,
        session_id=session_id,
    ) or await session_service.create_session(
        app_name="homework_coach",
        user_id=user_id,
    )

    content = types.Content(role="user", parts=[types.Part(text=message)])

    events = runner.run(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    )

    for event in events:
        if event.is_final_response():
            return event.content.parts[0].text
```

---

## Callbacks

### after_agent_callback

Execute code after agent completes:

```python
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

async def save_session_to_memory(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """Save session to memory bank after agent execution."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )
    # Return None to not modify response
    return None

root_agent = LlmAgent(
    name="coach",
    after_agent_callback=save_session_to_memory,
)
```

---

## Tool Integration

### Define Tool with FunctionDeclaration

```python
from google.genai import types

hint_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_hint",
            description="Generate a hint for the student",
            parameters={
                "type": "object",
                "properties": {
                    "problem": {"type": "string", "description": "The homework problem"},
                    "level": {"type": "integer", "description": "Hint level (1-3)",
                             "enum": [1, 2, 3]}
                },
                "required": ["problem", "level"]
            }
        )
    ]
)
```

### MCP Toolset

Use Model Context Protocol tools:

```python
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

maps_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mapstools.googleapis.com/mcp",
        headers={"X-Goog-Api-Key": API_KEY}
    )
)

root_agent = LlmAgent(
    name="agent",
    tools=[maps_toolset],
)
```

---

## Multi-Agent Systems

```python
from google.adk.agents import LlmAgent

greeter = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction="Greet users warmly.",
)

tutor = LlmAgent(
    name="tutor",
    model="gemini-2.5-flash",
    instruction="Help with homework using Socratic method.",
)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    description="Coordinates greetings and tutoring.",
    sub_agents=[greeter, tutor],
)
```

---

## Best Practices

### 1. Agent Structure

- **DO**: `my_agent/__init__.py` + `agent.py` with `root_agent`
- **DON'T**: Custom file names (won't be discovered by ADK CLI)

### 2. Session Management

- **DO**: Use ADK SessionService (don't build custom state tracker)
- **DO**: Store custom state in `session.state`
- **DON'T**: Manage session state manually

### 3. Memory

- **DO**: Use `PreloadMemoryTool` for personalization
- **DO**: Save important sessions with `after_agent_callback`
- **DON'T**: Store sensitive data in memory

### 4. Safety (for children)

```python
from google.genai import types

safety_settings = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT",
                       threshold="BLOCK_MEDIUM_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH",
                       threshold="BLOCK_MEDIUM_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                       threshold="BLOCK_MEDIUM_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT",
                       threshold="BLOCK_MEDIUM_AND_ABOVE"),
]
```

---

## Common Issues

### Issue #1: "Module not found" with `adk web`

**Cause**: Wrong structure
**Solution**: Ensure `my_agent/__init__.py` has `from . import agent` and `agent.py` has `root_agent`

### Issue #2: Session not persisting

**Cause**: Using InMemorySessionService in production
**Solution**: Use VertexAiSessionService with Agent Engine

### Issue #3: Memory not loading

**Cause**: Missing PreloadMemoryTool
**Solution**: Add `PreloadMemoryTool()` to agent tools

---

## Testing

### Unit Test

```python
import pytest
from my_agent.agent import root_agent

@pytest.mark.asyncio
async def test_agent_config():
    assert root_agent.name == "homework_coach"
    assert root_agent.model == "gemini-2.5-flash"
```

### Integration Test with InMemorySessionService

```python
import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

@pytest.mark.asyncio
async def test_agent_session():
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="test",
        agent=root_agent,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="test",
        user_id="test-user",
    )

    content = types.Content(role="user", parts=[types.Part(text="Hello")])
    events = runner.run(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    )

    for event in events:
        if event.is_final_response():
            assert event.content is not None
            break
```

---

## Checklist

### New Agent
- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Create venv: `uv venv --python "python3.10" ".venv"`
- [ ] Activate: `source .venv/bin/activate`
- [ ] Install: `uv pip install google-adk google-genai`
- [ ] Create: `my_agent/__init__.py` + `agent.py`
- [ ] Define: `root_agent = LlmAgent(...)` in `agent.py`
- [ ] Add: `from . import agent` in `__init__.py`
- [ ] Config: `.env` with API key
- [ ] Test: `adk web my_agent`

### Production
- [ ] Use `VertexAiSessionService`
- [ ] Use `VertexAiMemoryBankService`
- [ ] Add `PreloadMemoryTool`
- [ ] Implement `after_agent_callback`
- [ ] Error handling
- [ ] Safety settings
- [ ] Monitoring

---

## References

- [ADK Docs](https://google.github.io/adk-docs)
- [ADK Python](https://github.com/google/adk-python)
- [ADK Samples](https://github.com/google/adk-samples)
- [Memory Docs](https://google.github.io/adk-docs/sessions/memory)
- **For Live API**: Use `/google-adk-live` skill

---

**Version 2.0** | **Next**: Use `/google-adk-live` for real-time voice/video
