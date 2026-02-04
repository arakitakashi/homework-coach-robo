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
        from pydantic import ValidationError

        from app.services.adk.dialogue.models import ResponseAnalysis

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


class TestDialogueContext:
    """DialogueContext Pydanticモデルのテスト"""

    def test_dialogue_context_creation(self):
        """DialogueContextを作成できる"""
        from app.services.adk.dialogue.models import DialogueContext, DialogueTone

        context = DialogueContext(
            session_id="session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        assert context.session_id == "session-123"
        assert context.problem == "3 + 5 = ?"
        assert context.current_hint_level == 1
        assert context.tone == DialogueTone.ENCOURAGING
        assert context.turns == []

    def test_dialogue_context_with_turns(self):
        """DialogueContextにターンを追加できる"""
        from datetime import datetime

        from app.services.adk.dialogue.models import (
            DialogueContext,
            DialogueTone,
            DialogueTurn,
            QuestionType,
        )

        turns = [
            DialogueTurn(
                role="assistant",
                content="この問題は何を聞いていると思う？",
                timestamp=datetime(2026, 2, 2, 10, 0, 0),
                question_type=QuestionType.UNDERSTANDING_CHECK,
            ),
            DialogueTurn(
                role="child",
                content="足し算をする問題だと思う",
                timestamp=datetime(2026, 2, 2, 10, 0, 5),
            ),
        ]

        context = DialogueContext(
            session_id="session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=turns,
        )

        assert len(context.turns) == 2
        assert context.turns[0].role == "assistant"
        assert context.turns[1].role == "child"

    def test_dialogue_context_hint_level_range(self):
        """current_hint_levelは1-3の範囲"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.models import DialogueContext, DialogueTone

        # 有効な範囲
        for level in [1, 2, 3]:
            context = DialogueContext(
                session_id="session-123",
                problem="3 + 5 = ?",
                current_hint_level=level,
                tone=DialogueTone.NEUTRAL,
                turns=[],
            )
            assert context.current_hint_level == level

        # 無効な範囲
        with pytest.raises(ValidationError):
            DialogueContext(
                session_id="session-123",
                problem="3 + 5 = ?",
                current_hint_level=0,
                tone=DialogueTone.NEUTRAL,
                turns=[],
            )

        with pytest.raises(ValidationError):
            DialogueContext(
                session_id="session-123",
                problem="3 + 5 = ?",
                current_hint_level=4,
                tone=DialogueTone.NEUTRAL,
                turns=[],
            )

    def test_dialogue_context_default_values(self):
        """DialogueContextのデフォルト値"""
        from app.services.adk.dialogue.models import DialogueContext, DialogueTone

        context = DialogueContext(
            session_id="session-123",
            problem="3 + 5 = ?",
        )

        assert context.current_hint_level == 1
        assert context.tone == DialogueTone.ENCOURAGING
        assert context.turns == []


class TestFromAdkSession:
    """from_adk_session()ファクトリメソッドのテスト"""

    def test_from_adk_session_basic(self):
        """基本的なADKセッションからDialogueContextを作成"""
        from unittest.mock import MagicMock

        from app.services.adk.dialogue.models import DialogueContext, DialogueTone

        # ADKセッションのモック
        mock_session = MagicMock()
        mock_session.id = "adk-session-123"
        mock_session.state = {
            "problem": "3 + 5 = ?",
            "current_hint_level": 2,
            "tone": "neutral",
        }

        context = DialogueContext.from_adk_session(mock_session)

        assert context.session_id == "adk-session-123"
        assert context.problem == "3 + 5 = ?"
        assert context.current_hint_level == 2
        assert context.tone == DialogueTone.NEUTRAL
        assert context.turns == []

    def test_from_adk_session_with_empty_state(self):
        """空のstateを持つADKセッションからDialogueContextを作成"""
        from unittest.mock import MagicMock

        from app.services.adk.dialogue.models import DialogueContext, DialogueTone

        mock_session = MagicMock()
        mock_session.id = "adk-session-456"
        mock_session.state = {}

        context = DialogueContext.from_adk_session(mock_session)

        assert context.session_id == "adk-session-456"
        assert context.problem == ""
        assert context.current_hint_level == 1
        assert context.tone == DialogueTone.ENCOURAGING
        assert context.turns == []

    def test_from_adk_session_with_none_state(self):
        """stateがNoneのADKセッションからDialogueContextを作成"""
        from unittest.mock import MagicMock

        from app.services.adk.dialogue.models import DialogueContext, DialogueTone

        mock_session = MagicMock()
        mock_session.id = "adk-session-789"
        mock_session.state = None

        context = DialogueContext.from_adk_session(mock_session)

        assert context.session_id == "adk-session-789"
        assert context.problem == ""
        assert context.current_hint_level == 1
        assert context.tone == DialogueTone.ENCOURAGING


class TestHintLevel:
    """HintLevel Enumのテスト"""

    def test_hint_level_has_problem_understanding(self):
        """問題理解の確認レベルが存在する"""
        from app.services.adk.dialogue.models import HintLevel

        assert HintLevel.PROBLEM_UNDERSTANDING == 1

    def test_hint_level_has_prior_knowledge(self):
        """既習事項の想起レベルが存在する"""
        from app.services.adk.dialogue.models import HintLevel

        assert HintLevel.PRIOR_KNOWLEDGE == 2

    def test_hint_level_has_partial_support(self):
        """部分的支援レベルが存在する"""
        from app.services.adk.dialogue.models import HintLevel

        assert HintLevel.PARTIAL_SUPPORT == 3

    def test_hint_level_is_int_enum(self):
        """HintLevelはint Enumである"""
        from app.services.adk.dialogue.models import HintLevel

        assert isinstance(HintLevel.PROBLEM_UNDERSTANDING.value, int)
        assert isinstance(HintLevel.PROBLEM_UNDERSTANDING, int)


class TestAnswerRequestType:
    """AnswerRequestType Enumのテスト"""

    def test_answer_request_type_has_none(self):
        """リクエストなしタイプが存在する"""
        from app.services.adk.dialogue.models import AnswerRequestType

        assert AnswerRequestType.NONE.value == "none"

    def test_answer_request_type_has_explicit(self):
        """明示的リクエストタイプが存在する"""
        from app.services.adk.dialogue.models import AnswerRequestType

        assert AnswerRequestType.EXPLICIT.value == "explicit"

    def test_answer_request_type_has_implicit(self):
        """暗示的リクエストタイプが存在する"""
        from app.services.adk.dialogue.models import AnswerRequestType

        assert AnswerRequestType.IMPLICIT.value == "implicit"

    def test_answer_request_type_is_string_enum(self):
        """AnswerRequestTypeはstr Enumである"""
        from app.services.adk.dialogue.models import AnswerRequestType

        assert isinstance(AnswerRequestType.NONE.value, str)
        assert isinstance(AnswerRequestType.NONE, str)


class TestAnswerRequestAnalysis:
    """AnswerRequestAnalysis Pydanticモデルのテスト"""

    def test_answer_request_analysis_creation(self):
        """AnswerRequestAnalysisを作成できる"""
        from app.services.adk.dialogue.models import (
            AnswerRequestAnalysis,
            AnswerRequestType,
        )

        analysis = AnswerRequestAnalysis(
            request_type=AnswerRequestType.EXPLICIT,
            confidence=0.95,
            detected_phrases=["答え教えて"],
        )

        assert analysis.request_type == AnswerRequestType.EXPLICIT
        assert analysis.confidence == 0.95
        assert analysis.detected_phrases == ["答え教えて"]

    def test_answer_request_analysis_confidence_range(self):
        """confidenceは0.0-1.0の範囲"""
        from pydantic import ValidationError

        from app.services.adk.dialogue.models import (
            AnswerRequestAnalysis,
            AnswerRequestType,
        )

        # 有効な範囲
        analysis = AnswerRequestAnalysis(
            request_type=AnswerRequestType.NONE,
            confidence=0.0,
            detected_phrases=[],
        )
        assert analysis.confidence == 0.0

        analysis = AnswerRequestAnalysis(
            request_type=AnswerRequestType.NONE,
            confidence=1.0,
            detected_phrases=[],
        )
        assert analysis.confidence == 1.0

        # 無効な範囲
        with pytest.raises(ValidationError):
            AnswerRequestAnalysis(
                request_type=AnswerRequestType.NONE,
                confidence=-0.1,
                detected_phrases=[],
            )

        with pytest.raises(ValidationError):
            AnswerRequestAnalysis(
                request_type=AnswerRequestType.NONE,
                confidence=1.1,
                detected_phrases=[],
            )

    def test_answer_request_analysis_default_phrases(self):
        """detected_phrasesはデフォルトで空リスト"""
        from app.services.adk.dialogue.models import (
            AnswerRequestAnalysis,
            AnswerRequestType,
        )

        analysis = AnswerRequestAnalysis(
            request_type=AnswerRequestType.IMPLICIT,
            confidence=0.7,
        )

        assert analysis.detected_phrases == []
