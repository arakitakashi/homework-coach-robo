# Task List - InputModeSelectorのUI統合

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリ作成
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成
- [x] 現在の実装状態確認（camera.ts に inputModeAtom 既存確認）

## Phase 2: テスト実装（TDD）

### 2.1: inputModeAtom のテスト

- [x] camera.test.ts で既に実装済みを確認
  - [x] inputModeAtom の初期値が null であることをテスト（既存）
  - [x] inputModeAtom を "voice" に更新できることをテスト（既存）
  - [x] inputModeAtom を "image" に更新できることをテスト（既存）

### 2.2: SessionContent のモード選択テスト

- [x] SessionContent.test.tsx に新規テスト追加
  - [x] 初期表示時に InputModeSelector が表示されることをテスト
  - [x] 音声モード選択後、VoiceInterface が表示されることをテスト
  - [x] 画像モード選択後、プレースホルダーが表示されることをテスト
  - [x] 音声モード選択後、InputModeSelector が非表示になることをテスト
  - [x] 画像モード選択後、InputModeSelector が非表示になることをテスト

## Phase 3: 実装

### 3.1: inputModeAtom 実装

- [x] camera.ts で既に実装済みを確認
  - [x] inputModeAtom 定義済み
  - [x] 型定義: `"voice" | "image" | null` 済み
  - [x] 初期値: `null` 済み
  - [x] エクスポート済み

### 3.2: SessionContent 統合

- [x] SessionContent.tsx を編集
  - [x] InputModeSelector を import
  - [x] inputModeAtom を import（camera.ts から）
  - [x] useAtom(inputModeAtom) を使用
  - [x] 条件分岐ロジック実装（null → InputModeSelector表示）
  - [x] 条件分岐ロジック実装（voice → VoiceInterface表示）
  - [x] 条件分岐ロジック実装（image → プレースホルダー表示）

## Phase 4: テスト実行

- [x] `bunx vitest run` で全テスト実行
  - [x] SessionContent.test.tsx の新規5テストがパス
  - [x] tests/pages/Session.test.tsx の14テストがパス（inputModeAtom対応後）
  - [x] 全632テストがパス

## Phase 5: 品質チェック

- [x] リンター実行（`bun lint`）- 既存警告のみ、新規エラーなし
- [x] 型チェック実行（`bun typecheck`）- エラーなし
- [x] 全テスト実行（`bunx vitest run`）- 全632テストパス
- [x] テストカバレッジ確認

## Phase 6: コミット

- [x] 変更ファイルをステージング
- [x] コミットメッセージ作成
  - Type: `feat`
  - Scope: `frontend`
  - Summary: InputModeSelectorのUI統合
- [x] git commit 実行（a6f93e5）

## Phase 7: PR更新

- [x] git push で PR #159 を更新
- [x] PR説明文を更新（自動更新）
