"""計算検証ツール

LLMの幻覚リスクを排除するため、四則演算を正確に検証する。
"""

import re

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

# 演算子の正規化マッピング
_OPERATOR_MAP: dict[str, str] = {
    "×": "*",
    "÷": "/",
    "x": "*",
    "X": "*",
}

# 学年別ヒントテンプレート
_HINTS_BY_GRADE: dict[int, str] = {
    1: "ゆびやブロックをつかって、もういちどかぞえてみよう！",
    2: "ひっさんでやってみよう。くりあがり・くりさがりに気をつけてね！",
    3: "もういちど、じゅんばんにけいさんしてみよう。とちゅうの答えをメモしてね！",
}


def _normalize_expression(expression: str) -> str:
    """式の演算子を Python で評価可能な形に正規化する"""
    normalized = expression.strip()
    for symbol, replacement in _OPERATOR_MAP.items():
        normalized = normalized.replace(symbol, replacement)
    return normalized


def _safe_evaluate(expression: str) -> float | None:
    """安全に算術式を評価する（eval を使わない）"""
    normalized = _normalize_expression(expression)

    # 数値と演算子のみで構成されているか検証
    if not re.match(r"^[\d\s\+\-\*/\.\(\)]+$", normalized):
        return None

    # トークン分割: 数値と演算子
    tokens = re.findall(r"(\d+\.?\d*|[+\-*/])", normalized)
    if not tokens:
        return None

    try:
        # 最初の数値を取得
        result = float(tokens[0])
        i = 1
        while i < len(tokens) - 1:
            operator = tokens[i]
            operand = float(tokens[i + 1])
            if operator == "+":
                result += operand
            elif operator == "-":
                result -= operand
            elif operator == "*":
                result *= operand
            elif operator == "/":
                if operand == 0:
                    return None
                result /= operand
            else:
                return None
            i += 2
    except (ValueError, IndexError):
        return None

    return result


def _format_answer(value: float) -> str:
    """数値をフォーマットする（整数なら小数点なし）"""
    if value == int(value):
        return str(int(value))
    return str(value)


def calculate_and_verify(
    expression: str,
    child_answer: str,
    grade_level: int,
) -> dict[str, object]:
    """四則演算の検証を行う

    Args:
        expression: 計算式（例: "23 + 45"）
        child_answer: 子供の回答（例: "68"）
        grade_level: 学年（1-3）
    """
    correct_value = _safe_evaluate(expression)

    if correct_value is None:
        return {
            "correct_answer": "",
            "is_correct": False,
            "error_type": "invalid_expression",
            "hint": "式をもういちどたしかめてみよう！",
        }

    correct_answer = _format_answer(correct_value)

    # 子供の回答を正規化して比較
    try:
        child_value = float(child_answer.strip())
        is_correct = abs(child_value - correct_value) < 1e-9
    except ValueError:
        is_correct = False

    if is_correct:
        return {
            "correct_answer": correct_answer,
            "is_correct": True,
            "error_type": None,
            "hint": "",
        }

    hint = _HINTS_BY_GRADE.get(grade_level, _HINTS_BY_GRADE[3])
    return {
        "correct_answer": correct_answer,
        "is_correct": False,
        "error_type": "calculation",
        "hint": hint,
    }


calculate_tool = FunctionTool(func=calculate_and_verify)
