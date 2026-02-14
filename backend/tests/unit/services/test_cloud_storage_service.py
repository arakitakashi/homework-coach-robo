"""CloudStorageService のテスト"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.services.storage_service import (
    CloudStorageService,
    ImageTooLargeError,
    InvalidImageError,
    UploadFailedError,
)


@pytest.fixture
def mock_storage_client():
    """モックされたCloud Storageクライアント"""
    with patch("google.cloud.storage.Client") as mock_client_class:
        # モッククライアント、バケット、blobの設定
        client = MagicMock()
        bucket = MagicMock()
        blob = MagicMock()

        # upload_from_string を MagicMock に設定
        blob.upload_from_string = MagicMock()
        blob.generate_signed_url = MagicMock(
            return_value="https://storage.googleapis.com/bucket/signed-url"
        )
        blob.public_url = "https://storage.googleapis.com/bucket/path"

        bucket.blob = MagicMock(return_value=blob)
        client.bucket = MagicMock(return_value=bucket)
        mock_client_class.return_value = client

        yield {
            "client_class": mock_client_class,
            "client": client,
            "bucket": bucket,
            "blob": blob,
        }


class TestCloudStorageService:
    """CloudStorageService のテスト"""

    def test_init_with_bucket_name(self) -> None:
        """正常系: バケット名を指定して初期化"""
        # Act
        with patch("google.cloud.storage.Client"):
            service = CloudStorageService(bucket_name="test-bucket")

        # Assert
        assert service.bucket_name == "test-bucket"

    def test_init_with_project_id(self) -> None:
        """正常系: プロジェクトIDを指定して初期化"""
        # Act
        with patch("google.cloud.storage.Client"):
            service = CloudStorageService(bucket_name="test-bucket", project_id="test-project")

        # Assert
        assert service.bucket_name == "test-bucket"
        assert service.project_id == "test-project"

    @pytest.mark.asyncio
    async def test_upload_image_success(self, mock_storage_client: dict) -> None:
        """正常系: 画像アップロード成功"""
        # Arrange
        service = CloudStorageService(bucket_name="test-bucket")
        session_id = "session-123"
        image_data = b"\xff\xd8\xff\xe0" + b"\x00" * 1000  # 有効なJPEG
        filename = "test.jpg"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        assert result.storage_path.startswith(f"sessions/{session_id}/images/")
        assert result.storage_path.endswith(".jpg")
        assert result.signed_url.startswith("https://storage.googleapis.com/")
        assert result.file_size == len(image_data)
        assert result.mime_type == "image/jpeg"

        # Cloud Storage APIが呼び出されたことを確認
        blob = mock_storage_client["blob"]
        blob.upload_from_string.assert_called_once()
        blob.generate_signed_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_image_invalid_type(self, mock_storage_client: dict) -> None:
        """異常系: 不正なファイルタイプ"""
        # Arrange
        service = CloudStorageService(bucket_name="test-bucket")
        session_id = "session-123"
        image_data = b"Not an image"
        filename = "test.txt"

        # Act & Assert
        with pytest.raises(InvalidImageError):
            await service.upload_image(session_id, image_data, filename)

        # upload_from_string が呼ばれていないことを確認
        blob = mock_storage_client["blob"]
        blob.upload_from_string.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_image_too_large(self) -> None:
        """異常系: ファイルサイズ超過"""
        # Arrange
        with patch("google.cloud.storage.Client"):
            service = CloudStorageService(bucket_name="test-bucket")
        session_id = "session-123"
        # 11MB のJPEG画像
        image_data = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)
        filename = "large.jpg"

        # Act & Assert
        with pytest.raises(ImageTooLargeError):
            await service.upload_image(session_id, image_data, filename)

    @pytest.mark.asyncio
    async def test_upload_image_upload_fails(self, mock_storage_client: dict) -> None:
        """異常系: アップロード失敗"""
        # Arrange
        service = CloudStorageService(bucket_name="test-bucket")
        session_id = "session-123"
        image_data = b"\xff\xd8\xff\xe0" + b"\x00" * 1000
        filename = "test.jpg"

        # upload_from_string がエラーを発生させる
        blob = mock_storage_client["blob"]
        blob.upload_from_string.side_effect = Exception("Network error")

        # Act & Assert
        with pytest.raises(UploadFailedError) as exc_info:
            await service.upload_image(session_id, image_data, filename)

        assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_signed_url(self, mock_storage_client: dict) -> None:
        """正常系: Signed URL生成"""
        # Arrange
        service = CloudStorageService(bucket_name="test-bucket")
        storage_path = "sessions/session-123/images/test.jpg"

        # Act
        url = await service.generate_signed_url(storage_path)

        # Assert
        assert url.startswith("https://storage.googleapis.com/")
        blob = mock_storage_client["blob"]
        blob.generate_signed_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_signed_url_custom_expiration(self, mock_storage_client: dict) -> None:
        """正常系: カスタム有効期限でのSigned URL生成"""
        # Arrange
        service = CloudStorageService(bucket_name="test-bucket")
        storage_path = "sessions/session-123/images/test.jpg"
        expires_in = timedelta(hours=2)

        # Act
        url = await service.generate_signed_url(storage_path, expires_in)

        # Assert
        assert isinstance(url, str)
        blob = mock_storage_client["blob"]

        # generate_signed_url の呼び出しを確認
        call_args = blob.generate_signed_url.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_validate_image_jpeg(self) -> None:
        """正常系: JPEG画像の検証"""
        # Arrange
        with patch("google.cloud.storage.Client"):
            service = CloudStorageService(bucket_name="test-bucket")
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100

        # Act
        mime_type, file_size = await service.validate_image(image_data)

        # Assert
        assert mime_type == "image/jpeg"
        assert file_size == len(image_data)

    @pytest.mark.asyncio
    async def test_validate_image_png(self) -> None:
        """正常系: PNG画像の検証"""
        # Arrange
        with patch("google.cloud.storage.Client"):
            service = CloudStorageService(bucket_name="test-bucket")
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        # Act
        mime_type, file_size = await service.validate_image(image_data)

        # Assert
        assert mime_type == "image/png"
        assert file_size == len(image_data)

    @pytest.mark.asyncio
    async def test_validate_image_webp(self) -> None:
        """正常系: WebP画像の検証"""
        # Arrange
        with patch("google.cloud.storage.Client"):
            service = CloudStorageService(bucket_name="test-bucket")
        image_data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100

        # Act
        mime_type, file_size = await service.validate_image(image_data)

        # Assert
        assert mime_type == "image/webp"
        assert file_size == len(image_data)

    @pytest.mark.asyncio
    async def test_storage_path_generation(
        self,
        mock_storage_client: dict,  # noqa: ARG002 - フィクスチャのセットアップに使用
    ) -> None:
        """正常系: ストレージパスの生成形式が正しい"""
        # Arrange
        service = CloudStorageService(bucket_name="test-bucket")
        session_id = "session-abc123"
        image_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        filename = "homework.jpg"

        # Act
        result = await service.upload_image(session_id, image_data, filename)

        # Assert
        # パス形式: sessions/{session_id}/images/{timestamp}_{uuid}.{ext}
        path_parts = result.storage_path.split("/")
        assert len(path_parts) == 4
        assert path_parts[0] == "sessions"
        assert path_parts[1] == session_id
        assert path_parts[2] == "images"
        assert "_" in path_parts[3]  # timestamp_uuid 形式
        assert path_parts[3].endswith(".jpg")
