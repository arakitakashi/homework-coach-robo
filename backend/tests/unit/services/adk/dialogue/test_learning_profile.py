"""学習プロファイル - データモデルのテスト"""

import pytest
from datetime import datetime


class TestThinkingTendencies:
    """ThinkingTendencies Pydanticモデルのテスト"""

    def test_thinking_tendencies_creation(self):
        """ThinkingTendenciesを作成できる"""
        from app.services.adk.dialogue.learning_profile import ThinkingTendencies

        tendencies = ThinkingTendencies(
            persistence_score=7.5,
            independence_score=6.0,
            reflection_quality=8.0,
            hint_dependency=0.3,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert tendencies.persistence_score == 7.5
        assert tendencies.independence_score == 6.0
        assert tendencies.reflection_quality == 8.0
        assert tendencies.hint_dependency == 0.3
        assert tendencies.updated_at == datetime(2026, 2, 2, 10, 0, 0)

    def test_thinking_tendencies_score_range(self):
        """スコアは0-10の範囲"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import ThinkingTendencies

        # 有効な範囲（境界値）
        tendencies = ThinkingTendencies(
            persistence_score=0,
            independence_score=10,
            reflection_quality=5,
            hint_dependency=0.5,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert tendencies.persistence_score == 0
        assert tendencies.independence_score == 10

        # 無効な範囲
        with pytest.raises(ValidationError):
            ThinkingTendencies(
                persistence_score=-1,
                independence_score=5,
                reflection_quality=5,
                hint_dependency=0.5,
                updated_at=datetime(2026, 2, 2, 10, 0, 0),
            )

        with pytest.raises(ValidationError):
            ThinkingTendencies(
                persistence_score=11,
                independence_score=5,
                reflection_quality=5,
                hint_dependency=0.5,
                updated_at=datetime(2026, 2, 2, 10, 0, 0),
            )

    def test_thinking_tendencies_hint_dependency_range(self):
        """hint_dependencyは0-1の範囲"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import ThinkingTendencies

        # 有効な範囲
        tendencies = ThinkingTendencies(
            persistence_score=5,
            independence_score=5,
            reflection_quality=5,
            hint_dependency=0,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert tendencies.hint_dependency == 0

        tendencies = ThinkingTendencies(
            persistence_score=5,
            independence_score=5,
            reflection_quality=5,
            hint_dependency=1,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert tendencies.hint_dependency == 1

        # 無効な範囲
        with pytest.raises(ValidationError):
            ThinkingTendencies(
                persistence_score=5,
                independence_score=5,
                reflection_quality=5,
                hint_dependency=-0.1,
                updated_at=datetime(2026, 2, 2, 10, 0, 0),
            )

        with pytest.raises(ValidationError):
            ThinkingTendencies(
                persistence_score=5,
                independence_score=5,
                reflection_quality=5,
                hint_dependency=1.1,
                updated_at=datetime(2026, 2, 2, 10, 0, 0),
            )


class TestSubjectUnderstanding:
    """SubjectUnderstanding Pydanticモデルのテスト"""

    def test_subject_understanding_creation(self):
        """SubjectUnderstandingを作成できる"""
        from app.services.adk.dialogue.learning_profile import SubjectUnderstanding

        understanding = SubjectUnderstanding(
            subject="math",
            topic="addition",
            level=7.5,
            trend="improving",
            weak_points=["繰り上がり"],
            strong_points=["一桁の足し算"],
            assessed_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert understanding.subject == "math"
        assert understanding.topic == "addition"
        assert understanding.level == 7.5
        assert understanding.trend == "improving"
        assert understanding.weak_points == ["繰り上がり"]
        assert understanding.strong_points == ["一桁の足し算"]

    def test_subject_understanding_level_range(self):
        """levelは0-10の範囲"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import SubjectUnderstanding

        # 有効な範囲
        understanding = SubjectUnderstanding(
            subject="math",
            topic="addition",
            level=0,
            trend="stable",
            assessed_at=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert understanding.level == 0

        understanding = SubjectUnderstanding(
            subject="math",
            topic="addition",
            level=10,
            trend="stable",
            assessed_at=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert understanding.level == 10

        # 無効な範囲
        with pytest.raises(ValidationError):
            SubjectUnderstanding(
                subject="math",
                topic="addition",
                level=-1,
                trend="stable",
                assessed_at=datetime(2026, 2, 2, 10, 0, 0),
            )

        with pytest.raises(ValidationError):
            SubjectUnderstanding(
                subject="math",
                topic="addition",
                level=11,
                trend="stable",
                assessed_at=datetime(2026, 2, 2, 10, 0, 0),
            )

    def test_subject_understanding_trend_values(self):
        """trendはimproving/stable/decliningのみ"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import SubjectUnderstanding

        # 有効な値
        for trend in ["improving", "stable", "declining"]:
            understanding = SubjectUnderstanding(
                subject="math",
                topic="addition",
                level=5,
                trend=trend,
                assessed_at=datetime(2026, 2, 2, 10, 0, 0),
            )
            assert understanding.trend == trend

        # 無効な値
        with pytest.raises(ValidationError):
            SubjectUnderstanding(
                subject="math",
                topic="addition",
                level=5,
                trend="unknown",
                assessed_at=datetime(2026, 2, 2, 10, 0, 0),
            )

    def test_subject_understanding_default_lists(self):
        """weak_pointsとstrong_pointsはデフォルトで空リスト"""
        from app.services.adk.dialogue.learning_profile import SubjectUnderstanding

        understanding = SubjectUnderstanding(
            subject="math",
            topic="addition",
            level=5,
            trend="stable",
            assessed_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert understanding.weak_points == []
        assert understanding.strong_points == []


class TestSessionSummary:
    """SessionSummary Pydanticモデルのテスト"""

    def test_session_summary_creation(self):
        """SessionSummaryを作成できる"""
        from app.services.adk.dialogue.learning_profile import SessionSummary

        summary = SessionSummary(
            session_id="session-123",
            date=datetime(2026, 2, 2, 10, 0, 0),
            duration_seconds=1800,
            problems_attempted=5,
            problems_solved_independently=3,
            hints_used=2,
            subjects_covered=["math", "japanese"],
            insights=["足し算の概念を理解した"],
        )

        assert summary.session_id == "session-123"
        assert summary.duration_seconds == 1800
        assert summary.problems_attempted == 5
        assert summary.problems_solved_independently == 3
        assert summary.hints_used == 2
        assert summary.subjects_covered == ["math", "japanese"]
        assert summary.insights == ["足し算の概念を理解した"]

    def test_session_summary_default_values(self):
        """SessionSummaryのデフォルト値"""
        from app.services.adk.dialogue.learning_profile import SessionSummary

        summary = SessionSummary(
            session_id="session-123",
            date=datetime(2026, 2, 2, 10, 0, 0),
            duration_seconds=1800,
            problems_attempted=5,
            problems_solved_independently=3,
            hints_used=2,
            subjects_covered=["math"],
        )

        assert summary.insights == []

    def test_session_summary_non_negative_values(self):
        """数値フィールドは非負"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import SessionSummary

        # 有効な値（0も許可）
        summary = SessionSummary(
            session_id="session-123",
            date=datetime(2026, 2, 2, 10, 0, 0),
            duration_seconds=0,
            problems_attempted=0,
            problems_solved_independently=0,
            hints_used=0,
            subjects_covered=[],
        )
        assert summary.duration_seconds == 0

        # 負の値は無効
        with pytest.raises(ValidationError):
            SessionSummary(
                session_id="session-123",
                date=datetime(2026, 2, 2, 10, 0, 0),
                duration_seconds=-1,
                problems_attempted=5,
                problems_solved_independently=3,
                hints_used=2,
                subjects_covered=["math"],
            )
