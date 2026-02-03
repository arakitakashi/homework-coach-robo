"""SocraticDialogueManager のテスト"""

from datetime import datetime

import pytest

from app.services.adk.dialogue.models import (
    DialogueContext,
    DialogueTone,
    QuestionType,
)


class TestSystemPrompt:
    """SYSTEM_PROMPT 定数のテスト"""

    def test_system_prompt_exists(self):
        """SYSTEM_PROMPTが定義されている"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        assert hasattr(SocraticDialogueManager, "SYSTEM_PROMPT")
        assert isinstance(SocraticDialogueManager.SYSTEM_PROMPT, str)

    def test_system_prompt_contains_core_principles(self):
        """SYSTEM_PROMPTにコア原則が含まれている"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        prompt = SocraticDialogueManager.SYSTEM_PROMPT

        # ソクラテス式対話の原則
        assert "答え" in prompt  # 答えを直接教えない
        assert "質問" in prompt  # 質問で導く

        # 対象年齢への配慮
        assert "小学" in prompt or "低学年" in prompt

    def test_system_prompt_contains_safety_guidelines(self):
        """SYSTEM_PROMPTに安全ガイドラインが含まれている"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        prompt = SocraticDialogueManager.SYSTEM_PROMPT

        # 子供に対する配慮
        assert "責め" in prompt or "肯定" in prompt  # 間違いを責めない / 肯定的に受け止める


class TestBuildQuestionPrompt:
    """build_question_prompt() メソッドのテスト"""

    @pytest.fixture
    def manager(self):
        """SocraticDialogueManagerインスタンス"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self):
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_build_question_prompt_understanding_check(self, manager, basic_context):
        """理解確認タイプのプロンプトを構築できる"""
        prompt = manager.build_question_prompt(
            context=basic_context,
            question_type=QuestionType.UNDERSTANDING_CHECK,
            tone=DialogueTone.ENCOURAGING,
        )

        # プロンプトは文字列
        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # 問題文が含まれている
        assert basic_context.problem in prompt

        # 理解確認のキーワード
        assert "理解" in prompt or "問題" in prompt or "聞いて" in prompt

    def test_build_question_prompt_understanding_check_empathetic(
        self, manager, basic_context
    ):
        """共感トーンでの理解確認プロンプト"""
        prompt = manager.build_question_prompt(
            context=basic_context,
            question_type=QuestionType.UNDERSTANDING_CHECK,
            tone=DialogueTone.EMPATHETIC,
        )

        # 共感的なトーンの指示が含まれている
        assert "共感" in prompt or "寄り添" in prompt or "優しく" in prompt
