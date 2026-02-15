# Design - ツール実行結果のatom同期修正

## アーキテクチャ概要

`handleToolExecution`内でツール名を判定し、対応するatomのsetterを呼び出すブリッジコードを追加。

## 変更ファイル

1. `frontend/src/app/session/SessionContent.tsx` - atom setter取得 + ブリッジロジック
2. `frontend/src/app/session/SessionContent.test.tsx` - テスト追加

## 実装詳細

### hintLevelAtom同期
- ツール名: `manage_hint_tool`
- ステータス: `completed`
- 取得フィールド: `result.current_level`
- バリデーション: 0〜3の整数

### learningProgressAtom同期
- ツール名: `record_progress_tool`
- ステータス: `completed`
- 取得フィールド: `result.points_earned`
- ポイント→カウントマッピング: 3→selfDiscovery, 2→hintDiscovery, 1→together
