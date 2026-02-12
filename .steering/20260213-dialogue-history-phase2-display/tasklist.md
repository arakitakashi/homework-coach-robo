# Task List - Phase 2 対話履歴の拡張表示

## Phase 1: 環境セットアップ

- [x] ブランチ作成（`feature/dialogue-history-phase2-display-67`）
- [x] ステアリングディレクトリ作成（`.steering/20260213-dialogue-history-phase2-display`）
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成
- [x] `/frontend` スキル参照
- [x] `/frontend-design` スキル参照
- [x] `/tdd` スキル参照

## Phase 2: テスト実装（TDD - Red）

### 2.1. QuestionTypeIcon テスト

- [ ] `QuestionTypeIcon.test.tsx` 作成
  - [ ] `understanding_check` 表示テスト
  - [ ] `thinking_guide` 表示テスト
  - [ ] `hint` 表示テスト
  - [ ] aria-label テスト

### 2.2. EmotionIcon テスト

- [ ] `EmotionIcon.test.tsx` 作成
  - [ ] 6つの感情タイプ表示テスト
  - [ ] カラーコーディングテスト
  - [ ] aria-label テスト

### 2.3. AgentBadge テスト

- [ ] `AgentBadge.test.tsx` 作成
  - [ ] 5つのエージェントタイプ表示テスト
  - [ ] バッジスタイルテスト
  - [ ] aria-label テスト

### 2.4. UnderstandingIndicator テスト

- [ ] `UnderstandingIndicator.test.tsx` 作成
  - [ ] 理解度バー表示テスト
  - [ ] パーセンテージ計算テスト
  - [ ] 正しい方向/間違った方向の色分けテスト
  - [ ] 明確化フラグ表示テスト
  - [ ] aria-label テスト

### 2.5. ToolExecutionBadges テスト

- [ ] `ToolExecutionBadges.test.tsx` 作成
  - [ ] 5つのツールタイプ表示テスト
  - [ ] ステータス（pending, running, completed, error）表示テスト
  - [ ] 複数ツール同時表示テスト
  - [ ] 空配列の場合の表示テスト

### 2.6. DialogueMetadataHeader テスト

- [ ] `DialogueMetadataHeader.test.tsx` 作成
  - [ ] 質問タイプ表示テスト
  - [ ] 感情表示テスト
  - [ ] エージェント表示テスト
  - [ ] 複数メタデータ同時表示テスト
  - [ ] メタデータなしの場合の非表示テスト

### 2.7. DialogueMetadataFooter テスト

- [ ] `DialogueMetadataFooter.test.tsx` 作成
  - [ ] 理解度インジケータ表示テスト
  - [ ] ツール実行バッジ表示テスト
  - [ ] 複数メタデータ同時表示テスト
  - [ ] メタデータなしの場合の非表示テスト

### 2.8. DialogueBubble テスト

- [ ] `DialogueBubble.test.tsx` 作成
  - [ ] 基本的なテキスト表示テスト
  - [ ] Phase 2 メタデータありの表示テスト
  - [ ] Phase 2 メタデータなしの表示テスト（後方互換）
  - [ ] 子供の発話スタイルテスト
  - [ ] キャラクターの発話スタイルテスト

### 2.9. DialogueHistory 統合テスト

- [ ] `DialogueHistory.test.tsx` 拡張
  - [ ] Phase 2 メタデータを含む対話履歴の表示テスト
  - [ ] Phase 1（メタデータなし）との互換性テスト
  - [ ] 100+ ターンのパフォーマンステスト（オプション）

## Phase 3: 実装（TDD - Green）

### 3.1. QuestionTypeIcon 実装

- [ ] `QuestionTypeIcon.tsx` 作成
  - [ ] 質問タイプマッピング実装
  - [ ] Lucide アイコン統合
  - [ ] カラーコーディング実装
  - [ ] aria-label 実装

### 3.2. EmotionIcon 実装

- [ ] `EmotionIcon.tsx` 作成
  - [ ] 感情タイプマッピング実装
  - [ ] EmotionIndicator のアイコン再利用
  - [ ] カラーコーディング実装
  - [ ] aria-label 実装

### 3.3. AgentBadge 実装

- [ ] `AgentBadge.tsx` 作成
  - [ ] エージェントタイプマッピング実装
  - [ ] バッジスタイル実装
  - [ ] aria-label 実装

