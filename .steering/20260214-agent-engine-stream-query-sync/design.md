# Design - Agent Engine stream_query 同期ジェネレータ対応

## アーキテクチャ概要

Agent Engine SDK のプロキシは、登録された操作（`register_operations`）に対して**同期メソッド**を生成する。

```python
# Agent Engine プロキシの仕様
self._remote_app.stream_query(...)  # → 同期ジェネレータ（Generator）を返す
self._remote_app.create_session(...)  # → 同期関数（Session）を返す
```

一方、`AgentEngineClient` は非同期インターフェースを提供する必要があるため、以下の変換を行う：

1. **同期ジェネレータ → 非同期ジェネレータ**:
   - `for` で同期ジェネレータを反復
   - `yield` で非同期ジェネレータとして値を返す

2. **同期関数 → 非同期関数**:
   - `await` を使わず直接呼び出し
   - 結果を返す

## 技術選定

- **修正対象**: `backend/app/services/adk/runner/agent_engine_client.py`
- **修正方法**: `async for` → `for` に変更

## データ設計

変更なし。

## API設計

### `AgentEngineClient.stream_query`

**修正前**:
```python
async def stream_query(
    self, session_id: str, query: str
) -> AsyncGenerator[str, None]:
    try:
        async for event in self._remote_app.stream_query(  # ← エラー
            session_id=session_id, query=query
        ):
            yield event
    except Exception as e:
        ...
```

**修正後**:
```python
async def stream_query(
    self, session_id: str, query: str
) -> AsyncGenerator[str, None]:
    try:
        for event in self._remote_app.stream_query(  # ← 修正
            session_id=session_id, query=query
        ):
            yield event
    except Exception as e:
        ...
```

### `AgentEngineClient.create_session`

**修正前**:
```python
async def create_session(
    self, problem: str, child_grade: int  # noqa: ARG002
) -> str:
    try:
        session = await self._remote_app.create_session(problem=problem)  # ← 確認が必要
        return session.session_id
    except Exception as e:
        ...
```

**修正後（同期メソッドの場合）**:
```python
async def create_session(
    self, problem: str, child_grade: int  # noqa: ARG002
) -> str:
    try:
        session = self._remote_app.create_session(problem=problem)  # ← await 削除
        return session.session_id
    except Exception as e:
        ...
```

## ファイル構成

変更なし。以下のファイルのみ修正：
- `backend/app/services/adk/runner/agent_engine_client.py`

## 依存関係

変更なし。

## エラーハンドリング

既存のエラーハンドリング（try-except）を維持。

## セキュリティ考慮事項

変更なし。

## パフォーマンス考慮事項

同期ジェネレータを非同期ジェネレータに変換するオーバーヘッドは無視できる程度。

## 代替案と採用理由

### 代替案1: Agent Engine SDK を非同期版に変更

- **理由で不採用**: Agent Engine SDK の仕様を変更することはできない

### 代替案2: `asyncio.to_thread` で同期ジェネレータをラップ

```python
async def stream_query(...):
    gen = self._remote_app.stream_query(...)
    loop = asyncio.get_event_loop()
    while True:
        try:
            event = await loop.run_in_executor(None, next, gen)
            yield event
        except StopIteration:
            break
```

- **理由で不採用**: 複雑すぎる。同期ジェネレータを `for` で反復する方がシンプル。

### 採用案: `async for` → `for` に変更

- **理由**: シンプルで Agent Engine SDK の仕様に従う
- **制限**: 非同期ジェネレータ内で `for` を使うため、ブロッキングの可能性があるが、イベントループには影響しない（`yield` で制御を返すため）
