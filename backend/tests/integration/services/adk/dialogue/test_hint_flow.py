"""3段階ヒントシステムの統合テスト"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.services.adk.dialogue.manager import SocraticDialogueManager
from app.services.adk.dialogue.models import (
    AnswerRequestType,
    DialogueContext,
    DialogueTone,
    DialogueTurn,
    HintLevel,
    ResponseAnalysis,
)


class TestHintFlowLevel1:
    """レベル1（問題理解の確認）のフローテスト"""

    @pytest.fixture
    def manager_with_llm(self):
        """LLMクライアント付きSocraticDialogueManagerインスタンス"""
        mock_llm = AsyncMock()
        return SocraticDialogueManager(llm_client=mock_llm)

    @pytest.fixture
    def initial_context(self):
        """初期対話コンテキスト"""
        return DialogueContext(
            session_id="integration-test-001",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    @pytest.mark.asyncio
    async def test_level_1_flow_child_understands(self, manager_with_llm, initial_context):
        """レベル1: 子供が理解している場合はレベル維持"""
        # LLMの応答を設定
        manager_with_llm._llm_client.generate.return_value = "この問題は何を聞いていると思う？"

        # レベル1のヒントを生成
        response = await manager_with_llm.generate_hint_response(
            context=initial_context,
            is_answer_request=False,
        )

        assert "聞いて" in response or "問題" in response or "何" in response

        # 子供の回答を分析（理解している）
        analysis = ResponseAnalysis(
            understanding_level=7,
            is_correct_direction=True,
            needs_clarification=False,
            key_insights=["足し算を理解"],
        )

        # レベル進行を確認
        new_level = manager_with_llm.advance_hint_level(initial_context, analysis)
        assert new_level == 1  # 理解しているのでレベル維持


class TestHintFlowLevelTransition:
    """レベル遷移のフローテスト"""

    @pytest.fixture
    def manager_with_llm(self):
        """LLMクライアント付きSocraticDialogueManagerインスタンス"""
        mock_llm = AsyncMock()
        return SocraticDialogueManager(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_transition_level_1_to_2(self, manager_with_llm):
        """レベル1→2への遷移テスト"""
        # レベル1で2ターン対話した後の状態
        context = DialogueContext(
            session_id="integration-test-002",
            problem="7 - 3 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="この問題は何を聞いていると思う？",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="わからない...",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="数字が2つあるよね。何をするのかな？",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="うーん、なんだろう",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ],
        )

        # 子供が苦戦している
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        # レベル2へ進行
        new_level = manager_with_llm.advance_hint_level(context, analysis)
        assert new_level == 2

        # レベル2のプロンプトを確認
        context.current_hint_level = new_level
        prompt = manager_with_llm.build_hint_prompt(
            context=context,
            hint_level=HintLevel.PRIOR_KNOWLEDGE,
            tone=DialogueTone.EMPATHETIC,
        )

        assert "前" in prompt or "似た" in prompt or "思い出" in prompt

    @pytest.mark.asyncio
    async def test_transition_level_2_to_3(self, manager_with_llm):
        """レベル2→3への遷移テスト"""
        # レベル2で2ターン対話した後の状態
        context = DialogueContext(
            session_id="integration-test-003",
            problem="12 ÷ 4 = ?",
            current_hint_level=2,
            tone=DialogueTone.EMPATHETIC,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="前に九九をやったよね？",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="九九？忘れた...",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="4×3は何になるか思い出せる？",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="えっと...わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ],
        )

        # 子供がまだ苦戦している
        analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        # レベル3へ進行
        new_level = manager_with_llm.advance_hint_level(context, analysis)
        assert new_level == 3

        # レベル3のプロンプトを確認
        context.current_hint_level = new_level
        prompt = manager_with_llm.build_hint_prompt(
            context=context,
            hint_level=HintLevel.PARTIAL_SUPPORT,
            tone=DialogueTone.EMPATHETIC,
        )

        assert "最初" in prompt or "ステップ" in prompt or "一緒" in prompt
        # 答えを教えない指示が含まれている
        assert "答え" in prompt


class TestAnswerRequestHandling:
    """答えリクエスト対応のフローテスト"""

    @pytest.fixture
    def manager_with_llm(self):
        """LLMクライアント付きSocraticDialogueManagerインスタンス"""
        mock_llm = AsyncMock()
        return SocraticDialogueManager(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_answer_request_detection_and_response(self, manager_with_llm):
        """答えリクエストを検出して適切に対応する"""
        context = DialogueContext(
            session_id="integration-test-004",
            problem="5 + 7 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        # 子供が答えを求める
        child_message = "もう答え教えて！"

        # 答えリクエストを検出
        request_analysis = await manager_with_llm.detect_answer_request(child_message)
        assert request_analysis.request_type == AnswerRequestType.EXPLICIT
        assert request_analysis.confidence >= 0.8

        # 励ましを含むヒントを生成
        manager_with_llm._llm_client.generate.return_value = (
            "大丈夫だよ、一緒に考えよう！この問題は何を聞いていると思う？"
        )

        await manager_with_llm.generate_hint_response(
            context=context,
            is_answer_request=True,
        )

        # プロンプトに励ましの指示が含まれていることを確認
        call_args = manager_with_llm._llm_client.generate.call_args
        prompt = call_args[0][0]
        assert "大丈夫" in prompt or "一緒" in prompt or "励まし" in prompt

    @pytest.mark.asyncio
    async def test_implicit_answer_request_handling(self, manager_with_llm):
        """暗示的な答えリクエストを検出して対応する"""
        # 暗示的なリクエスト
        child_message = "もうできない、むずかしいよ..."

        # 答えリクエストを検出
        request_analysis = await manager_with_llm.detect_answer_request(child_message)
        assert request_analysis.request_type == AnswerRequestType.IMPLICIT
        assert len(request_analysis.detected_phrases) > 0


class TestLevelSkipPrevention:
    """レベルスキップ禁止のテスト"""

    @pytest.fixture
    def manager(self):
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager()

    def test_cannot_skip_from_1_to_3(self, manager):
        """レベル1から直接レベル3へは進めない"""
        # レベル1で1回目の分析
        context = DialogueContext(
            session_id="integration-test-005",
            problem="8 + 4 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="質問2",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="全然わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ],
        )

        # ひどく苦戦していても1レベルずつしか進まない
        analysis = ResponseAnalysis(
            understanding_level=0,  # 最低レベル
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        new_level = manager.advance_hint_level(context, analysis)
        assert new_level == 2  # レベル3ではなくレベル2へ

    def test_each_level_requires_minimum_turns(self, manager):
        """各レベルで最低ターン数が必要"""
        # 1ターンのみの状態
        context = DialogueContext(
            session_id="integration-test-006",
            problem="9 - 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
            ],
        )

        # ひどく苦戦していてもターン数が足りないと進まない
        analysis = ResponseAnalysis(
            understanding_level=0,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        new_level = manager.advance_hint_level(context, analysis)
        assert new_level == 1  # ターン数不足でレベル維持


class TestEndToEndHintFlow:
    """エンドツーエンドのヒントフローテスト"""

    @pytest.fixture
    def manager_with_llm(self):
        """LLMクライアント付きSocraticDialogueManagerインスタンス"""
        mock_llm = AsyncMock()
        return SocraticDialogueManager(llm_client=mock_llm)

    @pytest.mark.asyncio
    async def test_complete_hint_flow_to_level_3(self, manager_with_llm):
        """レベル1→2→3の完全なフロー"""
        context = DialogueContext(
            session_id="integration-test-007",
            problem="15 - 8 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        struggling_analysis = ResponseAnalysis(
            understanding_level=2,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        # レベル1で対話
        manager_with_llm._llm_client.generate.return_value = "この問題は何を聞いていると思う？"
        await manager_with_llm.generate_hint_response(context)

        # 2ターン追加
        context.turns.extend(
            [
                DialogueTurn(
                    role="assistant",
                    content="質問1",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="質問2",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="うーん",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ]
        )

        # レベル2へ進行
        new_level = manager_with_llm.advance_hint_level(context, struggling_analysis)
        assert new_level == 2
        context.current_hint_level = new_level
        context.tone = DialogueTone.EMPATHETIC

        # レベル2で対話
        manager_with_llm._llm_client.generate.return_value = "前に似たような問題をやったよね？"
        await manager_with_llm.generate_hint_response(context)

        # さらに2ターン追加
        context.turns.extend(
            [
                DialogueTurn(
                    role="assistant",
                    content="質問3",
                    timestamp=datetime(2026, 2, 4, 10, 0, 40),
                ),
                DialogueTurn(
                    role="child",
                    content="覚えてない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 50),
                ),
            ]
        )

        # レベル3へ進行
        new_level = manager_with_llm.advance_hint_level(context, struggling_analysis)
        assert new_level == 3
        context.current_hint_level = new_level

        # レベル3で対話（部分的支援）
        manager_with_llm._llm_client.generate.return_value = (
            "じゃあ、最初のステップだけ一緒にやろう。15という数字があるね。"
        )
        response = await manager_with_llm.generate_hint_response(context)
        assert "最初" in response or "ステップ" in response

        # これ以上はレベルが上がらない
        context.turns.extend(
            [
                DialogueTurn(
                    role="assistant",
                    content="質問4",
                    timestamp=datetime(2026, 2, 4, 10, 1, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="まだわからない",
                    timestamp=datetime(2026, 2, 4, 10, 1, 10),
                ),
            ]
        )

        final_level = manager_with_llm.advance_hint_level(context, struggling_analysis)
        assert final_level == 3  # 最大レベル維持
