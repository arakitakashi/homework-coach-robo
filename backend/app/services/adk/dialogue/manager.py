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
    from app.services.adk.dialogue.models import AnswerRequestAnalysis

# 明示的な答えリクエストキーワード（正規表現パターン）
_EXPLICIT_PATTERNS = [
    r"答え.*教えて",
    r"答え.*言って",
    r"正解.*教えて",
    r"正解.*言って",
    r"正解は[？\?]?$",
    r"答えは[？\?]?$",
]

# 暗示的な答えリクエストキーワード（正規表現パターン）
_IMPLICIT_PATTERNS = [
    r"できない",
    r"むずかしい",
    r"むりだ",
    r"無理だ",
    r"わからない",
    r"分からない",
    r"ギブアップ",
    r"あきらめ",
    r"諦め",
]


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
        self._question_history: list[str] = []

    @property
    def question_history(self) -> list[str]:
        """生成した質問の履歴を返す"""
        return self._question_history

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

    def determine_tone(
        self,
        analysis: ResponseAnalysis,
        context: DialogueContext,  # noqa: ARG002 - 将来の拡張用
    ) -> DialogueTone:
        """対話トーンを決定する

        Args:
            analysis: 回答分析結果
            context: 対話コンテキスト

        Returns:
            DialogueTone: 使用すべき対話トーン
        """
        # 正しい方向に進んでいる場合は励まし
        if analysis.is_correct_direction:
            return DialogueTone.ENCOURAGING

        # 理解度が低い場合は共感
        if analysis.understanding_level < 4:
            return DialogueTone.EMPATHETIC

        # その他は中立
        return DialogueTone.NEUTRAL

    async def generate_question(
        self,
        context: DialogueContext,
        question_type: QuestionType,
        tone: DialogueTone,
    ) -> str:
        """質問を生成する

        Args:
            context: 対話コンテキスト
            question_type: 質問タイプ
            tone: 対話トーン

        Returns:
            生成された質問文字列

        Raises:
            ValueError: LLMクライアントが設定されていない場合
        """
        if self._llm_client is None:
            raise ValueError("LLM client is not configured")

        prompt = self.build_question_prompt(context, question_type, tone)
        question = await self._llm_client.generate(prompt)

        # 履歴に追加
        self._question_history.append(question)

        return question

    # 最大ヒントレベル（3段階ヒントシステム）
    MAX_HINT_LEVEL = 3
    # 次のフェーズに進むための最小ターン数
    MIN_TURNS_BEFORE_MOVE = 2

    def should_move_to_next_phase(
        self,
        analysis: ResponseAnalysis,
        context: DialogueContext,
    ) -> bool:
        """次のヒントレベルに進むべきか判定する

        Args:
            analysis: 回答分析結果
            context: 対話コンテキスト

        Returns:
            次のフェーズに進むべきならTrue、そうでなければFalse
        """
        # 最大ヒントレベルに達している場合は進まない
        if context.current_hint_level >= self.MAX_HINT_LEVEL:
            return False

        # 理解度が改善している場合は進まない
        if analysis.is_correct_direction and analysis.understanding_level >= 4:
            return False

        # 十分なターン数があり、理解度が低い場合は次のフェーズへ
        return (
            len(context.turns) >= self.MIN_TURNS_BEFORE_MOVE
            and analysis.understanding_level < 4
            and not analysis.is_correct_direction
        )

    # 明示的な答えリクエストキーワード（正規表現パターン）
    _EXPLICIT_PATTERNS = [
        r"答え.*教えて",
        r"答え.*言って",
        r"正解.*教えて",
        r"正解.*言って",
        r"正解は[？\?]?$",
        r"答えは[？\?]?$",
    ]

    # 暗示的な答えリクエストキーワード（正規表現パターン）
    _IMPLICIT_PATTERNS = [
        r"できない",
        r"むずかしい",
        r"むりだ",
        r"無理だ",
        r"わからない",
        r"分からない",
        r"ギブアップ",
        r"あきらめ",
        r"諦め",
    ]

    def _detect_answer_request_keywords(
        self,
        child_response: str,
    ) -> "AnswerRequestAnalysis":
        """キーワードベースで答えリクエストを検出する

        Args:
            child_response: 子供の発話

        Returns:
            AnswerRequestAnalysis: 分析結果
        """
        import re

        from app.services.adk.dialogue.models import (
            AnswerRequestAnalysis,
            AnswerRequestType,
        )

        detected_phrases: list[str] = []

        # 明示的なリクエストをチェック
        for pattern in self._EXPLICIT_PATTERNS:
            match = re.search(pattern, child_response)
            if match:
                detected_phrases.append(match.group())
                return AnswerRequestAnalysis(
                    request_type=AnswerRequestType.EXPLICIT,
                    confidence=0.9,
                    detected_phrases=detected_phrases,
                )

        # 暗示的なリクエストをチェック
        for pattern in self._IMPLICIT_PATTERNS:
            match = re.search(pattern, child_response)
            if match:
                detected_phrases.append(match.group())
                return AnswerRequestAnalysis(
                    request_type=AnswerRequestType.IMPLICIT,
                    confidence=0.7,
                    detected_phrases=detected_phrases,
                )

        # リクエストなし
        return AnswerRequestAnalysis(
            request_type=AnswerRequestType.NONE,
            confidence=1.0,
            detected_phrases=[],
        )

    # 答えリクエスト検出用プロンプト
    _ANSWER_REQUEST_DETECTION_PROMPT = """子供の発話から「答えを教えてほしい」意図を検出してください。

子供の発話: {child_response}

以下のJSON形式で回答してください：
{{
    "request_type": "none" | "explicit" | "implicit",
    "confidence": 0.0-1.0,
    "detected_phrases": ["検出されたフレーズ"]
}}

判定基準:
- explicit: 「答え教えて」「答えを言って」「正解は？」など明示的な要求
- implicit: 「できない」「むずかしい」「わからない」「ギブアップ」「もういい」など暗示的な要求
- none: 答えリクエストではない通常の回答

JSON以外のテキストは含めないでください。"""

    async def detect_answer_request(
        self,
        child_response: str,
    ) -> "AnswerRequestAnalysis":
        """答えリクエストを検出する（キーワード優先、LLM補助）

        Args:
            child_response: 子供の発話

        Returns:
            AnswerRequestAnalysis: 分析結果
        """
        import json

        from app.services.adk.dialogue.models import (
            AnswerRequestAnalysis,
            AnswerRequestType,
        )

        # まずキーワードベースで検出を試みる
        keyword_result = self._detect_answer_request_keywords(child_response)
        if keyword_result.request_type != AnswerRequestType.NONE:
            return keyword_result

        # LLMクライアントがない場合はキーワード結果をそのまま返す
        if self._llm_client is None:
            return keyword_result

        # LLMで補助検出
        prompt = self._ANSWER_REQUEST_DETECTION_PROMPT.format(child_response=child_response)
        try:
            llm_response = await self._llm_client.generate(prompt)
            data = json.loads(llm_response)
            return AnswerRequestAnalysis(
                request_type=AnswerRequestType(data["request_type"]),
                confidence=data["confidence"],
                detected_phrases=data.get("detected_phrases", []),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            # パースエラーの場合はNONEを返す
            return AnswerRequestAnalysis(
                request_type=AnswerRequestType.NONE,
                confidence=0.5,
                detected_phrases=[],
            )

    # ヒントレベル別の指示テンプレート
    _HINT_LEVEL_INSTRUCTIONS = {
        1: """【レベル1: 問題理解の確認】
子供が問題を正しく理解しているか確認します。
- 問題文の再読を促す
- 何を求められているか質問する
- 例: 「この問題は何を聞いているかな？」「問題をもう一度読んでみよう」""",
        2: """【レベル2: 既習事項の想起】
子供が関連する知識を思い出せるよう導きます。
- 以前学んだ類似の概念を想起させる
- 関連する知識への橋渡しをする
- 例: 「前に似たような問題をやったよね」「○○のことを思い出してみて」""",
        3: """【レベル3: 部分的支援】
問題を小さく分解し、最初のステップのみ支援します。
- 問題を複数の小さなステップに分ける
- 最初のステップだけ一緒に考える
- 最終的な答えは絶対に教えない
- 例: 「まず最初のステップだけ一緒にやってみよう」""",
    }

    # 答えリクエスト時の励まし追加テンプレート
    _ENCOURAGEMENT_FOR_ANSWER_REQUEST = """
子供が「答えを教えて」と言っています。
大丈夫、一緒に考えようという励ましの気持ちを込めて、優しく導いてください。
直接答えを教えることは絶対にしないでください。"""

    def build_hint_prompt(
        self,
        context: DialogueContext,
        hint_level: int,
        tone: DialogueTone,
        is_answer_request: bool = False,
    ) -> str:
        """ヒントレベル別のプロンプトを構築する

        Args:
            context: 対話コンテキスト
            hint_level: ヒントレベル（1-3またはHintLevel Enum）
            tone: 対話トーン
            is_answer_request: 答えリクエストがあったか

        Returns:
            LLMに渡すプロンプト文字列
        """
        # HintLevel Enumの場合はintに変換
        level_value = int(hint_level)

        tone_instruction = self._TONE_INSTRUCTIONS[tone]
        hint_instruction = self._HINT_LEVEL_INSTRUCTIONS.get(
            level_value,
            self._HINT_LEVEL_INSTRUCTIONS[1],  # デフォルトはレベル1
        )

        prompt = f"""現在の問題: {context.problem}

{hint_instruction}

トーン: {tone_instruction}
"""

        if is_answer_request:
            prompt += self._ENCOURAGEMENT_FOR_ANSWER_REQUEST

        prompt += "\n子供への質問を1つだけ生成してください。"

        return prompt

    async def generate_hint_response(
        self,
        context: DialogueContext,
        is_answer_request: bool = False,
    ) -> str:
        """ヒントレベルに応じたレスポンスを生成する

        Args:
            context: 対話コンテキスト
            is_answer_request: 答えリクエストがあったか

        Returns:
            生成されたレスポンス文字列

        Raises:
            ValueError: LLMクライアントが設定されていない場合
        """
        if self._llm_client is None:
            raise ValueError("LLM client is not configured")

        # 現在のヒントレベルに応じたプロンプトを構築
        prompt = self.build_hint_prompt(
            context=context,
            hint_level=context.current_hint_level,
            tone=context.tone,
            is_answer_request=is_answer_request,
        )

        # LLMでレスポンスを生成
        response = await self._llm_client.generate(prompt)

        # 履歴に追加
        self._question_history.append(response)

        return response

    def advance_hint_level(
        self,
        context: DialogueContext,
        analysis: ResponseAnalysis,
    ) -> int:
        """ヒントレベルを進行させるべきか判定し、新しいレベルを返す

        ルール:
        - 各レベルで最低2ターン対話してから次へ
        - 理解度が改善傾向ならレベルを上げない
        - 最大レベル3を超えない

        Args:
            context: 対話コンテキスト
            analysis: 回答分析結果

        Returns:
            新しいヒントレベル（1-3）
        """
        current_level = context.current_hint_level

        # 最大レベルに達している場合は維持
        if current_level >= self.MAX_HINT_LEVEL:
            return current_level

        # 理解度が改善している場合は維持
        if analysis.is_correct_direction and analysis.understanding_level >= 4:
            return current_level

        # 最低ターン数に満たない場合は維持
        if len(context.turns) < self.MIN_TURNS_BEFORE_MOVE:
            return current_level

        # 苦戦している場合は次のレベルへ
        if analysis.understanding_level < 4 and not analysis.is_correct_direction:
            return min(current_level + 1, self.MAX_HINT_LEVEL)

        return current_level
