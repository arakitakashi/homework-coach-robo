"""学習プロファイル - データモデル（永続化用）"""

from datetime import datetime

from pydantic import BaseModel, Field


class ThinkingTendencies(BaseModel):
    """思考の傾向"""

    persistence_score: float = Field(..., ge=0, le=10, description="粘り強さ (0-10)")
    independence_score: float = Field(..., ge=0, le=10, description="自立性 (0-10)")
    reflection_quality: float = Field(..., ge=0, le=10, description="振り返り力 (0-10)")
    hint_dependency: float = Field(..., ge=0, le=1, description="ヒント依存度 (0-1)")
    updated_at: datetime = Field(..., description="最終更新日時")
