"""update_emotion_tool のテスト"""

from unittest.mock import MagicMock


def _make_tool_context(state: dict[str, object] | None = None) -> MagicMock:
    """テスト用のToolContextモックを作成する"""
    ctx = MagicMock()
    mock_state: dict[str, object] = dict(state) if state else {}
    ctx.state = mock_state
    return ctx


class TestUpdateEmotionBasic:
    """基本的な感情スコア記録のテスト"""

    def test_records_emotion_scores_in_state(self) -> None:
        """感情スコアが session.state["emotion"] に記録される"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=0.3,
            confidence=0.7,
            fatigue=0.2,
            excitement=0.5,
            primary_emotion="neutral",
            tool_context=ctx,
        )
        emotion = ctx.state["emotion"]
        assert emotion["frustration"] == 0.3
        assert emotion["confidence"] == 0.7
        assert emotion["fatigue"] == 0.2
        assert emotion["excitement"] == 0.5

    def test_records_primary_emotion(self) -> None:
        """primary_emotion が session.state に記録される"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=0.8,
            confidence=0.1,
            fatigue=0.3,
            excitement=0.1,
            primary_emotion="frustrated",
            tool_context=ctx,
        )
        assert ctx.state["emotion"]["primary_emotion"] == "frustrated"

    def test_returns_primary_emotion(self) -> None:
        """返り値に primary_emotion が含まれる"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.0,
            confidence=0.9,
            fatigue=0.0,
            excitement=0.8,
            primary_emotion="confident",
            tool_context=ctx,
        )
        assert result["primary_emotion"] == "confident"

    def test_records_updated_at(self) -> None:
        """updated_at タイムスタンプが記録される"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=0.0,
            confidence=0.5,
            fatigue=0.0,
            excitement=0.5,
            primary_emotion="neutral",
            tool_context=ctx,
        )
        assert "updated_at" in ctx.state["emotion"]


class TestSupportLevel:
    """サポートレベル計算のテスト"""

    def test_intensive_when_frustration_high(self) -> None:
        """frustration > 0.7 → intensive"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.8,
            confidence=0.2,
            fatigue=0.1,
            excitement=0.1,
            primary_emotion="frustrated",
            tool_context=ctx,
        )
        assert result["support_level"] == "intensive"

    def test_intensive_when_fatigue_high(self) -> None:
        """fatigue > 0.6 → intensive"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.1,
            confidence=0.3,
            fatigue=0.7,
            excitement=0.1,
            primary_emotion="tired",
            tool_context=ctx,
        )
        assert result["support_level"] == "intensive"

    def test_moderate_when_frustration_medium(self) -> None:
        """frustration > 0.4 → moderate"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.5,
            confidence=0.3,
            fatigue=0.2,
            excitement=0.2,
            primary_emotion="confused",
            tool_context=ctx,
        )
        assert result["support_level"] == "moderate"

    def test_moderate_when_fatigue_medium(self) -> None:
        """fatigue > 0.3 → moderate"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.2,
            confidence=0.5,
            fatigue=0.4,
            excitement=0.3,
            primary_emotion="neutral",
            tool_context=ctx,
        )
        assert result["support_level"] == "moderate"

    def test_minimal_when_low_stress(self) -> None:
        """低ストレス → minimal"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.1,
            confidence=0.8,
            fatigue=0.1,
            excitement=0.7,
            primary_emotion="happy",
            tool_context=ctx,
        )
        assert result["support_level"] == "minimal"

    def test_support_level_recorded_in_state(self) -> None:
        """support_level が session.state に記録される"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=0.8,
            confidence=0.1,
            fatigue=0.1,
            excitement=0.1,
            primary_emotion="frustrated",
            tool_context=ctx,
        )
        assert ctx.state["emotion"]["support_level"] == "intensive"


class TestActionRecommended:
    """action_recommended 計算のテスト"""

    def test_encourage_when_frustrated(self) -> None:
        """frustration > 0.7 → encourage"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.8,
            confidence=0.1,
            fatigue=0.2,
            excitement=0.1,
            primary_emotion="frustrated",
            tool_context=ctx,
        )
        assert result["action_recommended"] == "encourage"

    def test_rest_when_fatigued(self) -> None:
        """fatigue > 0.6 → rest"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.1,
            confidence=0.3,
            fatigue=0.7,
            excitement=0.1,
            primary_emotion="tired",
            tool_context=ctx,
        )
        assert result["action_recommended"] == "rest"

    def test_continue_when_stable(self) -> None:
        """安定状態 → continue"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.2,
            confidence=0.6,
            fatigue=0.2,
            excitement=0.5,
            primary_emotion="neutral",
            tool_context=ctx,
        )
        assert result["action_recommended"] == "continue"

    def test_rest_takes_priority_over_encourage(self) -> None:
        """fatigue と frustration 両方高い → rest が優先"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.9,
            confidence=0.1,
            fatigue=0.8,
            excitement=0.1,
            primary_emotion="frustrated",
            tool_context=ctx,
        )
        assert result["action_recommended"] == "rest"


class TestScoreValidation:
    """スコアバリデーションのテスト"""

    def test_clamps_negative_score(self) -> None:
        """負のスコアは 0.0 にクランプされる"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=-0.5,
            confidence=0.5,
            fatigue=0.0,
            excitement=0.5,
            primary_emotion="neutral",
            tool_context=ctx,
        )
        assert ctx.state["emotion"]["frustration"] == 0.0

    def test_clamps_score_above_1(self) -> None:
        """1.0 超のスコアは 1.0 にクランプされる"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=0.5,
            confidence=1.5,
            fatigue=0.0,
            excitement=0.5,
            primary_emotion="confident",
            tool_context=ctx,
        )
        assert ctx.state["emotion"]["confidence"] == 1.0

    def test_boundary_values_accepted(self) -> None:
        """境界値 0.0 と 1.0 はそのまま受け入れる"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        update_emotion(
            frustration=0.0,
            confidence=1.0,
            fatigue=0.0,
            excitement=1.0,
            primary_emotion="happy",
            tool_context=ctx,
        )
        assert ctx.state["emotion"]["frustration"] == 0.0
        assert ctx.state["emotion"]["confidence"] == 1.0


class TestPrimaryEmotionValidation:
    """primary_emotion バリデーションのテスト"""

    def test_valid_emotions_accepted(self) -> None:
        """有効な感情値が受け入れられる"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        valid_emotions = ["frustrated", "confident", "confused", "happy", "tired", "neutral"]
        for emotion in valid_emotions:
            ctx = _make_tool_context()
            result = update_emotion(
                frustration=0.5,
                confidence=0.5,
                fatigue=0.5,
                excitement=0.5,
                primary_emotion=emotion,
                tool_context=ctx,
            )
            assert "error" not in result

    def test_invalid_emotion_returns_error(self) -> None:
        """無効な感情値はエラーを返す"""
        from app.services.adk.tools.emotion_analyzer import update_emotion

        ctx = _make_tool_context()
        result = update_emotion(
            frustration=0.5,
            confidence=0.5,
            fatigue=0.5,
            excitement=0.5,
            primary_emotion="angry",
            tool_context=ctx,
        )
        assert "error" in result


class TestUpdateEmotionTool:
    """update_emotion_tool FunctionTool のテスト"""

    def test_is_function_tool_instance(self) -> None:
        """FunctionTool インスタンスである"""
        from app.services.adk.tools.emotion_analyzer import update_emotion_tool
        from google.adk.tools import FunctionTool

        assert isinstance(update_emotion_tool, FunctionTool)
