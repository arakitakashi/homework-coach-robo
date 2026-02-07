"""check_curriculum_tool のテスト"""


class TestCheckCurriculumMath:
    """算数カリキュラムのテスト"""

    def test_grade1_addition(self) -> None:
        """1年生の足し算カリキュラムを取得できる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="math", topic="addition")
        assert len(result["learning_objectives"]) > 0
        assert len(result["common_mistakes"]) > 0
        assert len(result["teaching_strategies"]) > 0

    def test_grade2_multiplication(self) -> None:
        """2年生の掛け算カリキュラムを取得できる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=2, subject="math", topic="multiplication")
        assert len(result["learning_objectives"]) > 0

    def test_grade3_division(self) -> None:
        """3年生の割り算カリキュラムを取得できる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=3, subject="math", topic="division")
        assert len(result["learning_objectives"]) > 0

    def test_grade1_subtraction(self) -> None:
        """1年生の引き算カリキュラムを取得できる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="math", topic="subtraction")
        assert len(result["learning_objectives"]) > 0


class TestCheckCurriculumJapanese:
    """国語カリキュラムのテスト"""

    def test_grade1_hiragana(self) -> None:
        """1年生のひらがなカリキュラムを取得できる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="japanese", topic="hiragana")
        assert len(result["learning_objectives"]) > 0

    def test_grade2_kanji(self) -> None:
        """2年生の漢字カリキュラムを取得できる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=2, subject="japanese", topic="kanji")
        assert len(result["learning_objectives"]) > 0


class TestCheckCurriculumUnknown:
    """未知のカリキュラムのテスト"""

    def test_unknown_topic_returns_general_info(self) -> None:
        """未知のトピックでも一般的な情報を返す"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="math", topic="unknown_topic")
        assert "learning_objectives" in result
        assert len(result["teaching_strategies"]) > 0

    def test_unknown_subject_returns_general_info(self) -> None:
        """未知の教科でも一般的な情報を返す"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="science", topic="weather")
        assert "learning_objectives" in result

    def test_invalid_grade_returns_general_info(self) -> None:
        """無効な学年でも一般的な情報を返す"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=5, subject="math", topic="addition")
        assert "learning_objectives" in result


class TestCheckCurriculumReturnKeys:
    """返り値のキー確認テスト"""

    def test_returns_required_keys(self) -> None:
        """必要なキーがすべて含まれる"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="math", topic="addition")
        assert "prerequisites" in result
        assert "learning_objectives" in result
        assert "common_mistakes" in result
        assert "teaching_strategies" in result
        assert "related_topics" in result

    def test_all_values_are_lists(self) -> None:
        """すべての値がリストである"""
        from app.services.adk.tools.curriculum import check_curriculum

        result = check_curriculum(grade_level=1, subject="math", topic="addition")
        assert isinstance(result["prerequisites"], list)
        assert isinstance(result["learning_objectives"], list)
        assert isinstance(result["common_mistakes"], list)
        assert isinstance(result["teaching_strategies"], list)
        assert isinstance(result["related_topics"], list)


class TestCheckCurriculumTool:
    """check_curriculum_tool FunctionTool のテスト"""

    def test_is_function_tool_instance(self) -> None:
        """FunctionTool インスタンスである"""
        from google.adk.tools import FunctionTool

        from app.services.adk.tools.curriculum import check_curriculum_tool

        assert isinstance(check_curriculum_tool, FunctionTool)
