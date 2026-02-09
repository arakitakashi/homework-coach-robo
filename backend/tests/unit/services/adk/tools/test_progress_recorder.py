"""record_progress_tool のテスト"""

from typing import Any
from unittest.mock import MagicMock


def _make_tool_context(state: dict[str, Any] | None = None) -> MagicMock:
    """テスト用のToolContextモックを作成する"""
    ctx = MagicMock()
    mock_state: dict[str, Any] = dict(state) if state else {}
    ctx.state = mock_state
    return ctx


class TestRecordProgressPoints:
    """ポイント付与のテスト"""

    def test_self_solved_gives_3_points(self) -> None:
        """自分で気づいた → 3ポイント"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="self_solved",
            hints_used=0,
            time_spent_seconds=60,
            tool_context=ctx,
        )
        assert result["points_earned"] == 3

    def test_hint_solved_gives_2_points(self) -> None:
        """ヒントで気づいた → 2ポイント"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="hint_solved",
            hints_used=2,
            time_spent_seconds=120,
            tool_context=ctx,
        )
        assert result["points_earned"] == 2

    def test_guided_solved_gives_1_point(self) -> None:
        """一緒に解いた → 1ポイント"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="guided_solved",
            hints_used=3,
            time_spent_seconds=180,
            tool_context=ctx,
        )
        assert result["points_earned"] == 1


class TestRecordProgressTotalPoints:
    """累計ポイントのテスト"""

    def test_accumulates_total_points(self) -> None:
        """合計ポイントが累積される"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context({"total_points": 10})
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="self_solved",
            hints_used=0,
            time_spent_seconds=60,
            tool_context=ctx,
        )
        assert result["total_points"] == 13
        assert ctx.state["total_points"] == 13

    def test_initial_total_points_is_zero(self) -> None:
        """初回は合計ポイントが0から始まる"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="hint_solved",
            hints_used=1,
            time_spent_seconds=90,
            tool_context=ctx,
        )
        assert result["total_points"] == 2


class TestRecordProgressStreak:
    """連続正解のテスト"""

    def test_streak_increments(self) -> None:
        """連続正解が増える"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context({"streak": 2})
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="self_solved",
            hints_used=0,
            time_spent_seconds=30,
            tool_context=ctx,
        )
        assert result["streak"] == 3

    def test_initial_streak_is_1(self) -> None:
        """初回の連続正解は1"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="self_solved",
            hints_used=0,
            time_spent_seconds=30,
            tool_context=ctx,
        )
        assert result["streak"] == 1


class TestRecordProgressEncouragement:
    """励ましメッセージのテスト"""

    def test_encouragement_message_exists(self) -> None:
        """励ましメッセージが返される"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="self_solved",
            hints_used=0,
            time_spent_seconds=60,
            tool_context=ctx,
        )
        assert isinstance(result["encouragement_message"], str)
        assert len(result["encouragement_message"]) > 0

    def test_encouragement_for_guided_is_positive(self) -> None:
        """一緒に解いた場合も肯定的メッセージ"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="guided_solved",
            hints_used=3,
            time_spent_seconds=300,
            tool_context=ctx,
        )
        assert isinstance(result["encouragement_message"], str)
        assert len(result["encouragement_message"]) > 0


class TestRecordProgressInvalidOutcome:
    """無効なoutcomeのテスト"""

    def test_invalid_outcome_returns_error(self) -> None:
        """無効なoutcomeはエラーを返す"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="invalid",
            hints_used=0,
            time_spent_seconds=60,
            tool_context=ctx,
        )
        assert "error" in result


class TestRecordProgressReturnKeys:
    """返り値のキー確認テスト"""

    def test_returns_required_keys(self) -> None:
        """必要なキーがすべて含まれる"""
        from app.services.adk.tools.progress_recorder import record_progress

        ctx = _make_tool_context()
        result = record_progress(
            user_id="user1",
            session_id="sess1",
            problem_id="prob1",
            outcome="self_solved",
            hints_used=0,
            time_spent_seconds=60,
            tool_context=ctx,
        )
        assert "points_earned" in result
        assert "total_points" in result
        assert "streak" in result
        assert "achievement_unlocked" in result
        assert "encouragement_message" in result


class TestRecordProgressTool:
    """record_progress_tool FunctionTool のテスト"""

    def test_is_function_tool_instance(self) -> None:
        """FunctionTool インスタンスである"""
        from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

        from app.services.adk.tools.progress_recorder import record_progress_tool

        assert isinstance(record_progress_tool, FunctionTool)
