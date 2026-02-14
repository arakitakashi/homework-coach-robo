"""依存性注入（Dependency Injection）設定

FastAPIのDependsで使用される依存関数を定義します。
テスト時にはこれらの関数をオーバーライドすることで、モック実装に切り替えられます。
"""

from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from app.services.storage_service import CloudStorageService, StorageService


def get_storage_service() -> StorageService:
    """StorageServiceの依存性を提供

    本番環境では CloudStorageService を返します。
    テスト環境では MockStorageService をオーバーライドして返します。

    Returns:
        StorageService: ストレージサービスインスタンス
    """
    return CloudStorageService(
        bucket_name=settings.GCS_BUCKET_NAME,
        project_id=settings.GCP_PROJECT_ID,
    )


# 型注釈付きの依存関係エイリアス
# 使用例: async def upload_image(storage: StorageServiceDep)
StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
