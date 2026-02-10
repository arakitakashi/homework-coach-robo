# Design - Agent Engine統合による内部完結型Router Agent実装（簡素化版）

## 🎉 設計の大幅簡素化

公式ドキュメント調査により、当初の設計が複雑すぎたことが判明しました。

**当初の誤解**: 「Runnerを使わず、AgentEngineWrapperで独自実装」
**正しい理解**: 「Runnerを継続使用し、SessionServiceを切り替えるだけ」

## アーキテクチャ概要

### 現在のアーキテクチャ（Phase 1 + Firestore依存）

```
┌─────────────────────────────────────┐
│  VoiceStreamingService              │
│  ┌───────────────────────────────┐  │
│  │ create_socratic_agent()       │  │  ← Phase 1単一エージェント
│  │ (単一エージェント)             │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Runner(                       │  │
│  │   agent=agent,                │  │
│  │   session_service=            │  │
│  │     FirestoreSessionService  │  │  ← Firestore依存
│  │ )                             │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
          │
          ↓
┌─────────────────────────────────────┐
│  Firestore                          │
│  - sessions                         │
└─────────────────────────────────────┘
```

### 新しいアーキテクチャ（Phase 2 + Agent Engine統合）

```
┌─────────────────────────────────────────┐
│  VoiceStreamingService                  │
│  ┌───────────────────────────────────┐  │
│  │ create_router_agent()             │  │  ← Phase 2 Router Agent
│  │ ├─ Math Coach                     │  │
│  │ ├─ Japanese Coach                 │  │
│  │ ├─ Encouragement                  │  │
│  │ └─ Review                         │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Runner(                           │  │
│  │   agent=agent,                    │  │
│  │   session_service=                │  │
│  │     VertexAiSessionService       │  │  ← Agent Engine提供
│  │ )                                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
          │
          ↓
┌─────────────────────────────────────────┐
│  Vertex AI Agent Engine                 │
│  ┌───────────────────────────────────┐  │
│  │ Session Management (内蔵)         │  │
│  │  - create_session                 │  │
│  │  - list_sessions                  │  │
│  │  - セッション自動管理              │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**変更点は最小限**:
1. `create_socratic_agent()` → `create_router_agent()`
2. `FirestoreSessionService()` → `VertexAiSessionService(...)`

**AgentEngineWrapperは不要**！

## 技術選定

### VertexAiSessionServiceの採用理由

| 項目 | FirestoreSessionService | VertexAiSessionService |
|------|------------------------|----------------------|
| 実装 | 自前実装 | Agent Engine提供 |
| セッション管理 | 手動 | **自動** |
| pickle化 | 困難（外部依存） | **簡単** |
| メンテナンス | 必要 | **不要** |
| コスト | Firestore料金 | Agent Engine込み |

### ADK公式ドキュメントに基づく実装

参照: https://docs.cloud.google.com/agent-builder/agent-engine/sessions/manage-sessions-adk?hl=ja

```python
# セッションサービス初期化
session_service = VertexAiSessionService(
    project_id="PROJECT_ID",
    location="LOCATION",
    agent_engine_id="AGENT_ENGINE_ID"
)

# Runner初期化（変更なし）
runner = adk.Runner(
    agent=root_agent,
    app_name=app_name,
    session_service=session_service  # ← ここだけ変更
)

# セッション作成（自動管理）
session = await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    state={'key': 'value'}
)

# セッション一覧取得
sessions = await session_service.list_sessions(
    app_name=app_name,
    user_id=user_id
)
```

## データ設計

### VoiceStreamingServiceの最小変更

```python
# backend/app/services/voice/streaming_service.py

from google.adk.sessions import VertexAiSessionService
from app.services.adk.agents.router import create_router_agent

class VoiceStreamingService:
    """音声ストリーミングサービス（Agent Engine統合版）"""

    def __init__(
        self,
        use_agent_engine: bool = True,  # 環境変数で制御
        project_id: str | None = None,
        location: str | None = None,
        agent_engine_id: str | None = None,
    ) -> None:
        # Phase 2 Router Agent（Phase 1からの変更）
        self._agent = create_router_agent(model=LIVE_MODEL)

        if use_agent_engine:
            # Agent Engine統合（新規）
            self._session_service = VertexAiSessionService(
                project_id=project_id or os.getenv("PROJECT_ID"),
                location=location or os.getenv("LOCATION"),
                agent_engine_id=agent_engine_id or os.getenv("AGENT_ENGINE_ID"),
            )
        else:
            # 既存のFirestoreベース（後方互換）
            self._session_service = FirestoreSessionService()

        # Runner初期化（既存のまま）
        self._runner = Runner(
            app_name=DEFAULT_APP_NAME,
            agent=self._agent,
            session_service=self._session_service,  # ← ここだけ変更
            memory_service=memory_service,  # ← Memory Bankは後で対応
        )

        self._queue = LiveRequestQueue()
        self._run_config = RunConfig(
            response_modalities=["AUDIO"],
        )

    # 既存のメソッドは変更なし
    def send_audio(self, data: bytes) -> None:
        """音声データをGemini Live APIに送信する"""
        blob = types.Blob(mime_type="audio/pcm", data=data)
        self._queue.send_realtime(blob)

    def send_text(self, text: str) -> None:
        """テキストメッセージをGemini Live APIに送信する"""
        content = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )
        self._queue.send_content(content)

    async def receive_events(
        self,
        user_id: str,
        session_id: str,
    ) -> AsyncIterator[ADKEventMessage]:
        """Gemini Live APIからイベントを受信する（既存のまま）"""
        async for event in self._runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=self._queue,
            run_config=self._run_config,
        ):
            message = self._convert_event_to_message(event)
            if message is not None:
                yield message

    # _convert_event_to_message は既存のまま変更なし
