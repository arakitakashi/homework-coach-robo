# Requirements - CameraInterface (Issue #153)

## 背景・目的

宿題プリントの画像をカメラ撮影またはファイルアップロードで取得し、バックエンドの画像認識APIで問題文を抽出するフロントエンドUIコンポーネント。

## 要求事項

### 機能要件
- カメラ撮影による画像キャプチャ
- ファイルアップロードによる画像取得（フォールバック）
- 画像認識APIによる問題文抽出
- 6状態の画面遷移（initial→active→preview→processing→recognized→error）

### 非機能要件
- 小学校低学年向けUI（大きなタッチターゲット、やさしい日本語）
- アクセシビリティ（aria属性、セマンティックHTML）

### 制約条件
- 既存の ImageAnalysisResult 型を再利用
- SessionClient と同じパターンで VisionClient を作成

## 対象範囲

### In Scope
- CameraInterface コンポーネント
- useCameraCapture フック
- VisionClient APIクライアント
- 型定義、Jotai atoms

### Out of Scope
- SessionContent への統合（別Issue）
- バックエンドAPI実装

## 成功基準
- 全テスト通過、lint/typecheck エラーなし
