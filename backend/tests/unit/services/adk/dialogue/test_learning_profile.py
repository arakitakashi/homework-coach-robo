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
