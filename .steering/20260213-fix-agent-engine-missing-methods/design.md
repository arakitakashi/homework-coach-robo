# Design - AgentEngine ラッパーメソッド追加

## アーキテクチャ概要

Agent Engine デプロイフロー:
1. `serialize_agent.py` で `HomeworkCoachAgent` を cloudpickle シリアライズ
2. GCS にアップロード → Agent Engine にデプロイ
3. クライアントが `agent_engines.get()` でプロキシ取得
4. プロキシが sync メソッドから `async_*` を自動生成

## 実装詳細

### `create_session(self, *, user_id: str) -> dict`

```python
def create_session(self, *, user_id: str) -> dict:
    runner = self._get_runner()
    session = asyncio.run(
        runner.session_service.create_session(
            app_name="homework-coach-agent-engine",
            user_id=user_id,
        )
    )
    return {"id": session.id}
```

### `stream_query(self, *, user_id: str, session_id: str, message: str) -> Generator`

```python
def stream_query(self, *, user_id: str, session_id: str, message: str):
    content = types.Content(role="user", parts=[types.Part(text=message)])

    async def collect_events():
        events = []
        async for event in runner.run_async(...):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        events.append({"content": {"parts": [{"text": part.text}]}})
        return events

    for event_dict in asyncio.run(collect_events()):
        yield event_dict
```

## イベント dict 形式

`AgentEngineClient.extract_text()` が期待する形式:
```python
{"content": {"parts": [{"text": "response text"}]}}
```
