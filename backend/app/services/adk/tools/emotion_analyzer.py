"""感情分析・更新ツール

子供の発言から推定された感情スコアを session.state に記録し、
サポートレベルと推奨アクションを返す。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

_VALID_EMOTIONS = frozenset({"frustrated", "confident", "confused", "happy", "tired", "neutral"})


def _clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """値を min_val〜max_val の範囲にクランプする"""
    return max(min_val, min(max_val, value))


def _determine_support_level(frustration: float, fatigue: float) -> str:
    """サポートレベルを決定する

    frustration > 0.7 OR fatigue > 0.6 → intensive
    frustration > 0.4 OR fatigue > 0.3 → moderate
    上記以外 → minimal
    """
    if frustration > 0.7 or fatigue > 0.6:
        return "intensive"
    if frustration > 0.4 or fatigue > 0.3:
        return "moderate"
    return "minimal"


def _determine_action(frustration: float, fatigue: float) -> str:
    """推奨アクションを決定する

    fatigue > 0.6 → rest（疲労優先）
    frustration > 0.7 → encourage
    上記以外 → continue
    """
    if fatigue > 0.6:
        return "rest"
    if frustration > 0.7:
        return "encourage"
    return "continue"


def update_emotion(
    frustration: float,
    confidence: float,
    fatigue: float,
    excitement: float,
    primary_emotion: str,
    tool_context: Any = None,
) -> dict[str, object]:
    """子供の感情状態を分析結果に基づいて更新する。

    Args:
        frustration: イライラ度 (0.0-1.0)
        confidence: 自信度 (0.0-1.0)
        fatigue: 疲労度 (0.0-1.0)
        excitement: 興奮度 (0.0-1.0)
        primary_emotion: 主な感情 (frustrated/confident/confused/happy/tired/neutral)
        tool_context: ADK ToolContext（session.state アクセス用）

    Returns:
        dict: {
            "primary_emotion": str,
            "support_level": str,  # minimal/moderate/intensive
            "action_recommended": str,  # continue/encourage/rest
        }
    """
    if primary_emotion not in _VALID_EMOTIONS:
        return {
            "error": f"Invalid primary_emotion: {primary_emotion}. "
            f"Must be one of: {', '.join(sorted(_VALID_EMOTIONS))}"
        }

    frustration = _clamp(frustration)
    confidence = _clamp(confidence)
    fatigue = _clamp(fatigue)
    excitement = _clamp(excitement)

    support_level = _determine_support_level(frustration, fatigue)
    action_recommended = _determine_action(frustration, fatigue)

    emotion_data: dict[str, object] = {
        "frustration": frustration,
        "confidence": confidence,
        "fatigue": fatigue,
        "excitement": excitement,
        "primary_emotion": primary_emotion,
        "support_level": support_level,
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
    }

    state: dict[str, Any] = tool_context.state if tool_context is not None else {}
    state["emotion"] = emotion_data

    return {
        "primary_emotion": primary_emotion,
        "support_level": support_level,
        "action_recommended": action_recommended,
    }


update_emotion_tool = FunctionTool(func=update_emotion)
