# Requirements - SSE Client Implementation

## 背景・目的

フロントエンド（Next.js）からバックエンド（FastAPI）のSSEストリーミングエンドポイント（`/api/v1/dialogue/run`）に接続し、リアルタイムで対話レスポンスを受信するクライアントを実装する。

現在、フロントエンドにはUIコンポーネント、状態管理（Jotai）、カスタムフック（useVoiceRecorder、useAudioPlayer、useWebSocket）が実装されているが、バックエンドとの接続部分が未実装。

## 要求事項

### 機能要件

1. **SSEクライアント**
   - `POST /api/v1/dialogue/run` にリクエストを送信
   - SSEイベント（text, done, error）を受信・パース
   - イベントごとにコールバックを呼び出し

2. **対話フック（useDialogue）**
   - SSEクライアントをラップしたReactフック
   - Jotai atomsと連携して状態を更新
   - 対話履歴の追加、キャラクター状態の変更

3. **エラーハンドリング**
   - ネットワークエラーの検出と通知
   - サーバーエラー（error イベント）の処理
   - 接続タイムアウトの処理

### 非機能要件

1. **型安全性**: TypeScript strict mode準拠
2. **テスト可能性**: モック可能な設計
3. **再利用性**: 他のSSEエンドポイントにも適用可能

### 制約条件

- フロントエンド: Next.js 16 (App Router) + Bun + TypeScript
- 状態管理: Jotai
- テスト: Vitest + Testing Library
- リンター: Biome

## 対象範囲

### In Scope

- SSEクライアント実装（`lib/api/dialogueClient.ts`）
- 対話フック実装（`lib/hooks/useDialogue.ts`）
- SSEイベント型定義
- ユニットテスト

### Out of Scope

- セッション作成API（別タスクで実装）
- 音声送信機能（録音データの送信）
- 追加キャラクターの実装
- 音声再生との統合

## 成功基準

1. SSEクライアントが3種類のイベント（text, done, error）を正しく処理する
2. useDialogueフックがJotai atomsと正しく連携する
3. テストカバレッジ80%以上
4. `bun lint && bun typecheck && bun test` がすべてパス
