# Requirements - WebSocket Phase 2 メッセージハンドラ統合 (Issue #65)

## 背景・目的

Phase 2aでツール実行（ToolExecution）のWebSocketメッセージハンドラを実装済み。
残り2つのPhase 2イベントタイプ（AgentTransition, EmotionUpdate）のハンドラを追加し、
WebSocketメッセージ処理パイプラインを完成させる。

これにより、Phase 2b（エージェント切り替えUI）とPhase 2d（感情適応UI）の
UIコンポーネント開発の基盤が整う。

## 要求事項

### 機能要件

1. **AgentTransition ハンドラ**: WebSocketからエージェント遷移イベントを受信し、Jotai atomsに反映
2. **EmotionUpdate ハンドラ**: WebSocketから感情分析イベントを受信し、Jotai atomsに反映
3. **既存パターンとの一貫性**: ToolExecution ハンドラと同じアーキテクチャパターンに従う

### 非機能要件

- テストカバレッジ80%以上維持
- 型安全性（TypeScript strict mode）
- 既存テスト全パス

### 制約条件

- Phase 2型定義・Jotai atoms は既に実装済み（PR #60）
- UIコンポーネント（AgentDisplay, EmotionDisplay等）は本Issue対象外
- TDD必須

## 対象範囲

### In Scope

- ADKEvent型の拡張（agentTransition, emotionUpdate フィールド追加）
- VoiceWebSocketOptions の拡張（onAgentTransition, onEmotionUpdate コールバック追加）
- VoiceWebSocketClient.processADKEvent の拡張
- useVoiceStream フックの拡張（コールバックパススルー）
- SessionContent の拡張（ハンドラ追加、Jotai atoms更新）
- 全レイヤーのテスト

### Out of Scope

- UIコンポーネント実装（Issue #63, #64）
- バックエンド変更
- E2Eテスト

## 成功基準

- AgentTransition イベントが WebSocket → Jotai atoms に正しく伝播する
- EmotionUpdate イベントが WebSocket → Jotai atoms に正しく伝播する
- 全テストパス、lint/typecheckエラーなし
