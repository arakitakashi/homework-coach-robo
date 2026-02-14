"""画像分析ツール

宿題写真から問題を抽出する。Gemini Vision APIを使用。
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

from google.adk.tools import FunctionTool  # type: ignore[attr-defined]

logger = logging.getLogger(__name__)

# 画像サイズ上限（10MB）
_MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

_VISION_PROMPT = """この画像は小学校の宿題の写真です。
画像から問題を読み取り、以下のJSON形式で返してください。

```json
{
  "problems": [
    {
      "text": "問題文のテキスト",
      "type": "arithmetic | word_problem | kanji | reading | other",
      "difficulty": 1,
      "expression": "計算式（算数の場合のみ、なければnull）"
    }
  ],
  "confidence": 0.0～1.0の信頼度,
  "needs_confirmation": true/false（子供に確認が必要か）
}
```

注意:
- 手書き文字も正確に読み取ってください
- 読み取れない部分がある場合はconfidenceを下げてください
- JSONのみを返してください
"""


async def _call_gemini_vision(
    image_bytes: bytes,
    expected_subject: str | None,
) -> Any:
    """Gemini Vision APIを呼び出す（テストでモック可能）"""
    from google import genai
    from google.genai import types

    client = genai.Client()

    prompt = _VISION_PROMPT
    if expected_subject:
        prompt += f"\n教科のヒント: {expected_subject}"

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, image_part],  # type: ignore[arg-type]
    )
    return response


async def analyze_homework_image(
    image_data: str,
    expected_subject: str | None = None,
) -> dict[str, Any]:
    """宿題の画像を分析して問題を抽出する

    Args:
        image_data: base64エンコードされた画像データ
        expected_subject: 予想される教科（オプション）
    """
    if not image_data:
        return {"error": "画像データが空です"}

    # base64デコードしてサイズチェック
    try:
        image_bytes = base64.b64decode(image_data)
    except Exception:
        return {"error": "画像データのデコードに失敗しました"}

    if len(image_bytes) > _MAX_IMAGE_SIZE_BYTES:
        return {"error": "画像サイズが大きすぎます（上限10MB）"}

    try:
        response = await _call_gemini_vision(image_bytes, expected_subject)
    except Exception:
        logger.exception("Gemini Vision API呼び出しエラー")
        return {"error": "画像分析に失敗しました。もう一度試してください。"}

    # JSONパース
    try:
        text = response.text
        # ```json ... ``` で囲まれている場合の処理
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        parsed: dict[str, Any] = json.loads(text.strip())
    except (json.JSONDecodeError, IndexError, AttributeError):
        logger.exception("Vision APIレスポンスのパースエラー")
        return {"error": "画像の解析結果を読み取れませんでした"}

    return {
        "problems": parsed.get("problems", []),
        "confidence": parsed.get("confidence", 0.0),
        "needs_confirmation": parsed.get("needs_confirmation", True),
    }


analyze_image_tool = FunctionTool(func=analyze_homework_image)
