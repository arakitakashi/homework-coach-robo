"""ストレージ関連のPydantic スキーマ定義"""

from datetime import datetime

from pydantic import BaseModel, Field


class ImageUploadRequest(BaseModel):
    """画像アップロードリクエスト

    フロントエンドからの画像アップロードリクエストを受け取るためのスキーマ。
    Base64エンコードされた画像データを含む。
    """

    session_id: str = Field(..., min_length=1, description="セッションID")
    image_data: str = Field(..., min_length=1, description="Base64エンコードされた画像データ")
    filename: str = Field(..., min_length=1, description="元のファイル名")


class UploadedImageSchema(BaseModel):
    """アップロード済み画像のメタデータ

    Cloud Storageにアップロードされた画像のメタデータを表すスキーマ。
    Firestoreに保存される情報と一致する。
    """

    storage_path: str = Field(..., description="Cloud Storage上のファイルパス")
    signed_url: str = Field(..., description="一時アクセス用のSigned URL")
    signed_url_expires_at: datetime = Field(..., description="Signed URLの有効期限")
    uploaded_at: datetime = Field(..., description="アップロード日時")
    file_size: int = Field(..., gt=0, description="ファイルサイズ（バイト単位）")
    mime_type: str = Field(..., description="MIMEタイプ（例: image/jpeg）")
    width: int | None = Field(None, gt=0, description="画像の幅（ピクセル）")
    height: int | None = Field(None, gt=0, description="画像の高さ（ピクセル）")
