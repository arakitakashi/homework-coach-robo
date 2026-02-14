# Requirements - WebSocket画像イベント（start_with_image）

## 背景・目的

画像認識結果を使ってセッションを開始するWebSocketイベントハンドラの実装。
フロントエンドから画像認識済みの問題データを受け取り、対話セッションを開始する。

Issue: #152

## 要求事項

### 機能要件

1. `start_with_image` WebSocketイベントハンドラの実装
2. 認識済み問題データ（テキスト、タイプ、画像URL）を受け取りセッション開始
3. `image_problem_confirmed` / `image_recognition_error` レスポンスイベント送信
4. 既存の音声ストリームWebSocketフローとの統合

### 非機能要件

- 既存のWebSocketイベント処理を破壊しない
- 型安全性を確保（Pydanticスキーマ定義）

### 制約条件

- 既存の `_client_to_agent` 関数にイベントタイプを追加する形で実装
- エージェントへのメッセージ送信は `service.send_text()` を使用
- コーチの応答は既存のADKイベントストリーム経由で返却

## 対象範囲

### In Scope

- `start_with_image` イベントの受信・処理
- `image_problem_confirmed` / `image_recognition_error` レスポンス送信
- スキーマ定義
- ユニットテスト

### Out of Scope

- 画像認識API自体（#150で実装済み）
- Cloud Storage統合（#151）
- フロントエンド側の実装

## 成功基準

- WebSocketで `start_with_image` イベントを受信し、問題テキストをエージェントに転送できる
- 成功時に `image_problem_confirmed` を返却する
- エラー時に `image_recognition_error` を返却する
- 全テストがパスする
