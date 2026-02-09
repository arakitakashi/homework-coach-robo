# Task List - Phase 2d 感情適応UIコンポーネント

## Phase 1: 環境セットアップ

- [ ] ディレクトリ作成（`components/features/EmotionIndicator/`）
- [ ] 依存パッケージの確認（`framer-motion`, `lucide-react` - 既存）
- [ ] 既存の型定義確認（`types/phase2.ts`, `store/atoms/phase2.ts`）

## Phase 2: EmotionIndicatorコンポーネント（TDD）

### 2.1 EmotionLevelBarサブコンポーネント

- [ ] `EmotionLevelBar.test.tsx` の作成（Red）
  - [ ] low/medium/high レベルが正しく表示される
  - [ ] アクセシビリティ属性（aria-label）が設定される
  - [ ] カスタムラベルが表示される
- [ ] `EmotionLevelBar.tsx` の実装（Green）
  - [ ] レベルに応じたバーの塗りつぶし
  - [ ] Tailwind CSSスタイリング
  - [ ] テストを通す
- [ ] リファクタリング（Refactor）

### 2.2 EmotionIndicatorメインコンポーネント

- [ ] `EmotionIndicator.test.tsx` の作成（Red）
  - [ ] `emotionAnalysisAtom` が null の場合、何も表示しない
  - [ ] 感情タイプごとに正しいアイコンと色が表示される（6パターン）
  - [ ] フラストレーションレベルが表示される
  - [ ] エンゲージメントレベルが表示される
  - [ ] `emotionAdaptationAtom` からサポートレベルが表示される
  - [ ] アクセシビリティ属性が設定される
- [ ] `EmotionIndicator.tsx` の実装（Green）
  - [ ] `emotionAnalysisAtom`, `emotionAdaptationAtom` の購読
  - [ ] 感情タイプ → アイコン・色のマッピング
  - [ ] EmotionLevelBarの統合
  - [ ] Tailwind CSSスタイリング
  - [ ] テストを通す
- [ ] `index.ts` の作成
- [ ] リファクタリング（Refactor）

## Phase 3: CharacterDisplay拡張（TDD）

### 3.1 感情連動の実装

- [ ] `CharacterDisplay.test.tsx` のテスト追加（Red）
  - [ ] `emotionAnalysisAtom` が設定されている場合、感情に応じた表情になる
  - [ ] frustrated: 目が困った形、口が下がる
  - [ ] confident: 目が輝く、口が笑顔
  - [ ] confused: 目が疑問形、口が「？」
  - [ ] happy: 目がキラキラ、口が大きな笑顔
  - [ ] tired: 目が半開き、口が平ら
  - [ ] neutral: デフォルトの表情
  - [ ] 感情が未設定の場合、既存の`state`プロップで動作する
- [ ] `CharacterDisplay.tsx` の実装（Green）
  - [ ] `emotionAnalysisAtom` の購読
  - [ ] 感情優先の表情決定ロジック
  - [ ] `RobotCharacter`の表情パラメータ追加
  - [ ] テストを通す
- [ ] リファクタリング（Refactor）

## Phase 4: SessionContentへの統合

- [ ] `SessionContent.tsx` の読み込み
  - [ ] `EmotionIndicator` コンポーネントのimport
  - [ ] 既存の`emotionAnalysisAtom`, `emotionAdaptationAtom`購読の確認（既存実装確認）
  - [ ] `EmotionIndicator` の配置（適切な位置を決定）
  - [ ] `CharacterDisplay` へのemotion連動確認
- [ ] `SessionContent.test.tsx` のテスト更新
  - [ ] `EmotionIndicator` が表示される
  - [ ] 感情更新時に `EmotionIndicator` が更新される
  - [ ] `CharacterDisplay` が感情に応じて変化する
- [ ] `frontend/components/features/index.ts` に `EmotionIndicator` をエクスポート追加

## Phase 5: アニメーション実装

- [ ] Framer Motionアニメーション追加
  - [ ] `EmotionIndicator` のフェードイン/アウト
  - [ ] レベルバーのスムーズな変化
  - [ ] `CharacterDisplay` の表情トランジション
- [ ] パフォーマンステスト
  - [ ] 感情更新時のレンダリングパフォーマンス確認
  - [ ] 60fps維持確認

## Phase 6: 品質チェック

- [ ] コードレビュー（セルフレビュー）
  - [ ] TDD原則に従っているか
  - [ ] 型安全性が確保されているか
  - [ ] アクセシビリティが考慮されているか
- [ ] セキュリティレビュー
  - [ ] XSS対策（型制約確認）
- [ ] テストカバレッジ確認
  - [ ] `bunx vitest run --coverage`
  - [ ] 80%以上を維持
- [ ] リンター・フォーマッター実行
  - [ ] `bun lint`
  - [ ] `bun typecheck`
  - [ ] `bunx vitest run`
- [ ] ドキュメント更新
  - [ ] `/update-docs` スキル使用

## Phase 7: PR作成

- [ ] PR作成前のローカルCIチェック
  - [ ] `bun lint` → エラーなし
  - [ ] `bun typecheck` → エラーなし
  - [ ] `bunx vitest run` → 全テスト通過
- [ ] `/create-pr` スキル使用
  - [ ] タイトル: `feat(frontend): Phase 2d emotion adaptation UI components`
  - [ ] Issue #64 をクローズ
