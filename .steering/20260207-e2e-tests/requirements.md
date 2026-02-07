# Requirements - E2Eテスト実装

## 背景・目的

WebSocket音声ストリーミング（Step 13）が完了し、フロントエンド・バックエンド間の3つの通信チャネル（REST、SSE、WebSocket）がすべて実装済み。これらの統合を検証するE2Eテストを実装する。

## 要求事項

### 機能要件

- Playwrightを使用した2層構造のE2Eテスト
  - Tier 1 (Functional): route interception でバックエンドをモック → UI動作・状態遷移検証
  - Tier 2 (Integration): Docker Compose + 実バックエンド → 実際の通信検証
- スモークテスト（ページロード、ナビゲーション）
- ファンクショナルテスト（キャラクター選択、セッション作成、テキスト対話、音声UI、セッション終了）
- 統合テスト（実バックエンドでのセッションCRUD、SSEストリーミング）

### 非機能要件

- 既存テスト（Vitest）に影響を与えない
- CI/CDパイプラインに統合可能

### 制約条件

- ヘッドレスブラウザでは実音声テスト不可 → UI状態遷移のみ
- Gemini APIは統合テストでもモック

## 対象範囲

### In Scope
- Playwright設定・フィクスチャ
- スモークテスト
- ファンクショナルテスト（route interception）
- バックエンドE2Eモード（モックサービス）
- 統合テスト（Docker Compose）
- CI/CDワークフロー

### Out of Scope
- 実Gemini API接続テスト
- 実音声入出力テスト
- 負荷テスト・パフォーマンステスト

## 成功基準
- 全E2Eテストがパスする
- 既存テスト（Vitest, pytest）に影響なし
- CI/CDで自動実行可能
