# Vertex AI Agent Engine デプロイ・運用ガイド

**Version**: 1.0 | **Last Updated**: 2026-02-14 | **For**: ADK Python SDK v1.0+ / Vertex AI Agent Engine

**前提スキル**: `/google-adk-basics` の知識が必要

---

## Overview

Vertex AI Agent Engine は、ADK エージェントをマネージドサービスとしてデプロイする仕組み。
エージェントは `cloudpickle` でシリアライズされ、Agent Engine ランタイムでデシリアライズされて実行される。

**このスキルは実際の本番デプロイで発生した問題と解決策をもとに構成している。**

---

## アーキテクチャ

### 全体構成

```
[Frontend] → [Cloud Run Backend] → [Agent Engine]
                  │                      │
                  │ AgentEngineClient     │ HomeworkCoachAgent (deserialized)
                  │   .stream_query()     │   .stream_query()
                  │                      │     └→ Runner.run_async()
                  │                      │         └→ genai.Client() → Gemini API
                  │                      │
                  │ SSE (text/event-stream)│
                  ▼                      ▼
            dialogue_runner.py     homework_coach_agent.py
```

### 2層構造の理解（重要）

| レイヤー | 環境 | 役割 |
|---------|------|------|
| **Cloud Run Backend** | Cloud Run コンテナ | SSE エンドポイント提供、Agent Engine プロキシ |
| **Agent Engine Runtime** | Google マネージド環境 | デシリアライズされたエージェントの実行 |

Cloud Run 側の `AgentEngineClient` は `agent_engines.get(resource_name)` でプロキシを取得し、
Agent Engine 側の `HomeworkCoachAgent` のメソッドをリモート呼び出しする。

---

## 🔴 最重要: ランタイム環境の罠

### 1. `vertexai.init()` と `genai.Client()` は別物

**これが最も危険な罠。** `vertexai.init()` は Vertex AI SDK を初期化するが、
ADK Runner が内部で作成する `google.genai.Client()` には設定が伝播しない。

```python
# ❌ これだけでは genai.Client() が Vertex AI モードにならない
vertexai.init()

# ✅ genai.Client() 用の環境変数も明示的に設定する
vertexai.init()

from google.cloud import aiplatform
project = aiplatform.initializer.global_config.project
location = aiplatform.initializer.global_config.location

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
if project:
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project)
if location:
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", location)
```

**エラー例:**
```
{'code': 498, 'message': 'Missing key inputs argument! To use the Google AI API,
provide (api_key) arguments. To use the Google Cloud API, provide
(vertexai, project & location) arguments.'}
```

**原因:** `genai.Client()` は `vertexai.init()` の設定を参照せず、
以下の環境変数を直接読む:
- `GOOGLE_GENAI_USE_VERTEXAI` — `"TRUE"` で Vertex AI モード
- `GOOGLE_CLOUD_PROJECT` — GCP プロジェクト ID
- `GOOGLE_CLOUD_LOCATION` — GCP リージョン

### 2. InMemorySessionService は session_id=None で自動作成しない

**ローカルの VertexAiSessionService とは挙動が異なる。**

```python
# ❌ InMemorySessionService では session_id=None が通らない
async for event in runner.run_async(
    user_id=user_id,
    session_id=None,  # → "Session not found: None" エラー
    new_message=content,
):

# ✅ 明示的にセッションを事前作成する
session = await runner.session_service.create_session(
    app_name="my-agent",
    user_id=user_id,
)
async for event in runner.run_async(
    user_id=user_id,
    session_id=session.id,  # 作成されたセッション ID を使用
    new_message=content,
):
```

**エラー例:**
```
Session not found: None
```

### 3. 既存イベントループ内での非同期実行

Agent Engine サーバー環境では既にイベントループが動作しているため、
`asyncio.run()` を直接呼ぶと `RuntimeError` が発生する。

```python
# ✅ 既存イベントループを検出して別スレッドで実行
def _run_coroutine_sync(coro: Coroutine[Any, Any, T]) -> T:
    try:
        loop = asyncio.get_running_loop()
        # 既存イベントループが存在 → 別スレッドで実行
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # イベントループなし → 直接実行
        return asyncio.run(coro)
```

### 4. VertexAiSessionService は Agent Engine 内で使用不可

Agent Engine 内部で `VertexAiSessionService` を使うと、
`session_events.list()` API が `INVALID_ARGUMENT` を返す。
**必ず `InMemorySessionService` を使用すること。**

---

## Agent Engine ラッパークラスのパターン

### 基本構造

