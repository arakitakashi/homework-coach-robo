# Task List - 学習プロファイル表示コンポーネント

## Phase 1: 環境セットアップ

- [x] ブランチ作成
- [x] ステアリングディレクトリ作成
- [x] LearningProfile ディレクトリ作成

## Phase 2: TDD実装

### TrendBadge（依存なし・最初に実装）
- [x] TrendBadge テスト作成（Red）
- [x] TrendBadge 実装（Green）

### ProfileSummary（依存なし）
- [x] ProfileSummary テスト作成（Red）
- [x] ProfileSummary 実装（Green）

### SubjectCard（TrendBadgeに依存）
- [x] SubjectCard テスト作成（Red）
- [x] SubjectCard 実装（Green）

### LearningProfile（全統合 + Jotai atom）
- [x] LearningProfile テスト作成（Red）
- [x] LearningProfile 実装（Green）

## Phase 3: エクスポート・統合

- [x] index.ts 作成
- [x] features/index.ts 更新

## Phase 4: 品質チェック

- [x] bun lint（既存の1 warningのみ、新規エラーなし）
- [x] bun typecheck（エラーなし）
- [x] bunx vitest run（52ファイル 550テスト全パス）

## Phase 5: コミット・PR

- [ ] コミット
- [ ] PR作成
