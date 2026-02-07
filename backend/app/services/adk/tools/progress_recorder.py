"""学習進捗記録ツール

学習プロセスを記録し、ポイントを付与する。
「自分で気づいた」→3pt、「ヒントで気づいた」→2pt、「一緒に解いた」→1pt
"""

from __future__ import annotations

from typing import Any

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

# outcome → ポイントのマッピング
_OUTCOME_POINTS: dict[str, int] = {
    "self_solved": 3,
    "hint_solved": 2,
    "guided_solved": 1,
}

# outcome → 励ましメッセージ
_ENCOURAGEMENT_MESSAGES: dict[str, str] = {
    "self_solved": "すごい！じぶんの力でとけたね！とってもがんばったよ！",
    "hint_solved": "ヒントをうまくつかって、じぶんで気づけたね！えらい！",
    "guided_solved": "いっしょにかんがえて、さいごまでがんばったね！つぎはもっとできるよ！",
}


def record_progress(
    user_id: str,  # noqa: ARG001
    session_id: str,  # noqa: ARG001
    problem_id: str,  # noqa: ARG001
    outcome: str,
    hints_used: int,  # noqa: ARG001
    time_spent_seconds: int,  # noqa: ARG001
    tool_context: Any = None,
) -> dict[str, object]:
    """学習進捗を記録しポイントを付与する

    Args:
        user_id: ユーザーID
        session_id: セッションID
        problem_id: 問題ID
        outcome: 結果（"self_solved", "hint_solved", "guided_solved"）
        hints_used: 使用したヒント数
        time_spent_seconds: 所要時間（秒）
    """
    if outcome not in _OUTCOME_POINTS:
        return {"error": f"Unknown outcome: {outcome}"}

    state: dict[str, Any] = tool_context.state if tool_context is not None else {}

    points_earned = _OUTCOME_POINTS[outcome]
    total_points: int = state.get("total_points", 0) + points_earned
    streak: int = state.get("streak", 0) + 1

    # セッション状態を更新
    state["total_points"] = total_points
    state["streak"] = streak

    encouragement = _ENCOURAGEMENT_MESSAGES[outcome]

    return {
        "points_earned": points_earned,
        "total_points": total_points,
        "streak": streak,
        "achievement_unlocked": None,
        "encouragement_message": encouragement,
    }


record_progress_tool = FunctionTool(func=record_progress)
