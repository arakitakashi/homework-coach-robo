# Design - 対話API統合

## アーキテクチャ概要

FastAPI SSEを使用してAgentRunnerServiceをストリーミングエンドポイントとして公開する。

```
┌─────────────────────────────────────────────────────────────┐
│                       Client                                 │
│                  (SSE Consumer)                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              POST /api/v1/dialogue/run                       │
│                  (StreamingResponse)                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   AgentRunnerService                         │
│  - run() → AsyncIterator[Event]                             │
│  - extract_text() → str | None                              │
└─────────────────────────────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ SocraticAgent    │ │ SessionService   │ │ MemoryService    │
│ (ADK Agent)      │ │ (Firestore)      │ │ (Firestore)      │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## 技術選定

| コンポーネント | 選定技術 | 理由 |
|--------------|---------|------|
| ストリーミング | FastAPI StreamingResponse + SSE | 標準的、ブラウザ互換性良好 |
| 永続化 | FirestoreSessionService | ADK準拠、既存実装 |
| 記憶 | FirestoreMemoryService | ADK準拠、既存実装 |
| 非同期処理 | asyncio | FastAPIネイティブ対応 |

## エンドポイント設計

### POST /api/v1/dialogue/run

ストリーミングで対話を実行する。

**Request**:
```json
{
  "user_id": "user-123",
  "session_id": "session-456",
  "message": "3+5の答え教えて"
}
```

**Response** (text/event-stream):
```
event: text
data: {"text": "こ"}

event: text
data: {"text": "の問題は"}

event: text
data: {"text": "何を聞いているかな？"}

event: done
data: {"session_id": "session-456"}
```

### イベントタイプ

| イベント | 説明 | データ |
|---------|------|--------|
| `text` | テキストチャンク | `{"text": "..."}` |
| `error` | エラー | `{"error": "...", "code": "..."}` |
| `done` | 完了 | `{"session_id": "..."}` |

## Pydanticスキーマ

```python
class RunDialogueRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class TextEvent(BaseModel):
    text: str

class ErrorEvent(BaseModel):
    error: str
    code: str

class DoneEvent(BaseModel):
    session_id: str
```

## 依存性注入

```python
def get_session_service() -> BaseSessionService:
    """FirestoreSessionServiceを取得"""
    return FirestoreSessionService()

def get_memory_service() -> BaseMemoryService:
    """FirestoreMemoryServiceを取得"""
    return FirestoreMemoryService()

def get_agent_runner_service(
    session_service: BaseSessionService = Depends(get_session_service),
    memory_service: BaseMemoryService = Depends(get_memory_service),
) -> AgentRunnerService:
    """AgentRunnerServiceを取得"""
    return AgentRunnerService(
        session_service=session_service,
        memory_service=memory_service,
    )
```

## SSEジェネレータ

```python
async def event_generator(
    runner: AgentRunnerService,
    user_id: str,
    session_id: str,
    message: str,
) -> AsyncIterator[str]:
    """SSEイベントを生成"""
    try:
        async for event in runner.run(user_id, session_id, message):
            text = runner.extract_text(event)
            if text:
                yield f"event: text\ndata: {json.dumps({'text': text})}\n\n"

        yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e), 'code': 'INTERNAL_ERROR'})}\n\n"
```

## ファイル構成

```
backend/app/
├── api/v1/
│   ├── dialogue.py          # 既存（変更なし）
│   └── dialogue_runner.py   # 新規：ストリーミングエンドポイント
├── schemas/
│   └── dialogue_runner.py   # 新規：スキーマ定義
└── services/adk/runner/     # 既存
```

## エラーハンドリング

| エラー | HTTPステータス | エラーコード |
|--------|---------------|-------------|
| セッション未存在 | 404 | SESSION_NOT_FOUND |
| LLM呼び出し失敗 | 503 | LLM_ERROR |
| 認証失敗 | 401 | UNAUTHORIZED |
| バリデーションエラー | 422 | VALIDATION_ERROR |

## セキュリティ考慮事項

1. **入力バリデーション**: Pydanticで厳密に検証
2. **レート制限**: 将来的にRedisで実装
3. **タイムアウト**: ストリーム30秒タイムアウト

## パフォーマンス考慮事項

1. **接続プール**: Firestoreクライアント再利用
2. **ストリーミング**: チャンク単位で送信
3. **非同期処理**: ブロッキングなしの並行処理
