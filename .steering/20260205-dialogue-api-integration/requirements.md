# Requirements - 対話API統合

## 背景・目的

ADK RunnerベースのAgentRunnerServiceをFastAPI エンドポイントとして公開し、ストリーミングレスポンスで対話を実行できるようにする。

現在の実装状況:
- `AgentRunnerService`: ADK Runner統合済み（SessionService/MemoryService）
- `dialogue.py`: 既存のエンドポイント（SocraticDialogueManager使用）

これらを統合し、新しいストリーミングエンドポイントを追加する。

## 要求事項

### 機能要件

1. **ストリーミングエンドポイント**
   - `POST /api/v1/dialogue/run` でエージェント実行
   - Server-Sent Events (SSE) でリアルタイムレスポンス
   - イベントごとにテキストを送信

2. **セッション管理**
   - FirestoreSessionServiceを使用した永続化
   - セッション作成・取得・削除

3. **エラーハンドリング**
   - セッション未存在: 404
   - LLMエラー: 503（リトライ可能）
   - 認証エラー: 401

### 非機能要件

1. **テストカバレッジ**: 80%以上
2. **レスポンスタイム**: ストリーム開始まで2秒以内（LLM除く）
3. **並行処理**: 複数リクエストの同時処理

### 制約条件

1. FastAPIのSSE機能を使用
2. 既存のエンドポイントとの互換性維持
3. TDD原則に従った開発

## 対象範囲

### In Scope

- ストリーミングエンドポイント実装
- AgentRunnerServiceの依存性注入
- Pydanticスキーマ定義
- ユニットテスト

### Out of Scope

- WebSocket実装（将来の拡張）
- Redisキャッシュ（別フェーズ）
- 認証・認可（別フェーズ）
- フロントエンド統合

## 成功基準

- [ ] ストリーミングエンドポイントが動作する
- [ ] イベントがリアルタイムで送信される
- [ ] テストカバレッジ80%以上
- [ ] mypy/ruff エラーなし
