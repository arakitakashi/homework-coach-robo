# Requirements - Voice Input Implementation

## 背景・目的

宿題コーチロボットのターゲットユーザーは小学校低学年（1〜3年生）であり、キーボード操作が苦手なため、音声のみで完結するハンズフリー操作が重要。

現在、テキスト入力によるSSE対話は実装済みだが、音声入力はまだ実装されていない。リファレンス実装（`ref/adk-streaming-guide-main/workshops/`）を参考に、WebSocket + AudioWorklet による双方向音声ストリーミングを実装する。

## 要求事項

### 機能要件

1. **音声録音**: AudioWorkletを使用して16kHz PCMオーディオをキャプチャ
2. **リアルタイム送信**: 録音した音声データをWebSocket経由でサーバーに送信
3. **音声再生**: サーバーからの音声レスポンスをAudioWorkletで再生
4. **UIインタラクション**: 録音開始/停止ボタンで制御
5. **状態表示**: 録音中、送信中、再生中の状態を視覚的に表示

### 非機能要件

1. **レイテンシ**: 音声入力から応答開始まで5秒以内（Gemini Live APIの制約）
2. **ブラウザ互換性**: Chrome、Edge、Safari（AudioWorklet対応ブラウザ）
3. **エラーハンドリング**: マイク権限拒否、接続エラーの適切な処理
4. **TDD原則**: テスト駆動開発を遵守

### 制約条件

1. リファレンス実装（`ref/adk-streaming-guide-main/workshops/`）のパターンを参考にする
2. 既存のコンポーネント（`VoiceInterface`、`useVoiceRecorder`）を活用・拡張
3. バックエンドのWebSocketエンドポイントは別途実装が必要（この実装ではフロントエンドのみ）

## 対象範囲

### In Scope

- WebSocketクライアント（音声用）の実装
- AudioWorklet Processor（PCM録音・再生）の実装
- useVoiceRecorderフックの拡張
- VoiceInterfaceコンポーネントの拡張
- ユニットテスト・統合テスト

### Out of Scope

- バックエンドのWebSocketエンドポイント実装
- 音声感情認識
- 音声テキスト表示（トランスクリプション）

## 成功基準

1. 録音ボタンで音声録音が開始/停止できる
2. 録音した音声データがWebSocket経由で送信される
3. サーバーからの音声レスポンスが再生される
4. テストカバレッジ80%以上
5. lint/typecheck/testがすべてパス
