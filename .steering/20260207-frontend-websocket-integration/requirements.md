# Requirements - Frontend WebSocket Integration

## 背景・目的

フロントエンドのWebSocket基盤（`VoiceWebSocketClient`, `useVoiceStream`, AudioWorkletプロセッサ）は実装済みだが、`SessionContent`コンポーネントに統合されていない。テキスト入力（SSE経由）のみが動作し、音声入力パイプラインは未接続。

`useVoiceStream`のコールバックを`SessionContent`に接続し、PCM音声再生・トランスクリプション・キャラクター状態遷移を完成させる。

## 要求事項

### 機能要件

1. **usePcmPlayer**: AudioWorkletベースのPCMストリーミング再生フック
2. **audioLevel**: useVoiceStreamにRMS計算による音量レベルを追加
3. **SessionContent統合**: WebSocketコールバック、PCM再生、トランスクリプション表示、キャラクター状態遷移

### 非機能要件

- テストカバレッジ80%以上を維持
- TDD（Red-Green-Refactor）で実装
- Biome lint / TypeScript typecheck パス

### 制約条件

- バックエンドWebSocketエンドポイントは未実装のため、E2E動作確認は不可
- 既存の`useAudioPlayer`は`decodeAudioData()`使用で生PCM非対応

## 対象範囲

### In Scope

- usePcmPlayerフック新規作成
- useVoiceStreamへのaudioLevel追加
- SessionContentへのWebSocket統合

### Out of Scope

- バックエンドWebSocketエンドポイント実装
- E2Eテスト
- 音声入力の有効化フラグ変更

## 成功基準

- `bun test` 全テストパス
- `bun lint` エラーなし
- `bun typecheck` エラーなし
