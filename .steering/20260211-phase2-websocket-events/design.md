# Design - Phase 2 WebSocket Events Implementation

## アーキテクチャ概要

```
┌─────────────────┐
│  Frontend       │
│  (Phase 2 UI)   │
└────────┬────────┘
         │ WebSocket
         ↓
┌─────────────────────────────────┐
│  streaming_service.py           │
│  ┌───────────────────────────┐  │
│  │ _send_phase2_event()      │  │  ← 新規追加
│  └───────────────────────────┘  │
└─────────┬───────────────────────┘
          │
          ↓
┌─────────────────────────────────┐
│  AgentRunnerService             │
│  ┌───────────────────────────┐  │
│  │ Router Agent              │  │
│  │  → Math Coach             │  │
│  │  → Japanese Coach         │  │
│  │  → Encouragement          │  │
│  │  → Review                 │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
          │
          ↓
┌─────────────────────────────────┐
│  ADK Tools                      │
│  - calculate_tool               │
│  - manage_hint_tool             │
│  - update_emotion_tool ← 感情   │
│  - record_progress_tool         │
│  - load_memory_tool             │
└─────────────────────────────────┘
```

## 技術選定

### Pydantic v2スキーマ

すべてのイベント型は`BaseModel`を継承し、Pydantic v2の機能を活用：
- `Field`での型制約とバリデーション
- `Literal`型での値制約
- `model_dump()`でのJSONシリアライズ

### WebSocket送信戦略

既存の`websocket.send_json()`を使用し、イベントタイプで振り分け：
```python
await websocket.send_json({
    "event": "toolExecution",
    "data": {...}
})
```

## データ設計

### voice_stream.pyスキーマ追加

```python
# backend/app/schemas/voice_stream.py

from pydantic import BaseModel, Field
from typing import Literal, Optional

# Tool Execution Events
class ToolExecutionData(BaseModel):
    tool_name: str = Field(..., description="実行されたツール名")
    status: Literal["started", "completed", "failed"] = Field(...)
    input: Optional[dict] = Field(None, description="ツール入力パラメータ")
    output: Optional[dict] = Field(None, description="ツール出力結果")
    error: Optional[str] = Field(None, description="エラーメッセージ（失敗時）")

class ToolExecutionEvent(BaseModel):
    event: Literal["toolExecution"] = "toolExecution"
    data: ToolExecutionData

# Agent Transition Events
class AgentTransitionData(BaseModel):
    from_agent: Optional[str] = Field(None, description="遷移元エージェント")
    to_agent: str = Field(..., description="遷移先エージェント")
    reason: Optional[str] = Field(None, description="遷移理由")

class AgentTransitionEvent(BaseModel):
    event: Literal["agentTransition"] = "agentTransition"
    data: AgentTransitionData

# Emotion Update Events
class EmotionUpdateData(BaseModel):
    emotion_type: Literal["frustration", "confidence", "fatigue", "joy"] = Field(...)
    level: int = Field(..., ge=1, le=5, description="感情レベル（1-5）")
    detected_from: Literal["voice_tone", "text_analysis", "interaction_pattern"] = Field(...)

class EmotionUpdateEvent(BaseModel):
    event: Literal["emotionUpdate"] = "emotionUpdate"
    data: EmotionUpdateData

# Union型でイベントをまとめる
Phase2Event = ToolExecutionEvent | AgentTransitionEvent | EmotionUpdateEvent
```

### streaming_service.py実装

```python
# backend/app/services/streaming_service.py

async def _send_phase2_event(
    self,
    websocket: WebSocket,
    event: Phase2Event
) -> None:
    """Phase 2イベントを送信する内部ヘルパー"""
    try:
        await websocket.send_json(event.model_dump())
    except Exception as e:
        logger.error(f"Failed to send Phase 2 event: {e}")
        # エラーでもメインフローは継続

async def _handle_tool_execution(
    self,
    websocket: WebSocket,
    tool_name: str,
    tool_input: dict
) -> dict:
    """ツール実行とイベント送信を統合"""
    # 1. 開始イベント送信
    await self._send_phase2_event(
        websocket,
        ToolExecutionEvent(
            data=ToolExecutionData(
                tool_name=tool_name,
                status="started",
                input=tool_input
            )
        )
    )

    try:
        # 2. ツール実行
        result = await self._execute_tool(tool_name, tool_input)

        # 3. 完了イベント送信
        await self._send_phase2_event(
            websocket,
            ToolExecutionEvent(
                data=ToolExecutionData(
                    tool_name=tool_name,
                    status="completed",
                    output=result
                )
            )
        )
        return result

    except Exception as e:
        # 4. 失敗イベント送信
        await self._send_phase2_event(
            websocket,
            ToolExecutionEvent(
                data=ToolExecutionData(
                    tool_name=tool_name,
                    status="failed",
                    error=str(e)
                )
            )
        )
        raise
```

