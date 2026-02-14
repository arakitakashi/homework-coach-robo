# Requirements - 学習プロファイル表示コンポーネント (Issue #66)

## 背景・目的

GitHub Issue #66 で、子供の学習プロファイル（思考の傾向、教科別理解度、セッションサマリー）を表示するコンポーネントの実装が求められている。`ChildLearningProfile` 型と `learningProfileAtom` は既に定義済みで、UIコンポーネントの新規作成が必要。

## 要求事項

### 機能要件

1. 学習プロファイルの概要表示（セッション数・問題解決数）
2. 思考の傾向表示（既存 `ThinkingTendenciesDisplay` を再利用）
3. 教科別理解度のカード表示（習熟度レベル・トレンド・得意/苦手）
4. トレンドバッジ（improving/stable/declining）

### 非機能要件

- 小学校低学年向けのやさしい日本語
- アクセシビリティ（aria属性）
- Tailwind CSSでのスタイリング
- Jotai atomとの連携

### 制約条件

- `ChildLearningProfile` 型に `sessionSummaries` フィールドは含まれない
- 初回実装では `totalSessions` / `totalProblemsSolved` の数値サマリー表示

## 対象範囲

### In Scope

- TrendBadge, ProfileSummary, SubjectCard, LearningProfile コンポーネント
- 各コンポーネントのテスト
- index.ts エクスポート

### Out of Scope

- SessionSummary 詳細表示（型拡張後に対応）
- バックエンドAPI連携
- Framer Motion アニメーション（将来追加可能）

## 成功基準

- 全テストパス
- lint/typecheck パス
- 既存テスト517件が引き続きパス
