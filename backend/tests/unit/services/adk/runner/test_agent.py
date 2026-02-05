"""SocraticDialogueAgent のテスト"""

from unittest.mock import MagicMock, patch


class TestSocraticSystemPrompt:
    """システムプロンプトのテスト"""

    def test_contains_three_level_hint_system(self) -> None:
        """3段階ヒントシステムの原則が含まれる"""
        from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT

        # レベル1: 問題理解の確認
        assert "問題理解" in SOCRATIC_SYSTEM_PROMPT or "レベル1" in SOCRATIC_SYSTEM_PROMPT
        # レベル2: 既習事項の想起
        assert "既習" in SOCRATIC_SYSTEM_PROMPT or "レベル2" in SOCRATIC_SYSTEM_PROMPT
        # レベル3: 部分的支援
        assert "部分的" in SOCRATIC_SYSTEM_PROMPT or "レベル3" in SOCRATIC_SYSTEM_PROMPT

    def test_contains_no_direct_answer_rule(self) -> None:
        """答えを直接教えないルールが含まれる"""
        from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT

        assert "答え" in SOCRATIC_SYSTEM_PROMPT
        assert "教えない" in SOCRATIC_SYSTEM_PROMPT or "直接" in SOCRATIC_SYSTEM_PROMPT

    def test_contains_child_friendly_instruction(self) -> None:
        """小学校低学年向けの言葉遣い指示が含まれる"""
        from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT

        assert "小学" in SOCRATIC_SYSTEM_PROMPT or "低学年" in SOCRATIC_SYSTEM_PROMPT
        assert "簡単" in SOCRATIC_SYSTEM_PROMPT or "やさしい" in SOCRATIC_SYSTEM_PROMPT

    def test_contains_encouragement_principle(self) -> None:
        """励ましの原則が含まれる"""
        from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT

        assert "励まし" in SOCRATIC_SYSTEM_PROMPT or "肯定" in SOCRATIC_SYSTEM_PROMPT

    def test_contains_one_question_at_a_time_rule(self) -> None:
        """一度に1つの質問だけするルールが含まれる"""
        from app.services.adk.runner.agent import SOCRATIC_SYSTEM_PROMPT

        assert "1つ" in SOCRATIC_SYSTEM_PROMPT or "一度に" in SOCRATIC_SYSTEM_PROMPT


class TestCreateSocraticAgent:
    """create_socratic_agent関数のテスト"""

    def test_creates_agent_with_correct_model(self) -> None:
        """正しいモデル名が設定される"""
        from app.services.adk.runner.agent import create_socratic_agent

        with patch("app.services.adk.runner.agent.Agent") as MockAgent:
            create_socratic_agent()
            MockAgent.assert_called_once()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-flash"

    def test_creates_agent_with_correct_name(self) -> None:
        """正しい名前が設定される"""
        from app.services.adk.runner.agent import create_socratic_agent

        with patch("app.services.adk.runner.agent.Agent") as MockAgent:
            create_socratic_agent()
            call_kwargs = MockAgent.call_args[1]
            assert "socratic" in call_kwargs["name"].lower()

    def test_creates_agent_with_description(self) -> None:
        """説明が設定される"""
        from app.services.adk.runner.agent import create_socratic_agent

        with patch("app.services.adk.runner.agent.Agent") as MockAgent:
            create_socratic_agent()
            call_kwargs = MockAgent.call_args[1]
            assert "description" in call_kwargs
            assert len(call_kwargs["description"]) > 0

    def test_creates_agent_with_instruction(self) -> None:
        """システムプロンプトが設定される"""
        from app.services.adk.runner.agent import (
            SOCRATIC_SYSTEM_PROMPT,
            create_socratic_agent,
        )

        with patch("app.services.adk.runner.agent.Agent") as MockAgent:
            create_socratic_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["instruction"] == SOCRATIC_SYSTEM_PROMPT

    def test_returns_agent_instance(self) -> None:
        """Agent インスタンスを返す"""
        from app.services.adk.runner.agent import create_socratic_agent

        mock_agent = MagicMock()
        with patch("app.services.adk.runner.agent.Agent", return_value=mock_agent):
            result = create_socratic_agent()
            assert result == mock_agent


class TestCreateSocraticAgentWithCustomModel:
    """カスタムモデルでのAgent作成テスト"""

    def test_accepts_custom_model(self) -> None:
        """カスタムモデルを受け入れる"""
        from app.services.adk.runner.agent import create_socratic_agent

        with patch("app.services.adk.runner.agent.Agent") as MockAgent:
            create_socratic_agent(model="gemini-2.5-pro")
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-pro"

    def test_uses_default_model_when_not_specified(self) -> None:
        """モデルが指定されない場合はデフォルトを使用"""
        from app.services.adk.runner.agent import create_socratic_agent

        with patch("app.services.adk.runner.agent.Agent") as MockAgent:
            create_socratic_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-flash"
