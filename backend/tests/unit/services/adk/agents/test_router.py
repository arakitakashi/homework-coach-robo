"""Router Agent のテスト"""

from typing import Any
from unittest.mock import MagicMock, patch

_ROUTER_PREFIX = "app.services.adk.agents.router"


def _patch_all_sub_agents(**overrides: MagicMock) -> tuple[Any, ...]:
    """Router の全サブエージェント作成関数をまとめてパッチするヘルパー

    Returns:
        tuple of patch context managers
    """
    return (
        patch(
            f"{_ROUTER_PREFIX}.create_math_coach_agent",
            **({"return_value": overrides["math"]} if "math" in overrides else {}),
        ),
        patch(
            f"{_ROUTER_PREFIX}.create_japanese_coach_agent",
            **({"return_value": overrides["japanese"]} if "japanese" in overrides else {}),
        ),
        patch(
            f"{_ROUTER_PREFIX}.create_encouragement_agent",
            **(
                {"return_value": overrides["encouragement"]} if "encouragement" in overrides else {}
            ),
        ),
        patch(
            f"{_ROUTER_PREFIX}.create_review_agent",
            **({"return_value": overrides["review"]} if "review" in overrides else {}),
        ),
    )


class TestRouterSystemPrompt:
    """ルーターエージェントのシステムプロンプトのテスト"""

    def test_contains_routing_role(self) -> None:
        """ルーティングの役割が含まれる"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert (
            "リーダー" in ROUTER_SYSTEM_PROMPT
            or "振り分" in ROUTER_SYSTEM_PROMPT
            or "繋" in ROUTER_SYSTEM_PROMPT
        )

    def test_contains_math_routing(self) -> None:
        """算数ルーティング基準が含まれる"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert "math_coach" in ROUTER_SYSTEM_PROMPT
        assert "算数" in ROUTER_SYSTEM_PROMPT

    def test_contains_japanese_routing(self) -> None:
        """国語ルーティング基準が含まれる"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert "japanese_coach" in ROUTER_SYSTEM_PROMPT
        assert "国語" in ROUTER_SYSTEM_PROMPT or "漢字" in ROUTER_SYSTEM_PROMPT

    def test_contains_encouragement_routing(self) -> None:
        """励ましルーティング基準が含まれる"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert "encouragement_agent" in ROUTER_SYSTEM_PROMPT
        assert "疲れた" in ROUTER_SYSTEM_PROMPT or "わからない" in ROUTER_SYSTEM_PROMPT

    def test_contains_review_routing(self) -> None:
        """振り返りルーティング基準が含まれる"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert "review_agent" in ROUTER_SYSTEM_PROMPT
        assert "振り返り" in ROUTER_SYSTEM_PROMPT

    def test_contains_uncertainty_handling(self) -> None:
        """判断困難時の対応指示がある"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert "難しい" in ROUTER_SYSTEM_PROMPT or "確認" in ROUTER_SYSTEM_PROMPT

    def test_does_not_solve_problems(self) -> None:
        """自分で問題を解かないルールがある"""
        from app.services.adk.agents.prompts.router import ROUTER_SYSTEM_PROMPT

        assert "解いたり" in ROUTER_SYSTEM_PROMPT or "教えたり" in ROUTER_SYSTEM_PROMPT


class TestCreateRouterAgent:
    """create_router_agent 関数のテスト"""

    def test_creates_agent_with_correct_name(self) -> None:
        """正しい名前が設定される"""
        from app.services.adk.agents.router import create_router_agent

        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents()
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["name"] == "router_agent"

    def test_creates_agent_with_default_model(self) -> None:
        """デフォルトモデルが設定される"""
        from app.services.adk.agents.router import create_router_agent

        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents()
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert call_kwargs["model"] == "gemini-2.5-flash"

    def test_has_description(self) -> None:
        """説明が設定される"""
        from app.services.adk.agents.router import create_router_agent

        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents()
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["description"]) > 0

    def test_has_no_tools(self) -> None:
        """ツールを持たない（ルーティングのみ）"""
        from app.services.adk.agents.router import create_router_agent

        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents()
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert "tools" not in call_kwargs or call_kwargs.get("tools") is None

    def test_has_four_sub_agents(self) -> None:
        """4つのサブエージェントが設定される"""
        from app.services.adk.agents.router import create_router_agent

        mock_math = MagicMock(name="math_coach")
        mock_japanese = MagicMock(name="japanese_coach")
        mock_encouragement = MagicMock(name="encouragement_agent")
        mock_review = MagicMock(name="review_agent")

        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents(
            math=mock_math,
            japanese=mock_japanese,
            encouragement=mock_encouragement,
            review=mock_review,
        )
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert len(call_kwargs["sub_agents"]) == 4

    def test_sub_agents_include_math_coach(self) -> None:
        """Math Coach がサブエージェントに含まれる"""
        from app.services.adk.agents.router import create_router_agent

        mock_math = MagicMock(name="math_coach")
        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents(math=mock_math)
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert mock_math in call_kwargs["sub_agents"]

    def test_sub_agents_include_japanese_coach(self) -> None:
        """Japanese Coach がサブエージェントに含まれる"""
        from app.services.adk.agents.router import create_router_agent

        mock_japanese = MagicMock(name="japanese_coach")
        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents(japanese=mock_japanese)
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert mock_japanese in call_kwargs["sub_agents"]

    def test_sub_agents_include_encouragement(self) -> None:
        """Encouragement がサブエージェントに含まれる"""
        from app.services.adk.agents.router import create_router_agent

        mock_encouragement = MagicMock(name="encouragement_agent")
        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents(encouragement=mock_encouragement)
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert mock_encouragement in call_kwargs["sub_agents"]

    def test_sub_agents_include_review(self) -> None:
        """Review がサブエージェントに含まれる"""
        from app.services.adk.agents.router import create_router_agent

        mock_review = MagicMock(name="review_agent")
        p_math, p_jp, p_enc, p_rev = _patch_all_sub_agents(review=mock_review)
        with (
            patch(f"{_ROUTER_PREFIX}.Agent") as MockAgent,
            p_math,
            p_jp,
            p_enc,
            p_rev,
        ):
            create_router_agent()
            call_kwargs = MockAgent.call_args[1]
            assert mock_review in call_kwargs["sub_agents"]

    def test_passes_model_to_sub_agents(self) -> None:
        """カスタムモデルがサブエージェントに渡される"""
        from app.services.adk.agents.router import create_router_agent

        with (
            patch(f"{_ROUTER_PREFIX}.Agent"),
            patch(f"{_ROUTER_PREFIX}.create_math_coach_agent") as mock_create_math,
            patch(f"{_ROUTER_PREFIX}.create_japanese_coach_agent") as mock_create_japanese,
            patch(f"{_ROUTER_PREFIX}.create_encouragement_agent") as mock_create_encouragement,
            patch(f"{_ROUTER_PREFIX}.create_review_agent") as mock_create_review,
        ):
            create_router_agent(model="gemini-2.5-pro")
            mock_create_math.assert_called_once_with(model="gemini-2.5-pro")
            mock_create_japanese.assert_called_once_with(model="gemini-2.5-pro")
            mock_create_encouragement.assert_called_once_with(model="gemini-2.5-pro")
            mock_create_review.assert_called_once_with(model="gemini-2.5-pro")
