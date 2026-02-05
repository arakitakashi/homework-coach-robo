# Design - ADK Runner統合

## アーキテクチャ概要

ADK Runnerを使用して、ソクラテス式対話エンジンを統合エージェント環境として実装する。

```
┌─────────────────────────────────────────────────────────────┐
│                       API Layer                              │
│                  (FastAPI Endpoints)                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentRunnerService                        │
│  - Runnerの初期化と管理                                       │
│  - run_async()によるエージェント実行                          │
│  - イベントストリーム処理                                     │
└─────────────────────────────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ SocraticAgent    │ │ SessionService   │ │ MemoryService    │
│ (ADK Agent)      │ │ (Firestore)      │ │ (Firestore)      │
│                  │ │                  │ │                  │
│ - system prompt  │ │ - セッション永続化│ │ - 記憶の保存/検索│
│ - tools          │ │ - 状態管理       │ │                  │
│ - callbacks      │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## 技術選定

| コンポーネント | 選定技術 | 理由 |
|--------------|---------|------|
| Agent Framework | Google ADK | 既存のFirestoreサービスとの親和性 |
| LLM | Gemini 2.5 Flash | コスト効率・日本語対応 |
| 永続化 | Firestore | 既存の実装を再利用 |
| 非同期処理 | asyncio | ADKの非同期APIに準拠 |

## コンポーネント設計

### 1. SocraticDialogueAgent

ADK Agentとしてソクラテス式対話エンジンを定義する。

```python
from google.adk.agents import Agent

def create_socratic_agent() -> Agent:
    """ソクラテス式対話エージェントを作成"""
    return Agent(
        name="socratic_dialogue_agent",
        model="gemini-2.5-flash",
        instruction=SOCRATIC_SYSTEM_PROMPT,
        description="小学校低学年向けのソクラテス式対話コーチ",
        tools=[],  # 将来的にツールを追加
    )
```

**システムプロンプト**:
- 既存の`SocraticDialogueManager.SYSTEM_PROMPT`を拡張
- 3段階ヒントシステムの原則を組み込み
- 答えリクエスト時の対応ルールを明記

### 2. AgentRunnerService

Runnerの初期化とエージェント実行を管理するサービス。

```python
from google.adk import Runner
from google.adk.sessions import BaseSessionService
from google.adk.memory import BaseMemoryService

class AgentRunnerService:
    def __init__(
        self,
        session_service: BaseSessionService,
        memory_service: BaseMemoryService,
        app_name: str = "homework-coach",
    ) -> None:
        self._agent = create_socratic_agent()
        self._runner = Runner(
            app_name=app_name,
            agent=self._agent,
            session_service=session_service,
            memory_service=memory_service,
        )

    async def run(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ) -> AsyncIterator[Event]:
        """エージェントを実行しイベントをストリーム"""
        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )
        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            yield event
```

### 3. 既存コンポーネントの再利用

| 既存コンポーネント | 再利用方法 |
|------------------|-----------|
| `FirestoreSessionService` | Runner初期化時に注入 |
| `FirestoreMemoryService` | Runner初期化時に注入 |
| `SocraticDialogueManager` | システムプロンプトのテンプレートを再利用 |

## ファイル構成

```
backend/app/services/adk/
├── dialogue/                    # 既存
│   ├── manager.py
│   ├── models.py
│   └── ...
├── sessions/                    # 既存
│   └── firestore_session_service.py
├── memory/                      # 既存
│   └── firestore_memory_service.py
└── runner/                      # 新規
    ├── __init__.py
    ├── agent.py                 # SocraticDialogueAgent定義
    └── runner_service.py        # AgentRunnerService
```

## API設計

### 対話実行エンドポイント

```
POST /api/v1/dialogue/run
```

**Request**:
```json
{
  "user_id": "user-123",
  "session_id": "session-456",
  "message": "3+5の答え教えて"
}
```

**Response** (Server-Sent Events):
```
event: agent_response
data: {"text": "この問題は何を聞いているかな？"}

event: done
data: {}
```

## 依存関係

```
AgentRunnerService
├── Runner (ADK)
│   ├── Agent
│   ├── SessionService (Firestore)
│   └── MemoryService (Firestore)
└── types (google.genai)
```

## エラーハンドリング

| エラー種別 | 対応 |
|-----------|------|
| セッション未存在 | 404 Not Found |
| LLM呼び出し失敗 | 503 Service Unavailable + リトライ |
| Firestoreエラー | 500 Internal Server Error |

## セキュリティ考慮事項

1. **user_id/session_idの検証**: 入力値バリデーション
2. **認可**: ユーザーは自分のセッションのみアクセス可能
3. **プロンプトインジェクション対策**: ユーザー入力のサニタイズ

## パフォーマンス考慮事項

1. **ストリーミング**: イベントをリアルタイムで返却
2. **接続プール**: Firestoreクライアントの再利用
3. **タイムアウト**: LLM呼び出しに30秒タイムアウト

## 代替案と採用理由

| 案 | 説明 | 採用/不採用 | 理由 |
|----|------|------------|------|
| InMemoryRunner | テスト用軽量Runner | 不採用（本番） | 永続化が必要 |
| カスタムツール追加 | 計算ツールなど | 将来検討 | MVPではシンプルに |
| マルチエージェント | 役割分担 | 将来検討 | 複雑性回避 |
