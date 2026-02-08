# Requirements - Phase 2a ツール実行状態UIコンポーネント

## 背景・目的

Issue #62: バックエンドのADK Function Tools実行状態をリアルタイムで表示するUIコンポーネントを実装する。

## 要求事項

### 機能要件
- ToolExecutionMessage WebSocketメッセージのハンドリング
- ツール実行中のローディング表示（pending → running → completed/error）
- activeToolExecutionsAtom / isToolRunningAtom を使った状態管理連携
- キャラクター状態との連動（thinking状態の表示）

### 非機能要件
- 小学校低学年向けのやさしい日本語表示
- アクセシビリティ対応（role="status", aria-live）
- TDD（テスト先行）

## 対象範囲

### In Scope
- ToolExecutionDisplay コンポーネント
- VoiceWebSocketClient / useVoiceStream のツール実行イベント拡張
- SessionContent への統合

### Out of Scope
- バックエンド側のツール実行イベント送信実装
- ツール結果の詳細表示UI

## 成功基準
- 全テスト通過
- lint / typecheck 通過
- ツール実行状態がリアルタイムで表示される
