"""アプリケーション設定

環境変数から設定値を読み込み、型安全な設定オブジェクトを提供します。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定

    環境変数または.envファイルから設定を読み込みます。
    """

    # API設定
    API_TITLE: str = "Homework Coach Robot API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "宿題コーチロボット - バックエンドAPI"

    # セキュリティ
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google Cloud Platform
    GCP_PROJECT_ID: str | None = None
    GCS_BUCKET_NAME: str = "homework-coach-assets"

    # Firebase / Firestore
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # フロントエンド開発サーバー
        "http://localhost:8000",  # バックエンド開発サーバー
    ]

    # ストレージ設定
    MAX_IMAGE_SIZE_MB: int = 10
    SIGNED_URL_EXPIRATION_HOURS: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# グローバル設定インスタンス
settings = Settings()
