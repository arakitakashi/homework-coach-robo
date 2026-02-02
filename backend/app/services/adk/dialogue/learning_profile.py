"""学習プロファイル - データモデル（永続化用）"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ThinkingTendencies(BaseModel):
    """思考の傾向"""

    persistence_score: float = Field(..., ge=0, le=10, description="粘り強さ (0-10)")
    independence_score: float = Field(..., ge=0, le=10, description="自立性 (0-10)")
    reflection_quality: float = Field(..., ge=0, le=10, description="振り返り力 (0-10)")
    hint_dependency: float = Field(..., ge=0, le=1, description="ヒント依存度 (0-1)")
    updated_at: datetime = Field(..., description="最終更新日時")


class SubjectUnderstanding(BaseModel):
    """科目別理解度"""

    subject: str = Field(..., description="科目 (math, japanese, etc.)")
    topic: str = Field(..., description="単元 (addition, kanji_grade1, etc.)")
    level: float = Field(..., ge=0, le=10, description="理解度 (0-10)")
    trend: Literal["improving", "stable", "declining"] = Field(..., description="傾向")
    weak_points: list[str] = Field(default_factory=list, description="苦手ポイント")
    strong_points: list[str] = Field(default_factory=list, description="得意ポイント")
    assessed_at: datetime = Field(..., description="評価日時")


class SessionSummary(BaseModel):
    """セッションサマリー"""

    session_id: str = Field(..., description="セッションID")
    date: datetime = Field(..., description="セッション日時")
    duration_seconds: int = Field(..., ge=0, description="セッション時間（秒）")
    problems_attempted: int = Field(..., ge=0, description="取り組んだ問題数")
    problems_solved_independently: int = Field(..., ge=0, description="独力で解いた問題数")
    hints_used: int = Field(..., ge=0, description="使用したヒント数")
    subjects_covered: list[str] = Field(..., description="取り組んだ科目")
    insights: list[str] = Field(default_factory=list, description="セッションからの気づき")


class ChildLearningProfile(BaseModel):
    """子供の学習プロファイル（Firestore永続化用）"""

    child_id: str = Field(..., description="子供ID")
    thinking: ThinkingTendencies = Field(..., description="思考の傾向")
    subjects: list[SubjectUnderstanding] = Field(..., description="科目別理解度")
    total_sessions: int = Field(..., ge=0, description="総セッション数")
    total_problems_solved: int = Field(..., ge=0, description="総解決問題数")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="最終更新日時")
