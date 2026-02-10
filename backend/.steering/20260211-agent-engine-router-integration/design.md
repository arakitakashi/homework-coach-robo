# Design - Agent Engine統合による内部完結型Router Agent実装

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
│  │   session_service=Firestore, │  │  ← 外部依存
│  │   memory_service=Firestore   │  │  ← 外部依存
│  │ )                             │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
          │
          ↓
┌─────────────────────────────────────┐
│  Firestore                          │
│  - sessions                         │
│  - memories                         │
└─────────────────────────────────────┘
```

**問題点**:
- Firestore依存がpickleファイルに含められない
- Phase 2 Router Agentが使われていない
- ツール実行・エージェント遷移の監視が困難

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
│  │ AgentEngineWrapper                │  │  ← 新規実装
│  │   (Runnerなし)                    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
          │
          ↓
┌─────────────────────────────────────────┐
│  Agent Engine (Managed Service)         │
│  ┌───────────────────────────────────┐  │
│  │ Session Management                │  │  ← 内蔵機能
│  │  - create_session                 │  │
│  │  - get_session                    │  │
│  │  - list_sessions                  │  │
│  │  - delete_session                 │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Memory Bank                       │  │  ← 内蔵機能
│  │  - async_add_session_to_memory    │  │
│  │  - async_search_memory            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**改善点**:
- Firestore依存の完全排除
- Phase 2 Router Agentの統合
- Agent Engine標準機能の活用
- pickleファイルの簡素化

## 技術選定

### Agent EngineラッパーとRunnerの比較

| 項目 | Runner（現在） | AgentEngineWrapper（新） |
|------|---------------|------------------------|
| セッション管理 | 外部サービス必要 | Agent Engine内蔵 |
| pickle化 | 外部依存で困難 | 簡単 |
| Memory Bank | 外部実装必要 | Agent Engine内蔵 |
| デプロイ | 複雑 | シンプル |

### Agent EngineセッションAPI選定

Agent Engineが提供するメソッド（デプロイ済み環境から確認）：

**セッション管理**:
- `create_session(user_id, session_id) -> Session`
- `async_create_session(user_id, session_id) -> Awaitable[Session]`
- `get_session(user_id, session_id) -> Session | None`
- `async_get_session(user_id, session_id) -> Awaitable[Session | None]`
- `list_sessions(user_id) -> list[Session]`
- `async_list_sessions(user_id) -> Awaitable[list[Session]]`
- `delete_session(user_id, session_id) -> None`
- `async_delete_session(user_id, session_id) -> Awaitable[None]`

**Memory Bank**:
- `async_add_session_to_memory(user_id, session_id) -> Awaitable[None]`
- `async_search_memory(user_id, query) -> Awaitable[list[Memory]]`

本実装では**非同期API（async_*）**を優先使用します。

## データ設計

### Agent EngineラッパークラスAPI

```python
# backend/app/services/adk/agent_engine/agent_wrapper.py

from typing import TYPE_CHECKING, AsyncIterator

from google.adk.agents import Agent

if TYPE_CHECKING:
    from google.adk.events import Event

class AgentEngineWrapper:
    """Agent Engine内蔵セッション管理を使用するラッパー

    Firestoreに依存せず、Agent Engineが提供するセッション管理APIを利用。
    ADK RunnerのようなインターフェースでAgent Engineを利用する。
    """

    def __init__(self, agent: Agent, agent_engine_client=None):
        """
        Args:
            agent: ADK Agent（Router Agent）
            agent_engine_client: Agent Engine API クライアント（オプション、テスト用）
        """
        self._agent = agent
        self._client = agent_engine_client  # 後で実装

    async def create_session(self, user_id: str, session_id: str) -> None:
        """Agent Engineでセッションを作成

        Args:
            user_id: ユーザーID
            session_id: セッションID
        """
        # Agent Engine API: async_create_session()
        pass

    async def get_session(self, user_id: str, session_id: str):
        """Agent Engineからセッションを取得

        Args:
            user_id: ユーザーID
            session_id: セッションID

        Returns:
            Session | None: セッション情報
        """
        # Agent Engine API: async_get_session()
        pass

    async def query(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ) -> AsyncIterator["Event"]:
        """Agent Engineを使ったクエリ処理

        Args:
            user_id: ユーザーID
            session_id: セッションID
            message: ユーザーメッセージ

        Yields:
            Event: ADK Event（音声、トランスクリプション、ツール実行等）
        """
        # 1. セッション取得/作成
        session = await self.get_session(user_id, session_id)
        if session is None:
            await self.create_session(user_id, session_id)

        # 2. Agent Engineでクエリ実行
        # （具体的な実装はAgent Engine API仕様に基づく）
        # 3. イベントをyield
        pass

    async def add_to_memory(self, user_id: str, session_id: str) -> None:
        """セッションからMemory Bankに記憶を追加

        Args:
            user_id: ユーザーID
            session_id: セッションID
        """
        # Agent Engine API: async_add_session_to_memory()
        pass

    async def search_memory(self, user_id: str, query: str):
        """Memory Bankから記憶を検索

        Args:
            user_id: ユーザーID
            query: 検索クエリ

        Returns:
            list[Memory]: 検索結果
        """
        # Agent Engine API: async_search_memory()
        pass
```

### VoiceStreamingServiceの更新

```python
# backend/app/services/voice/streaming_service.py

from app.services.adk.agent_engine.agent_wrapper import AgentEngineWrapper
from app.services.adk.agents.router import create_router_agent

