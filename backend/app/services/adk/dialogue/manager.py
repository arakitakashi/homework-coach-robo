"""ソクラテス式対話マネージャ"""

import json
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from app.services.adk.dialogue.models import (
    DialogueContext,
    DialogueTone,
    QuestionType,
    ResponseAnalysis,
)

if TYPE_CHECKING:
    pass


@runtime_checkable
class LLMClient(Protocol):
    """LLMクライアントのプロトコル"""

    async def generate(self, prompt: str) -> str:
        """プロンプトからテキストを生成する"""
        ...


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

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """SocraticDialogueManagerを初期化する

        Args:
            llm_client: LLMクライアント（テスト時にモックを注入可能）
        """
        self._llm_client = llm_client

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

    async def analyze_response(
        self,
        child_response: str,
        context: DialogueContext,
    ) -> ResponseAnalysis:
        """子供の回答を分析する

        Args:
            child_response: 子供の回答
            context: 対話コンテキスト

        Returns:
            ResponseAnalysis: 分析結果

        Raises:
            ValueError: LLMクライアントが設定されていない場合
            json.JSONDecodeError: LLMの応答がJSON形式でない場合
        """
        if self._llm_client is None:
            raise ValueError("LLM client is not configured")

        prompt = self.build_analysis_prompt(child_response, context)
        llm_response = await self._llm_client.generate(prompt)

        # JSONをパースしてResponseAnalysisを構築
        data = json.loads(llm_response)
        return ResponseAnalysis(
            understanding_level=data["understanding_level"],
            is_correct_direction=data["is_correct_direction"],
            needs_clarification=data["needs_clarification"],
            key_insights=data.get("key_insights", []),
        )

    def determine_question_type(
        self,
        analysis: ResponseAnalysis,
        context: DialogueContext,
    ) -> QuestionType:
        """次の質問タイプを決定する

        Args:
            analysis: 回答分析結果
            context: 対話コンテキスト

        Returns:
            QuestionType: 次に行うべき質問タイプ
        """
        # 理解度が低い場合は理解確認
        if analysis.understanding_level < 4:
            return QuestionType.UNDERSTANDING_CHECK

        # ヒントレベルが高く、clarificationが必要な場合はヒント
        if context.current_hint_level >= 2 and analysis.needs_clarification:
            return QuestionType.HINT

        # 正しい方向に向かっている場合は思考誘導
        if analysis.is_correct_direction:
            return QuestionType.THINKING_GUIDE

        # その他は理解確認
        return QuestionType.UNDERSTANDING_CHECK