### 3.4. UnderstandingIndicator 実装

- [ ] `UnderstandingIndicator.tsx` 作成
  - [ ] 理解度バー実装
  - [ ] パーセンテージ計算実装
  - [ ] 正しい方向/間違った方向の色分け実装
  - [ ] 明確化フラグ表示実装
  - [ ] aria-label 実装

### 3.5. ToolExecutionBadges 実装

- [ ] `ToolExecutionBadges.tsx` 作成
  - [ ] ツール名マッピング実装
  - [ ] ステータスアイコン実装
  - [ ] バッジスタイル実装
  - [ ] 複数ツール表示実装

### 3.6. DialogueMetadataHeader 実装

- [ ] `DialogueMetadataHeader.tsx` 作成
  - [ ] サブコンポーネント統合
  - [ ] 条件付きレンダリング実装
  - [ ] レイアウト実装

### 3.7. DialogueMetadataFooter 実装

- [ ] `DialogueMetadataFooter.tsx` 作成
  - [ ] サブコンポーネント統合
  - [ ] 条件付きレンダリング実装
  - [ ] レイアウト実装

### 3.8. DialogueBubble 拡張

- [ ] `DialogueBubble.tsx` を `DialogueHistory.tsx` から分離
  - [ ] DialogueMetadataHeader 統合
  - [ ] DialogueMetadataFooter 統合
  - [ ] 条件付きレンダリング実装
  - [ ] 既存スタイル維持

### 3.9. DialogueHistory 更新

- [ ] `DialogueHistory.tsx` 更新
  - [ ] DialogueBubble コンポーネントのインポート
  - [ ] 既存コードのリファクタリング

### 3.10. エクスポート集約

- [ ] `index.ts` 更新
  - [ ] 新規コンポーネントのエクスポート追加

## Phase 4: リファクタリング（TDD - Refactor）

- [ ] コードレビュー（セルフレビュー）
  - [ ] DRY原則の確認（重複コード削除）
  - [ ] 単一責任の原則の確認
  - [ ] コメント・ドキュメント追加
- [ ] パフォーマンス最適化
  - [ ] `React.memo` の適用（必要に応じて）
  - [ ] 不要な再レンダリングの削減
- [ ] アクセシビリティ確認
  - [ ] すべてのアイコンに aria-label が付いているか確認
  - [ ] セマンティックHTML の確認

## Phase 5: 品質チェック

- [ ] ローカルテスト実行
  - [ ] `bun lint` → エラーなし
  - [ ] `bun typecheck` → エラーなし
  - [ ] `bun test` → 全テスト通過
  - [ ] テストカバレッジ確認（80%以上）
- [ ] ビジュアル確認
  - [ ] 開発サーバー起動（`bun dev`）
  - [ ] Phase 2 メタデータありの対話表示確認
  - [ ] Phase 2 メタデータなしの対話表示確認（後方互換）
  - [ ] モバイル表示確認
- [ ] セキュリティレビュー（`/security-review` スキル使用）
- [ ] ドキュメント更新
  - [ ] `CLAUDE.md` 更新（Development Context）
  - [ ] `docs/implementation-status.md` 更新（完了済み機能一覧）
  - [ ] ステアリングディレクトリ一覧追加

## Phase 6: コミット・PR作成

- [ ] 適切な粒度でコミット
  - [ ] コミット1: テストファイル作成（Phase 2）
  - [ ] コミット2: サブコンポーネント実装（Phase 3.1-3.5）
  - [ ] コミット3: メタデータヘッダー・フッター実装（Phase 3.6-3.7）
  - [ ] コミット4: DialogueBubble 拡張（Phase 3.8-3.9）
  - [ ] コミット5: リファクタリング（Phase 4）
  - [ ] コミット6: ドキュメント更新（Phase 5）
- [ ] PR作成前の最終チェック
  - [ ] `bun lint && bun typecheck && bun test` → 全パス
  - [ ] ドキュメント更新確認
- [ ] PR作成（`/create-pr` スキル使用）

## Phase 7: レビュー・マージ

- [ ] PR レビュー対応
- [ ] CI/CD 確認
- [ ] マージ

## 完了サマリー

実装完了後、`.steering/20260213-dialogue-history-phase2-display/COMPLETED.md` を作成し、以下を記録：

- 実装内容の要約
- 発生した問題と解決方法
- 今後の改善点
- 学んだこと（Lessons Learned）
