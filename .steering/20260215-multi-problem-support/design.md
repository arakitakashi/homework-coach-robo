# Design - 複数問題認識サポート

## アーキテクチャ概要

### データフロー
```
CameraInterface → onRecognitionComplete(全問題) → SessionContent
  → worksheetProblemsAtom更新 → ProblemSelector表示
  → ユーザー選択 → sendImageStart(選択問題, index, total)
  → Backend受信 → エージェントへコンテキスト付き転送
```

### 状態管理（Jotai Atoms）
- `worksheetProblemsAtom`: 全問題の状態配列
- `currentProblemIndexAtom`: 選択中の問題インデックス
- `currentProblemAtom`: 現在の問題（derived）
- `remainingProblemsCountAtom`: 未完了問題数（derived）
- `showProblemSelectorAtom`: セレクター表示フラグ

## コンポーネント設計

### ProblemSelector
- `ProblemItem`: 個別問題カード（ステータス表示、タッチターゲット64px）
- `ProblemSelector`: 問題一覧（staggerアニメーション）

### CameraInterface変更
- `onRecognitionComplete` propを追加
- recognized状態で全問題プレビュー + 「もんだいをえらぶ」ボタン

### WebSocket型拡張
- `StartWithImageMessage.payload` に `problem_index`, `total_problems` 追加（オプショナル）

### Backend変更
- `_handle_start_with_image` で問題番号コンテキストをエージェントメッセージに含める
