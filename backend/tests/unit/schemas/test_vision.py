"""画像認識スキーマのテスト"""

import pytest
from pydantic import ValidationError

from app.schemas.vision import (
    ProblemDetail,
    RecognitionType,
    RecognizeImageErrorResponse,
    RecognizeImageRequest,
    RecognizeImageResponse,
)


class TestRecognitionType:
    """RecognitionTypeのテスト"""

    def test_homework_problem(self) -> None:
        """homework_problemが定義されている"""
        assert RecognitionType.HOMEWORK_PROBLEM == "homework_problem"

    def test_handwriting(self) -> None:
        """handwritingが定義されている"""
        assert RecognitionType.HANDWRITING == "handwriting"

    def test_diagram(self) -> None:
        """diagramが定義されている"""
        assert RecognitionType.DIAGRAM == "diagram"


class TestRecognizeImageRequest:
    """RecognizeImageRequestのテスト"""

    def test_valid_request(self) -> None:
        """有効なリクエストを作成できる"""
        request = RecognizeImageRequest(image="aGVsbG8=")

        assert request.image == "aGVsbG8="
        assert request.recognition_type == RecognitionType.HOMEWORK_PROBLEM
        assert request.expected_subject is None

    def test_with_all_fields(self) -> None:
        """全フィールド指定でリクエストを作成できる"""
        request = RecognizeImageRequest(
            image="aGVsbG8=",
            recognition_type=RecognitionType.HANDWRITING,
            expected_subject="算数",
        )

        assert request.image == "aGVsbG8="
        assert request.recognition_type == RecognitionType.HANDWRITING
        assert request.expected_subject == "算数"

    def test_image_required(self) -> None:
        """imageは必須"""
        with pytest.raises(ValidationError) as exc_info:
            RecognizeImageRequest()  # type: ignore[call-arg]

        assert "image" in str(exc_info.value)

    def test_image_not_empty(self) -> None:
        """imageは空文字列不可"""
        with pytest.raises(ValidationError):
            RecognizeImageRequest(image="")

    def test_recognition_type_default(self) -> None:
        """recognition_typeのデフォルトはHOMEWORK_PROBLEM"""
        request = RecognizeImageRequest(image="aGVsbG8=")
        assert request.recognition_type == RecognitionType.HOMEWORK_PROBLEM

    def test_expected_subject_optional(self) -> None:
        """expected_subjectはオプション"""
        request = RecognizeImageRequest(image="aGVsbG8=")
        assert request.expected_subject is None

    def test_recognition_type_string_value(self) -> None:
        """recognition_typeは文字列値で指定可能"""
        request = RecognizeImageRequest(
            image="aGVsbG8=",
            recognition_type="diagram",  # type: ignore[arg-type]
        )
        assert request.recognition_type == RecognitionType.DIAGRAM


class TestProblemDetail:
    """ProblemDetailのテスト"""

    def test_valid_problem(self) -> None:
        """有効な問題詳細を作成できる"""
        problem = ProblemDetail(
            text="3 + 5 = ?",
            type="arithmetic",
            difficulty=1,
        )

        assert problem.text == "3 + 5 = ?"
        assert problem.type == "arithmetic"
        assert problem.difficulty == 1
        assert problem.expression is None

    def test_with_expression(self) -> None:
        """expressionを指定できる"""
        problem = ProblemDetail(
            text="3 + 5 = ?",
            type="arithmetic",
            difficulty=1,
            expression="3 + 5",
        )

        assert problem.expression == "3 + 5"

    def test_all_fields_required(self) -> None:
        """text, type, difficultyは必須"""
        with pytest.raises(ValidationError):
            ProblemDetail(type="arithmetic", difficulty=1)  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            ProblemDetail(text="test", difficulty=1)  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            ProblemDetail(text="test", type="arithmetic")  # type: ignore[call-arg]


class TestRecognizeImageResponse:
    """RecognizeImageResponseのテスト"""

    def test_valid_response(self) -> None:
        """有効なレスポンスを作成できる"""
        response = RecognizeImageResponse(
            success=True,
            problems=[
                ProblemDetail(text="3 + 5 = ?", type="arithmetic", difficulty=1),
            ],
            confidence=0.95,
            needs_confirmation=False,
        )

        assert response.success is True
        assert len(response.problems) == 1
        assert response.confidence == 0.95
        assert response.needs_confirmation is False

    def test_empty_problems(self) -> None:
        """空のproblems配列でレスポンスを作成できる"""
        response = RecognizeImageResponse(
            success=True,
            problems=[],
            confidence=0.5,
            needs_confirmation=True,
        )

        assert response.problems == []

    def test_confidence_range(self) -> None:
        """confidenceは0.0-1.0の範囲"""
        # 有効な値
        for conf in [0.0, 0.5, 1.0]:
            response = RecognizeImageResponse(
                success=True,
                problems=[],
                confidence=conf,
                needs_confirmation=False,
            )
            assert response.confidence == conf

        # 無効な値: 範囲外
        with pytest.raises(ValidationError):
            RecognizeImageResponse(
                success=True,
                problems=[],
                confidence=-0.1,
                needs_confirmation=False,
            )

        with pytest.raises(ValidationError):
            RecognizeImageResponse(
                success=True,
                problems=[],
                confidence=1.1,
                needs_confirmation=False,
            )

    def test_multiple_problems(self) -> None:
        """複数の問題を含むレスポンスを作成できる"""
        response = RecognizeImageResponse(
            success=True,
            problems=[
                ProblemDetail(text="3 + 5 = ?", type="arithmetic", difficulty=1),
                ProblemDetail(text="りんごが3つ、みかんが5つ", type="word_problem", difficulty=2),
            ],
            confidence=0.85,
            needs_confirmation=False,
        )

        assert len(response.problems) == 2


class TestRecognizeImageErrorResponse:
    """RecognizeImageErrorResponseのテスト"""

    def test_valid_error_response(self) -> None:
        """有効なエラーレスポンスを作成できる"""
        response = RecognizeImageErrorResponse(
            error_type="recognition_failed",
            message="画像を認識できませんでした",
        )

        assert response.success is False
        assert response.error_type == "recognition_failed"
        assert response.message == "画像を認識できませんでした"
        assert response.suggestions == []

    def test_with_suggestions(self) -> None:
        """suggestionsを指定できる"""
        response = RecognizeImageErrorResponse(
            error_type="low_confidence",
            message="信頼度が低いです",
            suggestions=[
                "もう少し明るい場所で撮影してください",
                "文字がはっきり見えるようにしてください",
            ],
        )

        assert len(response.suggestions) == 2

    def test_success_always_false(self) -> None:
        """successは常にFalse"""
        response = RecognizeImageErrorResponse(
            error_type="invalid_image",
            message="画像が無効です",
        )
        assert response.success is False
