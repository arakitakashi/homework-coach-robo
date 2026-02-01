"""ソクラテス式対話エンジン - データモデル"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from typing import Self


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


class DialogueTurn(BaseModel):
    """対話ターン（1回の発話）"""

    role: Literal["child", "assistant"] = Field(..., description="発話者")
    content: str = Field(..., description="発話内容")
    timestamp: datetime = Field(..., description="発話時刻")
    question_type: QuestionType | None = Field(
        default=None, description="質問タイプ（アシスタントの場合）"
    )
    response_analysis: ResponseAnalysis | None = Field(
        default=None, description="回答分析（子供の回答の場合）"
    )


class DialogueContext(BaseModel):
    """対話コンテキスト（セッション全体の状態）"""

    session_id: str = Field(..., description="セッションID")
    problem: str = Field(..., description="現在の問題")
    current_hint_level: int = Field(
        default=1, ge=1, le=3, description="現在のヒントレベル（1-3）"
    )
    tone: DialogueTone = Field(
        default=DialogueTone.ENCOURAGING, description="対話トーン"
    )
    turns: list[DialogueTurn] = Field(default_factory=list, description="対話履歴")

    @classmethod
    def from_adk_session(cls, session: Any) -> "Self":
        """ADKセッションからDialogueContextを構築

        Args:
            session: ADKのSessionオブジェクト（id, state属性を持つ）

        Returns:
            DialogueContext: 構築されたコンテキスト
        """
        state = session.state or {}

        # toneの変換（文字列 -> Enum）
        tone_str = state.get("tone", "encouraging")
        try:
            tone = DialogueTone(tone_str)
        except ValueError:
            tone = DialogueTone.ENCOURAGING

        return cls(
            session_id=session.id,
            problem=state.get("problem", ""),
            current_hint_level=state.get("current_hint_level", 1),
            tone=tone,
            turns=[],
        )
