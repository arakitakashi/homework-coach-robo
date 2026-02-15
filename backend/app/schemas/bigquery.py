"""BigQuery用のPydanticスキーマ定義

このモジュールは、BigQueryテーブルにデータを保存する際に使用する
Pydanticスキーマを定義します。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class DialogueTurnBQ(BaseModel):
    """BigQuery用の対話ターンスキーマ

    dialogue_sessionsテーブルのdialogue_turns配列要素に対応。
    """

    turn_id: int
    speaker: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime
    emotion: str | None = None


class DialogueSessionBQ(BaseModel):
    """BigQuery用のセッションスキーマ

    dialogue_sessionsテーブルに対応。
    """

    session_id: str
    user_id: str
    problem: str
    start_time: datetime
    end_time: datetime | None = None
    dialogue_turns: list[DialogueTurnBQ] = Field(default_factory=list)
    total_hints_used: int = 0
    self_solved_count: int = 0
    total_points: int = 0


class LearningHistoryBQ(BaseModel):
    """BigQuery用の学習履歴スキーマ

    learning_historyテーブルに対応。
    """

    id: str
    user_id: str
    problem_id: str
    subject: str
    grade_level: int
    attempted_at: datetime
    solved_independently: bool
    hints_used: int
    time_spent_seconds: int
    points_earned: int
    session_id: str


class SubjectUnderstandingBQ(BaseModel):
    """BigQuery用の科目別理解度スキーマ

    learning_profile_snapshotsテーブルのsubject_understanding配列要素に対応。
    """

    subject: str
    topic: str
    level: str  # 'beginner' | 'intermediate' | 'advanced'
    trend: str  # 'improving' | 'stable' | 'declining'


class LearningProfileSnapshotBQ(BaseModel):
    """BigQuery用の学習プロファイルスナップショットスキーマ

    learning_profile_snapshotsテーブルに対応。
    """

    id: str
    user_id: str
    snapshot_at: datetime
    persistence_score: float
    independence_score: float
    reflection_quality: float
    hint_dependency: float
    subject_understanding: list[SubjectUnderstandingBQ] = Field(default_factory=list)
