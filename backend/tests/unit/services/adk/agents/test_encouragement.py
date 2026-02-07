"""Encouragement Agent のテスト"""

from unittest.mock import patch


class TestEncouragementSystemPrompt:
    """励ましエージェントのシステムプロンプトのテスト"""

    def test_contains_encouragement_role(self) -> None:
        """励まし・応援の役割が含まれる"""
        from app.services.adk.agents.prompts.encouragement import (
            ENCOURAGEMENT_SYSTEM_PROMPT,
        )

        assert "励まし" in ENCOURAGEMENT_SYSTEM_PROMPT or "応援" in ENCOURAGEMENT_SYSTEM_PROMPT

    def test_contains_break_suggestion(self) -> None:
        """休憩提案の内容が含まれる"""
        from app.services.adk.agents.prompts.encouragement import (
            ENCOURAGEMENT_SYSTEM_PROMPT,
        )

        assert "休憩" in ENCOURAGEMENT_SYSTEM_PROMPT

    def test_contains_growth_mindset(self) -> None:
        """成長マインドセットの内容が含まれる"""
        from app.services.adk.agents.prompts.encouragement import (
            ENCOURAGEMENT_SYSTEM_PROMPT,
        )

        assert "成長" in ENCOURAGEMENT_SYSTEM_PROMPT or "間違い" in ENCOURAGEMENT_SYSTEM_PROMPT

    def test_contains_negative_emotion_handling(self) -> None:
        """ネガティブ感情への対応が含まれる"""
        from app.services.adk.agents.prompts.encouragement import (
            ENCOURAGEMENT_SYSTEM_PROMPT,
        )

        assert "疲れた" in ENCOURAGEMENT_SYSTEM_PROMPT
        assert "わからない" in ENCOURAGEMENT_SYSTEM_PROMPT

    def test_does_not_blame(self) -> None:
        """叱らない・責めないルールが含まれる"""
        from app.services.adk.agents.prompts.encouragement import (
            ENCOURAGEMENT_SYSTEM_PROMPT,
        )

        assert (
            "叱らない" in ENCOURAGEMENT_SYSTEM_PROMPT or "責めない" in ENCOURAGEMENT_SYSTEM_PROMPT
        )


class TestCreateEncouragementAgent:
    """create_encouragement_agent 関数のテスト"""

    def test_creates_agent_with_correct_name(self) -> None:
        """正しい名前が設定される"""
        from app.services.adk.agents.encouragement import create_encouragement_agent

        with patch("app.services.adk.agents.encouragement.Agent") as MockAgent:
            create_encouragement_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["name"] == "encouragement_agent"

    def test_creates_agent_with_default_model(self) -> None:
        """デフォルトモデルが設定される"""
        from app.services.adk.agents.encouragement import create_encouragement_agent

        with patch("app.services.adk.agents.encouragement.Agent") as MockAgent:
            create_encouragement_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-flash"

    def test_has_description(self) -> None:
        """説明が設定される"""
        from app.services.adk.agents.encouragement import create_encouragement_agent

        with patch("app.services.adk.agents.encouragement.Agent") as MockAgent:
            create_encouragement_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["description"]) > 0

    def test_has_one_tool(self) -> None:
        """1つのツールが設定される"""
        from app.services.adk.agents.encouragement import create_encouragement_agent

        with patch("app.services.adk.agents.encouragement.Agent") as MockAgent:
            create_encouragement_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["tools"]) == 1

    def test_includes_record_progress_tool(self) -> None:
        """record_progress_tool が含まれる"""
        from app.services.adk.agents.encouragement import create_encouragement_agent
        from app.services.adk.tools.progress_recorder import record_progress_tool

        with patch("app.services.adk.agents.encouragement.Agent") as MockAgent:
            create_encouragement_agent()
            call_kwargs = MockAgent.call_args[1]
            assert record_progress_tool in call_kwargs["tools"]

    def test_has_no_sub_agents(self) -> None:
        """サブエージェントを持たない"""
        from app.services.adk.agents.encouragement import create_encouragement_agent

        with patch("app.services.adk.agents.encouragement.Agent") as MockAgent:
            create_encouragement_agent()
            call_kwargs = MockAgent.call_args[1]
            assert "sub_agents" not in call_kwargs or call_kwargs.get("sub_agents") is None