```python
class MyAgent:
    """Agent Engine デプロイ用ラッパー"""

    def __init__(self, agent: Agent) -> None:
        self._agent = agent
        self._runner: Runner | None = None  # Lazy initialization

    def register_operations(self) -> dict[str, list[str]]:
        """Agent Engine プロキシに公開するメソッドを登録"""
        return {
            "": ["query", "create_session"],       # 同期メソッド
            "stream": ["stream_query"],             # ストリーミングメソッド
        }

    def _get_runner(self) -> Runner:
        """Runner を遅延初期化する（デシリアライズ後に初めて呼ばれる）"""
        if self._runner is None:
            ae_services = _create_agent_engine_services()
            if ae_services is not None:
                session_service, memory_service = ae_services
            else:
                # ローカル開発フォールバック
                session_service = create_session_service()
                memory_service = create_memory_service()

            self._runner = Runner(
                app_name="my-agent",
                agent=self._agent,
                session_service=session_service,
                memory_service=memory_service,
            )
        return self._runner
```

### Agent Engine ランタイム検出パターン

```python
def _create_agent_engine_services():
    """Agent Engine ランタイムを検出し、適切なサービスを初期化"""
    agent_engine_id = os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID", "").strip()
    if not agent_engine_id:
        return None  # ローカル環境

    # 1. Vertex AI SDK 初期化
    vertexai.init()

    # 2. genai クライアント用の環境変数設定（★最重要★）
    from google.cloud import aiplatform
    project = aiplatform.initializer.global_config.project
    location = aiplatform.initializer.global_config.location
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
    if project:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project)
    if location:
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", location)

    # 3. InMemory サービスを使用（VertexAiSessionService は不可）
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    return session_service, memory_service
```

### stream_query のパターン（セッション事前作成）

```python
def stream_query(self, *, user_id, session_id, message):
    runner = self._get_runner()
    content = types.Content(role="user", parts=[types.Part(text=message)])

    async def collect_events():
        events = []
        # ★ セッションを事前作成（InMemorySessionService 必須）
        session = await runner.session_service.create_session(
            app_name="my-agent",
            user_id=user_id,
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,  # 事前作成した ID を使用
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        events.append({
                            "content": {"parts": [{"text": part.text}]}
                        })
        return events

    yield from _run_coroutine_sync(collect_events())
```

---

## Cloud Run プロキシ（AgentEngineClient）

### プロキシ取得

```python
from vertexai import agent_engines

class AgentEngineClient:
    def __init__(self, resource_name: str) -> None:
        # agent_engines.get() は同期メソッドを自動的にラップする
        # create_session → async_create_session を自動生成
        # stream_query → async_stream_query を自動生成
        self._remote_app = agent_engines.get(resource_name)

    async def stream_query(self, user_id, session_id, message):
        # 同期ジェネレータを async イテレータとして yield
        for event in self._remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            yield event
```

### SSE エンドポイントでのルーティング

```python
# AGENT_ENGINE_RESOURCE_NAME が設定されていれば Agent Engine 経由
# 未設定ならローカル Runner にフォールバック
engine_client = get_agent_engine_client()  # None or AgentEngineClient

if engine_client is not None:
    return StreamingResponse(
        agent_engine_event_generator(engine_client, ...),
        media_type="text/event-stream",
    )
else:
    return StreamingResponse(
        local_event_generator(runner, ...),
        media_type="text/event-stream",
    )
```

---

## デプロイ

### シリアライズ & GCS アップロード

```python
# serialize_agent.py
import cloudpickle
from my_agent import MyAgent
from my_agents import create_router_agent

agent = create_router_agent()
wrapper = MyAgent(agent)

with open("agent.pkl", "wb") as f:
    cloudpickle.dump(wrapper, f)
```

### Agent Engine 更新

```python
# deploy_agent_engine.py
import vertexai
from vertexai import agent_engines

vertexai.init(project=project, location=location)

# 既存エンジンを更新
agent_engine = agent_engines.get(resource_name)
agent_engine.update(
    agent_engine=resource_name,
    requirements="requirements.txt のパス",
    extra_packages=["agent.pkl のパス"],
)
```

### CI/CD パイプライン

```yaml
# cd.yml - Agent Engine デプロイジョブ
deploy-agent-engine:
  steps:
    - serialize: cloudpickle でエージェントをシリアライズ
    - upload: GCS にアーティファクトをアップロード
    - update: deploy_agent_engine.py で Agent Engine を更新
```

---

## テスト戦略

### 🔴 CI 環境での注意点

CI 環境には GCP 認証情報がないため、以下をすべてモックすること:

```python
# ✅ 正しいテスト: vertexai + aiplatform.global_config の両方をモック
@patch.dict("os.environ", {"GOOGLE_CLOUD_AGENT_ENGINE_ID": "test-123"})
@patch("google.cloud.aiplatform.initializer.global_config")  # ★ これが必須
@patch("my_module.vertexai")
@patch("my_module.InMemoryMemoryService")
@patch("my_module.InMemorySessionService")
@patch("my_module.Runner")
def test_agent_engine_services(
    self, mock_runner, mock_session_cls, mock_memory_cls,
    mock_vertexai, mock_global_config,
):
    # aiplatform.global_config のモック
    mock_global_config.project = "test-project"
    mock_global_config.location = "us-central1"
    # ... テストロジック

# ❌ CI で失敗する: aiplatform.global_config をモックしていない
# → google.auth.exceptions.DefaultCredentialsError
```

