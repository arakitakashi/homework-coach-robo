"""対話フロー統合テスト"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.services.adk.dialogue.manager import SocraticDialogueManager
from app.services.adk.dialogue.models import (
    DialogueContext,
    DialogueTone,
    DialogueTurn,
    QuestionType,
)


class TestBasicDialogueFlow:
    """基本対話フローのテスト"""

    @pytest.fixture
    def mock_llm_client(self):
        """モック化されたLLMクライアント"""
        return AsyncMock()

    @pytest.fixture
    def manager(self, mock_llm_client):
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager(llm_client=mock_llm_client)

    @pytest.fixture
    def initial_context(self):
        """初期対話コンテキスト"""
        return DialogueContext(
            session_id="test-session-001",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

    @pytest.mark.asyncio
    async def test_full_dialogue_flow_success(self, manager, mock_llm_client):
        """子供が正しく答えに至る対話フロー"""
        # 初期コンテキスト
        context = DialogueContext(
            session_id="test-session-001",
            problem="3 + 5 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        # Step 1: 最初の質問を生成
        mock_llm_client.generate.return_value = "この問題は何を聞いていると思う？"
        question1 = await manager.generate_question(
            context=context,
            question_type=QuestionType.UNDERSTANDING_CHECK,
            tone=DialogueTone.ENCOURAGING,
        )
        assert "問題" in question1 or "聞いて" in question1

        # Step 2: 子供の回答を分析（部分的に理解）
        mock_llm_client.generate.return_value = """{
            "understanding_level": 5,
            "is_correct_direction": true,
            "needs_clarification": false,
            "key_insights": ["足し算だと理解している"]
        }"""
        analysis1 = await manager.analyze_response(
            child_response="たし算だよね？",
            context=context,
        )
        assert analysis1.understanding_level == 5
        assert analysis1.is_correct_direction is True

        # Step 3: 次の質問タイプとトーンを決定
        question_type2 = manager.determine_question_type(analysis1, context)
        tone2 = manager.determine_tone(analysis1, context)
        assert question_type2 == QuestionType.THINKING_GUIDE
        assert tone2 == DialogueTone.ENCOURAGING

        # Step 4: フェーズを進めるか判定（進めない）
        should_move = manager.should_move_to_next_phase(analysis1, context)
        assert should_move is False

        # Step 5: 次の質問を生成
        mock_llm_client.generate.return_value = "3と5を合わせると、いくつになるかな？"
        await manager.generate_question(
            context=context,
            question_type=question_type2,
            tone=tone2,
        )
        assert len(manager.question_history) == 2

        # Step 6: 最終回答を分析（正解）
        mock_llm_client.generate.return_value = """{
            "understanding_level": 10,
            "is_correct_direction": true,
            "needs_clarification": false,
            "key_insights": ["完全に理解している", "正しく計算できた"]
        }"""
        analysis2 = await manager.analyze_response(
            child_response="8だよ！",
            context=context,
        )
        assert analysis2.understanding_level == 10
        assert analysis2.is_correct_direction is True

    @pytest.mark.asyncio
    async def test_dialogue_flow_with_hint_escalation(self, manager, mock_llm_client):
        """ヒントレベルが上がる対話フロー"""
        # 複数ターン後に理解度が低い状態
        context = DialogueContext(
            session_id="test-session-002",
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
                    content="7と3があるね。どうするのかな？",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="うーん...",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ],
        )

        # 理解度が低い分析結果
        mock_llm_client.generate.return_value = """{
            "understanding_level": 2,
            "is_correct_direction": false,
            "needs_clarification": true,
            "key_insights": ["引き算の概念を理解していない"]
        }"""
        analysis = await manager.analyze_response(
            child_response="うーん...",
            context=context,
        )

        # フェーズを進めるべき
        should_move = manager.should_move_to_next_phase(analysis, context)
        assert should_move is True

        # トーンは共感的
        tone = manager.determine_tone(analysis, context)
        assert tone == DialogueTone.EMPATHETIC


class TestEdgeCases:
    """エッジケーステスト"""

    @pytest.fixture
    def mock_llm_client(self):
        """モック化されたLLMクライアント"""
        return AsyncMock()

    @pytest.fixture
    def manager(self, mock_llm_client):
        """SocraticDialogueManagerインスタンス"""
        return SocraticDialogueManager(llm_client=mock_llm_client)

    @pytest.mark.asyncio
    async def test_long_dialogue_maintains_history(self, manager, mock_llm_client):
        """長い対話でも質問履歴が維持される"""
        context = DialogueContext(
            session_id="test-session-003",
            problem="2 + 2 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        # 10個の質問を生成
        for i in range(10):
            mock_llm_client.generate.return_value = f"質問{i + 1}"
            await manager.generate_question(
                context=context,
                question_type=QuestionType.UNDERSTANDING_CHECK,
                tone=DialogueTone.ENCOURAGING,
            )

        # 全ての質問が履歴に残っている
        assert len(manager.question_history) == 10
        assert "質問1" in manager.question_history
        assert "質問10" in manager.question_history

    def test_max_hint_level_prevents_escalation(self, manager):
        """最大ヒントレベルでは次のフェーズに進まない"""
        context = DialogueContext(
            session_id="test-session-004",
            problem="5 + 5 = ?",
            current_hint_level=3,  # 最大レベル
            tone=DialogueTone.EMPATHETIC,
            turns=[
                DialogueTurn(
                    role="assistant",
                    content="一緒にやろうね",
                    timestamp=datetime(2026, 2, 4, 10, 0, 0),
                ),
                DialogueTurn(
                    role="child",
                    content="わからない",
                    timestamp=datetime(2026, 2, 4, 10, 0, 10),
                ),
                DialogueTurn(
                    role="assistant",
                    content="5があって、もう5つあるね",
                    timestamp=datetime(2026, 2, 4, 10, 0, 20),
                ),
                DialogueTurn(
                    role="child",
                    content="えっと...",
                    timestamp=datetime(2026, 2, 4, 10, 0, 30),
                ),
            ],
        )

        from app.services.adk.dialogue.models import ResponseAnalysis

        analysis = ResponseAnalysis(
            understanding_level=1,
            is_correct_direction=False,
            needs_clarification=True,
            key_insights=[],
        )

        # 最大レベルでは進まない
        should_move = manager.should_move_to_next_phase(analysis, context)
        assert should_move is False


class TestErrorHandling:
    """エラーハンドリングテスト"""

    def test_generate_question_without_llm_client_raises(self):
        """LLMクライアントなしで質問生成するとエラー"""
        manager = SocraticDialogueManager(llm_client=None)
        context = DialogueContext(
            session_id="test-session-005",
            problem="1 + 1 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        with pytest.raises(ValueError, match="LLM client is not configured"):
            import asyncio

            asyncio.get_event_loop().run_until_complete(
                manager.generate_question(
                    context=context,
                    question_type=QuestionType.UNDERSTANDING_CHECK,
                    tone=DialogueTone.ENCOURAGING,
                )
            )

    def test_analyze_response_without_llm_client_raises(self):
        """LLMクライアントなしで回答分析するとエラー"""
        manager = SocraticDialogueManager(llm_client=None)
        context = DialogueContext(
            session_id="test-session-006",
            problem="1 + 1 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        with pytest.raises(ValueError, match="LLM client is not configured"):
            import asyncio

            asyncio.get_event_loop().run_until_complete(
                manager.analyze_response(
                    child_response="2かな？",
                    context=context,
                )
            )

    @pytest.mark.asyncio
    async def test_analyze_response_with_invalid_json_raises(self):
        """LLMが無効なJSONを返した場合のエラー"""
        import json

        mock_llm_client = AsyncMock()
        mock_llm_client.generate.return_value = "これはJSONではありません"

        manager = SocraticDialogueManager(llm_client=mock_llm_client)
        context = DialogueContext(
            session_id="test-session-007",
            problem="1 + 1 = ?",
            current_hint_level=1,
            tone=DialogueTone.ENCOURAGING,
            turns=[],
        )

        with pytest.raises(json.JSONDecodeError):
            await manager.analyze_response(
                child_response="2",
                context=context,
            )
