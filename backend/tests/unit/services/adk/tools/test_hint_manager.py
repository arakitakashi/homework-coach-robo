"""manage_hint_tool のテスト"""

from unittest.mock import MagicMock


def _make_tool_context(state: dict[str, object] | None = None) -> MagicMock:
    """テスト用のToolContextモックを作成する"""
    ctx = MagicMock()
    mock_state: dict[str, object] = dict(state) if state else {}
    ctx.state = mock_state
    return ctx


class TestManageHintGetCurrent:
    """get_current アクションのテスト"""

    def test_initial_state_returns_level_0(self) -> None:
        """初期状態ではレベル0を返す"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        result = manage_hint(session_id="sess1", action="get_current", tool_context=ctx)
        assert result["current_level"] == 0
        assert result["can_advance"] is True

    def test_existing_level_returned(self) -> None:
        """既存のレベルが正しく返される"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 2})
        result = manage_hint(session_id="sess1", action="get_current", tool_context=ctx)
        assert result["current_level"] == 2

    def test_max_level_is_3(self) -> None:
        """最大レベルは3"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        result = manage_hint(session_id="sess1", action="get_current", tool_context=ctx)
        assert result["max_level"] == 3


class TestManageHintAdvance:
    """advance アクションのテスト"""

    def test_advance_from_0_to_1(self) -> None:
        """レベル0から1に進む"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["current_level"] == 1
        assert ctx.state["hint_level"] == 1

    def test_advance_from_1_to_2(self) -> None:
        """レベル1から2に進む"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 1})
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["current_level"] == 2
        assert ctx.state["hint_level"] == 2

    def test_advance_from_2_to_3(self) -> None:
        """レベル2から3に進む"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 2})
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["current_level"] == 3
        assert result["can_advance"] is False

    def test_cannot_advance_beyond_3(self) -> None:
        """レベル3を超えられない"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 3})
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["current_level"] == 3
        assert result["can_advance"] is False

    def test_advance_increments_hints_used(self) -> None:
        """advance するとヒント使用回数が増える"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["hints_used_total"] == 2

    def test_hint_template_for_level_1(self) -> None:
        """レベル1のヒントテンプレートが返される"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert "問題" in result["hint_template"]

    def test_hint_template_for_level_2(self) -> None:
        """レベル2のヒントテンプレートが返される"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 1, "hints_used_total": 1})
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["current_level"] == 2

    def test_hint_template_for_level_3(self) -> None:
        """レベル3のヒントテンプレートが返される"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 2, "hints_used_total": 2})
        result = manage_hint(session_id="sess1", action="advance", tool_context=ctx)
        assert result["current_level"] == 3
        assert "ステップ" in result["hint_template"] or "一緒" in result["hint_template"]


class TestManageHintReset:
    """reset アクションのテスト"""

    def test_reset_sets_level_to_0(self) -> None:
        """リセットするとレベル0に戻る"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 3, "hints_used_total": 3})
        result = manage_hint(session_id="sess1", action="reset", tool_context=ctx)
        assert result["current_level"] == 0
        assert ctx.state["hint_level"] == 0
        assert result["can_advance"] is True

    def test_reset_preserves_hints_used_total(self) -> None:
        """リセットしてもヒント使用合計は保持"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context({"hint_level": 2, "hints_used_total": 5})
        result = manage_hint(session_id="sess1", action="reset", tool_context=ctx)
        assert result["hints_used_total"] == 5


class TestManageHintInvalidAction:
    """無効なアクションのテスト"""

    def test_invalid_action_returns_error(self) -> None:
        """無効なアクションはエラーを返す"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        result = manage_hint(session_id="sess1", action="invalid", tool_context=ctx)
        assert "error" in result


class TestManageHintReturnKeys:
    """返り値のキー確認テスト"""

    def test_returns_required_keys(self) -> None:
        """必要なキーがすべて含まれる"""
        from app.services.adk.tools.hint_manager import manage_hint

        ctx = _make_tool_context()
        result = manage_hint(session_id="sess1", action="get_current", tool_context=ctx)
        assert "current_level" in result
        assert "max_level" in result
        assert "hint_template" in result
        assert "can_advance" in result
        assert "hints_used_total" in result


class TestManageHintTool:
    """manage_hint_tool FunctionTool のテスト"""

    def test_is_function_tool_instance(self) -> None:
        """FunctionTool インスタンスである"""
        from google.adk.tools import FunctionTool

        from app.services.adk.tools.hint_manager import manage_hint_tool

        assert isinstance(manage_hint_tool, FunctionTool)