class VoiceStreamingService:
    """音声ストリーミングサービス（Agent Engine統合版）"""

    def __init__(
        self,
        use_agent_engine: bool = True,  # 環境変数で制御
    ) -> None:
        # Phase 2 Router Agent
        self._agent = create_router_agent(model=LIVE_MODEL)

        if use_agent_engine:
            # Agent Engine統合
            self._agent_wrapper = AgentEngineWrapper(self._agent)
            self._use_wrapper = True
        else:
            # 既存のFirestoreベース（後方互換）
            self._runner = Runner(
                agent=self._agent,
                session_service=FirestoreSessionService(),
                memory_service=FirestoreMemoryService(),
            )
            self._use_wrapper = False

        self._queue = LiveRequestQueue()

    async def receive_events(
        self,
        user_id: str,
        session_id: str,
    ) -> AsyncIterator[ADKEventMessage]:
        """イベント受信（Agent Engine or Firestore）"""
        if self._use_wrapper:
            # Agent Engine経由
            async for event in self._agent_wrapper.query(
                user_id=user_id,
                session_id=session_id,
                message="",  # LiveRequestQueueから取得
            ):
                message = self._convert_event_to_message(event)
                if message is not None:
                    yield message
        else:
            # 既存のFirestoreベース
            async for event in self._runner.run_live(...):
                message = self._convert_event_to_message(event)
                if message is not None:
                    yield message
```

## ファイル構成

```
backend/app/services/
├── adk/
│   ├── agent_engine/                    # ← 新規ディレクトリ
│   │   ├── __init__.py
│   │   ├── agent_wrapper.py             # ← 新規実装
│   │   └── agent_engine_client.py       # 既存（更新）
│   │
│   ├── agents/
│   │   ├── router.py                    # 既存（Phase 2b実装済み）
│   │   ├── math_coach.py
│   │   ├── japanese_coach.py
│   │   ├── encouragement.py
│   │   └── review.py
│   │
│   └── runner/
│       └── agent.py                     # 既存（create_socratic_agent）
│
└── voice/
    └── streaming_service.py             # ← 更新（Router Agent統合）

backend/scripts/
└── serialize_agent.py                   # ← 更新（Firestore依存排除）

tests/
├── unit/
│   └── services/
│       ├── test_agent_wrapper.py        # ← 新規テスト
│       └── test_streaming_service_v2.py # ← 更新テスト
└── integration/
    └── test_agent_engine_flow.py       # ← 新規E2Eテスト
```

## 依存関係

### 新規依存

なし（既存のADK SDK, Agent Engine APIのみ使用）

### 既存依存の変更

- `VoiceStreamingService`: `create_socratic_agent()` → `create_router_agent()`
- `serialize_agent.py`: Firestore依存排除

## エラーハンドリング

### 1. Agent Engineセッション作成失敗

```python
try:
    await self._agent_wrapper.create_session(user_id, session_id)
except AgentEngineError as e:
    logger.error(f"Failed to create session: {e}")
    # フォールバック: Firestoreベース
    if self._fallback_enabled:
        return await self._create_firestore_session(...)
    raise
```

### 2. Agent Engineクエリ実行失敗

```python
try:
    async for event in self._agent_wrapper.query(...):
        yield event
except AgentEngineError as e:
    logger.error(f"Agent Engine query failed: {e}")
    # ユーザーにエラーを通知
    yield ADKEventMessage(error="一時的に利用できません")
```

### 3. Memory Bank統合失敗

```python
try:
    await self._agent_wrapper.add_to_memory(user_id, session_id)
except MemoryBankError as e:
    logger.warning(f"Memory Bank add failed: {e}")
    # Memory Bankは必須ではないため、警告ログのみ
```

## セキュリティ考慮事項

### 1. セッションID検証

```python
def validate_session_id(session_id: str) -> bool:
    """セッションIDのバリデーション"""
    # UUIDv4形式
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    return bool(re.match(pattern, session_id))
```

### 2. ユーザーID検証

```python
def validate_user_id(user_id: str) -> bool:
    """ユーザーIDのバリデーション"""
    # 英数字とハイフンのみ、最大64文字
    pattern = r"^[a-zA-Z0-9-]{1,64}$"
    return bool(re.match(pattern, user_id))
```

## パフォーマンス考慮事項

### 1. セッション取得のキャッシング

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_session_cached(user_id: str, session_id: str):
    """セッション取得（キャッシュ付き）"""
    return await self._agent_wrapper.get_session(user_id, session_id)
```

### 2. Memory Bank検索の最適化

```python
async def search_memory(
    self,
    user_id: str,
    query: str,
    max_results: int = 5,  # 結果数制限
) -> list[Memory]:
    """Memory Bank検索（結果数制限）"""
    results = await self._agent_wrapper.search_memory(user_id, query)
    return results[:max_results]
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

### Phase 3: Firestore完全廃止

Firestoreベースのコードを削除（将来）。

## 代替案と採用理由

### 代替案1: Firestoreを継続使用

**不採用理由**:
- Agent Engineデプロイ時の複雑性
- セッション管理の二重実装
- Agent Engine標準機能を活用できない

### 代替案2: 独自のセッション管理実装

**不採用理由**:
- Agent Engine標準機能があるのに再実装は無駄
- メンテナンスコストが高い
- スケーラビリティが不明

### 採用案: Agent Engine内蔵セッション管理

**理由**:
- Agent Engine標準機能でサポート保証
- シンプルなアーキテクチャ
- スケーラビリティと信頼性が保証されている
- pickleファイルの簡素化
