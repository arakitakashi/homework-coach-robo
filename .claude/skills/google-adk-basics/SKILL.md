# Google ADK Basics - Agent Development Fundamentals

**Version**: 1.0 | **Last Updated**: 2026-01-31 | **For**: ADK Python SDK v1.0+

---

## Overview

Google Agent Development Kit (ADK) is a code-first framework for building AI agents with Gemini models.

**Key Features:** Code-first Python, multi-agent systems, rich tools, model-agnostic, deploy anywhere

**Requirements:** Python 3.11+, `uv` package manager, Google AI Studio OR Vertex AI

---

## Quick Start

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create Project

```bash
uv venv --python "python3.11" ".venv"
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install google-adk google-genai
```

### 3. Environment Setup

```bash
# .env - Option 1: Google AI Studio (simplest)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key

# Option 2: Vertex AI
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
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Use Google Search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

**Run:** `adk web my_agent` or `adk run my_agent`

---

## App Pattern with Plugins

Use when you need plugins, event compaction, or custom configuration.

```python
# my_agent/__init__.py
from . import agent

# my_agent/agent.py
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.plugins import ContextFilterPlugin

root_agent = Agent(
    name="advanced_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    tools=[],
)

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ContextFilterPlugin(num_invocations_to_keep=3),  # Keep last 3 turns
    ],
)
```

**Plugins:** `ContextFilterPlugin`, custom callbacks

---

## Multi-Agent Systems

```python
from google.adk.agents import Agent

greeter = Agent(name="greeter", model="gemini-2.5-flash", 
                instruction="Greet users warmly.")

task_executor = Agent(name="task_executor", model="gemini-2.5-flash",
                      instruction="Execute tasks efficiently.")

coordinator = Agent(
    name="coordinator",
    model="gemini-2.5-flash",
    description="Coordinates greetings and tasks.",
    sub_agents=[greeter, task_executor],
)
```

---

## Tool Integration

### Define Tool

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

### Implement Handler

```python
from typing import Dict, Any
import json

async def handle_generate_hint(args: Dict[str, Any]) -> str:
    problem = args["problem"]
    level = args["level"]
    hint = f"Hint level {level} for: {problem}"
    return json.dumps({"hint": hint, "level": level})

TOOL_HANDLERS = {"generate_hint": handle_generate_hint}

async def dispatch_tool_call(function_name: str, args: Dict[str, Any]) -> str:
    handler = TOOL_HANDLERS.get(function_name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {function_name}"})
    try:
        return await handler(args)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

### Use Tool

```python
from google.adk.agents import Agent
from .tools import hint_tool

root_agent = Agent(
    name="tutor_agent",
    model="gemini-2.5-flash",
    instruction="Use generate_hint to help students.",
    tools=[hint_tool],
)
```

---

## Session Management

### InMemoryRunner (Development)

```python
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(app_name="my_app", agent=root_agent)

session = await runner.session_service.create_session(
    app_name="my_app",
    user_id="user123",
)

result = await runner.run_async(session=session, new_message="Hello")
```

### VertexAIRunner (Production)

```python
from google.adk.runners import VertexAIRunner

runner = VertexAIRunner(
    app_name="my_app",
    agent=root_agent,
    project_id="your-project-id",
    location="us-central1",
)
# Sessions auto-persisted in Vertex AI
```

---

## Best Practices

### 1. Agent Structure

✅ **DO**: `my_agent/__init__.py` + `agent.py` with `root_agent`
❌ **DON'T**: Custom file names (won't be discovered)

### 2. Development

✅ **DO**: `uv` + Python 3.11+
❌ **DON'T**: `pip` or Python 3.9

### 3. Error Handling

```python
try:
    result = await agent.run_async(session, message)
except Exception as e:
    logger.error(f"Agent error: {e}", exc_info=True)
    return {"error": "Sorry, I encountered an issue."}
```

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

### 5. Context Management

```python
from google.adk.plugins import ContextFilterPlugin

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[ContextFilterPlugin(num_invocations_to_keep=3)],
)
```

---

## Common Issues

### Issue #1: "Module not found" with `adk web`

**Cause**: Wrong structure
**Solution**: Ensure `my_agent/__init__.py` has `from . import agent` and `agent.py` has `root_agent`

### Issue #2: Tool calls fail

**Cause**: Missing error handling
**Solution**: Add try-except in `dispatch_tool_call` (see Tool Integration section)

### Issue #3: High latency

**Solutions**:
- Use `gemini-2.5-flash`
- Reduce system instruction length
- Minimize tool count
- Use `ContextFilterPlugin`

---

## Testing

### Unit Test

```python
import pytest
from example_agent.agent import root_agent

@pytest.mark.asyncio
async def test_agent_config():
    assert root_agent.name == "tutor_agent"
    assert root_agent.model == "gemini-2.5-flash"
```

### Integration Test

```python
import pytest
from google.adk.runners import InMemoryRunner

@pytest.mark.asyncio
async def test_agent_run():
    runner = InMemoryRunner(app_name="test", agent=root_agent)
    session = await runner.session_service.create_session(
        app_name="test", user_id="test-user"
    )
    result = await runner.run_async(session=session, new_message="Hello")
    assert result is not None
```

---

## Checklist

### New Agent
- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Create venv: `uv venv --python "python3.11" ".venv"`
- [ ] Activate: `source .venv/bin/activate`
- [ ] Install: `uv pip install google-adk google-genai`
- [ ] Create: `my_agent/__init__.py` + `agent.py`
- [ ] Define: `root_agent = Agent(...)` in `agent.py`
- [ ] Add: `from . import agent` in `__init__.py`
- [ ] Config: `.env` with API key
- [ ] Test: `adk web my_agent`

### Production
- [ ] Use `VertexAIRunner`
- [ ] Error handling
- [ ] Rate limiting
- [ ] Safety settings
- [ ] Monitoring
- [ ] Load testing

---

## References

- [ADK Docs](https://google.github.io/adk-docs)
- [ADK Python](https://github.com/google/adk-python)
- [AGENTS.md](https://github.com/google/adk-python/blob/main/AGENTS.md)
- [Samples](https://github.com/google/adk-samples)
- **For Live API**: Use `/google-adk-live` skill
- [Reddit](https://www.reddit.com/r/agentdevelopmentkit/)

---

**Version 1.0** | **Next**: Use `/google-adk-live` for real-time voice/video
