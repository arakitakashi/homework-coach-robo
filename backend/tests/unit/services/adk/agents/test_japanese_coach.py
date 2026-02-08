"""Japanese Coach Agent のテスト"""

from unittest.mock import patch


class TestJapaneseCoachSystemPrompt:
    """国語コーチのシステムプロンプトのテスト"""

    def test_contains_japanese_focus(self) -> None:
        """国語に特化した内容が含まれる"""
        from app.services.adk.agents.prompts.japanese_coach import (
            JAPANESE_COACH_SYSTEM_PROMPT,
        )

        assert "国語" in JAPANESE_COACH_SYSTEM_PROMPT

    def test_contains_socratic_principle(self) -> None:
        """ソクラテス式の原則が含まれる"""
        from app.services.adk.agents.prompts.japanese_coach import (
            JAPANESE_COACH_SYSTEM_PROMPT,
        )

        assert "答え" in JAPANESE_COACH_SYSTEM_PROMPT
        assert "教えない" in JAPANESE_COACH_SYSTEM_PROMPT

    def test_contains_three_level_hint_system(self) -> None:
        """3段階ヒントシステムが含まれる"""
        from app.services.adk.agents.prompts.japanese_coach import (
            JAPANESE_COACH_SYSTEM_PROMPT,
        )

        assert "レベル1" in JAPANESE_COACH_SYSTEM_PROMPT
        assert "レベル2" in JAPANESE_COACH_SYSTEM_PROMPT
        assert "レベル3" in JAPANESE_COACH_SYSTEM_PROMPT

    def test_contains_japanese_topics(self) -> None:
        """国語の主要トピックが含まれる"""
        from app.services.adk.agents.prompts.japanese_coach import (
            JAPANESE_COACH_SYSTEM_PROMPT,
        )

        assert "漢字" in JAPANESE_COACH_SYSTEM_PROMPT
        assert "読解" in JAPANESE_COACH_SYSTEM_PROMPT
        assert "作文" in JAPANESE_COACH_SYSTEM_PROMPT

    def test_mentions_manage_hint_tool(self) -> None:
        """manage_hint ツールの使用指示がある"""
        from app.services.adk.agents.prompts.japanese_coach import (
            JAPANESE_COACH_SYSTEM_PROMPT,
        )

        assert "manage_hint" in JAPANESE_COACH_SYSTEM_PROMPT


class TestCreateJapaneseCoachAgent:
    """create_japanese_coach_agent 関数のテスト"""

    def test_creates_agent_with_correct_name(self) -> None:
        """正しい名前が設定される"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["name"] == "japanese_coach"

    def test_creates_agent_with_default_model(self) -> None:
        """デフォルトモデルが設定される"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-flash"

    def test_accepts_custom_model(self) -> None:
        """カスタムモデルを受け入れる"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent(model="gemini-2.5-pro")
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-pro"

    def test_has_description(self) -> None:
        """説明が設定される"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["description"]) > 0

    def test_has_three_tools(self) -> None:
        """3つのツールが設定される"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["tools"]) == 3

    def test_includes_manage_hint_tool(self) -> None:
        """manage_hint_tool が含まれる"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
        from app.services.adk.tools.hint_manager import manage_hint_tool

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert manage_hint_tool in call_kwargs["tools"]

    def test_includes_check_curriculum_tool(self) -> None:
        """check_curriculum_tool が含まれる"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
        from app.services.adk.tools.curriculum import check_curriculum_tool

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert check_curriculum_tool in call_kwargs["tools"]

    def test_includes_record_progress_tool(self) -> None:
        """record_progress_tool が含まれる"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
        from app.services.adk.tools.progress_recorder import record_progress_tool

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert record_progress_tool in call_kwargs["tools"]

    def test_does_not_include_calculate_tool(self) -> None:
        """calculate_tool は含まれない（Math Coach 専用）"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent
        from app.services.adk.tools.calculate import calculate_tool

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert calculate_tool not in call_kwargs["tools"]

    def test_has_no_sub_agents(self) -> None:
        """サブエージェントを持たない"""
        from app.services.adk.agents.japanese_coach import create_japanese_coach_agent

        with patch("app.services.adk.agents.japanese_coach.Agent") as MockAgent:
            create_japanese_coach_agent()
            call_kwargs = MockAgent.call_args[1]
            assert "sub_agents" not in call_kwargs or call_kwargs.get("sub_agents") is None
