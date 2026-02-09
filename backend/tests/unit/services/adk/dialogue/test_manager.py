"""SocraticDialogueManager のテスト"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.services.adk.dialogue.manager import SocraticDialogueManager
from app.services.adk.dialogue.models import (
    DialogueContext,
    DialogueTone,
    QuestionType,
    ResponseAnalysis,
)


class TestSystemPrompt:
    """SYSTEM_PROMPT 定数のテスト"""

    def test_system_prompt_exists(self) -> None:
        """SYSTEM_PROMPTが定義されている"""
        assert hasattr(SocraticDialogueManager, "SYSTEM_PROMPT")
        assert isinstance(SocraticDialogueManager.SYSTEM_PROMPT, str)

    def test_system_prompt_contains_core_principles(self) -> None:
        """SYSTEM_PROMPTにコア原則が含まれている"""
        prompt = SocraticDialogueManager.SYSTEM_PROMPT

        # ソクラテス式対話の原則
        assert "答え" in prompt  # 答えを直接教えない
        assert "質問" in prompt  # 質問で導く

        # 対象年齢への配慮
        assert "小学" in prompt or "低学年" in prompt

    def test_system_prompt_contains_safety_guidelines(self) -> None:
        """SYSTEM_PROMPTに安全ガイドラインが含まれている"""
        prompt = SocraticDialogueManager.SYSTEM_PROMPT

        # 子供に対する配慮
        assert "責め" in prompt or "肯定" in prompt  # 間違いを責めない / 肯定的に受け止める


class TestBuildQuestionPrompt:
    """build_question_prompt() メソッドのテスト"""

    @pytest.fixture
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_build_question_prompt_understanding_check(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
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
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """共感トーンでの理解確認プロンプト"""
        prompt = manager.build_question_prompt(
            context=basic_context,
            question_type=QuestionType.UNDERSTANDING_CHECK,
            tone=DialogueTone.EMPATHETIC,
        )

        # 共感的なトーンの指示が含まれている
        assert "共感" in prompt or "寄り添" in prompt or "優しく" in prompt

    def test_build_question_prompt_thinking_guide(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
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

    def test_build_question_prompt_hint(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
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
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_build_analysis_prompt_contains_child_response(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """子供の回答がプロンプトに含まれる"""
        child_response = "えっと、8かな？"

        prompt = manager.build_analysis_prompt(
            child_response=child_response,
            context=basic_context,
        )

        assert isinstance(prompt, str)
        assert child_response in prompt

    def test_build_analysis_prompt_contains_problem(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """問題文がプロンプトに含まれる"""
        prompt = manager.build_analysis_prompt(
            child_response="わからない",
            context=basic_context,
        )

        assert basic_context.problem in prompt

    def test_build_analysis_prompt_requests_json_format(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """JSON形式での回答を要求する"""
        prompt = manager.build_analysis_prompt(
            child_response="3たす5は8だよ",
            context=basic_context,
        )

        # JSONフォーマットに関する指示
        assert "JSON" in prompt or "json" in prompt

    def test_build_analysis_prompt_requests_analysis_fields(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
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
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    @pytest.fixture
    def mock_llm_client(self) -> AsyncMock:
        """モック化されたLLMクライアント"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_analyze_response_correct_understanding(
        self, basic_context: DialogueContext, mock_llm_client: AsyncMock
    ) -> None:
        """正しい理解の場合のResponseAnalysisを返す"""
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
        self, basic_context: DialogueContext, mock_llm_client: AsyncMock
    ) -> None:
        """誤解がある場合のResponseAnalysisを返す"""
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
        self, basic_context: DialogueContext, mock_llm_client: AsyncMock
    ) -> None:
        """LLMクライアントに正しいプロンプトを渡す"""
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
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_determine_question_type_low_understanding(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """理解度が低い場合は理解確認を返す"""
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.determine_question_type(analysis, basic_context)

        assert result == QuestionType.UNDERSTANDING_CHECK

    def test_determine_question_type_medium_understanding(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """理解度が中程度で正しい方向なら思考誘導を返す"""
        analysis = ResponseAnalysis(
            understanding_level=5,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["部分的に理解している"],
        )

        result = manager.determine_question_type(analysis, basic_context)

        assert result == QuestionType.THINKING_GUIDE

    def test_determine_question_type_needs_hint(self, manager: SocraticDialogueManager) -> None:
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
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_determine_tone_encouraging_for_correct_direction(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """正しい方向に進んでいる場合は励ましトーン"""
        analysis = ResponseAnalysis(
            understanding_level=6,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["良い理解"],
        )

        result = manager.determine_tone(analysis, basic_context)

        assert result == DialogueTone.ENCOURAGING

    def test_determine_tone_empathetic_for_struggling(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """理解に苦しんでいる場合は共感トーン"""
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        result = manager.determine_tone(analysis, basic_context)

        assert result == DialogueTone.EMPATHETIC

    def test_determine_tone_neutral_for_medium_understanding(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
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
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    @pytest.fixture
    def mock_llm_client(self) -> AsyncMock:
        """モック化されたLLMクライアント"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_generate_question_returns_llm_response(
        self, basic_context: DialogueContext, mock_llm_client: AsyncMock
    ) -> None:
        """LLMの応答を返す"""
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
        self, basic_context: DialogueContext, mock_llm_client: AsyncMock
    ) -> None:
        """build_question_promptで生成したプロンプトをLLMに渡す"""
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
    async def test_generate_question_tracks_question_history(
        self, basic_context: DialogueContext, mock_llm_client: AsyncMock
    ) -> None:
        """生成した質問を履歴に追加する"""
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
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_should_not_move_when_understanding_is_improving(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """理解度が改善している場合は次のフェーズに進まない"""
        analysis = ResponseAnalysis(
            understanding_level=6,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["理解が進んでいる"],
        )

        result = manager.should_move_to_next_phase(analysis, basic_context)

        assert result is False

    def test_should_move_when_struggling_at_current_level(
        self, manager: SocraticDialogueManager
    ) -> None:
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

    def test_should_not_move_beyond_max_hint_level(self, manager: SocraticDialogueManager) -> None:
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


class TestDetectAnswerRequestKeywords:
    """_detect_answer_request_keywords() メソッドのテスト（キーワードベースの検出）"""

    @pytest.fixture
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    def test_detect_explicit_answer_request(self, manager: SocraticDialogueManager) -> None:
        """明示的な答えリクエストを検出できる"""
        from app.services.adk.dialogue.models import AnswerRequestType

        # 明示的なリクエストフレーズ
        test_cases = [
            "答え教えて",
            "答えを教えてよ",
            "正解は？",
            "正解を言って",
            "もう答え言って",
        ]

        for phrase in test_cases:
            result = manager._detect_answer_request_keywords(phrase)
            assert result.request_type == AnswerRequestType.EXPLICIT, f"Failed for: {phrase}"
            assert result.confidence >= 0.8
            assert len(result.detected_phrases) > 0

    def test_detect_implicit_answer_request(self, manager: SocraticDialogueManager) -> None:
        """暗示的な答えリクエストを検出できる"""
        from app.services.adk.dialogue.models import AnswerRequestType

        # 暗示的なリクエストフレーズ
        test_cases = [
            "できない",
            "むずかしい",
            "わからない",
            "ギブアップ",
            "無理だよ",
        ]

        for phrase in test_cases:
            result = manager._detect_answer_request_keywords(phrase)
            assert result.request_type == AnswerRequestType.IMPLICIT, f"Failed for: {phrase}"
            assert result.confidence >= 0.6
            assert len(result.detected_phrases) > 0

    def test_no_answer_request(self, manager: SocraticDialogueManager) -> None:
        """通常の回答はリクエストなしと判定される"""
        from app.services.adk.dialogue.models import AnswerRequestType

        # 通常の回答
        test_cases = [
            "3と5を足すんだと思う",
            "8かな？",
            "足し算だよね",
            "うーん、考えてる",
        ]

        for phrase in test_cases:
            result = manager._detect_answer_request_keywords(phrase)
            assert result.request_type == AnswerRequestType.NONE, f"Failed for: {phrase}"
            assert result.detected_phrases == []


class TestDetectAnswerRequest:
    """detect_answer_request() メソッドのテスト（LLM補助検出）"""

    @pytest.fixture
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def manager_with_llm(self) -> SocraticDialogueManager:
        """LLMクライアント付きSocraticDialogueManagerインスタンス"""
        mock_llm = AsyncMock()
        return SocraticDialogueManager(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_detect_answer_request_uses_keywords_first(
        self, manager_with_llm: SocraticDialogueManager
    ) -> None:
        """キーワードマッチで検出できる場合はLLMを呼ばない"""
        from app.services.adk.dialogue.models import AnswerRequestType

        result = await manager_with_llm.detect_answer_request("答え教えて")

        assert result.request_type == AnswerRequestType.EXPLICIT
        # LLMは呼ばれない
        manager_with_llm._llm_client.generate.assert_not_called()  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_detect_answer_request_falls_back_to_llm(
        self, manager_with_llm: SocraticDialogueManager
    ) -> None:
        """キーワードマッチで検出できない場合はLLMを使用"""
        from app.services.adk.dialogue.models import AnswerRequestType

        # LLMの応答をモック
        _mock_response = """{
            "request_type": "implicit",
            "confidence": 0.75,
            "detected_phrases": ["もういいや"]
        }"""
        manager_with_llm._llm_client.generate.return_value = _mock_response  # type: ignore[union-attr]

        result = await manager_with_llm.detect_answer_request("もういいや、これ")

        assert result.request_type == AnswerRequestType.IMPLICIT
        assert result.confidence == 0.75
        manager_with_llm._llm_client.generate.assert_called_once()  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_detect_answer_request_without_llm_keywords_only(
        self, manager: SocraticDialogueManager
    ) -> None:
        """LLMなしでもキーワード検出は動作する"""
        from app.services.adk.dialogue.models import AnswerRequestType

        result = await manager.detect_answer_request("正解は？")

        assert result.request_type == AnswerRequestType.EXPLICIT

    @pytest.mark.asyncio
    async def test_detect_answer_request_without_llm_returns_none(
        self, manager: SocraticDialogueManager
    ) -> None:
        """LLMなしでキーワードに一致しない場合はNONEを返す"""
        from app.services.adk.dialogue.models import AnswerRequestType

        result = await manager.detect_answer_request("もういいや、これ")

        # LLMがないのでキーワードに一致しない曖昧な表現はNONE
        assert result.request_type == AnswerRequestType.NONE


class TestBuildHintPrompt:
    """build_hint_prompt() メソッドのテスト"""

    @pytest.fixture
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    def test_build_hint_prompt_level_1(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """レベル1: 問題理解の確認プロンプトを構築できる"""
        from app.services.adk.dialogue.models import HintLevel

        prompt = manager.build_hint_prompt(
            context=basic_context,
            hint_level=HintLevel.PROBLEM_UNDERSTANDING,
            tone=DialogueTone.ENCOURAGING,
        )

        # プロンプトは文字列
        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # 問題文が含まれている
        assert basic_context.problem in prompt

        # レベル1のキーワード（問題理解）
        assert "問題" in prompt or "理解" in prompt or "聞いて" in prompt

    def test_build_hint_prompt_level_2(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """レベル2: 既習事項の想起プロンプトを構築できる"""
        from app.services.adk.dialogue.models import HintLevel

        basic_context.current_hint_level = 2

        prompt = manager.build_hint_prompt(
            context=basic_context,
            hint_level=HintLevel.PRIOR_KNOWLEDGE,
            tone=DialogueTone.NEUTRAL,
        )

        # レベル2のキーワード（既習事項）
        assert "前" in prompt or "似た" in prompt or "やった" in prompt or "思い出" in prompt

    def test_build_hint_prompt_level_3(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """レベル3: 部分的支援プロンプトを構築できる"""
        from app.services.adk.dialogue.models import HintLevel

        basic_context.current_hint_level = 3

        prompt = manager.build_hint_prompt(
            context=basic_context,
            hint_level=HintLevel.PARTIAL_SUPPORT,
            tone=DialogueTone.EMPATHETIC,
        )

        # レベル3のキーワード（部分的支援）
        assert "最初" in prompt or "ステップ" in prompt or "分解" in prompt or "一緒" in prompt

        # 答えを教えない指示
        assert "答え" in prompt and ("教え" in prompt or "言わ" in prompt)

    def test_build_hint_prompt_with_answer_request(
        self, manager: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """答えリクエストがある場合は励ましを追加"""
        from app.services.adk.dialogue.models import HintLevel

        prompt = manager.build_hint_prompt(
            context=basic_context,
            hint_level=HintLevel.PROBLEM_UNDERSTANDING,
            tone=DialogueTone.ENCOURAGING,
            is_answer_request=True,
        )

        # 励ましの言葉が含まれている
        assert "励まし" in prompt or "大丈夫" in prompt or "一緒" in prompt or "頑張" in prompt


class TestGenerateHintResponse:
    """generate_hint_response() メソッドのテスト"""

    @pytest.fixture
    def manager_with_llm(self) -> SocraticDialogueManager:
        """LLMクライアント付きSocraticDialogueManagerインスタンス"""
        mock_llm = AsyncMock()
        return SocraticDialogueManager(llm_client=mock_llm)

    @pytest.fixture
    def basic_context(self) -> DialogueContext:
        """基本的なDialogueContext"""
        return DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    @pytest.mark.asyncio
    async def test_generate_hint_response_level_1(
        self, manager_with_llm: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """レベル1のヒントレスポンスを生成できる"""
        manager_with_llm._llm_client.generate.return_value = "この問題は何を聞いていると思う？"  # type: ignore[union-attr]

        response = await manager_with_llm.generate_hint_response(
            context=basic_context,
            is_answer_request=False,
        )

        assert response == "この問題は何を聞いていると思う？"
        manager_with_llm._llm_client.generate.assert_called_once()  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_generate_hint_response_level_2(
        self, manager_with_llm: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """レベル2のヒントレスポンスを生成できる"""
        basic_context.current_hint_level = 2
        manager_with_llm._llm_client.generate.return_value = "前に似た問題をやったよね？"  # type: ignore[union-attr]

        response = await manager_with_llm.generate_hint_response(
            context=basic_context,
            is_answer_request=False,
        )

        assert response == "前に似た問題をやったよね？"

    @pytest.mark.asyncio
    async def test_generate_hint_response_level_3(
        self, manager_with_llm: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """レベル3のヒントレスポンスを生成できる"""
        basic_context.current_hint_level = 3
        manager_with_llm._llm_client.generate.return_value = (  # type: ignore[union-attr]
            "最初のステップだけ一緒にやろう。3という数字があるよね。"
        )

        response = await manager_with_llm.generate_hint_response(
            context=basic_context,
            is_answer_request=False,
        )

        assert "最初" in response or "ステップ" in response

    @pytest.mark.asyncio
    async def test_generate_hint_response_with_answer_request(
        self, manager_with_llm: SocraticDialogueManager, basic_context: DialogueContext
    ) -> None:
        """答えリクエスト時は励ましを含むレスポンスを生成する"""
        manager_with_llm._llm_client.generate.return_value = (  # type: ignore[union-attr]
            "大丈夫だよ、一緒に考えよう！この問題は何を聞いていると思う？"
        )

        await manager_with_llm.generate_hint_response(
            context=basic_context,
            is_answer_request=True,
        )

        # プロンプトに励ましの指示が含まれていることを確認
        call_args = manager_with_llm._llm_client.generate.call_args  # type: ignore[union-attr]
        prompt = call_args[0][0]
        assert "大丈夫" in prompt or "一緒" in prompt or "励まし" in prompt

    @pytest.mark.asyncio
    async def test_generate_hint_response_without_llm_raises_error(
        self, basic_context: DialogueContext
    ) -> None:
        """LLMクライアントがない場合はエラー"""
        manager = SocraticDialogueManager()

        with pytest.raises(ValueError, match="LLM client"):
            await manager.generate_hint_response(context=basic_context)


class TestAdvanceHintLevel:
    """advance_hint_level() メソッドのテスト"""

    @pytest.fixture
    def manager(self) -> SocraticDialogueManager:
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    def test_advance_hint_level_stays_at_1_when_improving(
        self, manager: SocraticDialogueManager
    ) -> None:
        """理解度が改善している場合はレベル1のまま"""
        from app.services.adk.dialogue.models import DialogueTurn

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
                    content="足し算かな",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
            ],
        )
        analysis = ResponseAnalysis(
            understanding_level=6,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["足し算を理解"],
        )

        new_level = manager.advance_hint_level(context, analysis)

        assert new_level == 1  # レベル維持

    def test_advance_hint_level_from_1_to_2(self, manager: SocraticDialogueManager) -> None:
        """レベル1で苦戦している場合はレベル2へ"""
        from app.services.adk.dialogue.models import DialogueTurn

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

        new_level = manager.advance_hint_level(context, analysis)

        assert new_level == 2

    def test_advance_hint_level_from_2_to_3(self, manager: SocraticDialogueManager) -> None:
        """レベル2で苦戦している場合はレベル3へ"""
        from app.services.adk.dialogue.models import DialogueTurn

        context = DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=2,
            tone=DialogueTone.EMPATHETIC,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="前のやつも忘れた",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="質問2",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="やっぱりわからない",
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

        new_level = manager.advance_hint_level(context, analysis)

        assert new_level == 3

    def test_advance_hint_level_caps_at_3(self, manager: SocraticDialogueManager) -> None:
        """最大レベル3を超えない"""
        from app.services.adk.dialogue.models import DialogueTurn

        context = DialogueContext(
            session_id="test-session-123",
            problem="3 + 5 = ?",
            current_hint_level=3,
            tone=DialogueTone.EMPATHETIC,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="まだわからない",
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
            understanding_level=1,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        new_level = manager.advance_hint_level(context, analysis)

        assert new_level == 3  # 最大レベル維持

    def test_advance_hint_level_requires_minimum_turns(
        self, manager: SocraticDialogueManager
    ) -> None:
        """最低ターン数に満たない場合は進行しない"""
        from app.services.adk.dialogue.models import DialogueTurn

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
                # 1ターンのみ（最低2ターン必要）
            ],
        )
        analysis = ResponseAnalysis(
            understanding_level=1,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        new_level = manager.advance_hint_level(context, analysis)

        assert new_level == 1  # ターン数不足でレベル維持
