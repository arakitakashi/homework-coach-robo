"""Review Agent のテスト"""

from unittest.mock import patch


class TestReviewSystemPrompt:
    """振り返りエージェントのシステムプロンプトのテスト"""

    def test_contains_review_role(self) -> None:
        """振り返りの役割が含まれる"""
        from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT

        assert "振り返" in REVIEW_SYSTEM_PROMPT

    def test_contains_parent_report(self) -> None:
        """保護者向けレポートの内容が含まれる"""
        from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT

        assert "保護者" in REVIEW_SYSTEM_PROMPT

    def test_contains_session_summary(self) -> None:
        """セッションサマリーの内容が含まれる"""
        from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT

        assert (
            "サマリー" in REVIEW_SYSTEM_PROMPT
            or "まとめ" in REVIEW_SYSTEM_PROMPT
            or "学習内容" in REVIEW_SYSTEM_PROMPT
        )

    def test_contains_positive_content(self) -> None:
        """ポジティブな内容が含まれる"""
        from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT

        assert (
            "頑張り" in REVIEW_SYSTEM_PROMPT
            or "褒める" in REVIEW_SYSTEM_PROMPT
            or "頑張った" in REVIEW_SYSTEM_PROMPT
        )

    def test_mentions_record_progress_tool(self) -> None:
        """record_progress ツールの使用指示がある"""
        from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT

        assert "record_progress" in REVIEW_SYSTEM_PROMPT

    def test_mentions_load_memory_tool(self) -> None:
        """load_memory ツールの使用指示がある"""
        from app.services.adk.agents.prompts.review import REVIEW_SYSTEM_PROMPT

        assert "load_memory" in REVIEW_SYSTEM_PROMPT


class TestCreateReviewAgent:
    """create_review_agent 関数のテスト"""

    def test_creates_agent_with_correct_name(self) -> None:
        """正しい名前が設定される"""
        from app.services.adk.agents.review import create_review_agent

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["name"] == "review_agent"

    def test_creates_agent_with_default_model(self) -> None:
        """デフォルトモデルが設定される"""
        from app.services.adk.agents.review import create_review_agent

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-flash"

    def test_has_description(self) -> None:
        """説明が設定される"""
        from app.services.adk.agents.review import create_review_agent

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["description"]) > 0

    def test_has_two_tools(self) -> None:
        """2つのツールが設定される（record_progress + load_memory）"""
        from app.services.adk.agents.review import create_review_agent

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["tools"]) == 2

    def test_includes_record_progress_tool(self) -> None:
        """record_progress_tool が含まれる"""
        from app.services.adk.agents.review import create_review_agent
        from app.services.adk.tools.progress_recorder import record_progress_tool

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert record_progress_tool in call_kwargs["tools"]

    def test_includes_load_memory_tool(self) -> None:
        """load_memory ツールが含まれる"""
        from google.adk.tools import load_memory  # type: ignore[attr-defined]

        from app.services.adk.agents.review import create_review_agent

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert load_memory in call_kwargs["tools"]

    def test_has_no_sub_agents(self) -> None:
        """サブエージェントを持たない"""
        from app.services.adk.agents.review import create_review_agent

        with patch("app.services.adk.agents.review.Agent") as MockAgent:
            create_review_agent()
            call_kwargs = MockAgent.call_args[1]
            assert "sub_agents" not in call_kwargs or call_kwargs.get("sub_agents") is None
