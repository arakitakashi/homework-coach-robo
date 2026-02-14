# Task List - セッションページへの画像アップロード機能統合

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリ作成（`.steering/20260214-session-image-upload-integration/`）
- [x] requirements.md作成
- [x] design.md作成
- [x] tasklist.md作成（本ファイル）
- [ ] 新しいブランチ作成（`feature/session-image-upload-integration`） - 作成済み
- [ ] 既存コードの確認
  - [ ] CameraInterfaceコンポーネント
  - [ ] VoiceWebSocketClient
  - [ ] useVoiceStream
  - [ ] 既存の型定義

## Phase 2: 型定義拡張（TDD: Red）

### 2.1 WebSocket送信メッセージ型

- [ ] `types/session.ts`に`StartWithImageMessage`型を追加（Red）
  - [ ] テスト: `types/session.test.ts`作成
  - [ ] テスト: `StartWithImageMessage`型の検証
  - [ ] テスト: `WebSocketOutgoingMessage`ユニオン型の検証

### 2.2 WebSocket受信イベント型

- [ ] `types/phase2.ts`または`lib/api/types.ts`に画像イベント型を追加（Red）
  - [ ] テスト: 既存の型テストファイル確認
  - [ ] テスト: `ImageProblemConfirmedEvent`型の検証（必要に応じて）
  - [ ] テスト: `ImageRecognitionErrorEvent`型の検証（必要に応じて）
  - [ ] 既存の型定義に含まれているか確認し、不足があれば追加

### 2.3 Jotai Atoms

- [ ] `store/atoms/camera.ts`の存在確認（Red）
  - [ ] テスト: `store/atoms/camera.test.ts`作成
  - [ ] テスト: `inputModeAtom`の初期値と更新
  - [ ] テスト: `recognizedProblemTextAtom`の初期値と更新
  - [ ] 存在しない場合は作成、存在する場合は確認のみ

## Phase 3: VoiceWebSocketClient拡張（TDD: Red → Green → Refactor）

### 3.1 sendImageStart()メソッド追加

- [ ] テスト: `lib/api/voiceWebSocket.test.ts`更新（Red）
  - [ ] `sendImageStart()`メソッドのテスト追加
  - [ ] WebSocketに正しいJSONメッセージが送信されることを検証
  - [ ] 接続未確立時のエラーハンドリングを検証

- [ ] 実装: `lib/api/voiceWebSocket.ts`更新（Green）
  - [ ] `sendImageStart()`メソッド実装
  - [ ] `StartWithImageMessage`型を使用

- [ ] リファクタリング（Refactor）
  - [ ] コードの整理
  - [ ] 型定義の最適化

### 3.2 画像イベント受信ハンドラ追加

- [ ] テスト: `lib/api/voiceWebSocket.test.ts`更新（Red）
  - [ ] `onImageProblemConfirmed`コールバックのテスト追加
  - [ ] `onImageRecognitionError`コールバックのテスト追加
  - [ ] `processADKEvent()`メソッドの型ガード検証

- [ ] 実装: `lib/api/voiceWebSocket.ts`更新（Green）
  - [ ] `VoiceWebSocketOptions`にコールバック追加
  - [ ] `processADKEvent()`メソッドに型ガードと処理追加

- [ ] リファクタリング（Refactor）
  - [ ] イベント処理ロジックの整理

### 3.3 型定義ファイル更新

- [ ] テスト: `lib/api/types.ts`の型テスト（必要に応じて）
- [ ] 実装: `lib/api/types.ts`更新
  - [ ] `VoiceWebSocketOptions`に新規コールバック追加
  - [ ] 必要に応じてイベント型を追加

## Phase 4: useVoiceStream フック拡張（TDD: Red → Green → Refactor）

### 4.1 フックオプション拡張

- [ ] テスト: `lib/hooks/useVoiceStream.test.ts`更新（Red）
  - [ ] `onImageProblemConfirmed`コールバックのテスト追加
  - [ ] `onImageRecognitionError`コールバックのテスト追加

- [ ] 実装: `lib/hooks/useVoiceStream.ts`更新（Green）
  - [ ] `UseVoiceStreamOptions`にコールバック追加
  - [ ] VoiceWebSocketClient初期化時にコールバックを渡す

- [ ] リファクタリング（Refactor）
  - [ ] オプション処理の整理

### 4.2 sendImageStart()メソッド公開

- [ ] テスト: `lib/hooks/useVoiceStream.test.ts`更新（Red）
  - [ ] `sendImageStart()`メソッドのテスト追加
  - [ ] VoiceWebSocketClientへの委譲を検証

- [ ] 実装: `lib/hooks/useVoiceStream.ts`更新（Green）
  - [ ] `UseVoiceStreamReturn`に`sendImageStart`追加
  - [ ] `useCallback`でラップして実装