## ファイル構成

```
backend/app/
├── schemas/
│   └── voice_stream.py          # ← 型追加
│       ├── ToolExecutionEvent
│       ├── AgentTransitionEvent
│       └── EmotionUpdateEvent
│
└── services/
    └── streaming_service.py     # ← ロジック追加
        ├── _send_phase2_event()
        ├── _handle_tool_execution()
        ├── _handle_agent_transition()
        └── _handle_emotion_update()
```

## 依存関係

### 既存コンポーネントへの依存

1. **AgentRunnerService** (`backend/app/services/adk/runner/runner_service.py`)
   - ツール実行のフック
   - エージェント遷移の監視

2. **Router Agent** (`backend/app/services/adk/agents/router.py`)
   - サブエージェント呼び出しの検知

3. **update_emotion_tool** (`backend/app/services/adk/tools/emotion_analyzer.py`)
   - 感情更新時のフック

### 新規依存の追加

なし（既存のPydantic, FastAPI, WebSocketのみ使用）

## エラーハンドリング

### 1. イベント送信失敗

```python
try:
    await websocket.send_json(event.model_dump())
except WebSocketDisconnect:
    logger.warning("WebSocket disconnected during Phase 2 event send")
    raise  # 接続切断は上位に伝播
except Exception as e:
    logger.error(f"Failed to send Phase 2 event: {e}")
    # その他のエラーは握りつぶして継続
```

### 2. イベントシリアライズ失敗

```python
try:
    event_dict = event.model_dump()
except Exception as e:
    logger.error(f"Failed to serialize Phase 2 event: {e}")
    return  # シリアライズ失敗は送信しない
```

### 3. ツール実行失敗

```python
try:
    result = await self._execute_tool(tool_name, tool_input)
except Exception as e:
    # 失敗イベントを送信してから例外を再送出
    await self._send_phase2_event(...)
    raise
```

## セキュリティ考慮事項

### 1. 機密情報のフィルタリング

ツール入力/出力に機密情報が含まれる可能性があるため、以下をフィルタ：
- パスワード、トークン
- 個人情報（PII）

```python
def _sanitize_tool_data(self, data: dict) -> dict:
    """機密情報をマスク"""
    SENSITIVE_KEYS = {"password", "token", "api_key", "email"}
    return {
        k: "***REDACTED***" if k in SENSITIVE_KEYS else v
        for k, v in data.items()
    }
```

### 2. イベントサイズ制限

大きなツール出力がWebSocketを圧迫しないよう制限：
```python
MAX_EVENT_SIZE = 10_000  # 10KB

if len(json.dumps(event.model_dump())) > MAX_EVENT_SIZE:
    logger.warning("Phase 2 event too large, truncating")
    event.data.output = {"truncated": True}
```

## パフォーマンス考慮事項

### 1. 非同期送信

すべてのイベント送信は`async/await`で非ブロッキング：
```python
await websocket.send_json(...)  # ブロックしない
```

### 2. イベント送信のオーバーヘッド測定

```python
import time

start = time.perf_counter()
await self._send_phase2_event(...)
elapsed = time.perf_counter() - start

if elapsed > 0.01:  # 10ms以上
    logger.warning(f"Slow Phase 2 event send: {elapsed:.3f}s")
```

### 3. バッチ送信の検討（将来）

現状は1イベント1送信だが、将来的にはバッチ送信を検討：
```python
# 将来的な実装案
async def _send_phase2_events_batch(self, events: list[Phase2Event]):
    await websocket.send_json({
        "event": "batchEvents",
        "data": [e.model_dump() for e in events]
    })
```

## 代替案と採用理由

### 代替案1: ADK直接統合

**案**: ADKのRuntime Hookを使ってイベントを直接取得

**不採用理由**:
- ADK Agent Engineのカスタマイズが必要
- 既存のAgentRunnerServiceとの整合性が取りにくい
- デプロイ複雑化

### 代替案2: Server-Sent Events (SSE)

**案**: WebSocketの代わりにSSEを使用

**不採用理由**:
- 既存のWebSocket実装を置き換えるコストが高い
- 双方向通信が必要（音声データアップロード）
- WebSocketで十分機能している

### 採用案: streaming_service.py統合

**理由**:
- 既存のWebSocketインフラを活用
- AgentRunnerServiceとの疎結合を維持
- 段階的な実装・テストが可能
