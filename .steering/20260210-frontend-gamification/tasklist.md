# Task List - フロントエンド ゲーミフィケーション要素

## Phase 1: 環境セットアップ

- [ ] 依存パッケージの確認（Framer Motion, Lucide React は既存）
- [ ] 型定義ファイル作成（`types/gamification.ts`）
- [ ] Atomsファイル作成（`store/atoms/gamification.ts`）

## Phase 2: テスト実装（TDD - ボトムアップ）

### Step 1: Atoms のテスト
- [ ] `gamification.test.ts` 作成
- [ ] gamificationStateAtom 初期値テスト
- [ ] addPointsAtom ポイント加算テスト
- [ ] unlockBadgeAtom バッジ獲得テスト
- [ ] recentBadgeAtom 最近のバッジ取得テスト

### Step 2: PointDisplay のテスト
- [ ] `PointDisplay.test.tsx` 作成
- [ ] ポイント表示テスト
- [ ] レベル表示テスト
- [ ] プログレスバー表示テスト

### Step 3: BadgeNotification のテスト
- [ ] `BadgeNotification.test.tsx` 作成
- [ ] バッジ通知表示テスト
- [ ] アニメーション実行テスト
- [ ] 自動消滅テスト

### Step 4: StoryProgress のテスト
- [ ] `StoryProgress.test.tsx` 作成
- [ ] チャプター情報表示テスト
- [ ] 進行度プログレスバー表示テスト
- [ ] チャプター完了状態テスト

### Step 5: SessionContent 統合テスト
- [ ] `SessionContent.test.tsx` 更新
- [ ] ゲーミフィケーション要素の表示テスト
- [ ] 既存機能との共存テスト

## Phase 3: 実装

### Step 1: 型定義とAtoms
- [ ] `types/gamification.ts` 実装
- [ ] `store/atoms/gamification.ts` 実装
- [ ] `types/index.ts` の LearningProgress 拡張

### Step 2: PointDisplay コンポーネント
- [ ] `PointDisplay.tsx` 実装
- [ ] `LevelProgressBar.tsx` 実装
- [ ] Tailwind CSS スタイリング
- [ ] Framer Motion アニメーション追加

### Step 3: BadgeNotification コンポーネント
- [ ] `BadgeNotification.tsx` 実装
- [ ] Framer Motion トースト演出
- [ ] Lucide React アイコン統合

### Step 4: StoryProgress コンポーネント
- [ ] `StoryProgress.tsx` 実装
- [ ] `ChapterCard.tsx` 実装
- [ ] プログレスバーUI

### Step 5: SessionContent 統合
- [ ] SessionContent.tsx にゲーミフィケーション要素を追加
- [ ] レイアウト調整（既存UIとの共存）
- [ ] レスポンシブ対応

### Step 6: モックデータ準備
- [ ] デモ用バッジデータ作成
- [ ] デモ用ストーリーチャプター作成
- [ ] PointEvent サンプルデータ

## Phase 4: 統合テスト

- [ ] 全コンポーネント統合テスト
- [ ] ポイント加算からバッジ獲得までのフローテスト
- [ ] レベルアップ時の挙動テスト
- [ ] 既存機能（VoiceInterface, AgentIndicator, EmotionIndicator）との共存確認

## Phase 5: 品質チェック

- [ ] `/quality-check` スキルで品質チェック（lint, typecheck, test）
- [ ] テストカバレッジ確認（80%以上）
- [ ] アクセシビリティチェック（aria-label, キーボード操作）
- [ ] パフォーマンス確認（60fps アニメーション）
- [ ] `/update-docs` スキルでドキュメント更新
  - [ ] `CLAUDE.md` の Development Context 更新
  - [ ] `docs/implementation-status.md` に完了機能追加
  - [ ] `.steering/` ディレクトリ一覧更新

## Phase 6: PR作成

- [ ] コミット（feat: add gamification UI components）
- [ ] `/create-pr` スキルでPR作成
- [ ] PR説明にスクリーンショット追加（任意）

## 完了条件

- [ ] 全テストパス（ローカル: `bun lint && bun typecheck && bun test`）
- [ ] テストカバレッジ 80% 以上
- [ ] SessionContent でゲーミフィケーション要素が表示される
- [ ] ポイント加算・バッジ獲得のアニメーションが動作する
- [ ] 既存機能が正常に動作する
- [ ] ドキュメントが最新