- [ ] リファクタリング（Refactor）
  - [ ] メソッド定義の整理

## Phase 5: InputModeSelector コンポーネント（TDD: Red → Green → Refactor）

### 5.1 コンポーネント作成

- [ ] テスト: `components/features/InputModeSelector/InputModeSelector.test.tsx`作成（Red）
  - [ ] コンポーネントのレンダリングテスト
  - [ ] 「声で伝える」ボタンクリックテスト
  - [ ] 「写真で伝える」ボタンクリックテスト
  - [ ] `onModeSelect`コールバックの呼び出し検証
  - [ ] アクセシビリティ検証（aria-label）

- [ ] 実装: `components/features/InputModeSelector/InputModeSelector.tsx`作成（Green）
  - [ ] Props定義: `onModeSelect: (mode: 'voice' | 'image') => void`
  - [ ] 2つのボタン（🎤 声で伝える、📷 写真で伝える）
  - [ ] Tailwind CSSでスタイリング（大きなボタン、タッチターゲット44px以上）
  - [ ] アクセシビリティ対応（aria-label）

- [ ] リファクタリング（Refactor）
  - [ ] コンポーネント構造の最適化
  - [ ] スタイルの整理

### 5.2 エクスポート

- [ ] `components/features/InputModeSelector/index.ts`作成
  - [ ] `InputModeSelector`をエクスポート
- [ ] `components/features/index.ts`更新
  - [ ] `InputModeSelector`を追加

## Phase 6: SessionContent 統合（TDD: Red → Green → Refactor）

### 6.1 Jotai atoms統合

- [ ] テスト: `src/app/session/SessionContent.test.tsx`更新（Red）
  - [ ] `inputModeAtom`の初期値テスト
  - [ ] `recognizedProblemTextAtom`の初期値テスト
  - [ ] モード切り替え時の状態変化テスト

- [ ] 実装: `src/app/session/SessionContent.tsx`更新（Green）
  - [ ] `inputModeAtom`, `recognizedProblemTextAtom`のimport
  - [ ] `useAtom`でatoms取得

- [ ] リファクタリング（Refactor）
  - [ ] atoms使用の最適化

### 6.2 InputModeSelector統合

- [ ] テスト: `src/app/session/SessionContent.test.tsx`更新（Red）
  - [ ] セッション未作成時にInputModeSelectorが表示されることを検証
  - [ ] セッション作成後はInputModeSelectorが非表示になることを検証
  - [ ] モード選択時の処理を検証

- [ ] 実装: `src/app/session/SessionContent.tsx`更新（Green）
  - [ ] `InputModeSelector`のimport
  - [ ] セッション未作成時の条件分岐
  - [ ] `onModeSelect`ハンドラ実装
    - [ ] voice選択時: `inputModeAtom = 'voice'` + セッション作成
    - [ ] image選択時: `inputModeAtom = 'image'`（セッション作成は後）

- [ ] リファクタリング（Refactor）
  - [ ] 条件分岐の整理
  - [ ] ハンドラの最適化

### 6.3 CameraInterface統合

- [ ] テスト: `src/app/session/SessionContent.test.tsx`更新（Red）
  - [ ] 画像モード選択時にCameraInterfaceが表示されることを検証
  - [ ] `onProblemRecognized`コールバックの処理を検証
  - [ ] 認識完了後の状態遷移を検証

- [ ] 実装: `src/app/session/SessionContent.tsx`更新（Green）
  - [ ] `CameraInterface`のimport（既に存在する可能性）
  - [ ] 画像モード時の条件分岐
  - [ ] `onProblemRecognized`ハンドラ実装
    - [ ] `recognizedProblemTextAtom`更新
    - [ ] セッション作成（既存`createSession`を使用）
    - [ ] WebSocket接続後に`sendImageStart()`呼び出し

- [ ] リファクタリング（Refactor）
  - [ ] 画像モードフローの整理

### 6.4 WebSocketイベントハンドラ統合

- [ ] テスト: `src/app/session/SessionContent.test.tsx`更新（Red）
  - [ ] `onImageProblemConfirmed`ハンドラのテスト
  - [ ] `onImageRecognitionError`ハンドラのテスト
  - [ ] 対話履歴への追加を検証
  - [ ] 音声モードへの自動切り替えを検証

- [ ] 実装: `src/app/session/SessionContent.tsx`更新（Green）
  - [ ] `useVoiceStream`オプションに新規コールバック追加
  - [ ] `handleImageProblemConfirmed`実装
    - [ ] 対話履歴に追加（robot発話）
    - [ ] `inputModeAtom = 'voice'`（音声モードに切り替え）
  - [ ] `handleImageRecognitionError`実装
    - [ ] エラーメッセージ表示
    - [ ] 画像モードを維持（リトライ可能）

