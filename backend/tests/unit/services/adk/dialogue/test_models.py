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
