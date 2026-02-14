# Requirements - InputModeSelectorのUI統合

## 背景・目的

Issue #154の基盤実装（PR #159）により、以下が完了しました：
- InputModeSelectorコンポーネントの作成
- useVoiceStreamフックの画像イベント対応
- SessionContentの画像イベントハンドラ統合

次のステップとして、SessionContentにInputModeSelectorを統合し、セッション開始時に入力モード（音声 or 画像）を選択できるようにします。

## 要求事項

### 機能要件

1. **セッション開始時のモード選択**
   - セッション開始時（初回表示時）にInputModeSelectorを表示
   - ユーザーが「音声」または「画像」を選択
   - モード選択後、適切なインターフェースを表示

2. **音声モード選択時**
   - InputModeSelectorを非表示
   - VoiceInterfaceを表示
   - WebSocket接続を開始
   - 既存の音声入力フローに移行

3. **画像モード選択時**
   - InputModeSelectorを非表示
   - 将来実装予定のCameraInterfaceへの準備（現時点ではプレースホルダー）
   - モード選択状態を保持

### 非機能要件

1. **テストカバレッジ**
   - 新規実装部分のカバレッジ80%以上維持
   - TDD原則に従った実装

2. **アクセシビリティ**
   - 小学校低学年でも使いやすいUI
   - キーボードナビゲーション対応

3. **後方互換性**
   - 既存のSessionContentの動作に影響を与えない
   - 既存の27テストすべてパス

### 制約条件

1. **スコープ制限**
   - CameraInterfaceの実装は含まない（別Issue/PR）
   - 画像モード選択後のフローは最小限の実装（プレースホルダー）

2. **技術制約**
   - Next.js 16 App Router
   - Jotai状態管理
   - Vitest + Testing Library

## 対象範囲

### In Scope

- InputModeSelectorのSessionContent統合
- モード選択状態の管理（Jotai atom）
- モード選択に応じたUI切り替えロジック
- VoiceInterfaceの条件付き表示
- テストケースの追加

### Out of Scope

- CameraInterfaceの実装
- 画像モードから音声モードへの切り替え機能
- モード選択のパーシステンス（LocalStorageなど）

## 成功基準

1. セッション開始時にInputModeSelectorが表示される
2. 音声モード選択後、VoiceInterfaceが表示され、既存フローが動作する
3. 画像モード選択後、プレースホルダーメッセージが表示される
4. 全テストがパスする（27 + 新規テスト）
5. リンター・型チェックがパスする
