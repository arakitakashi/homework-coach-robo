"""画像認識APIエンドポイント

宿題プリントの画像をアップロードし、問題を認識するエンドポイント。
既存の analyze_homework_image() を HTTP API として公開する。
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.vision import (
    ProblemDetail,
    RecognizeImageRequest,
    RecognizeImageResponse,
)
from app.services.adk.tools.image_analyzer import analyze_homework_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vision", tags=["vision"])

# 画像サイズ超過を示すエラーメッセージのキーワード
_SIZE_ERROR_KEYWORDS = ["大きすぎ", "上限", "サイズ"]


def _classify_error_type(error_message: str) -> str:
    """エラーメッセージからエラータイプを判定する"""
    if any(keyword in error_message for keyword in _SIZE_ERROR_KEYWORDS):
        return "image_too_large"
    return "recognition_failed"


def _build_suggestions(error_type: str) -> list[str]:
    """エラータイプに応じた改善提案を生成する"""
    if error_type == "image_too_large":
        return ["画像サイズを小さくしてから再度お試しください"]
    return ["もう一度撮影してお試しください", "明るい場所で撮影するときれいに読み取れます"]


@router.post(
    "/recognize",
    response_model=RecognizeImageResponse,
    summary="宿題画像を認識する",
    description="base64エンコードされた画像を受け取り、Gemini Vision APIで問題を認識する",
)
async def recognize_image(request: RecognizeImageRequest) -> RecognizeImageResponse:
    """宿題画像を受け取り、問題を認識して返す"""
    # analyze_homework_image を呼び出し
    result = await analyze_homework_image(
        image_data=request.image,
        expected_subject=request.expected_subject,
    )

    # エラーチェック: analyze_homework_image は error キーを含む dict を返す
    if "error" in result:
        error_message: str = result["error"]
        error_type = _classify_error_type(error_message)
        suggestions = _build_suggestions(error_type)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "success": False,
                "error_type": error_type,
                "message": error_message,
                "suggestions": suggestions,
            },
        )

    # 正常レスポンスの組み立て
    problems = [
        ProblemDetail(
            text=p.get("text", ""),
            type=p.get("type", "other"),
            difficulty=p.get("difficulty", 1),
            expression=p.get("expression"),
        )
        for p in result.get("problems", [])
    ]

    return RecognizeImageResponse(
        success=True,
        problems=problems,
        confidence=result.get("confidence", 0.0),
        needs_confirmation=result.get("needs_confirmation", True),
    )
