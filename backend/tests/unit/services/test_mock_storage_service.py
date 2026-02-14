"""MockStorageService のテスト"""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.storage_service import (
    ImageTooLargeError,
    InvalidImageError,
    MockStorageService,
)


class TestMockStorageService:
    """MockStorageService のテスト"""

    @pytest.mark.asyncio
    async def test_upload_valid_jpeg(self) -> None:
        """正常系: JPEG画像のアップロード"""
        # Arrange
        service = MockStorageService()
        session_id = "session-123"
        # 小さな有効なJPEG画像データ（magic number: FF D8 FF）
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
        filename = "test.jpg"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        assert result.storage_path.startswith(f"sessions/{session_id}/images/")
        assert result.storage_path.endswith(".jpg")
        assert result.signed_url.startswith("https://storage.googleapis.com/")
        assert result.file_size == len(image_data)
        assert result.mime_type == "image/jpeg"
        assert isinstance(result.uploaded_at, datetime)
        assert isinstance(result.signed_url_expires_at, datetime)

    @pytest.mark.asyncio
    async def test_upload_valid_png(self) -> None:
        """正常系: PNG画像のアップロード"""
        # Arrange
        service = MockStorageService()
        session_id = "session-456"
        # 小さな有効なPNG画像データ（magic number: 89 50 4E 47）
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        filename = "test.png"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        assert result.storage_path.endswith(".png")
        assert result.mime_type == "image/png"

    @pytest.mark.asyncio
    async def test_upload_valid_webp(self) -> None:
        """正常系: WebP画像のアップロード"""
        # Arrange
        service = MockStorageService()
        session_id = "session-789"
        # 小さな有効なWebP画像データ（magic number: RIFF...WEBP）
        image_data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
        filename = "test.webp"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        assert result.storage_path.endswith(".webp")
        assert result.mime_type == "image/webp"

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self) -> None:
        """異常系: 不正なファイルタイプの拒否"""
        # Arrange
        service = MockStorageService()
        session_id = "session-123"
        # テキストファイル（不正）
        image_data = b"This is not an image"
        filename = "test.txt"

        # Act & Assert
        with pytest.raises(InvalidImageError) as exc_info:
            await service.upload_image(session_id, image_data, filename)

        assert "not supported" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self) -> None:
        """異常系: ファイルサイズ超過の拒否"""
        # Arrange
        service = MockStorageService()
        session_id = "session-123"
        # 11MB の画像データ（10MBを超える）
        large_image = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)
        filename = "large.jpg"

        # Act & Assert
        with pytest.raises(ImageTooLargeError) as exc_info:
            await service.upload_image(session_id, image_data=large_image, filename=filename)

        assert "10" in str(exc_info.value) or "large" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_signed_url(self) -> None:
        """正常系: Signed URL の生成"""
        # Arrange
        service = MockStorageService()
        storage_path = "sessions/session-123/images/test.jpg"

        # Act
        url = await service.generate_signed_url(storage_path)

        # Assert
        assert url.startswith("https://storage.googleapis.com/")
        assert storage_path in url or "mock" in url.lower()

    @pytest.mark.asyncio
    async def test_generate_signed_url_with_custom_expiration(self) -> None:
        """正常系: カスタム有効期限でのSigned URL生成"""
        # Arrange
        service = MockStorageService()
        storage_path = "sessions/session-123/images/test.jpg"
        expires_in = timedelta(hours=2)

        # Act
        url = await service.generate_signed_url(storage_path, expires_in)

        # Assert
        assert isinstance(url, str)
        assert len(url) > 0

    @pytest.mark.asyncio
    async def test_validate_jpeg_image(self) -> None:
        """正常系: JPEG画像の検証"""
        # Arrange
        service = MockStorageService()
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100

        # Act
        mime_type, file_size = await service.validate_image(image_data)

        # Assert
        assert mime_type == "image/jpeg"
        assert file_size == len(image_data)

    @pytest.mark.asyncio
    async def test_validate_png_image(self) -> None:
        """正常系: PNG画像の検証"""
        # Arrange
        service = MockStorageService()
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        # Act
        mime_type, file_size = await service.validate_image(image_data)

        # Assert
        assert mime_type == "image/png"
        assert file_size == len(image_data)

    @pytest.mark.asyncio
    async def test_validate_webp_image(self) -> None:
        """正常系: WebP画像の検証"""
        # Arrange
        service = MockStorageService()
        image_data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100

        # Act
        mime_type, file_size = await service.validate_image(image_data)

        # Assert
        assert mime_type == "image/webp"
        assert file_size == len(image_data)

    @pytest.mark.asyncio
    async def test_validate_invalid_image(self) -> None:
        """異常系: 不正な画像の検証失敗"""
        # Arrange
        service = MockStorageService()
        invalid_data = b"This is not an image"

        # Act & Assert
        with pytest.raises(InvalidImageError):
            await service.validate_image(invalid_data)

    @pytest.mark.asyncio
    async def test_validate_image_too_large(self) -> None:
        """異常系: サイズ超過画像の検証失敗"""
        # Arrange
        service = MockStorageService()
        # 11MB の画像
        large_image = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)

        # Act & Assert
        with pytest.raises(ImageTooLargeError):
            await service.validate_image(large_image, max_size_mb=10)

    @pytest.mark.asyncio
    async def test_signed_url_expiration_time(self) -> None:
        """正常系: Signed URLの有効期限が正しく設定される"""
        # Arrange
        service = MockStorageService()
        session_id = "session-123"
        image_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        filename = "test.jpg"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        # デフォルトは1時間後に期限切れ
        now = datetime.now(timezone.utc)
        expected_expiry = now + timedelta(hours=1)

        # 誤差を考慮して±5分以内であることを確認
        time_diff = abs((result.signed_url_expires_at - expected_expiry).total_seconds())
        assert time_diff < 300, f"Expiry time difference: {time_diff}s"

    @pytest.mark.asyncio
    async def test_storage_path_format(self) -> None:
        """正常系: ストレージパスの形式が正しい"""
        # Arrange
        service = MockStorageService()
        session_id = "session-abc123"
        image_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        filename = "homework.jpg"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        # パス形式: sessions/{session_id}/images/{timestamp}_{uuid}.{ext}
        path_parts = result.storage_path.split("/")
        assert path_parts[0] == "sessions"
        assert path_parts[1] == session_id
        assert path_parts[2] == "images"
        assert len(path_parts) == 4
        assert "_" in path_parts[3]  # timestamp_uuid 形式
