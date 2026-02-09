"""calculate_tool のテスト"""


class TestCalculateAndVerify:
    """calculate_and_verify 関数のテスト"""

    def test_correct_addition(self) -> None:
        """正しい足し算を検証できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="23 + 45", child_answer="68", grade_level=1)
        assert result["is_correct"] is True
        assert result["correct_answer"] == "68"
        assert result["error_type"] is None

    def test_incorrect_addition(self) -> None:
        """間違った足し算を検出できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="23 + 45", child_answer="67", grade_level=1)
        assert result["is_correct"] is False
        assert result["correct_answer"] == "68"
        assert result["error_type"] == "calculation"
        assert isinstance(result["hint"], str)
        assert len(result["hint"]) > 0

    def test_subtraction(self) -> None:
        """引き算を検証できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="50 - 23", child_answer="27", grade_level=2)
        assert result["is_correct"] is True
        assert result["correct_answer"] == "27"

    def test_multiplication(self) -> None:
        """掛け算を検証できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="6 × 7", child_answer="42", grade_level=2)
        assert result["is_correct"] is True
        assert result["correct_answer"] == "42"

    def test_multiplication_with_asterisk(self) -> None:
        """* 記号の掛け算を検証できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="6 * 7", child_answer="42", grade_level=2)
        assert result["is_correct"] is True

    def test_division(self) -> None:
        """割り算を検証できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="56 ÷ 8", child_answer="7", grade_level=3)
        assert result["is_correct"] is True
        assert result["correct_answer"] == "7"

    def test_division_with_slash(self) -> None:
        """/ 記号の割り算を検証できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="56 / 8", child_answer="7", grade_level=3)
        assert result["is_correct"] is True

    def test_division_by_zero(self) -> None:
        """ゼロ除算をエラーとして返す"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="10 ÷ 0", child_answer="0", grade_level=3)
        assert result["is_correct"] is False
        assert result["error_type"] == "invalid_expression"

    def test_invalid_expression(self) -> None:
        """無効な式をエラーとして返す"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="abc + xyz", child_answer="0", grade_level=1)
        assert result["is_correct"] is False
        assert result["error_type"] == "invalid_expression"

    def test_hint_for_grade_1(self) -> None:
        """1年生向けのヒントが返される"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="3 + 5", child_answer="9", grade_level=1)
        assert result["is_correct"] is False
        assert isinstance(result["hint"], str)
        assert len(result["hint"]) > 0

    def test_decimal_result(self) -> None:
        """小数結果は整数に丸められる（小学校低学年向け）"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="7 ÷ 2", child_answer="3.5", grade_level=3)
        assert result["correct_answer"] == "3.5"

    def test_integer_result_has_no_decimal(self) -> None:
        """整数結果に小数点がつかない"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="6 + 4", child_answer="10", grade_level=1)
        assert result["correct_answer"] == "10"
        assert isinstance(result["correct_answer"], str)
        assert "." not in result["correct_answer"]

    def test_whitespace_handling(self) -> None:
        """空白が含まれていても正しく計算できる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="  3  +  5  ", child_answer="8", grade_level=1)
        assert result["is_correct"] is True

    def test_returns_dict_with_required_keys(self) -> None:
        """必要なキーがすべて含まれる"""
        from app.services.adk.tools.calculate import calculate_and_verify

        result = calculate_and_verify(expression="1 + 1", child_answer="2", grade_level=1)
        assert "correct_answer" in result
        assert "is_correct" in result
        assert "error_type" in result
        assert "hint" in result


class TestCalculateTool:
    """calculate_tool FunctionTool のテスト"""

    def test_is_function_tool_instance(self) -> None:
        """FunctionTool インスタンスである"""
        from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

        from app.services.adk.tools.calculate import calculate_tool

        assert isinstance(calculate_tool, FunctionTool)