```

## ファイル構成

```
backend/app/services/
├── voice/
│   └── streaming_service.py             # ← 最小限の変更
│
└── adk/
    ├── agents/
    │   ├── router.py                    # 既存（Phase 2b実装済み）
    │   ├── math_coach.py
    │   ├── japanese_coach.py
    │   ├── encouragement.py
    │   └── review.py
    │
    └── runner/
        └── agent.py                     # 既存（create_socratic_agent）

backend/scripts/
└── serialize_agent.py                   # ← 最小限の変更

tests/
├── unit/
│   └── services/
│       └── test_streaming_service_v2.py # ← テスト更新
└── integration/
    └── test_agent_engine_flow.py       # ← E2Eテスト（新規）
```

**AgentEngineWrapper関連のファイルは不要**！

## 依存関係

### 新規依存

**VertexAiSessionService**のみ（ADK標準提供）:
```python
from google.adk.sessions import VertexAiSessionService
```

### 既存依存の変更

- `VoiceStreamingService`:
  - `create_socratic_agent()` → `create_router_agent()`
  - `FirestoreSessionService()` → `VertexAiSessionService(...)`

## エラーハンドリング

### 1. VertexAiSessionService初期化失敗

```python
try:
    session_service = VertexAiSessionService(
        project_id=project_id,
        location=location,
        agent_engine_id=agent_engine_id,
    )
except Exception as e:
    logger.error(f"Failed to initialize VertexAiSessionService: {e}")
    # フォールバック: Firestoreベース
    if fallback_enabled:
        session_service = FirestoreSessionService()
    else:
        raise
```

### 2. セッション作成失敗

```python
try:
    session = await session_service.create_session(...)
except Exception as e:
    logger.error(f"Failed to create session: {e}")
    # リトライまたはエラーレスポンス
    raise
```

## セキュリティ考慮事項

### 1. 環境変数の管理

```python
# 本番環境
PROJECT_ID = os.getenv("PROJECT_ID")  # Secret Manager
LOCATION = os.getenv("LOCATION")  # Secret Manager
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")  # Secret Manager
```

### 2. セッションIDの検証

```python
def validate_session_id(session_id: str) -> bool:
    """セッションIDのバリデーション"""
    # UUIDv4形式
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    return bool(re.match(pattern, session_id))
```

## パフォーマンス考慮事項

### 1. セッションサービスの再利用

```python
# グローバルインスタンスを再利用
_session_service_cache: VertexAiSessionService | None = None

def get_session_service() -> VertexAiSessionService:
    global _session_service_cache
    if _session_service_cache is None:
        _session_service_cache = VertexAiSessionService(...)
    return _session_service_cache
```

## 移行戦略

### Phase 1: 並行稼働

環境変数で切り替え：

```python
USE_AGENT_ENGINE = os.getenv("USE_AGENT_ENGINE", "false").lower() == "true"

if USE_AGENT_ENGINE:
    service = VoiceStreamingService(use_agent_engine=True)
else:
    service = VoiceStreamingService(use_agent_engine=False)  # Firestore
```

### Phase 2: Agent Engine優先

デフォルトをAgent Engineに変更：

```python
USE_AGENT_ENGINE = os.getenv("USE_AGENT_ENGINE", "true").lower() == "true"
```

### Phase 3: Firestore完全廃止（将来）

Firestoreベースのコードを削除。

## Live Audio（run_live）のサポート状況

**重要**: 公式ドキュメントでは`run_live()`についての記載がありません。

### 調査が必要な点

1. **VertexAiSessionServiceは`run_live()`をサポートするか？**
2. **LiveRequestQueueは動作するか？**
3. **音声ストリーミングの代替方法はあるか？**

### 実装方針

1. まず**テキストベース**（`run()`）で実装
2. `run_live()`のサポートを確認
3. 必要に応じて代替実装を検討

## 代替案と採用理由

### 代替案1: AgentEngineWrapper独自実装

**不採用理由**:
- ADK公式がRunnerとVertexAiSessionServiceの統合をサポート
- 独自実装は複雑で、メンテナンスコストが高い
- 公式ドキュメントに準拠すべき

### 採用案: Runner + VertexAiSessionService

**理由**:
- ADK公式ドキュメントに準拠
- 実装がシンプル（最小限の変更）
- メンテナンスコストが低い
- Agent Engineの自動セッション管理を活用
