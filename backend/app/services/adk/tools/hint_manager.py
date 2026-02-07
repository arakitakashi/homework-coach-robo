"""3段階ヒント管理ツール

ヒントレベル（0→1→2→3）の遷移をセッション状態で管理する。
LLMが直接レベルを変更することを防ぎ、ツール経由でのみ状態を更新する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

if TYPE_CHECKING:
    pass

_MAX_HINT_LEVEL = 3

# ヒントレベル別テンプレート
_HINT_TEMPLATES: dict[int, str] = {
    0: "",
    1: "問題をもういちどよく読んでみよう。何を聞かれているかな？",
    2: "前にやった似た問題を思い出してみよう。どんなやり方だったかな？",
    3: "一緒にステップを分けて考えてみよう。まず最初は何をすればいいかな？",
}


def manage_hint(
    session_id: str,  # noqa: ARG001
    action: str,
    problem_id: str | None = None,  # noqa: ARG001
    tool_context: Any = None,
) -> dict[str, object]:
    """3段階ヒントシステムの状態を管理する

    Args:
        session_id: セッションID
        action: アクション（"get_current", "advance", "reset"）
        problem_id: 問題ID（オプション）
    """
    state: dict[str, Any] = tool_context.state if tool_context is not None else {}

    current_level: int = state.get("hint_level", 0)
    hints_used_total: int = state.get("hints_used_total", 0)

    if action == "get_current":
        pass
    elif action == "advance":
        if current_level < _MAX_HINT_LEVEL:
            current_level += 1
            hints_used_total += 1
            state["hint_level"] = current_level
            state["hints_used_total"] = hints_used_total
    elif action == "reset":
        current_level = 0
        state["hint_level"] = 0
    else:
        return {"error": f"Unknown action: {action}"}

    return {
        "current_level": current_level,
        "max_level": _MAX_HINT_LEVEL,
        "hint_template": _HINT_TEMPLATES.get(current_level, ""),
        "can_advance": current_level < _MAX_HINT_LEVEL,
        "hints_used_total": hints_used_total,
    }


manage_hint_tool = FunctionTool(func=manage_hint)
