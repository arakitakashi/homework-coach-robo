# Requirements - セッションページへの画像アップロード機能統合

## 背景・目的

Issue #153で実装したCameraInterfaceコンポーネントをセッションページに組み込み、子供が音声だけでなく写真を使って宿題の問題を伝えられるようにする。Issue #152で実装されたWebSocketの`start_with_image`イベントとの連携を含む。

### 関連Issue
- Issue #150: 画像認識APIエンドポイント追加（完了）
- Issue #151: Cloud Storage統合（完了）
- Issue #152: WebSocket画像イベント追加（完了）
- Issue #153: カメラインターフェースコンポーネント実装（完了）
- **Issue #154**: セッションページへの画像アップロード機能統合（本作業）

## 要求事項

### 機能要件

#### 1. 入力モード選択UI

- セッション開始時に入力モードを選択できる
  - 🎤 「声で伝える」（音声入力モード）
  - 📷 「写真で伝える」（画像アップロードモード）
- モード選択後、適切なUIを表示
  - 音声モード: 既存のVoiceInterfaceコンポーネント
  - 画像モード: CameraInterfaceコンポーネント
- モード切り替えボタンを表示（セッション開始前のみ）

#### 2. CameraInterface統合

- SessionContentコンポーネントにCameraInterfaceを統合
- 画像認識完了後、自動的に音声モードに切り替え
- 認識された問題文をセッションコンテキストに反映

#### 3. WebSocket統合

- **送信イベント**:
  - `start_with_image`: 画像アップロード完了時に送信
    - `session_id`: セッションID
    - `image_url`: アップロード済み画像URL
    - `problem_text`: Gemini Visionで認識された問題文

- **受信イベント**:
  - `image_problem_confirmed`: 画像問題がサーバー側で確認された
    - `confirmed_text`: 最終確認された問題文
  - `image_recognition_error`: 画像認識エラー
    - `error`: エラーメッセージ

#### 4. 型定義拡張

- `types/session.ts`:
  - `WebSocketOutgoingMessage`に`start_with_image`イベント型を追加
- `types/phase2.ts`:
  - `WebSocketIncomingMessage`に画像関連イベント型を追加（すでに存在する場合は確認）

#### 5. 状態管理

- Jotai atomsで以下の状態を管理:
  - `inputModeAtom`: 'voice' | 'image' | null（選択前はnull）
  - `recognizedProblemTextAtom`: 画像から認識された問題文
- セッション開始時のみモード選択を表示
- 画像モード選択後、CameraInterfaceを表示
- 画像認識完了後、自動的に音声モードに切り替え

### 非機能要件

#### パフォーマンス

- 画像アップロード中もUIがブロックされない
- モード切り替えがスムーズ（300ms以内）

#### アクセシビリティ

- モード選択ボタンにaria-labelを設定
- キーボードナビゲーション対応
- スクリーンリーダー対応

#### ユーザビリティ

- 小学校低学年向けのシンプルなUI
- 大きなタッチターゲット（最小44×44px）
- わかりやすいアイコンとラベル

### 制約条件

- Next.js 16 App Router構成を維持
- 既存のVoiceInterfaceコンポーネントとの共存
- 既存のWebSocketハンドラとの互換性
- TDD原則に従ったテスト実装

## 対象範囲

### In Scope

- SessionContentコンポーネントへのCameraInterface統合
- 入力モード選択UIの実装
- WebSocketイベント（start_with_image, image_problem_confirmed, image_recognition_error）の送受信
- 型定義の拡張
- Jotai atoms追加
- 統合テスト

### Out of Scope

- CameraInterfaceコンポーネント自体の実装（Issue #153で完了）
- バックエンドのWebSocketハンドラ実装（Issue #152で完了）
- 画像認識API実装（Issue #150で完了）
- Cloud Storage統合（Issue #151で完了）

## 成功基準

1. ✅ セッション開始時に入力モード選択UIが表示される
2. ✅ 「写真で伝える」選択時、CameraInterfaceが表示される
3. ✅ 画像アップロード完了時、`start_with_image`イベントが送信される
4. ✅ `image_problem_confirmed`イベント受信時、問題文が反映される
5. ✅ 画像認識完了後、自動的に音声モードに切り替わる
6. ✅ 全テストが通る（`bun lint && bun typecheck && bun test`）
7. ✅ テストカバレッジ80%以上
8. ✅ アクセシビリティチェック通過
