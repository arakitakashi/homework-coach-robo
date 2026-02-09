# Requirements - Phase 2d 感情適応UIコンポーネント

## 背景・目的

Phase 2dのバックエンドで実装された感情適応機能（`update_emotion_tool`、感情ベースルーティング）に対応するフロントエンドUIを実装する。子供の感情状態（フラストレーション、エンゲージメント）を視覚的にフィードバックし、適切なサポートを提供するための基盤を構築する。

## 要求事項

### 機能要件

#### FR1: 感情インジケーターコンポーネント
- 現在の感情状態を表示（frustrated, confident, confused, happy, tired, neutral）
- フラストレーションレベル（low/medium/high）を視覚化
- エンゲージメントレベル（low/medium/high）を視覚化
- サポートレベル（minimal/moderate/intensive）を表示

#### FR2: キャラクター感情連動
- `CharacterDisplay`コンポーネントを拡張し、感情に応じた表情変化を実装
- 感情タイプごとに異なる目・口の表現
- スムーズなトランジションアニメーション

#### FR3: WebSocketメッセージハンドリング（既存実装の活用）
- `EmotionUpdateMessage`の処理は既に`useVoiceStream`で実装済み
- `SessionContent`で`emotionAnalysisAtom`と`emotionAdaptationAtom`の購読
- 感情履歴の記録（`emotionHistoryAtom`）

### 非機能要件

#### NFR1: アクセシビリティ
- 感情状態のテキスト表現（スクリーンリーダー対応）
- 色だけに依存しない視覚表現（アイコン併用）

#### NFR2: パフォーマンス
- 感情更新時のスムーズなアニメーション（60fps）
- 不要な再レンダリングの防止

#### NFR3: テストカバレッジ
- 80%以上のカバレッジを維持

### 制約条件

- 既存のデザインシステム（Tailwind CSS）に準拠
- 小学校低学年（1〜3年生）向けのシンプルで直感的なUI
- Framer Motionを使用したアニメーション

## 対象範囲

### In Scope
- `EmotionIndicator`コンポーネントの新規作成
- `CharacterDisplay`の感情連動拡張
- `SessionContent`での感情状態購読と表示統合
- 単体テスト・統合テストの作成

### Out of Scope
- WebSocketメッセージハンドリング（既に実装済み）
- バックエンドの感情分析ロジック
- 感情履歴の詳細分析UI（将来のフェーズ）

## 成功基準

1. 感情状態がリアルタイムでUIに反映される
2. キャラクターの表情が感情に応じて変化する
3. すべてのテストがパスする（`bun lint && bun typecheck && bun test`）
4. アクセシビリティチェックをパスする
