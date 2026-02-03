"""ソクラテス式対話マネージャ"""

from app.services.adk.dialogue.models import DialogueContext, DialogueTone, QuestionType


class SocraticDialogueManager:
    """ソクラテス式対話マネージャ（プロンプト管理を含む）"""

    SYSTEM_PROMPT = """あなたは小学校低学年の子供を導く優しいコーチです。
子供が自分で答えに気づけるよう、質問で導いてください。
決して答えを直接教えないでください。

重要なルール:
1. 簡単な言葉を使う（小学1-3年生が理解できるレベル）
2. 一度に1つの質問だけする
3. 子供の回答を肯定的に受け止める
4. 間違いを責めない
"""

    # トーン別の指示テンプレート
    _TONE_INSTRUCTIONS = {
        DialogueTone.ENCOURAGING: "励ましの言葉をかけながら質問してください。",
        DialogueTone.NEUTRAL: "落ち着いた口調で質問してください。",
        DialogueTone.EMPATHETIC: "子供の気持ちに寄り添い、共感しながら優しく質問してください。",
    }

    # 質問タイプ別の指示テンプレート
    _QUESTION_TYPE_INSTRUCTIONS = {
        QuestionType.UNDERSTANDING_CHECK: (
            "子供が問題を理解しているか確認する質問をしてください。"
            "「この問題は何を聞いていると思う？」のような質問が効果的です。"
        ),
        QuestionType.THINKING_GUIDE: (
            "子供の思考を導く質問をしてください。"
            "「もし○○だったらどうなるかな？」のような質問が効果的です。"
        ),
        QuestionType.HINT: (
            "直接答えを教えずに、ヒントとなる質問をしてください。"
            "「前に似たような問題をやったよね？」のような質問が効果的です。"
        ),
    }

    def build_question_prompt(
        self,
        context: DialogueContext,
        question_type: QuestionType,
        tone: DialogueTone,
    ) -> str:
        """質問生成用プロンプトを構築する

        Args:
            context: 対話コンテキスト
            question_type: 質問タイプ
            tone: 対話トーン

        Returns:
            LLMに渡すプロンプト文字列
        """
        tone_instruction = self._TONE_INSTRUCTIONS[tone]
        question_instruction = self._QUESTION_TYPE_INSTRUCTIONS[question_type]

        prompt = f"""現在の問題: {context.problem}

{question_instruction}

トーン: {tone_instruction}

子供への質問を1つだけ生成してください。"""

        return prompt

    def build_analysis_prompt(
        self,
        child_response: str,
        context: DialogueContext,
    ) -> str:
        """回答分析用プロンプトを構築する

        Args:
            child_response: 子供の回答
            context: 対話コンテキスト

        Returns:
            LLMに渡すプロンプト文字列
        """
        prompt = f"""子供の回答を分析してください。

問題: {context.problem}
子供の回答: {child_response}

以下の項目を分析し、JSON形式で回答してください：

{{
    "understanding_level": 0-10の整数（理解度。0=全く理解していない、10=完全に理解）,
    "is_correct_direction": true/false（正しい方向に向かっているか）,
    "needs_clarification": true/false（追加の説明が必要か）,
    "key_insights": ["子供の回答から得られた重要な気づき"]
}}

JSON以外のテキストは含めないでください。"""

        return prompt
