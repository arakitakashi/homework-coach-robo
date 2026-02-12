# Requirements - AgentEngine ラッパーメソッド追加

## 背景・目的

フロントエンドからメッセージ送信時に `'AgentEngine' object has no attribute 'async_stream_query'` エラーが発生する。

`HomeworkCoachAgent` ラッパーに `query()` メソッドしかなく、Agent Engine クライアント (`agent_engine_client.py`) が必要とする `create_session` / `stream_query` メソッドが存在しない。

Agent Engine プロキシ (`agent_engines.get()`) は、デプロイ済みオブジェクトの sync メソッドから `async_*` を自動生成するため、sync 版を定義すれば解決する。

## 要求事項

### 機能要件

- `HomeworkCoachAgent.create_session(*, user_id: str) -> dict` を追加
- `HomeworkCoachAgent.stream_query(*, user_id: str, session_id: str, message: str) -> Generator` を追加
- `AgentEngineClient.extract_text()` が期待する `{"content": {"parts": [{"text": "..."}]}}` 形式を返す

### 非機能要件

- 既存の `query()` メソッドに影響しない
- cloudpickle でシリアライズ可能であること

### 制約条件

- Agent Engine プロキシが `async_*` を自動生成するため sync 版のみ定義

## 対象範囲

### In Scope

- `backend/scripts/serialize_agent.py` の `HomeworkCoachAgent` クラス修正

### Out of Scope

- `agent_engine_client.py` の変更
- デプロイスクリプトの変更

## 成功基準

- lint / type check がパス
- 再デプロイ後 `async_create_session` / `async_stream_query` がエラーなく動作
