"""ソクラテス式対話エンジン - データモデルのテスト"""

import pytest


class TestQuestionType:
    """QuestionType Enumのテスト"""

    def test_question_type_has_understanding_check(self):
        """理解確認タイプが存在する"""
        from app.services.adk.dialogue.models import QuestionType

        assert QuestionType.UNDERSTANDING_CHECK.value == "understanding_check"

    def test_question_type_has_thinking_guide(self):
        """思考誘導タイプが存在する"""
        from app.services.adk.dialogue.models import QuestionType

        assert QuestionType.THINKING_GUIDE.value == "thinking_guide"

    def test_question_type_has_hint(self):
        """ヒントタイプが存在する"""
        from app.services.adk.dialogue.models import QuestionType

        assert QuestionType.HINT.value == "hint"

    def test_question_type_is_string_enum(self):
        """QuestionTypeはstr Enumである"""
        from app.services.adk.dialogue.models import QuestionType

        assert isinstance(QuestionType.UNDERSTANDING_CHECK.value, str)
        assert isinstance(QuestionType.UNDERSTANDING_CHECK, str)


class TestDialogueTone:
    """DialogueTone Enumのテスト"""

    def test_dialogue_tone_has_encouraging(self):
        """励ましトーンが存在する"""
        from app.services.adk.dialogue.models import DialogueTone

        assert DialogueTone.ENCOURAGING.value == "encouraging"

    def test_dialogue_tone_has_neutral(self):
        """中立トーンが存在する"""
        from app.services.adk.dialogue.models import DialogueTone

        assert DialogueTone.NEUTRAL.value == "neutral"

    def test_dialogue_tone_has_empathetic(self):
        """共感トーンが存在する"""
        from app.services.adk.dialogue.models import DialogueTone

        assert DialogueTone.EMPATHETIC.value == "empathetic"

    def test_dialogue_tone_is_string_enum(self):
        """DialogueToneはstr Enumである"""
        from app.services.adk.dialogue.models import DialogueTone

        assert isinstance(DialogueTone.ENCOURAGING.value, str)
        assert isinstance(DialogueTone.ENCOURAGING, str)


class TestResponseAnalysis:
    """ResponseAnalysis Pydanticモデルのテスト"""

    def test_response_analysis_creation(self):
        """ResponseAnalysisを作成できる"""
        from app.services.adk.dialogue.models import ResponseAnalysis

        analysis = ResponseAnalysis(
            understanding_level=7,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["足し算の概念を理解している"],
        )

        assert analysis.understanding_level == 7
        assert analysis.is_correct_direction is True
        assert analysis.needs_clarification is False
        assert analysis.key_insights == ["足し算の概念を理解している"]

    def test_response_analysis_understanding_level_range(self):
        """understanding_levelは0-10の範囲"""
        from app.services.adk.dialogue.models import ResponseAnalysis
        from pydantic import ValidationError

        # 有効な範囲
        analysis = ResponseAnalysis(
            understanding_level=0,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=[],
        )
        assert analysis.understanding_level == 0

        analysis = ResponseAnalysis(
            understanding_level=10,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=[],
        )
        assert analysis.understanding_level == 10

        # 無効な範囲
        with pytest.raises(ValidationError):
            ResponseAnalysis(
                understanding_level=-1,
                is_correct_direction=True,
                needs_clarification=False,
                key_insights=[],
            )

        with pytest.raises(ValidationError):
            ResponseAnalysis(
                understanding_level=11,
                is_correct_direction=True,
                needs_clarification=False,
                key_insights=[],
            )


class TestDialogueTurn:
    """DialogueTurn Pydanticモデルのテスト"""

    def test_dialogue_turn_child_message(self):
        """子供のメッセージを作成できる"""
        from datetime import datetime

        from app.services.adk.dialogue.models import DialogueTurn

        turn = DialogueTurn(
            role="child",
            content="3と5を足すの？",
            timestamp=datetime(2026, 2, 2, 10, 0, 0),
        )

        assert turn.role == "child"
        assert turn.content == "3と5を足すの？"
        assert turn.timestamp == datetime(2026, 2, 2, 10, 0, 0)
        assert turn.question_type is None
        assert turn.response_analysis is None

    def test_dialogue_turn_assistant_message_with_question_type(self):
        """アシスタントのメッセージに質問タイプを設定できる"""
        from datetime import datetime

        from app.services.adk.dialogue.models import DialogueTurn, QuestionType

        turn = DialogueTurn(
            role="assistant",
            content="この問題は何を聞いていると思う？",
            timestamp=datetime(2026, 2, 2, 10, 0, 1),
            question_type=QuestionType.UNDERSTANDING_CHECK,
        )

        assert turn.role == "assistant"
        assert turn.content == "この問題は何を聞いていると思う？"
        assert turn.question_type == QuestionType.UNDERSTANDING_CHECK

    def test_dialogue_turn_with_response_analysis(self):
        """子供のメッセージに回答分析を付与できる"""
        from datetime import datetime

        from app.services.adk.dialogue.models import DialogueTurn, ResponseAnalysis

        analysis = ResponseAnalysis(
            understanding_level=6,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["問題の意図を理解している"],
        )

        turn = DialogueTurn(
            role="child",
            content="足し算をするんだと思う",
            timestamp=datetime(2026, 2, 2, 10, 0, 2),
            response_analysis=analysis,
        )

        assert turn.response_analysis is not None
        assert turn.response_analysis.understanding_level == 6

    def test_dialogue_turn_role_validation(self):
        """roleはchildまたはassistantのみ許可"""
        from datetime import datetime

        from pydantic import ValidationError

        from app.services.adk.dialogue.models import DialogueTurn

        # 有効なrole
        turn = DialogueTurn(
            role="child",
            content="テスト",
            timestamp=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert turn.role == "child"

        turn = DialogueTurn(
            role="assistant",
            content="テスト",
            timestamp=datetime(2026, 2, 2, 10, 0, 0),
        )
        assert turn.role == "assistant"

        # 無効なrole
        with pytest.raises(ValidationError):
            DialogueTurn(
                role="teacher",
                content="テスト",
                timestamp=datetime(2026, 2, 2, 10, 0, 0),
            )