- [ ] リファクタリング（Refactor）
  - [ ] ハンドラの整理
  - [ ] エラー処理の統一

### 6.5 UI条件分岐の整理

- [ ] テスト: `src/app/session/SessionContent.test.tsx`更新（Red）
  - [ ] セッション未作成 → InputModeSelector表示
  - [ ] 画像モード → CameraInterface表示
  - [ ] 音声モード（またはnull） → VoiceInterface表示
  - [ ] 各状態での他のコンポーネント表示を検証

- [ ] 実装: `src/app/session/SessionContent.tsx`更新（Green）
  - [ ] 条件分岐ロジックの整理
  - [ ] 不要なコードの削除

- [ ] リファクタリング（Refactor）
  - [ ] レンダリングロジックの最適化

## Phase 7: 統合テスト

### 7.1 ページレベル統合テスト

- [ ] テスト: `tests/pages/Session.test.tsx`更新（Red → Green）
  - [ ] セッション開始→画像モード選択→画像アップロード→認識→音声モード遷移の全フロー
  - [ ] エラーケース（画像認識エラー、WebSocketエラー）
  - [ ] モックの更新（`@/lib/api`に`VoiceWebSocketClient`の新規メソッド追加）

### 7.2 E2Eシナリオ（手動確認）

- [ ] シナリオ1: 音声モード選択フロー
  - [ ] InputModeSelectorで「声で伝える」選択
  - [ ] セッション作成
  - [ ] VoiceInterface表示
  - [ ] 音声入力可能

- [ ] シナリオ2: 画像モード選択フロー
  - [ ] InputModeSelectorで「写真で伝える」選択
  - [ ] CameraInterface表示
  - [ ] 画像キャプチャ/アップロード
  - [ ] 認識完了→音声モードに自動切り替え
  - [ ] VoiceInterface表示

- [ ] シナリオ3: エラーハンドリング
  - [ ] 画像認識エラー時のメッセージ表示
  - [ ] リトライ可能

## Phase 8: 品質チェック

### 8.1 Lint・Type Check

- [ ] `bun lint` → エラーなし
- [ ] `bun typecheck` → エラーなし

### 8.2 テスト実行

- [ ] `bunx vitest run` → 全テスト通過
- [ ] カバレッジ確認（80%以上）

### 8.3 アクセシビリティチェック

- [ ] InputModeSelectorのaria-label確認
- [ ] キーボードナビゲーション確認
- [ ] スクリーンリーダー対応確認

## Phase 9: ドキュメント更新

### 9.1 実装ステータス更新

- [ ] `docs/implementation-status.md`更新
  - [ ] Issue #154完了を記載
  - [ ] ステアリングディレクトリ一覧に追加

### 9.2 CLAUDE.md更新

- [ ] `CLAUDE.md`のDevelopment Context更新
  - [ ] 画像アップロード機能統合完了を記載

### 9.3 コンポーネントドキュメント

- [ ] `InputModeSelector`のJSDocコメント確認
- [ ] 使用例を含むコメント追加

## Phase 10: PR準備

### 10.1 コミット

- [ ] 段階的なコミット（TDDサイクルごと）
  - [ ] feat(frontend): 型定義拡張（WebSocket画像イベント）
  - [ ] feat(frontend): VoiceWebSocketClient画像イベント対応
  - [ ] feat(frontend): useVoiceStream画像イベント対応
  - [ ] feat(frontend): InputModeSelectorコンポーネント実装
  - [ ] feat(frontend): SessionContent画像アップロード統合
  - [ ] test(frontend): 統合テスト追加
  - [ ] docs: 実装ステータス更新

### 10.2 ローカルCI確認

- [ ] `bun lint && bun typecheck && bunx vitest run` → すべて成功

### 10.3 PR作成

- [ ] PR作成（Conventional Commits形式）
  - [ ] タイトル: `feat(frontend): セッションページへの画像アップロード機能統合 (Issue #154)`
  - [ ] 本文: requirements.mdの内容を参照
  - [ ] 関連Issue: #154をリンク

## 完了条件チェックリスト

- [ ] ✅ セッション開始時に入力モード選択UIが表示される
- [ ] ✅ 「写真で伝える」選択時、CameraInterfaceが表示される
- [ ] ✅ 画像アップロード完了時、`start_with_image`イベントが送信される
- [ ] ✅ `image_problem_confirmed`イベント受信時、問題文が反映される
- [ ] ✅ 画像認識完了後、自動的に音声モードに切り替わる
- [ ] ✅ 全テストが通る（`bun lint && bun typecheck && bun test`）
- [ ] ✅ テストカバレッジ80%以上
- [ ] ✅ アクセシビリティチェック通過
