"""SocraticDialogueManager のテスト"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.adk.dialogue.models import (
    DialogueContext,
    DialogueTone,
    QuestionType,
    ResponseAnalysis,
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

    def test_build_question_prompt_thinking_guide(self, manager, basic_context):
        """思考誘導タイプのプロンプトを構築できる"""
        prompt = manager.build_question_prompt(
            context=basic_context,
            question_type=QuestionType.THINKING_GUIDE,
            tone=DialogueTone.NEUTRAL,
        )

        # プロンプトは文字列
        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # 問題文が含まれている
        assert basic_context.problem in prompt

        # 思考誘導のキーワード
        assert "思考" in prompt or "導" in prompt or "もし" in prompt

    def test_build_question_prompt_hint(self, manager, basic_context):
        """ヒントタイプのプロンプトを構築できる"""
        prompt = manager.build_question_prompt(
            context=basic_context,
            question_type=QuestionType.HINT,
            tone=DialogueTone.ENCOURAGING,
        )

        # ヒントのキーワード
        assert "ヒント" in prompt or "前に" in prompt or "似た" in prompt


class TestBuildAnalysisPrompt:
    """build_analysis_prompt() メソッドのテスト"""

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

    def test_build_analysis_prompt_contains_child_response(self, manager, basic_context):
        """子供の回答がプロンプトに含まれる"""
        child_response = "えっと、8かな？"

        prompt = manager.build_analysis_prompt(
            child_response=child_response,
            context=basic_context,
        )

        assert isinstance(prompt, str)
        assert child_response in prompt

    def test_build_analysis_prompt_contains_problem(self, manager, basic_context):
        """問題文がプロンプトに含まれる"""
        prompt = manager.build_analysis_prompt(
            child_response="わからない",
            context=basic_context,
        )

        assert basic_context.problem in prompt

    def test_build_analysis_prompt_requests_json_format(self, manager, basic_context):
        """JSON形式での回答を要求する"""
        prompt = manager.build_analysis_prompt(
            child_response="3たす5は8だよ",
            context=basic_context,
        )

        # JSONフォーマットに関する指示
        assert "JSON" in prompt or "json" in prompt

    def test_build_analysis_prompt_requests_analysis_fields(self, manager, basic_context):
        """分析に必要なフィールドを要求する"""
        prompt = manager.build_analysis_prompt(
            child_response="うーん、難しい",
            context=basic_context,
        )

        # ResponseAnalysisの各フィールド
        assert "understanding_level" in prompt or "理解度" in prompt
        assert "is_correct_direction" in prompt or "正しい方向" in prompt


class TestAnalyzeResponse:
    """analyze_response() メソッドのテスト"""

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

    @pytest.fixture
    def mock_llm_client(self):
        """モック化されたLLMクライアント"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_analyze_response_correct_understanding(
        self, basic_context, mock_llm_client
    ):
        """正しい理解の場合のResponseAnalysisを返す"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        # LLMの応答をモック
        mock_llm_client.generate.return_value = """{
            "understanding_level": 8,
            "is_correct_direction": true,
            "needs_clarification": false,
            "key_insights": ["足し算の概念を理解している"]
        }"""

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        result = await manager.analyze_response(
            child_response="8だよ！",
            context=basic_context,
        )

        assert isinstance(result, ResponseAnalysis)
        assert result.understanding_level == 8
        assert result.is_correct_direction is True
        assert result.needs_clarification is False
        assert "足し算の概念を理解している" in result.key_insights

    @pytest.mark.asyncio
    async def test_analyze_response_misconception(
        self, basic_context, mock_llm_client
    ):
        """誤解がある場合のResponseAnalysisを返す"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        # LLMの応答をモック（誤解のケース）
        mock_llm_client.generate.return_value = """{
            "understanding_level": 3,
            "is_correct_direction": false,
            "needs_clarification": true,
            "key_insights": ["引き算と混同している可能性がある"]
        }"""

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        result = await manager.analyze_response(
            child_response="2かな？",
            context=basic_context,
        )

        assert isinstance(result, ResponseAnalysis)
        assert result.understanding_level == 3
        assert result.is_correct_direction is False
        assert result.needs_clarification is True

    @pytest.mark.asyncio
    async def test_analyze_response_calls_llm_with_prompt(
        self, basic_context, mock_llm_client
    ):
        """LLMクライアントに正しいプロンプトを渡す"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        mock_llm_client.generate.return_value = """{
            "understanding_level": 5,
            "is_correct_direction": true,
            "needs_clarification": false,
            "key_insights": []
        }"""

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        await manager.analyze_response(
            child_response="うーん",
            context=basic_context,
        )

        # LLMが呼び出されたことを確認
        mock_llm_client.generate.assert_called_once()

        # プロンプトに必要な情報が含まれていることを確認
        call_args = mock_llm_client.generate.call_args
        prompt = call_args[0][0] if call_args[0] else call_args[1].get("prompt", "")
        assert basic_context.problem in prompt
        assert "うーん" in prompt
