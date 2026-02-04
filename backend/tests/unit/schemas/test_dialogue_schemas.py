"""対話関連スキーマのテスト"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.dialogue import (
    AnalyzeRequest,
    AnalyzeResponse,
    CreateSessionRequest,
    GenerateQuestionRequest,
    QuestionResponse,
    SessionResponse,
)


class TestCreateSessionRequest:
    """CreateSessionRequestのテスト"""

    def test_valid_request(self):
        """有効なリクエストを作成できる"""
        request = CreateSessionRequest(
            problem="3 + 5 = ?",
            child_grade=2,
        )

        assert request.problem == "3 + 5 = ?"
        assert request.child_grade == 2
        assert request.character_type is None

    def test_with_character_type(self):
        """キャラクタータイプを指定できる"""
        request = CreateSessionRequest(
            problem="3 + 5 = ?",
            child_grade=1,
            character_type="robot",
        )

        assert request.character_type == "robot"

    def test_problem_required(self):
        """problemは必須"""
        with pytest.raises(ValidationError) as exc_info:
            CreateSessionRequest(child_grade=2)

        assert "problem" in str(exc_info.value)

    def test_child_grade_required(self):
        """child_gradeは必須"""
        with pytest.raises(ValidationError) as exc_info:
            CreateSessionRequest(problem="3 + 5 = ?")

        assert "child_grade" in str(exc_info.value)

    def test_child_grade_range(self):
        """child_gradeは1-3の範囲"""
        # 有効な値
        for grade in [1, 2, 3]:
            request = CreateSessionRequest(problem="test", child_grade=grade)
            assert request.child_grade == grade

        # 無効な値
        with pytest.raises(ValidationError):
            CreateSessionRequest(problem="test", child_grade=0)

        with pytest.raises(ValidationError):
            CreateSessionRequest(problem="test", child_grade=4)

    def test_problem_not_empty(self):
        """problemは空文字列不可"""
        with pytest.raises(ValidationError):
            CreateSessionRequest(problem="", child_grade=2)


class TestSessionResponse:
    """SessionResponseのテスト"""

    def test_valid_response(self):
        """有効なレスポンスを作成できる"""
        now = datetime.now()
        response = SessionResponse(
            session_id="session-123",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone="encouraging",
            turns_count=0,
            created_at=now,
        )

        assert response.session_id == "session-123"
        assert response.problem == "3 + 5 = ?"
        assert response.current_hint_level == 1
        assert response.tone == "encouraging"
        assert response.turns_count == 0
        assert response.created_at == now

    def test_hint_level_range(self):
        """hint_levelは1-3の範囲"""
        now = datetime.now()

        # 有効な値
        for level in [1, 2, 3]:
            response = SessionResponse(
                session_id="session-123",
                problem="test",
                current_hint_level=level,
                tone="neutral",
                turns_count=0,
                created_at=now,
            )
            assert response.current_hint_level == level

        # 無効な値
        with pytest.raises(ValidationError):
            SessionResponse(
                session_id="session-123",
                problem="test",
                current_hint_level=0,
                tone="neutral",
                turns_count=0,
                created_at=now,
            )

        with pytest.raises(ValidationError):
            SessionResponse(
                session_id="session-123",
                problem="test",
                current_hint_level=4,
                tone="neutral",
                turns_count=0,
                created_at=now,
            )

    def test_turns_count_non_negative(self):
        """turns_countは0以上"""
        now = datetime.now()

        # 有効な値
        response = SessionResponse(
            session_id="session-123",
            problem="test",
            current_hint_level=1,
            tone="neutral",
            turns_count=5,
            created_at=now,
        )
        assert response.turns_count == 5

        # 無効な値
        with pytest.raises(ValidationError):
            SessionResponse(
                session_id="session-123",
                problem="test",
                current_hint_level=1,
                tone="neutral",
                turns_count=-1,
                created_at=now,
            )


class TestAnalyzeRequest:
    """AnalyzeRequestのテスト"""

    def test_valid_request(self):
        """有効なリクエストを作成できる"""
        request = AnalyzeRequest(child_response="8だと思う")
        assert request.child_response == "8だと思う"

    def test_child_response_required(self):
        """child_responseは必須"""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest()

        assert "child_response" in str(exc_info.value)

    def test_child_response_not_empty(self):
        """child_responseは空文字列不可"""
        with pytest.raises(ValidationError):
            AnalyzeRequest(child_response="")


class TestAnalyzeResponse:
    """AnalyzeResponseのテスト"""

    def test_valid_response(self):
        """有効なレスポンスを作成できる"""
        response = AnalyzeResponse(
            understanding_level=7,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["足し算を理解"],
            recommended_question_type="thinking_guide",
            recommended_tone="encouraging",
            should_advance_hint_level=False,
            answer_request_detected=False,
            answer_request_type="none",
        )

        assert response.understanding_level == 7
        assert response.is_correct_direction is True
        assert response.needs_clarification is False
        assert response.key_insights == ["足し算を理解"]
        assert response.recommended_question_type == "thinking_guide"
        assert response.recommended_tone == "encouraging"
        assert response.should_advance_hint_level is False
        assert response.answer_request_detected is False
        assert response.answer_request_type == "none"

    def test_understanding_level_range(self):
        """understanding_levelは0-10の範囲"""
        # 有効な値
        for level in [0, 5, 10]:
            response = AnalyzeResponse(
                understanding_level=level,
                is_correct_direction=True,
                needs_clarification=False,
                recommended_question_type="hint",
                recommended_tone="neutral",
                should_advance_hint_level=False,
                answer_request_detected=False,
            )
            assert response.understanding_level == level

        # 無効な値
        with pytest.raises(ValidationError):
            AnalyzeResponse(
                understanding_level=-1,
                is_correct_direction=True,
                needs_clarification=False,
                recommended_question_type="hint",
                recommended_tone="neutral",
                should_advance_hint_level=False,
                answer_request_detected=False,
            )

        with pytest.raises(ValidationError):
            AnalyzeResponse(
                understanding_level=11,
                is_correct_direction=True,
                needs_clarification=False,
                recommended_question_type="hint",
                recommended_tone="neutral",
                should_advance_hint_level=False,
                answer_request_detected=False,
            )

    def test_key_insights_defaults_to_empty(self):
        """key_insightsはデフォルトで空リスト"""
        response = AnalyzeResponse(
            understanding_level=5,
            is_correct_direction=True,
            needs_clarification=False,
            recommended_question_type="hint",
            recommended_tone="neutral",
            should_advance_hint_level=False,
            answer_request_detected=False,
        )
        assert response.key_insights == []

    def test_answer_request_type_defaults_to_none(self):
        """answer_request_typeはデフォルトで'none'"""
        response = AnalyzeResponse(
            understanding_level=5,
            is_correct_direction=True,
            needs_clarification=False,
            recommended_question_type="hint",
            recommended_tone="neutral",
            should_advance_hint_level=False,
            answer_request_detected=False,
        )
        assert response.answer_request_type == "none"


class TestGenerateQuestionRequest:
    """GenerateQuestionRequestのテスト"""

    def test_empty_request(self):
        """空のリクエストを作成できる（すべてオプショナル）"""
        request = GenerateQuestionRequest()
        assert request.question_type is None
        assert request.tone is None

    def test_with_question_type(self):
        """質問タイプを指定できる"""
        request = GenerateQuestionRequest(question_type="understanding_check")
        assert request.question_type == "understanding_check"

    def test_with_tone(self):
        """対話トーンを指定できる"""
        request = GenerateQuestionRequest(tone="encouraging")
        assert request.tone == "encouraging"

    def test_with_both(self):
        """両方を指定できる"""
        request = GenerateQuestionRequest(
            question_type="hint",
            tone="empathetic",
        )
        assert request.question_type == "hint"
        assert request.tone == "empathetic"


class TestQuestionResponse:
    """QuestionResponseのテスト"""

    def test_valid_response(self):
        """有効なレスポンスを作成できる"""
        response = QuestionResponse(
            question="この問題は何を聞いていると思う？",
            question_type="understanding_check",
            tone="encouraging",
        )

        assert response.question == "この問題は何を聞いていると思う？"
        assert response.question_type == "understanding_check"
        assert response.tone == "encouraging"

    def test_all_fields_required(self):
        """すべてのフィールドが必須"""
        with pytest.raises(ValidationError):
            QuestionResponse(question_type="hint", tone="neutral")

        with pytest.raises(ValidationError):
            QuestionResponse(question="test", tone="neutral")

        with pytest.raises(ValidationError):
            QuestionResponse(question="test", question_type="hint")


class TestGenerateHintRequest:
    """GenerateHintRequestのテスト"""

    def test_empty_request(self):
        """空のリクエストを作成できる（force_levelはオプショナル）"""
        from app.schemas.dialogue import GenerateHintRequest

        request = GenerateHintRequest()
        assert request.force_level is None

    def test_with_force_level(self):
        """force_levelを指定できる"""
        from app.schemas.dialogue import GenerateHintRequest

        request = GenerateHintRequest(force_level=2)
        assert request.force_level == 2

    def test_force_level_range(self):
        """force_levelは1-3の範囲"""
        from app.schemas.dialogue import GenerateHintRequest

        # 有効な値
        for level in [1, 2, 3]:
            request = GenerateHintRequest(force_level=level)
            assert request.force_level == level

        # 無効な値
        with pytest.raises(ValidationError):
            GenerateHintRequest(force_level=0)

        with pytest.raises(ValidationError):
            GenerateHintRequest(force_level=4)


class TestHintResponse:
    """HintResponseのテスト"""

    def test_valid_response(self):
        """有効なレスポンスを作成できる"""
        from app.schemas.dialogue import HintResponse

        response = HintResponse(
            hint="この問題は何を聞いていると思う？",
            hint_level=1,
            hint_level_name="問題理解の確認",
            is_answer_request_response=False,
        )

        assert response.hint == "この問題は何を聞いていると思う？"
        assert response.hint_level == 1
        assert response.hint_level_name == "問題理解の確認"
        assert response.is_answer_request_response is False

    def test_hint_level_range(self):
        """hint_levelは1-3の範囲"""
        from app.schemas.dialogue import HintResponse

        # 有効な値
        for level in [1, 2, 3]:
            response = HintResponse(
                hint="test",
                hint_level=level,
                hint_level_name="test",
                is_answer_request_response=False,
            )
            assert response.hint_level == level

        # 無効な値
        with pytest.raises(ValidationError):
            HintResponse(
                hint="test",
                hint_level=0,
                hint_level_name="test",
                is_answer_request_response=False,
            )

        with pytest.raises(ValidationError):
            HintResponse(
                hint="test",
                hint_level=4,
                hint_level_name="test",
                is_answer_request_response=False,
            )


class TestAnswerRequestAnalysisRequest:
    """AnswerRequestAnalysisRequestのテスト"""

    def test_valid_request(self):
        """有効なリクエストを作成できる"""
        from app.schemas.dialogue import AnswerRequestAnalysisRequest

        request = AnswerRequestAnalysisRequest(child_response="答え教えて！")
        assert request.child_response == "答え教えて！"

    def test_child_response_required(self):
        """child_responseは必須"""
        from app.schemas.dialogue import AnswerRequestAnalysisRequest

        with pytest.raises(ValidationError) as exc_info:
            AnswerRequestAnalysisRequest()

        assert "child_response" in str(exc_info.value)

    def test_child_response_not_empty(self):
        """child_responseは空文字列不可"""
        from app.schemas.dialogue import AnswerRequestAnalysisRequest

        with pytest.raises(ValidationError):
            AnswerRequestAnalysisRequest(child_response="")


class TestAnswerRequestAnalysisResponse:
    """AnswerRequestAnalysisResponseのテスト"""

    def test_valid_response(self):
        """有効なレスポンスを作成できる"""
        from app.schemas.dialogue import AnswerRequestAnalysisResponse

        response = AnswerRequestAnalysisResponse(
            request_type="explicit",
            confidence=0.95,
            detected_phrases=["答え教えて"],
        )

        assert response.request_type == "explicit"
        assert response.confidence == 0.95
        assert response.detected_phrases == ["答え教えて"]

    def test_confidence_range(self):
        """confidenceは0.0-1.0の範囲"""
        from app.schemas.dialogue import AnswerRequestAnalysisResponse

        # 有効な値
        for conf in [0.0, 0.5, 1.0]:
            response = AnswerRequestAnalysisResponse(
                request_type="none",
                confidence=conf,
            )
            assert response.confidence == conf

        # 無効な値
        with pytest.raises(ValidationError):
            AnswerRequestAnalysisResponse(
                request_type="none",
                confidence=-0.1,
            )

        with pytest.raises(ValidationError):
            AnswerRequestAnalysisResponse(
                request_type="none",
                confidence=1.1,
            )

    def test_detected_phrases_defaults_to_empty(self):
        """detected_phrasesはデフォルトで空リスト"""
        from app.schemas.dialogue import AnswerRequestAnalysisResponse

        response = AnswerRequestAnalysisResponse(
            request_type="none",
            confidence=0.5,
        )
        assert response.detected_phrases == []
