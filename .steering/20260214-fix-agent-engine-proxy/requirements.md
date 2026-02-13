# Requirements - Agent Engine プロキシ修正

## 背景・目的

Issue #131 で報告された Agent Engine プロキシの問題を修正する。

### 現在の問題

1. **`register_operations()` メソッドが未定義**
   - `HomeworkCoachAgent` にカスタムメソッド（`create_session`, `stream_query`）を登録する `register_operations()` メソッドが実装されていない
   - その結果、Agent Engine プロキシがこれらのメソッドを公開していない

2. **存在しないメソッドの呼び出し**
   - `AgentEngineClient` が `async_stream_query` / `async_create_session` を呼び出している
   - これらのメソッドは Agent Engine プロキシに存在しない（`AttributeError` が発生）

### 発生している現象

フロントエンドからメッセージ送信時のエラー：
```
'AgentEngine' object has no attribute 'async_stream_query'
```

## 要求仕様

### 機能要件

1. **`HomeworkCoachAgent.register_operations()` の実装**
   - カスタムメソッド `create_session` と `stream_query` を Agent Engine プロキシに登録
   - Agent Engine ドキュメントに従った形式で実装

2. **`AgentEngineClient` のプロキシメソッド呼び出し修正**
   - 正しいメソッド名（`create_session`, `stream_query`）を使用
   - Agent Engine プロキシの仕様に準拠

3. **動作確認**
   - フロントエンドからメッセージ送信時にエラーが発生しないこと
   - Agent Engine 経由でのセッション作成・クエリ送信が正常に動作すること

### 非機能要件

1. **後方互換性**
   - 既存のローカル Runner（`AgentRunnerService`）の動作に影響しないこと
   - フォールバック機構が引き続き正常に動作すること

2. **テストカバレッジ**
   - 修正箇所のユニットテストを追加
   - カバレッジ80%以上を維持

### 制約条件

1. **Agent Engine の仕様に準拠**
   - [Agent Engine カスタムメソッド登録ドキュメント](https://docs.cloud.google.com/agent-builder/agent-engine/develop/custom#registering_custom_methods)に従う

2. **既存のインターフェース維持**
   - `create_session()` / `stream_query()` メソッドのシグネチャは変更しない

## 対象範囲

### In Scope

- `HomeworkCoachAgent.register_operations()` の実装
- `AgentEngineClient` のプロキシメソッド呼び出し修正
- 修正箇所のユニットテスト追加

### Out of Scope

- Agent Engine デプロイスクリプトの変更（既に正常動作確認済み）
- フロントエンドの変更（バックエンドの修正のみで解決）
- CI/CD パイプラインの変更（既存のもので対応可能）

## 成功基準

1. **ユニットテストがすべて通過**
   - `register_operations()` のテスト
   - プロキシメソッド呼び出しのテスト

2. **品質チェックがすべてパス**
   - Ruff lint
   - mypy 型チェック
   - pytest（カバレッジ80%以上）

3. **Agent Engine デプロイ後の動作確認**
   - デプロイスクリプトで Agent Engine を更新
   - フロントエンドからメッセージ送信が成功
   - Cloud Run ログにエラーが出力されない

## 関連 Issue / PR

- Issue #114 (PR #121): `create_session` / `stream_query` メソッド追加
- Issue #131: 本 Issue
