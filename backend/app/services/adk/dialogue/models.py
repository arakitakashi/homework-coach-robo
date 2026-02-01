"""ソクラテス式対話エンジン - データモデル"""

from enum import Enum

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """質問タイプ"""

    UNDERSTANDING_CHECK = "understanding_check"  # 理解確認
    THINKING_GUIDE = "thinking_guide"  # 思考誘導
    HINT = "hint"  # ヒント


class DialogueTone(str, Enum):
    """対話トーン"""

    ENCOURAGING = "encouraging"  # 励まし
    NEUTRAL = "neutral"  # 中立
    EMPATHETIC = "empathetic"  # 共感


class ResponseAnalysis(BaseModel):
    """回答分析結果"""

    understanding_level: int = Field(..., ge=0, le=10, description="理解度（0-10）")
    is_correct_direction: bool = Field(..., description="正しい方向に向かっているか")
    needs_clarification: bool = Field(..., description="追加の説明が必要か")
    key_insights: list[str] = Field(..., description="重要な気づき")
