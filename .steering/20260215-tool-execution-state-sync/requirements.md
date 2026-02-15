# Requirements - ツール実行結果のatom同期修正

## 背景・目的

SessionContentの`handleToolExecution`コールバックは`activeToolExecutionsAtom`のみ更新しており、
`hintLevelAtom`と`learningProgressAtom`への同期が欠落している。

## 要求事項

### 機能要件

- `manage_hint_tool` completed時に `hintLevelAtom` を更新
- `record_progress_tool` completed時に `learningProgressAtom` を更新

### 非機能要件

- 既存テストの破壊なし
- TypeScript型安全性の維持

## 対象範囲

### In Scope

- `SessionContent.tsx` の `handleToolExecution` 修正
- テスト追加

### Out of Scope

- バックエンド変更（既に正しいデータを送信）

## 成功基準

- ヒントツール実行時にhintLevelAtomが正しく更新される
- 進捗記録ツール実行時にlearningProgressAtomが正しく更新される
- 全テスト通過
