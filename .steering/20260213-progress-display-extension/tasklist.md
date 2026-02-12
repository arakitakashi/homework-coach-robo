# Task List - ProgressDisplay拡張（教科・トピック対応）

## Phase 1: 環境セットアップ

- [x] ブランチ作成（`feature/progress-display-extension-68`）
- [x] ステアリングディレクトリ作成（`.steering/20260213-progress-display-extension`）
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成
- [ ] 既存ファイルの確認（`ProgressDisplay.tsx`, `ProgressDisplay.test.tsx`）
- [ ] 型定義の確認（`types/session.ts`, `types/phase2.ts`）

## Phase 2: テスト実装（TDD）

### 2.1. SubjectBadge コンポーネントのテスト

- [ ] `SubjectBadge.test.tsx` 作成
  - [ ] 算数バッジの表示テスト（アイコン🧮、ラベル「算数」、青系カラー）
  - [ ] 国語バッジの表示テスト（アイコン📖、ラベル「国語」、緑系カラー）
  - [ ] アクセシビリティ確認（aria-label）

### 2.2. TopicLabel コンポーネントのテスト

- [ ] `TopicLabel.test.tsx` 作成
  - [ ] トピック表示テスト
  - [ ] 長いトピック名の表示テスト

### 2.3. SubjectDisplay コンポーネントのテスト

- [ ] `SubjectDisplay.test.tsx` 作成
  - [ ] 教科のみ存在する場合のテスト
  - [ ] トピックのみ存在する場合のテスト
  - [ ] 両方存在する場合のテスト
  - [ ] 両方未設定の場合（nullを返す）のテスト

### 2.4. TendencyBar コンポーネントのテスト

- [ ] `TendencyBar.test.tsx` 作成
  - [ ] スコア0のテスト
  - [ ] スコア50のテスト
  - [ ] スコア100のテスト
  - [ ] スコアが範囲外（0未満、100超）の場合の正規化テスト
  - [ ] invert=true の場合のカラー反転テスト
  - [ ] プログレスバーのaria属性テスト

### 2.5. ThinkingTendenciesDisplay コンポーネントのテスト

- [ ] `ThinkingTendenciesDisplay.test.tsx` 作成
  - [ ] 正常な傾向データの表示テスト
  - [ ] 4つの傾向バーがすべて表示されることを確認
  - [ ] 未設定の場合（nullを返す）のテスト

### 2.6. ProgressDisplay 統合テスト

- [ ] `ProgressDisplay.test.tsx` 更新
  - [ ] 既存テストの確認（変更がないことを確認）
  - [ ] currentSubject と currentTopic が存在する場合のテスト
  - [ ] thinkingTendencies が存在する場合のテスト
  - [ ] すべてのPhase 2フィールドが存在する場合のテスト
  - [ ] Phase 2フィールドがすべて未設定の場合のテスト（既存表示のみ）
  - [ ] スナップショットテスト

## Phase 3: 実装

### 3.1. SubjectBadge コンポーネント

- [ ] `SubjectBadge.tsx` 作成
  - [ ] `SUBJECT_CONFIG` 定数定義（アイコン、ラベル、カラー）
  - [ ] `SubjectBadgeProps` 型定義
  - [ ] コンポーネント実装
  - [ ] Tailwind CSS スタイリング
  - [ ] アクセシビリティ対応（aria-label）

### 3.2. TopicLabel コンポーネント

- [ ] `TopicLabel.tsx` 作成
  - [ ] `TopicLabelProps` 型定義
  - [ ] コンポーネント実装
  - [ ] Tailwind CSS スタイリング

### 3.3. SubjectDisplay コンポーネント

- [ ] `SubjectDisplay.tsx` 作成
  - [ ] `SubjectDisplayProps` 型定義
  - [ ] コンポーネント実装
  - [ ] 条件付きレンダリング（subject と topic が両方未設定の場合 null）
  - [ ] レスポンシブレイアウト（モバイル: 縦並び、デスクトップ: 横並び）
  - [ ] Tailwind CSS スタイリング
  - [ ] アクセシビリティ対応（section, aria-label）

