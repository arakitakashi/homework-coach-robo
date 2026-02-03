"""SocraticDialogueManager のテスト"""

from datetime import datetime
from unittest.mock import AsyncMock

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

    def test_build_question_prompt_understanding_check_empathetic(self, manager, basic_context):
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
    async def test_analyze_response_correct_understanding(self, basic_context, mock_llm_client):
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
    async def test_analyze_response_misconception(self, basic_context, mock_llm_client):
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
    async def test_analyze_response_calls_llm_with_prompt(self, basic_context, mock_llm_client):
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


class TestDetermineQuestionType:
    """determine_question_type() メソッドのテスト"""

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

    def test_determine_question_type_low_understanding(self, manager, basic_context):
        """理解度が低い場合は理解確認を返す"""
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.determine_question_type(analysis, basic_context)

        assert result == QuestionType.UNDERSTANDING_CHECK

    def test_determine_question_type_medium_understanding(self, manager, basic_context):
        """理解度が中程度で正しい方向なら思考誘導を返す"""
        analysis = ResponseAnalysis(
            understanding_level=5,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["部分的に理解している"],
        )

        result = manager.determine_question_type(analysis, basic_context)

        assert result == QuestionType.THINKING_GUIDE

    def test_determine_question_type_needs_hint(self, manager):
        """高ヒントレベルでclarification必要ならヒントを返す"""
        context = DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=2,  # ヒントレベル2
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )
        analysis = ResponseAnalysis(
            understanding_level=4,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.determine_question_type(analysis, context)

        assert result == QuestionType.HINT


class TestDetermineTone:
    """determine_tone() メソッドのテスト"""

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

    def test_determine_tone_encouraging_for_correct_direction(self, manager, basic_context):
        """正しい方向に進んでいる場合は励ましトーン"""
        analysis = ResponseAnalysis(
            understanding_level=6,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["良い理解"],
        )

        result = manager.determine_tone(analysis, basic_context)

        assert result == DialogueTone.ENCOURAGING

    def test_determine_tone_empathetic_for_struggling(self, manager, basic_context):
        """理解に苦しんでいる場合は共感トーン"""
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.determine_tone(analysis, basic_context)

        assert result == DialogueTone.EMPATHETIC

    def test_determine_tone_neutral_for_medium_understanding(self, manager, basic_context):
        """中程度の理解度では中立トーン"""
        analysis = ResponseAnalysis(
            understanding_level=5,
            is_correct_direction=False,
            needs_clarification=False,
            key_insights=[],
        )

        result = manager.determine_tone(analysis, basic_context)

        assert result == DialogueTone.NEUTRAL


class TestGenerateQuestion:
    """generate_question() メソッドのテスト"""

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
    async def test_generate_question_returns_llm_response(self, basic_context, mock_llm_client):
        """LLMの応答を返す"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        mock_llm_client.generate.return_value = "この問題は何を聞いていると思う？"

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        result = await manager.generate_question(
            context=basic_context,
            question_type=QuestionType.UNDERSTANDING_CHECK,
            tone=DialogueTone.ENCOURAGING,
        )

        assert result == "この問題は何を聞いていると思う？"

    @pytest.mark.asyncio
    async def test_generate_question_calls_build_question_prompt(
        self, basic_context, mock_llm_client
    ):
        """build_question_promptで生成したプロンプトをLLMに渡す"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        mock_llm_client.generate.return_value = "質問です"

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        await manager.generate_question(
            context=basic_context,
            question_type=QuestionType.THINKING_GUIDE,
            tone=DialogueTone.NEUTRAL,
        )

        # LLMが呼び出されたことを確認
        mock_llm_client.generate.assert_called_once()

        # プロンプトに問題が含まれていることを確認
        call_args = mock_llm_client.generate.call_args
        prompt = call_args[0][0] if call_args[0] else call_args[1].get("prompt", "")
        assert basic_context.problem in prompt

    @pytest.mark.asyncio
    async def test_generate_question_tracks_question_history(self, basic_context, mock_llm_client):
        """生成した質問を履歴に追加する"""
        from app.services.adk.dialogue.manager import SocraticDialogueManager

        mock_llm_client.generate.return_value = "最初の質問"

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        await manager.generate_question(
            context=basic_context,
            question_type=QuestionType.UNDERSTANDING_CHECK,
            tone=DialogueTone.ENCOURAGING,
        )

        # 履歴に追加されていることを確認
        assert "最初の質問" in manager.question_history


class TestShouldMoveToNextPhase:
    """should_move_to_next_phase() メソッドのテスト"""

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

    def test_should_not_move_when_understanding_is_improving(self, manager, basic_context):
        """理解度が改善している場合は次のフェーズに進まない"""
        analysis = ResponseAnalysis(
            understanding_level=6,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["理解が進んでいる"],
        )

        result = manager.should_move_to_next_phase(analysis, basic_context)

        assert result is False

    def test_should_move_when_struggling_at_current_level(self, manager):
        """現在のレベルで苦戦している場合は次のフェーズに進む"""
        from app.services.adk.dialogue.models import DialogueTurn

        # 複数ターン経過後も理解度が低い
        context = DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="質問2",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="うーん",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ],
        )
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.should_move_to_next_phase(analysis, context)

        assert result is True

    def test_should_not_move_beyond_max_hint_level(self, manager):
        """最大ヒントレベルに達している場合は進まない"""
        from app.services.adk.dialogue.models import DialogueTurn

        context = DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=3,  # 最大レベル
            tone=DialogueTone.ENCOURAGING,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
            ],
        )
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.should_move_to_next_phase(analysis, context)

        assert result is False
