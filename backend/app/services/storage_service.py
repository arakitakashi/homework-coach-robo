"""Cloud Storage サービス

このモジュールは、Google Cloud Storage への画像アップロードとメタデータ管理を提供します。
子供の個人情報が含まれる可能性のある画像を扱うため、セキュリティを最優先に設計されています。
"""

from abc import abstractmethod
from datetime import timedelta
from typing import Protocol

from app.schemas.storage import UploadedImageSchema

# カスタム例外クラス


class StorageError(Exception):
    """ストレージ操作に関するベース例外"""

    pass


class InvalidImageError(StorageError):
    """不正な画像ファイル

    以下の場合に発生:
    - サポートされていないファイル形式
    - magic number が不正
    - 破損したファイル
    """

    pass


class ImageTooLargeError(StorageError):
    """ファイルサイズ超過

    10MBを超える画像ファイルをアップロードしようとした場合に発生。
    """

    pass


class UploadFailedError(StorageError):
    """アップロード失敗

    ネットワークエラーや権限エラーなど、Cloud Storageへのアップロード時のエラー。
    """

    pass


# StorageService プロトコル


class StorageService(Protocol):
    """Cloud Storage サービスのインターフェース

    Cloud Storageへの画像アップロードとSigned URL生成を提供する
    抽象インターフェース。テスト用のモック実装と本番用の実装を
    切り替えるためにProtocolを使用。
    """

    @abstractmethod
    async def upload_image(
        self,
        session_id: str,
        image_data: bytes,
        filename: str,
    ) -> UploadedImageSchema:
        """画像をCloud Storageにアップロードし、メタデータを返す

        Args:
            session_id: セッションID（ストレージパスの生成に使用）
            image_data: アップロードする画像のバイナリデータ
            filename: 元のファイル名（拡張子の判定に使用）

        Returns:
            UploadedImageSchema: アップロードされた画像のメタデータ

        Raises:
            InvalidImageError: 不正な画像ファイル
            ImageTooLargeError: ファイルサイズ超過（10MB以上）
            UploadFailedError: アップロード失敗
        """
        ...

    @abstractmethod
    async def generate_signed_url(
        self,
        storage_path: str,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        """Signed URLを生成する

        Args:
            storage_path: Cloud Storage上のファイルパス
            expires_in: URL有効期限（デフォルト: 1時間）

        Returns:
            str: 一時アクセス用のSigned URL

        Raises:
            StorageError: URL生成失敗
        """
        ...

    @abstractmethod
    async def validate_image(
        self,
        image_data: bytes,
        max_size_mb: int = 10,
    ) -> tuple[str, int]:
        """画像データを検証する

        Args:
            image_data: 検証する画像のバイナリデータ
            max_size_mb: 最大ファイルサイズ（MB単位、デフォルト: 10MB）

        Returns:
            tuple[str, int]: (MIME type, file_size)の タプル

        Raises:
            InvalidImageError: 不正なファイル形式
            ImageTooLargeError: ファイルサイズ超過
        """
        ...


# MockStorageService 実装


class MockStorageService:
    """テスト用のモックストレージサービス

    実際のCloud Storageに接続せず、ローカルでストレージ操作をシミュレートします。
    ユニットテストやE2Eテストで使用します。
    """

    # サポートされている画像形式のmagic number
    MAGIC_NUMBERS = {
        b"\xff\xd8\xff": "image/jpeg",  # JPEG
        b"\x89PNG\r\n\x1a\n": "image/png",  # PNG
        b"RIFF": "image/webp",  # WebP (RIFFヘッダーの後にWEBPが続く)
    }

    async def upload_image(
        self,
        session_id: str,
        image_data: bytes,
        filename: str,
    ) -> UploadedImageSchema:
        """画像をモックアップロードし、メタデータを返す"""
        from datetime import datetime, timezone
        from uuid import uuid4

        # 画像検証
        mime_type, file_size = await self.validate_image(image_data)

        # 拡張子の取得
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"

        # ストレージパスの生成
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        unique_id = str(uuid4()).split("-")[0]
        storage_path = f"sessions/{session_id}/images/{timestamp}_{unique_id}.{ext}"

        # Signed URLの生成
        signed_url = await self.generate_signed_url(storage_path)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        return UploadedImageSchema(
            storage_path=storage_path,
            signed_url=signed_url,
            signed_url_expires_at=expires_at,
            uploaded_at=datetime.now(timezone.utc),
            file_size=file_size,
            mime_type=mime_type,
            width=None,
            height=None,
        )

    async def generate_signed_url(
        self,
        storage_path: str,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        """モックSigned URLを生成"""
        # モックURLを返す（実際のGCS URLの形式に似せる）
        return f"https://storage.googleapis.com/homework-coach-assets-mock/{storage_path}?expires={int(expires_in.total_seconds())}"

    async def validate_image(
        self,
        image_data: bytes,
        max_size_mb: int = 10,
    ) -> tuple[str, int]:
        """画像データを検証"""
        file_size = len(image_data)

        # サイズチェック
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise ImageTooLargeError(f"File size {file_size} bytes exceeds maximum {max_size_mb}MB")

        # Magic numberチェック
        mime_type = None
        for magic, mime in self.MAGIC_NUMBERS.items():
            if image_data.startswith(magic):
                # WebPの追加チェック
                if mime == "image/webp":
                    if len(image_data) >= 12 and image_data[8:12] == b"WEBP":
                        mime_type = mime
                        break
                else:
                    mime_type = mime
                    break

        if mime_type is None:
            raise InvalidImageError(
                "File type not supported. Only JPEG, PNG, and WebP are allowed."
            )

        return mime_type, file_size


# CloudStorageService 実装


class CloudStorageService:
    """本番用のCloud Storageサービス

    Google Cloud Storageに実際に接続して画像をアップロードします。
    本番環境およびステージング環境で使用します。
    """

    # サポートされている画像形式のmagic number
    MAGIC_NUMBERS = {
        b"\xff\xd8\xff": "image/jpeg",  # JPEG
        b"\x89PNG\r\n\x1a\n": "image/png",  # PNG
        b"RIFF": "image/webp",  # WebP
    }

    def __init__(self, bucket_name: str, project_id: str | None = None):
        """CloudStorageServiceの初期化

        Args:
            bucket_name: Cloud Storageバケット名
            project_id: GCPプロジェクトID（オプショナル）
        """
        import google.cloud.storage

        self.bucket_name = bucket_name
        self.project_id = project_id
        self.client = google.cloud.storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    async def upload_image(
        self,
        session_id: str,
        image_data: bytes,
        filename: str,
    ) -> UploadedImageSchema:
        """画像をCloud Storageにアップロード"""
        from datetime import datetime, timezone
        from uuid import uuid4

        # 画像検証
        mime_type, file_size = await self.validate_image(image_data)

        # 拡張子の取得
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"

        # ストレージパスの生成
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        unique_id = str(uuid4()).split("-")[0]
        storage_path = f"sessions/{session_id}/images/{timestamp}_{unique_id}.{ext}"

        try:
            # Cloud Storageにアップロード
            blob = self.bucket.blob(storage_path)
            blob.upload_from_string(image_data, content_type=mime_type)

            # Signed URLの生成
            signed_url = await self.generate_signed_url(storage_path)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            return UploadedImageSchema(
                storage_path=storage_path,
                signed_url=signed_url,
                signed_url_expires_at=expires_at,
                uploaded_at=datetime.now(timezone.utc),
                file_size=file_size,
                mime_type=mime_type,
                width=None,
                height=None,
            )
        except Exception as e:
            raise UploadFailedError(f"Failed to upload image: {e}") from e

    async def generate_signed_url(
        self,
        storage_path: str,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        """Signed URLを生成"""
        from datetime import datetime, timezone

        try:
            blob = self.bucket.blob(storage_path)
            expiration = datetime.now(timezone.utc) + expires_in

            url: str = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET",
            )

            return url
        except Exception as e:
            raise StorageError(f"Failed to generate signed URL: {e}") from e

    async def validate_image(
        self,
        image_data: bytes,
        max_size_mb: int = 10,
    ) -> tuple[str, int]:
        """画像データを検証"""
        file_size = len(image_data)

        # サイズチェック
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise ImageTooLargeError(f"File size {file_size} bytes exceeds maximum {max_size_mb}MB")

        # Magic numberチェック
        mime_type = None
        for magic, mime in self.MAGIC_NUMBERS.items():
            if image_data.startswith(magic):
                # WebPの追加チェック
                if mime == "image/webp":
                    if len(image_data) >= 12 and image_data[8:12] == b"WEBP":
                        mime_type = mime
                        break
                else:
                    mime_type = mime
                    break

        if mime_type is None:
            raise InvalidImageError(
                "File type not supported. Only JPEG, PNG, and WebP are allowed."
            )

        return mime_type, file_size
