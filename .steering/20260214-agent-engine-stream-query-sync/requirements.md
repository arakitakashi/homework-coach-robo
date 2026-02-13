# Requirements - Agent Engine stream_query 同期ジェネレータ対応

## 背景・目的

PR #132 で Agent Engine プロキシの `async_stream_query` を `stream_query` にリネームしたが、Agent Engine SDK が生成するプロキシメソッドは**同期ジェネレータ**を返す仕様である。

現在 `AgentEngineClient.stream_query()` では `async for` で反復しようとしているため、以下のエラーが発生する：

```
'async for' requires an object with __aiter__ method, got generator
```

この問題を修正し、Agent Engine プロキシの同期ジェネレータを正しく処理できるようにする。

## 要求事項

### 機能要件

1. **`stream_query` の修正**:
   - `async for` を `for` に変更し、同期ジェネレータを正しく反復
   - 非同期ジェネレータとして動作を維持（`yield` で値を返す）

2. **`create_session` の確認**:
   - Agent Engine プロキシの `create_session` が同期メソッドか非同期メソッドかを確認
   - 同期メソッドの場合、`await` を削除

### 非機能要件

- 既存のフォールバック動作を維持
- テストが通ること
- 型ヒントが正確であること

### 制約条件

- Agent Engine SDK のプロキシ仕様に従う（同期メソッドを返す）
- `AgentEngineClient` は非同期ジェネレータとしてのインターフェースを維持

## 対象範囲

### In Scope

- `backend/app/services/adk/runner/agent_engine_client.py` の `stream_query` メソッド修正
- `backend/app/services/adk/runner/agent_engine_client.py` の `create_session` メソッド確認
- 型ヒントの修正（必要に応じて）

### Out of Scope

- Agent Engine SDK の仕様変更
- その他のエージェントアーキテクチャの変更

## 成功基準

- [ ] フロントエンドでメッセージ送信時にエラーダイアログが表示されない
- [ ] ストリーミングレスポンスが正常に返される
- [ ] バックエンドのテストが全て通る
- [ ] mypy 型チェックが通る
