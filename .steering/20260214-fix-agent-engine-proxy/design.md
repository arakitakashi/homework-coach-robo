# Design - Agent Engine プロキシ修正

## アーキテクチャ概要

Agent Engine は、デプロイされたエージェントのメソッドをリモートプロキシとして公開します。
カスタムメソッドを公開するには、`register_operations()` メソッドで明示的に登録する必要があります。

### 現在の構成

```
AgentEngineClient (クライアント)
  ↓ プロキシ呼び出し
AgentEngine (プロキシ) ← ここに register_operations() で登録
  ↓ デプロイ済み
HomeworkCoachAgent (エージェント本体)
```

## 技術選定

### Agent Engine のメソッド登録形式

[Agent Engine ドキュメント](https://docs.cloud.google.com/agent-builder/agent-engine/develop/custom#registering_custom_methods)に従い、以下の形式で実装：

```python
def register_operations(self):
    return {
        "": ["query", "create_session"],  # 同期メソッド
        "stream": ["stream_query"],  # ストリーミングメソッド
    }
```

**注意点:**
- `query` はデフォルトで登録されるが、明示的に含める
- `create_session` は同期メソッドとして登録（`""`キー）
- `stream_query` はストリーミングメソッドとして登録（`"stream"`キー）

### プロキシメソッド名

Agent Engine プロキシは、登録されたメソッドを**そのままの名前**で公開します。
- ❌ `async_stream_query` （存在しない）
- ✅ `stream_query` （正しい）

Agent Engine は自動的に非同期対応するため、`async_` プレフィックスは不要です。

## データ設計

変更なし（既存のメソッドシグネチャを維持）。

## 実装設計

### 1. `HomeworkCoachAgent.register_operations()` の追加

**対象ファイル:** `backend/app/services/adk/runner/homework_coach_agent.py`

```python
def register_operations(self):
    """Agent Engine プロキシに公開するメソッドを登録.

    Returns:
        dict[str, list[str]]: メソッド登録情報
            - "": 同期メソッドのリスト
            - "stream": ストリーミングメソッドのリスト
    """
    return {
        "": ["query", "create_session"],
        "stream": ["stream_query"],
    }
```

### 2. `AgentEngineClient` のプロキシメソッド呼び出し修正

**対象ファイル:** `backend/app/services/adk/runner/agent_engine_client.py`

#### 修正箇所1: `create_session()` メソッド（47行目）

```python
# ❌ 修正前
session: dict[str, Any] = await self._remote_app.async_create_session(  # type: ignore[attr-defined]
    user_id=user_id,
)

# ✅ 修正後
session: dict[str, Any] = await self._remote_app.create_session(
    user_id=user_id,
)
```

#### 修正箇所2: `stream_query()` メソッド（70行目）

```python
# ❌ 修正前
async for event in self._remote_app.async_stream_query(  # type: ignore[attr-defined]
    user_id=user_id,
    session_id=session_id,
    message=message,
):

# ✅ 修正後
async for event in self._remote_app.stream_query(
    user_id=user_id,
    session_id=session_id,
    message=message,
):
```

**重要:**
- `# type: ignore[attr-defined]` は削除可能（正しいメソッド名になるため）
- ただし、Agent Engine プロキシは動的なオブジェクトなので、型チェックを抑制する必要がある場合は残す

## ファイル構成

```
backend/app/services/adk/runner/
├── homework_coach_agent.py    # 修正: register_operations() 追加
├── agent_engine_client.py     # 修正: プロキシメソッド呼び出し修正
└── ...
```

## 依存関係

- Agent Engine SDK（既にインストール済み）
- 既存の `create_session` / `stream_query` メソッド実装（PR #121で追加済み）

## エラーハンドリング

既存のエラーハンドリングを維持：
- `AgentEngineClient.stream_query()` は既存のエラーハンドリングをそのまま使用
- `register_operations()` は登録情報を返すのみ（エラーなし）

## セキュリティ考慮事項

変更なし（既存のセキュリティ対策を維持）。

## パフォーマンス考慮事項

変更なし（メソッド名の修正のみ）。

## テスト戦略

### 1. `register_operations()` のユニットテスト

**テストファイル:** `backend/tests/unit/services/adk/runner/test_homework_coach_agent.py`

```python
def test_register_operations_returns_correct_format():
    """register_operations が正しい形式を返すこと"""
    agent = HomeworkCoachAgent(...)
    operations = agent.register_operations()

    assert "" in operations
    assert "stream" in operations
    assert "query" in operations[""]
    assert "create_session" in operations[""]
    assert "stream_query" in operations["stream"]
```

### 2. `AgentEngineClient` のモックテスト

**テストファイル:** `backend/tests/unit/services/adk/runner/test_agent_engine_client.py`

```python
@pytest.mark.asyncio
async def test_create_session_calls_correct_proxy_method(mocker):
    """create_session が正しいプロキシメソッドを呼び出すこと"""
    mock_remote_app = mocker.MagicMock()
    mock_remote_app.create_session = AsyncMock(return_value={"session_id": "test"})

    client = AgentEngineClient(...)
    client._remote_app = mock_remote_app

    session = await client.create_session(user_id="user1")

    mock_remote_app.create_session.assert_called_once_with(user_id="user1")

@pytest.mark.asyncio
async def test_stream_query_calls_correct_proxy_method(mocker):
    """stream_query が正しいプロキシメソッドを呼び出すこと"""
    mock_remote_app = mocker.MagicMock()
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = iter([{"event": "test"}])
    mock_remote_app.stream_query = AsyncMock(return_value=mock_stream)

    client = AgentEngineClient(...)
    client._remote_app = mock_remote_app

    events = []
    async for event in client.stream_query(user_id="user1", session_id="sess1", message="test"):
        events.append(event)

    mock_remote_app.stream_query.assert_called_once()
```

## デプロイ方法

1. **コード修正後、Agent Engine に再デプロイ**
   ```bash
   cd backend
   uv run python scripts/deploy_agent_engine.py
   ```

2. **CD パイプラインでの自動デプロイ**
   - PR マージ後、`main` ブランチへのプッシュで自動的に Agent Engine が更新される
   - `.github/workflows/cd.yml` の `deploy-agent-engine` ジョブが実行

## 代替案と採用理由

### 代替案1: `async_` プレフィックスを使用

- Agent Engine が `async_create_session` を公開するよう、カスタム設定する
- **不採用理由:** Agent Engine のドキュメントに記載がなく、標準的な方法ではない

### 代替案2: ローカル Runner のみ使用（Agent Engine を使用しない）

- Agent Engine を完全に無効化し、ローカル Runner のみで動作させる
- **不採用理由:** Phase 3 の目的（Agent Engine デプロイ基盤構築）に反する

### 採用案: 標準的な `register_operations()` 実装

- **採用理由:**
  - Agent Engine ドキュメントに準拠した標準的な方法
  - メソッド名も標準的（`async_` プレフィックスなし）
  - 既存のコードへの影響が最小限
