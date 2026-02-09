# Task List - Phase 2b エージェント切り替えUIコンポーネント

## Phase 1: 環境セットアップ

- [ ] 依存パッケージの確認（`framer-motion`, `lucide-react`）
- [ ] 必要に応じてパッケージをインストール
- [ ] ディレクトリ作成（`components/features/AgentIndicator/`）

## Phase 2: テスト実装（TDD）

### 2.1 AgentIconコンポーネントのテスト

- [ ] `AgentIcon.test.tsx` の作成（Red）
  - [ ] エージェントタイプごとに正しいアイコンが表示される
  - [ ] `aria-hidden="true"` が設定される
  - [ ] カスタム className が適用される

### 2.2 AgentIndicatorコンポーネントのテスト

- [ ] `AgentIndicator.test.tsx` の作成（Red）
  - [ ] `activeAgentAtom` が null の場合、何も表示しない
  - [ ] `activeAgentAtom` が設定されている場合、エージェント名とアイコンを表示
  - [ ] 算数コーチが表示される（`math_coach`）
  - [ ] 国語コーチが表示される（`japanese_coach`）
  - [ ] 励ましが表示される（`encouragement`）
  - [ ] 振り返りが表示される（`review`）
  - [ ] `aria-label` が正しく設定される

## Phase 3: 実装

### 3.1 AgentIconコンポーネント

- [ ] `AgentIcon.tsx` の実装（Green）
  - [ ] AgentType → Icon のマッピング
  - [ ] Lucide Reactアイコンの使用
  - [ ] `aria-hidden="true"` の設定
  - [ ] テストを通す

### 3.2 AgentIndicatorコンポーネント

- [ ] `AgentIndicator.tsx` の実装（Green）
  - [ ] `activeAgentAtom` の購読
  - [ ] エージェント名のマッピング（`AGENT_LABELS`）
  - [ ] AgentIconコンポーネントの統合
  - [ ] Tailwind CSSスタイリング
  - [ ] テストを通す

### 3.3 アニメーション実装

- [ ] Framer Motion統合
  - [ ] `AnimatePresence` の使用
  - [ ] フェードイン/フェードアウトアニメーション
  - [ ] `mode="wait"` の設定

### 3.4 index.ts作成

- [ ] エクスポート集約ファイルの作成

## Phase 4: SessionContentへの統合

- [ ] `SessionContent.tsx` の読み込み
- [ ] `AgentIndicator` コンポーネントの統合位置を決定
- [ ] 統合実装
- [ ] 既存テストの更新（必要に応じて）

## Phase 5: 品質チェック

- [ ] コードレビュー（セルフレビュー）
  - [ ] TDD原則に従っているか
  - [ ] 型安全性が確保されているか
  - [ ] アクセシビリティが考慮されているか
- [ ] セキュリティレビュー
  - [ ] XSS対策（エージェント名は定数から取得）
  - [ ] 入力検証（AgentType型制約）
- [ ] テストカバレッジ確認
  - [ ] `bunx vitest run --coverage`
  - [ ] 80%以上を維持
- [ ] リンター・フォーマッター実行
  - [ ] `bun lint`
  - [ ] `bun typecheck`
  - [ ] `bunx vitest run`
- [ ] ドキュメント更新
  - [ ] `docs/implementation-status.md` に追記（必要に応じて）

## Phase 6: デプロイ準備

- [ ] PR作成前のローカルCIチェック
  - [ ] `bun lint` → エラーなし
  - [ ] `bun typecheck` → エラーなし
  - [ ] `bunx vitest run` → 全テスト通過
- [ ] PR作成
  - [ ] タイトル: `feat(frontend): Phase 2b エージェント切り替えUIコンポーネント`
  - [ ] 説明文にIssue #63をリンク
  - [ ] スクリーンショット追加（可能であれば）
