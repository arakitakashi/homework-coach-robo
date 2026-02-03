"""SocraticDialogueManager のテスト"""

import pytest


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
