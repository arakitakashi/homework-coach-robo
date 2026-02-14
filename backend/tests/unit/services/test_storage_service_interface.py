"""StorageService インターフェースのテスト"""

import pytest

from app.services.storage_service import (
    ImageTooLargeError,
    InvalidImageError,
    StorageError,
    UploadFailedError,
)


class TestStorageExceptions:
    """ストレージ関連の例外のテスト"""

    def test_storage_error_base_exception(self) -> None:
        """StorageError は Exception を継承している"""
        # Act
        error = StorageError("Base storage error")

        # Assert
        assert isinstance(error, Exception)
        assert str(error) == "Base storage error"

    def test_invalid_image_error_inherits_storage_error(self) -> None:
        """InvalidImageError は StorageError を継承している"""
        # Act
        error = InvalidImageError("Invalid file type")

        # Assert
        assert isinstance(error, StorageError)
        assert isinstance(error, Exception)
        assert str(error) == "Invalid file type"

    def test_image_too_large_error_inherits_storage_error(self) -> None:
        """ImageTooLargeError は StorageError を継承している"""
        # Act
        error = ImageTooLargeError("File too large")

        # Assert
        assert isinstance(error, StorageError)
        assert str(error) == "File too large"

    def test_upload_failed_error_inherits_storage_error(self) -> None:
        """UploadFailedError は StorageError を継承している"""
        # Act
        error = UploadFailedError("Upload failed")

        # Assert
        assert isinstance(error, StorageError)
        assert str(error) == "Upload failed"

    def test_can_raise_and_catch_invalid_image_error(self) -> None:
        """InvalidImageError を raise して catch できる"""
        # Act & Assert
        with pytest.raises(InvalidImageError) as exc_info:
            raise InvalidImageError("Not a valid image")

        assert "Not a valid image" in str(exc_info.value)

    def test_can_raise_and_catch_image_too_large_error(self) -> None:
        """ImageTooLargeError を raise して catch できる"""
        # Act & Assert
        with pytest.raises(ImageTooLargeError) as exc_info:
            raise ImageTooLargeError("Image size exceeds limit")

        assert "Image size exceeds limit" in str(exc_info.value)

    def test_can_raise_and_catch_upload_failed_error(self) -> None:
        """UploadFailedError を raise して catch できる"""
        # Act & Assert
        with pytest.raises(UploadFailedError) as exc_info:
            raise UploadFailedError("Network error during upload")

        assert "Network error during upload" in str(exc_info.value)

    def test_can_catch_specific_error_as_storage_error(self) -> None:
        """個別の例外を StorageError として catch できる"""
        # Act & Assert
        with pytest.raises(StorageError):
            raise InvalidImageError("Test error")

        with pytest.raises(StorageError):
            raise ImageTooLargeError("Test error")

        with pytest.raises(StorageError):
            raise UploadFailedError("Test error")
