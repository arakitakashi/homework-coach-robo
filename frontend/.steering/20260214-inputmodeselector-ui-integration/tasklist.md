# Task List - InputModeSelectorのUI統合

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリ作成
- [x] requirements.md 作成
- [x] design.md 作成
- [x] tasklist.md 作成
- [ ] 現在の実装状態確認（session.ts atoms確認）

## Phase 2: テスト実装（TDD）

### 2.1: inputModeAtom のテスト

- [ ] store/atoms/session.test.ts を作成（または既存ファイルに追加）
  - [ ] inputModeAtom の初期値が null であることをテスト
  - [ ] inputModeAtom を "voice" に更新できることをテスト
  - [ ] inputModeAtom を "image" に更新できることをテスト

### 2.2: SessionContent のモード選択テスト

- [ ] SessionContent.test.tsx に新規テスト追加
  - [ ] 初期表示時に InputModeSelector が表示されることをテスト
  - [ ] 音声モード選択後、VoiceInterface が表示されることをテスト
  - [ ] 画像モード選択後、プレースホルダーが表示されることをテスト
  - [ ] 音声モード選択後、InputModeSelector が非表示になることをテスト
  - [ ] 画像モード選択後、InputModeSelector が非表示になることをテスト

## Phase 3: 実装

### 3.1: inputModeAtom 実装

- [ ] store/atoms/session.ts を作成（または既存ファイルに追加）
  - [ ] inputModeAtom を定義
  - [ ] 型定義: `"voice" | "image" | null`
  - [ ] 初期値: `null`
  - [ ] エクスポート

### 3.2: SessionContent 統合

- [ ] SessionContent.tsx を編集
  - [ ] InputModeSelector を import
  - [ ] inputModeAtom を import
  - [ ] useAtom(inputModeAtom) を使用
  - [ ] 条件分岐ロジック実装（null → InputModeSelector表示）
  - [ ] 条件分岐ロジック実装（voice → VoiceInterface表示）
  - [ ] 条件分岐ロジック実装（image → プレースホルダー表示）

## Phase 4: テスト実行

- [ ] `bunx vitest run` で全テスト実行
  - [ ] Phase 2.1 のテストがパス
  - [ ] Phase 2.2 のテストがパス
  - [ ] 既存の27テストがパス
  - [ ] 合計テスト数確認（27 + 新規 = ?）

## Phase 5: 品質チェック

- [ ] リンター実行（`bun lint`）
- [ ] 型チェック実行（`bun typecheck`）
- [ ] 全テスト実行（`bunx vitest run`）
- [ ] テストカバレッジ確認

## Phase 6: コミット

- [ ] 変更ファイルをステージング
- [ ] コミットメッセージ作成
  - Type: `feat`
  - Scope: `frontend`
  - Summary: InputModeSelectorのUI統合
- [ ] git commit 実行

## Phase 7: PR更新

- [ ] git push で PR #159 を更新
- [ ] PR説明文を更新（新規コミット内容を追記）