### 3.4. TendencyBar コンポーネント

- [ ] `TendencyBar.tsx` 作成
  - [ ] `TendencyBarProps` 型定義
  - [ ] スコアの正規化ロジック（0〜100）
  - [ ] プログレスバー実装
  - [ ] invert オプション実装（色の反転）
  - [ ] Tailwind CSS スタイリング
  - [ ] アクセシビリティ対応（role="progressbar", aria-valuenow, aria-valuemin, aria-valuemax, aria-label）

### 3.5. ThinkingTendenciesDisplay コンポーネント

- [ ] `ThinkingTendenciesDisplay.tsx` 作成
  - [ ] `ThinkingTendenciesDisplayProps` 型定義
  - [ ] 条件付きレンダリング（tendencies が未設定の場合 null）
  - [ ] 4つのTendencyBarコンポーネントの配置
    - [ ] 粘り強さ（persistenceScore）
    - [ ] 自立度（independenceScore）
    - [ ] 振り返り（reflectionQuality）
    - [ ] ヒント依存度（hintDependency, invert=true）
  - [ ] Tailwind CSS スタイリング
  - [ ] アクセシビリティ対応（section, aria-label）

### 3.6. ProgressDisplay 拡張

- [ ] `ProgressDisplay.tsx` 更新
  - [ ] Props に currentSubject, currentTopic, thinkingTendencies を追加
  - [ ] SubjectDisplay の条件付き表示
  - [ ] ThinkingTendenciesDisplay の条件付き表示
  - [ ] レイアウト調整（既存の進捗表示との統合）
  - [ ] Tailwind CSS スタイリング
  - [ ] アクセシビリティ対応

### 3.7. エクスポート集約

- [ ] `index.ts` 更新
  - [ ] SubjectDisplay のエクスポート追加
  - [ ] ThinkingTendenciesDisplay のエクスポート追加

## Phase 4: リファクタリングと最適化

- [ ] コードの整理
- [ ] 不要なコメントの削除
- [ ] パフォーマンス最適化（useMemo の検討）
- [ ] コードの重複排除

## Phase 5: 品質チェック

- [ ] コードレビュー（セルフレビュー）
  - [ ] 型安全性の確認（any型を使用していない）
  - [ ] Tailwind CSS のみ使用（インラインスタイルなし）
  - [ ] アクセシビリティの確認（aria属性、セマンティックHTML）
  - [ ] レスポンシブデザインの確認
- [ ] セキュリティレビュー（`/security-review` スキル使用）
- [ ] テストカバレッジ確認（80%以上）
  - [ ] `bunx vitest run --coverage`
- [ ] リンター実行
  - [ ] `bun lint`
- [ ] 型チェック実行
  - [ ] `bun typecheck`
- [ ] テスト実行
  - [ ] `bunx vitest run`
- [ ] ドキュメント更新
  - [ ] `CLAUDE.md` の Development Context 更新（必要に応じて）
  - [ ] `docs/implementation-status.md` の完了済み機能一覧に追加
  - [ ] `docs/implementation-status.md` のステアリングディレクトリ一覧に追加

## Phase 6: PR作成準備

- [ ] 全品質チェックの最終確認
  - [ ] `bun lint && bun typecheck && bunx vitest run`
- [ ] コミット作成
  - [ ] git add
  - [ ] git commit（Conventional Commits形式）
- [ ] プッシュ
  - [ ] git push -u origin feature/progress-display-extension-68
- [ ] PR作成
  - [ ] `/create-pr` スキル使用
  - [ ] Issue #68 への参照（`closes #68`）
- [ ] Issue #68 にコメント追加
  - [ ] PR作成報告
