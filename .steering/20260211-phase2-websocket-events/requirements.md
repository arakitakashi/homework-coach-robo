# Requirements - Phase 2 WebSocket Events Implementation

## 背景・目的

Phase 2のフロントエンド実装（PR #74, #77, #81, #84）により、以下のWebSocketイベント受信ハンドラが実装済み：
- `toolExecution` - ADK Function Toolsの実行状態
- `agentTransition` - マルチエージェント間の遷移
- `emotionUpdate` - 感情適応の状態更新

しかし、Backendがこれらのイベントを送信していないため、Phase 2機能が動作しない状態です。
本実装により、Backend→Frontend間のPhase 2イベント送信を完成させ、フルスタックでPhase 2機能を動作可能にします。

## 要求事項

### 機能要件

#### FR1: WebSocketイベント型定義の追加

`backend/app/schemas/voice_stream.py`に以下の型を追加：

1. **ToolExecutionEvent**
   - `event`: "toolExecution"
   - `data`: ToolExecutionData
     - `toolName`: str
     - `status`: "started" | "completed" | "failed"
     - `input`: dict (optional)
     - `output`: dict (optional)
     - `error`: str (optional)

2. **AgentTransitionEvent**
   - `event`: "agentTransition"
   - `data`: AgentTransitionData
     - `fromAgent`: str | None
     - `toAgent`: str
     - `reason`: str (optional)

3. **EmotionUpdateEvent**
   - `event`: "emotionUpdate"
   - `data`: EmotionUpdateData
     - `emotionType`: "frustration" | "confidence" | "fatigue" | "joy"
     - `level`: int (1-5)
     - `detectedFrom`: "voice_tone" | "text_analysis" | "interaction_pattern"

#### FR2: streaming_service.pyでのイベント送信

`backend/app/services/streaming_service.py`に以下のロジックを実装：

1. **ADK Runner実行時のtoolExecutionイベント送信**
   - ツール実行開始時: `status="started"`
   - ツール実行完了時: `status="completed"` + `output`
   - ツール実行失敗時: `status="failed"` + `error`

2. **Router Agent遷移時のagentTransitionイベント送信**
   - サブエージェント呼び出し前: `fromAgent="router"`, `toAgent="math_coach"` など
   - サブエージェント完了後: `fromAgent="math_coach"`, `toAgent="router"` など

3. **感情分析時のemotionUpdateイベント送信**
   - `update_emotion_tool`実行時
   - 音声トーン分析結果に基づく自動更新時

### 非機能要件

#### NFR1: 後方互換性の維持

- 既存のWebSocketイベント（`dialogue`, `progressUpdate`等）に影響を与えない
- 既存のクライアントがPhase 2イベントを受信しなくてもエラーにならない

#### NFR2: パフォーマンス

- イベント送信のオーバーヘッドを最小化（1イベント < 10ms）
- 大量のツール実行でもWebSocket接続を圧迫しない

#### NFR3: エラーハンドリング

- イベント送信失敗時もメインの対話フローを継続
- イベントシリアライズエラーをログに記録

### 制約条件

1. **ADK統合の変更を最小限に**
   - `AgentRunnerService`の既存ロジックを破壊しない
   - Router AgentのAutoFlow委譲に影響を与えない

2. **Pydantic v2準拠**
   - すべてのスキーマはPydantic v2で定義

3. **型安全性**
   - mypy, ruffのチェックをすべてパス

## 対象範囲

### In Scope

- `backend/app/schemas/voice_stream.py`への型追加
- `backend/app/services/streaming_service.py`へのイベント送信ロジック追加
- 既存のWebSocketハンドラへの統合
- ユニットテストの追加

### Out of Scope

- フロントエンドの変更（すでに実装済み）
- Agent Engineへの変更（既存のAgent Engine経由でイベントを取得）
- Memory Bank統合（別issue）
- 音声感情認識AIの高度化（Phase 2d完了、AutoMLは#52で将来検討）

## 成功基準

1. **機能的成功**
   - [ ] Backend起動時、3種類のPhase 2イベント型が定義されている
   - [ ] ツール実行時、`toolExecution`イベントがWebSocket経由で送信される
   - [ ] エージェント遷移時、`agentTransition`イベントがWebSocket経由で送信される
   - [ ] 感情更新時、`emotionUpdate`イベントがWebSocket経由で送信される

2. **品質的成功**
   - [ ] 全ユニットテストが通過（pytest）
   - [ ] mypy型チェックがパス
   - [ ] ruff lintがパス
   - [ ] テストカバレッジ80%以上

3. **統合的成功**
   - [ ] 既存のWebSocketイベント（dialogue, progressUpdate）が正常動作
   - [ ] フロントエンドのPhase 2 UIコンポーネントが動作開始
   - [ ] CI/CDパイプラインがすべてパス
