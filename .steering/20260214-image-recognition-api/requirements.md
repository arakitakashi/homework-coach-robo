# Requirements - 画像認識APIエンドポイント（Issue #150）

## 背景・目的

宿題プリントの画像をアップロードして問題を認識する機能のバックエンドAPI層を実装する。
既存の `analyze_homework_image()` 関数（Gemini Vision API）は Phase 2a で実装済みだが、
HTTPエンドポイントとして公開されていないため、フロントエンドから呼び出せない。

## 要求事項

### 機能要件

- base64エンコードされた画像をPOSTで受け取り、問題を認識するエンドポイント
- 認識タイプ（宿題問題/手書き/図形）の指定が可能
- 信頼度（confidence）付きのレスポンスを返す
- 低信頼度の場合は確認フラグを付与

### 非機能要件

- 既存の dialogue.py / dialogue_runner.py のパターンに準拠
- TDDで実装（テストカバレッジ80%以上）
- 画像サイズ上限 10MB

### 制約条件

- 既存の `analyze_homework_image()` を再利用（重複実装を避ける）
- 依存性注入でVision APIをモック可能にする

## 対象範囲

### In Scope

- Pydantic スキーマ（リクエスト/レスポンス）
- POST /api/v1/vision/recognize エンドポイント
- ルーター登録
- ユニットテスト（スキーマ + API）

### Out of Scope

- フロントエンド実装
- 画像前処理・圧縮
- 認識結果のキャッシュ

## 成功基準

- 全テストがパスする
- ruff, mypy エラーなし
- エンドポイントが正常にルーティングされる
