"""ストレージスキーマのテスト"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.storage import ImageUploadRequest, UploadedImageSchema


class TestImageUploadRequest:
    """ImageUploadRequest スキーマのテスト"""

    def test_valid_jpeg_upload(self) -> None:
        """正常系: 有効なJPEG画像アップロードリクエスト"""
        # Arrange
        data = {
            "session_id": "session-123",
            "image_data": "base64encodeddata==",
            "filename": "homework.jpg",
        }

        # Act
        request = ImageUploadRequest(**data)

        # Assert
        assert request.session_id == "session-123"
        assert request.image_data == "base64encodeddata=="
        assert request.filename == "homework.jpg"

    def test_valid_png_upload(self) -> None:
        """正常系: 有効なPNG画像アップロードリクエスト"""
        # Arrange
        data = {
            "session_id": "session-456",
            "image_data": "pngbase64data==",
            "filename": "problem.png",
        }

        # Act
        request = ImageUploadRequest(**data)

        # Assert
        assert request.session_id == "session-456"
        assert request.filename == "problem.png"

    def test_valid_webp_upload(self) -> None:
        """正常系: 有効なWebP画像アップロードリクエスト"""
        # Arrange
        data = {
            "session_id": "session-789",
            "image_data": "webpbase64data==",
            "filename": "test.webp",
        }

        # Act
        request = ImageUploadRequest(**data)

        # Assert
        assert request.filename == "test.webp"

    def test_missing_session_id(self) -> None:
        """異常系: session_idが欠落している"""
        # Arrange
        data = {
            "image_data": "base64data==",
            "filename": "test.jpg",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ImageUploadRequest(**data)

        assert "session_id" in str(exc_info.value)

    def test_missing_image_data(self) -> None:
        """異常系: image_dataが欠落している"""
        # Arrange
        data = {
            "session_id": "session-123",
            "filename": "test.jpg",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ImageUploadRequest(**data)

        assert "image_data" in str(exc_info.value)

    def test_missing_filename(self) -> None:
        """異常系: filenameが欠落している"""
        # Arrange
        data = {
            "session_id": "session-123",
            "image_data": "base64data==",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ImageUploadRequest(**data)

        assert "filename" in str(exc_info.value)

    def test_empty_session_id(self) -> None:
        """異常系: session_idが空文字列"""
        # Arrange
        data = {
            "session_id": "",
            "image_data": "base64data==",
            "filename": "test.jpg",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ImageUploadRequest(**data)

        assert "session_id" in str(exc_info.value)


class TestUploadedImageSchema:
    """UploadedImageSchema スキーマのテスト"""

    def test_valid_uploaded_image(self) -> None:
        """正常系: 有効なアップロード済み画像メタデータ"""
        # Arrange
        now = datetime.now(timezone.utc)
        expires_at = datetime(2026, 2, 14, 13, 0, 0, tzinfo=timezone.utc)

        data = {
            "storage_path": "sessions/session-123/images/20260214T120000_uuid.jpg",
            "signed_url": "https://storage.googleapis.com/bucket/signed-url",
            "signed_url_expires_at": expires_at,
            "uploaded_at": now,
            "file_size": 1024000,  # 1MB
            "mime_type": "image/jpeg",
        }

        # Act
        schema = UploadedImageSchema(**data)

        # Assert
        assert schema.storage_path == data["storage_path"]
        assert schema.signed_url == data["signed_url"]
        assert schema.signed_url_expires_at == expires_at
        assert schema.uploaded_at == now
        assert schema.file_size == 1024000
        assert schema.mime_type == "image/jpeg"
        assert schema.width is None
        assert schema.height is None

    def test_valid_uploaded_image_with_dimensions(self) -> None:
        """正常系: 画像サイズ情報を含むアップロード済み画像"""
        # Arrange
        now = datetime.now(timezone.utc)
        expires_at = datetime(2026, 2, 14, 13, 0, 0, tzinfo=timezone.utc)

        data = {
            "storage_path": "sessions/session-123/images/test.jpg",
            "signed_url": "https://example.com/signed",
            "signed_url_expires_at": expires_at,
            "uploaded_at": now,
            "file_size": 2048000,  # 2MB
            "mime_type": "image/png",
            "width": 1920,
            "height": 1080,
        }

        # Act
        schema = UploadedImageSchema(**data)

        # Assert
        assert schema.width == 1920
        assert schema.height == 1080

    def test_missing_required_fields(self) -> None:
        """異常系: 必須フィールドが欠落している"""
        # Arrange
        data = {
            "storage_path": "path/to/image.jpg",
            # 他の必須フィールドが欠落
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UploadedImageSchema(**data)

        errors = exc_info.value.errors()
        required_fields = {
            "signed_url",
            "signed_url_expires_at",
            "uploaded_at",
            "file_size",
            "mime_type",
        }

        error_fields = {error["loc"][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_negative_file_size(self) -> None:
        """異常系: ファイルサイズが負の値"""
        # Arrange
        now = datetime.now(timezone.utc)
        expires_at = datetime(2026, 2, 14, 13, 0, 0, tzinfo=timezone.utc)

        data = {
            "storage_path": "path/to/image.jpg",
            "signed_url": "https://example.com/signed",
            "signed_url_expires_at": expires_at,
            "uploaded_at": now,
            "file_size": -1000,  # 負の値
            "mime_type": "image/jpeg",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UploadedImageSchema(**data)

        assert "file_size" in str(exc_info.value)

    def test_zero_file_size(self) -> None:
        """異常系: ファイルサイズがゼロ"""
        # Arrange
        now = datetime.now(timezone.utc)
        expires_at = datetime(2026, 2, 14, 13, 0, 0, tzinfo=timezone.utc)

        data = {
            "storage_path": "path/to/image.jpg",
            "signed_url": "https://example.com/signed",
            "signed_url_expires_at": expires_at,
            "uploaded_at": now,
            "file_size": 0,  # ゼロ
            "mime_type": "image/jpeg",
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UploadedImageSchema(**data)

        assert "file_size" in str(exc_info.value)

    def test_negative_width(self) -> None:
        """異常系: 幅が負の値"""
        # Arrange
        now = datetime.now(timezone.utc)
        expires_at = datetime(2026, 2, 14, 13, 0, 0, tzinfo=timezone.utc)

        data = {
            "storage_path": "path/to/image.jpg",
            "signed_url": "https://example.com/signed",
            "signed_url_expires_at": expires_at,
            "uploaded_at": now,
            "file_size": 1000,
            "mime_type": "image/jpeg",
            "width": -100,  # 負の値
            "height": 100,
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UploadedImageSchema(**data)

        assert "width" in str(exc_info.value)

    def test_negative_height(self) -> None:
        """異常系: 高さが負の値"""
        # Arrange
        now = datetime.now(timezone.utc)
        expires_at = datetime(2026, 2, 14, 13, 0, 0, tzinfo=timezone.utc)

        data = {
            "storage_path": "path/to/image.jpg",
            "signed_url": "https://example.com/signed",
            "signed_url_expires_at": expires_at,
            "uploaded_at": now,
            "file_size": 1000,
            "mime_type": "image/jpeg",
            "width": 100,
            "height": -100,  # 負の値
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UploadedImageSchema(**data)

        assert "height" in str(exc_info.value)
