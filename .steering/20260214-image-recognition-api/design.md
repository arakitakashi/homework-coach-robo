# Design - 画像認識APIエンドポイント

## アーキテクチャ概要

既存の dialogue.py パターンに準拠:
- APIRouter + Pydantic スキーマ + 依存性注入 + HTTPException

## ファイル構成

| ファイル | 操作 | 内容 |
|---------|------|------|
| `backend/app/schemas/vision.py` | 新規 | Pydantic スキーマ |
| `backend/app/api/v1/vision.py` | 新規 | エンドポイント |
| `backend/app/api/v1/router.py` | 編集 | ルーター登録 |
| `backend/tests/unit/schemas/test_vision.py` | 新規 | スキーマテスト |
| `backend/tests/unit/api/v1/test_vision.py` | 新規 | APIテスト |

## スキーマ設計

- `RecognitionType`: Enum (homework_problem, handwriting, diagram)
- `RecognizeImageRequest`: image (base64), recognition_type, expected_subject
- `ProblemDetail`: text, type, difficulty, expression
- `RecognizeImageResponse`: success, problems, confidence, needs_confirmation
- `RecognizeImageErrorResponse`: success, error_type, message, suggestions

## エンドポイント設計

- `POST /api/v1/vision/recognize`
- 依存性注入で `analyze_homework_image` をラップ（テストでモック可能）
- エラー: 400（バリデーション）、422（認識失敗）

## セキュリティ考慮事項

- 画像サイズ上限チェック（10MB）
- base64デコード失敗時の適切なエラーハンドリング
