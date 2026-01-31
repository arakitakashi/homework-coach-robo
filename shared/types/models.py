"""
API共通型定義
フロントエンド・バックエンド間で共有される型（Python版）
"""

from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiError(BaseModel):
    """APIエラー型"""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiResponse(BaseModel, Generic[T]):
    """APIレスポンスの基本型"""

    success: bool
    data: T | None = None
    error: ApiError | None = None


class Pagination(BaseModel):
    """ページネーション"""

    page: int
    limit: int
    total: int
    has_more: bool


class SessionStatus(str, Enum):
    """セッションステータス"""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class HintLevel(int, Enum):
    """ヒントレベル（3段階）"""

    LEVEL_1 = 1  # 問題理解の確認
    LEVEL_2 = 2  # 既習事項の想起
    LEVEL_3 = 3  # 部分的支援


class CharacterType(str, Enum):
    """キャラクタータイプ"""

    ROBOT = "robot"
    WIZARD = "wizard"
    ASTRONAUT = "astronaut"
