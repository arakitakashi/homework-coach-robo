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


class TestChildLearningProfile:
    """ChildLearningProfile Pydanticモデルのテスト"""

    def test_child_learning_profile_creation(self):
        """ChildLearningProfileを作成できる"""
        from app.services.adk.dialogue.learning_profile import (
            ChildLearningProfile,
            SubjectUnderstanding,
            ThinkingTendencies,
        )

        thinking = ThinkingTendencies(
            persistence_score=7.5,
            independence_score=6.0,
            reflection_quality=8.0,
            hint_dependency=0.3,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        subjects = [
            SubjectUnderstanding(
                subject="math",
                topic="addition",
                level=7.5,
                trend="improving",
                assessed_at=datetime(2026, 2, 2, 10, 0, 0),
            )
        ]

        profile = ChildLearningProfile(
            child_id="child-123",
            thinking=thinking,
            subjects=subjects,
            total_sessions=10,
            total_problems_solved=50,
            created_at=datetime(2026, 1, 1, 0, 0, 0),
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert profile.child_id == "child-123"
        assert profile.thinking.persistence_score == 7.5
        assert len(profile.subjects) == 1
        assert profile.total_sessions == 10
        assert profile.total_problems_solved == 50

    def test_child_learning_profile_empty_subjects(self):
        """subjects は空リストでも作成可能"""
        from app.services.adk.dialogue.learning_profile import (
            ChildLearningProfile,
            ThinkingTendencies,
        )

        thinking = ThinkingTendencies(
            persistence_score=5,
            independence_score=5,
            reflection_quality=5,
            hint_dependency=0.5,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        profile = ChildLearningProfile(
            child_id="child-123",
            thinking=thinking,
            subjects=[],
            total_sessions=0,
            total_problems_solved=0,
            created_at=datetime(2026, 2, 2, 10, 0, 0),
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert profile.subjects == []
        assert profile.total_sessions == 0

    def test_child_learning_profile_non_negative_counts(self):
        """カウント系フィールドは非負"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import (
            ChildLearningProfile,
            ThinkingTendencies,
        )

        thinking = ThinkingTendencies(
            persistence_score=5,
            independence_score=5,
            reflection_quality=5,
            hint_dependency=0.5,
            updated_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        with pytest.raises(ValidationError):
            ChildLearningProfile(
                child_id="child-123",
                thinking=thinking,
                subjects=[],
                total_sessions=-1,
                total_problems_solved=0,
                created_at=datetime(2026, 2, 2, 10, 0, 0),
                updated_at=datetime(2026, 2, 2, 10, 0, 0),
            )


class TestLearningMemory:
    """LearningMemory Pydanticモデルのテスト"""

    def test_learning_memory_creation(self):
        """LearningMemoryを作成できる"""
        from app.services.adk.dialogue.learning_profile import LearningMemory

        memory = LearningMemory(
            memory_type="learning_insight",
            content="たろうくんは足し算は得意だが、繰り上がりがある問題では混乱しやすい。",
            tags=["math", "addition", "weakness"],
            created_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert memory.memory_type == "learning_insight"
        assert "繰り上がり" in memory.content
        assert memory.tags == ["math", "addition", "weakness"]

    def test_learning_memory_type_values(self):
        """memory_typeは指定された値のみ許可"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.learning_profile import LearningMemory

        # 有効な値
        for memory_type in ["learning_insight", "thinking_pattern", "effective_approach"]:
            memory = LearningMemory(
                memory_type=memory_type,
                content="テスト",
                created_at=datetime(2026, 2, 2, 10, 0, 0),
            )
            assert memory.memory_type == memory_type

        # 無効な値
        with pytest.raises(ValidationError):
            LearningMemory(
                memory_type="invalid_type",
                content="テスト",
                created_at=datetime(2026, 2, 2, 10, 0, 0),
            )

    def test_learning_memory_default_tags(self):
        """tagsはデフォルトで空リスト"""
        from app.services.adk.dialogue.learning_profile import LearningMemory

        memory = LearningMemory(
            memory_type="thinking_pattern",
            content="最初は諦めそうになるが、励ましの言葉で粘り強く取り組める。",
            created_at=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert memory.tags == []
