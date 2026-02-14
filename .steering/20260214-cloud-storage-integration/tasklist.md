# Task List - Cloud Storage画像保存統合

## Phase 1: 環境セットアップ

- [ ] 依存パッケージの追加（google-cloud-storage, python-magic, Pillow）
- [ ] 環境変数の設定（GCS_BUCKET_NAME, GCS_PROJECT_ID）
- [ ] スキルの参照（/tdd, /fastapi, /security-review）

## Phase 2: スキーマ定義（TDD準備）

- [ ] `backend/app/schemas/storage.py` のテスト作成
- [ ] `UploadedImageSchema` の実装
- [ ] `ImageUploadRequest` スキーマの実装

## Phase 3: StorageService インターフェース（TDD）

### 3.1 テスト実装（Red）

- [ ] `test_storage_service.py` の作成
- [ ] `test_upload_valid_jpeg` テスト作成
- [ ] `test_upload_valid_png` テスト作成
- [ ] `test_upload_valid_webp` テスト作成
- [ ] `test_reject_invalid_file_type` テスト作成
- [ ] `test_reject_too_large_file` テスト作成

### 3.2 インターフェース実装（Green）

- [ ] `StorageService` Protocol 定義
- [ ] `UploadedImage` dataclass 定義
- [ ] カスタム例外クラス定義（InvalidImageError, ImageTooLargeError, UploadFailedError）

### 3.3 リファクタリング（Refactor）

- [ ] 型ヒントの完全性確認
- [ ] ドキュメント文字列の追加

## Phase 4: MockStorageService 実装（TDD）

### 4.1 テスト実装（Red）

- [ ] `test_mock_storage_upload` テスト作成
- [ ] `test_mock_storage_signed_url` テスト作成

### 4.2 モック実装（Green）

- [ ] `MockStorageService` クラス実装
- [ ] `upload_image` メソッド実装（モック）
- [ ] `generate_signed_url` メソッド実装（モック）
- [ ] `validate_image` メソッド実装（モック）

### 4.3 リファクタリング（Refactor）

- [ ] モックデータの整理
- [ ] テストヘルパー関数の作成

## Phase 5: ファイル検証ロジック（TDD）

### 5.1 テスト実装（Red）

- [ ] `test_validate_jpeg` テスト作成
- [ ] `test_validate_png` テスト作成
- [ ] `test_validate_webp` テスト作成
- [ ] `test_reject_invalid_magic_number` テスト作成
- [ ] `test_reject_too_large_file` テスト作成
- [ ] `test_get_file_size` テスト作成

### 5.2 検証ロジック実装（Green）

- [ ] `validate_image` メソッド実装
- [ ] magic number チェック（python-magic使用）
- [ ] ファイルサイズチェック
- [ ] MIME type 判定

### 5.3 リファクタリング（Refactor）

- [ ] 定数の整理（MAX_FILE_SIZE_MB, ALLOWED_MIME_TYPES）
- [ ] エラーメッセージの改善

## Phase 6: CloudStorageService 実装（TDD）

### 6.1 テスト実装（Red）

- [ ] `test_cloud_storage_init` テスト作成
- [ ] `test_generate_storage_path` テスト作成
- [ ] `test_upload_to_gcs` テスト作成（モック使用）
- [ ] `test_generate_signed_url` テスト作成（モック使用）
- [ ] `test_upload_image_integration` テスト作成

### 6.2 CloudStorageService 実装（Green）

- [ ] `CloudStorageService.__init__` 実装
- [ ] `_generate_storage_path` メソッド実装
- [ ] `upload_image` メソッド実装
- [ ] `generate_signed_url` メソッド実装
- [ ] リトライロジック追加

### 6.3 リファクタリング（Refactor）

- [ ] プライベートメソッドの整理
- [ ] ロギングの追加
- [ ] エラーハンドリングの改善

## Phase 7: Firestore 統合（TDD）

### 7.1 テスト実装（Red）

- [ ] `test_save_image_metadata_to_firestore` テスト作成
- [ ] `test_get_session_images` テスト作成

### 7.2 Firestore 統合実装（Green）

- [ ] セッションドキュメントへの `uploaded_images` フィールド追加
- [ ] 画像メタデータの保存ロジック実装
- [ ] 画像一覧取得ロジック実装

### 7.3 リファクタリング（Refactor）

- [ ] スキーマ変換ロジックの整理
- [ ] エラーハンドリング

## Phase 8: 依存性注入（DI）設定

- [ ] `backend/app/core/config.py` に環境変数追加
- [ ] `backend/app/core/dependencies.py` に `get_storage_service` 追加
- [ ] テスト用 DI オーバーライドの設定

## Phase 9: 統合テスト

- [ ] エンドツーエンドテストの作成（モック使用）
- [ ] 正常系フロー全体のテスト
- [ ] 異常系フロー全体のテスト

## Phase 10: 品質チェック

### 10.1 自動チェック

- [ ] `/quality-check` スキル実行（mypy/ruff/pytest の一括実行）
- [ ] テストカバレッジ確認（80%以上）

### 10.2 手動チェック

- [ ] セキュリティレビュー（`/security-review` スキル使用）
- [ ] セルフコードレビュー
- [ ] ドキュメント文字列の確認

### 10.3 修正

- [ ] 品質チェックで見つかった問題の修正
- [ ] 再度品質チェック実行

## Phase 11: インフラストラクチャ更新（必要な場合）

- [ ] IAM 権限の確認
- [ ] `infrastructure/terraform/modules/iam/main.tf` の更新（必要な場合）
- [ ] `storage.objectCreator` ロールの追加確認

## Phase 12: ドキュメント更新

- [ ] `/update-docs` スキル実行（CLAUDE.md, docs/implementation-status.md の更新）
- [ ] `CLAUDE.md` の Development Context 更新確認
- [ ] `docs/implementation-status.md` の完了済み機能一覧更新確認
- [ ] `docs/implementation-status.md` のステアリングディレクトリ一覧更新確認

## Phase 13: PR作成

- [ ] `/create-pr` スキル実行（PR作成をサブエージェントに委譲）
- [ ] PR本文の確認
- [ ] Issue #151 へのリンク確認

## 実装メモ

### 重要な注意点

1. **TDD原則の厳守**: すべてのテストを先に書く（Red-Green-Refactor）
2. **セキュリティ優先**: 入力検証を徹底する
3. **非同期処理**: すべての Cloud Storage 操作は async/await
4. **エラーハンドリング**: 明確なエラーメッセージを提供
5. **型ヒント**: すべての関数に型ヒントを付与

### テストデータ

テスト用の画像データは以下のように準備:

```python
# テストヘルパー
def create_test_jpeg() -> bytes:
    """テスト用のJPEG画像を生成"""
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()
```

### モックパターン

Cloud Storage のモックには `unittest.mock` を使用:

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_gcs_client():
    client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    blob.upload_from_string = AsyncMock()
    blob.generate_signed_url = MagicMock(return_value="https://example.com/signed")
    bucket.blob = MagicMock(return_value=blob)
    client.bucket = MagicMock(return_value=bucket)
    return client
```