### stream_query テスト用ヘルパー

```python
def _make_stream_runner_mock(mock_runner_cls, run_async_fn):
    """セッション事前作成をモックする共通ヘルパー"""
    mock_session = MagicMock()
    mock_session.id = "auto-created-session"

    mock_runner_instance = MagicMock()
    mock_runner_instance.run_async = run_async_fn
    mock_runner_instance.session_service.create_session = AsyncMock(
        return_value=mock_session,
    )
    mock_runner_cls.return_value = mock_runner_instance
    return mock_runner_instance
```

### イベントループ内テスト

```python
def test_works_inside_running_event_loop(self):
    """Agent Engine サーバー環境を模倣"""
    async def run_in_loop():
        return wrapper.create_session(user_id="test-user")

    result = asyncio.run(run_in_loop())
    assert result == {"id": "expected-session-id"}
```

---

## デバッグ手法

### 1. Cloud Run ログで切り分け

```bash
# Cloud Run 側のログ確認
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=homework-coach-backend" --limit=50

# Agent Engine 側は Cloud Run ログの中に表示される
# （Agent Engine のレスポンスが Cloud Run に返される）
```

### 2. curl で SSE エンドポイント直接テスト

```bash
curl -s -N -X POST "https://<backend-url>/api/v1/dialogue/run" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","session_id":"test","message":"1+1は？"}' \
  --max-time 60
```

**期待する正常レスポンス:**
```
event: text
data: {"text":"応答テキスト"}

event: done
data: {"session_id":"test"}
```

**よくあるエラーパターン:**

| レスポンス | 原因 | 対策 |
|-----------|------|------|
| `event: done` のみ（text なし） | Agent Engine 内でエラー | Cloud Run ログで詳細確認 |
| `Missing key inputs argument` | genai 環境変数未設定 | `GOOGLE_GENAI_USE_VERTEXAI` 等を設定 |
| `Session not found: None` | セッション未作成 | `create_session()` を事前呼び出し |
| `INVALID_ARGUMENT` | VertexAiSessionService 使用 | InMemorySessionService に変更 |

### 3. Agent Engine デプロイ確認

```bash
# CD のジョブを確認
gh run view <run-id> --log

# Agent Engine の状態確認
# "Upload artifacts to GCS" と "Update Agent Engine" が成功しているか
```

---

## チェックリスト

### Agent Engine デプロイ前

- [ ] `GOOGLE_CLOUD_AGENT_ENGINE_ID` 検出ロジックがある
- [ ] `vertexai.init()` を呼んでいる
- [ ] `GOOGLE_GENAI_USE_VERTEXAI=TRUE` 環境変数を設定している
- [ ] `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` を設定している
- [ ] `InMemorySessionService` を使用している（VertexAi ではない）
- [ ] セッションを事前作成してから `run_async()` に渡している
- [ ] `_run_coroutine_sync()` で既存イベントループに対応している
- [ ] `register_operations()` でメソッドを登録している
- [ ] テストで `aiplatform.initializer.global_config` をモックしている

### トラブルシューティング

- [ ] Cloud Run ログでエラー内容を確認した
- [ ] curl で SSE エンドポイントを直接テストした
- [ ] CD の Agent Engine 更新ジョブが成功しているか確認した
- [ ] Agent Engine に最新のコードがデプロイされているか確認した

---

## 反省・教訓

### 1. ローカルとランタイムの差異を早期に検証する

ローカルで動くコードが Agent Engine ランタイムで動くとは限らない。
特に以下は環境依存:
- 認証情報の取得方法
- セッションサービスの挙動
- イベントループの有無
- 環境変数の自動設定

### 2. SDK の内部実装を理解する

`vertexai.init()` と `genai.Client()` が別の設定系統であることは、
ドキュメントからは読み取りにくい。SDK のソースコードを追って理解することが重要。

### 3. CI と本番の両方で動くテストを書く

GCP 認証情報に依存するコードは、CI 環境では必ず失敗する。
`aiplatform.initializer.global_config` のような深い依存もモックが必要。
**テストはローカルだけでなく、CI でも実行して確認すること。**

### 4. エラーメッセージを表面に出す仕組みを作る

Agent Engine 内部のエラーは SSE では `event: done` のみ返され、
テキストイベントが空になるだけで分かりにくい。
Cloud Run ログを確認する習慣を持つこと。

### 5. 段階的にデバッグする

複数の問題が重なっている場合（セッション + 認証 + 環境変数）、
一度にすべて直そうとせず、1つずつ修正してデプロイ・確認を繰り返す。
