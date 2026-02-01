"""ソクラテス式対話エンジン - データモデル"""

from enum import Enum


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
