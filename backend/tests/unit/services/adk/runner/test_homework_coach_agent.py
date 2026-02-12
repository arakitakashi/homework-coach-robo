"""HomeworkCoachAgent のテスト

Agent Engine デプロイ用ラッパークラスのテスト。
インスタンス化とメソッドシグネチャの確認を行う。
"""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.adk.runner.homework_coach_agent import HomeworkCoachAgent


class TestHomeworkCoachAgentInit:
    """初期化テスト"""

    def test_stores_agent(self) -> None:
        """エージェントを保持する"""
        mock_agent = MagicMock()
        wrapper = HomeworkCoachAgent(mock_agent)
        assert wrapper._agent is mock_agent

    def test_runner_is_initially_none(self) -> None:
        """Runner は初期状態で None"""
        mock_agent = MagicMock()
        wrapper = HomeworkCoachAgent(mock_agent)
        assert wrapper._runner is None


class TestGetRunner:
    """_get_runner のテスト"""

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_lazy_initializes_runner(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_memory_factory: MagicMock,
    ) -> None:
        """Runner を遅延初期化する"""
        mock_agent = MagicMock()
        mock_session = MagicMock()
        mock_memory = MagicMock()
        mock_session_factory.return_value = mock_session
        mock_memory_factory.return_value = mock_memory
        mock_runner_instance = MagicMock()
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(mock_agent)
        runner = wrapper._get_runner()

        assert runner is mock_runner_instance
        mock_runner_cls.assert_called_once_with(
            app_name="homework-coach-agent-engine",
            agent=mock_agent,
            session_service=mock_session,
            memory_service=mock_memory,
        )

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_returns_cached_runner(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """2回目以降はキャッシュされた Runner を返す"""
        mock_agent = MagicMock()
        wrapper = HomeworkCoachAgent(mock_agent)

        runner1 = wrapper._get_runner()
        runner2 = wrapper._get_runner()

        assert runner1 is runner2
        mock_runner_cls.assert_called_once()


class TestCreateSession:
    """create_session のテスト"""

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_creates_session_and_returns_id(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """セッションを作成し ID を返す"""
        mock_session = MagicMock()
        mock_session.id = "test-session-id"

        mock_runner_instance = MagicMock()
        mock_runner_instance.session_service.create_session = AsyncMock(
            return_value=mock_session,
        )
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())
        result = wrapper.create_session(user_id="user-1")

        assert result == {"id": "test-session-id"}

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_passes_correct_app_name_and_user_id(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """正しい app_name と user_id を渡す"""
        mock_session = MagicMock()
        mock_session.id = "s-1"
        mock_create = AsyncMock(return_value=mock_session)

        mock_runner_instance = MagicMock()
        mock_runner_instance.session_service.create_session = mock_create
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())
        wrapper.create_session(user_id="user-42")

        mock_create.assert_called_once_with(
            app_name="homework-coach-agent-engine",
            user_id="user-42",
        )


class TestStreamQuery:
    """stream_query のテスト"""

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_returns_generator(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """Generator を返す"""

        # run_async が空のイベントを返すようにモック
        async def mock_run_async(**kwargs: object) -> None:  # noqa: ARG001
            return
            yield  # noqa: B027 - async generator にするため

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())
        result = wrapper.stream_query(
            user_id="u-1",
            session_id="s-1",
            message="テスト",
        )

        assert isinstance(result, Generator)

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_yields_events_in_expected_format(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """イベントを期待するフォーマットで yield する"""

        async def mock_run_async(**kwargs: object) -> None:  # noqa: ARG001
            event1 = MagicMock()
            part1 = MagicMock()
            part1.text = "こんにちは"
            event1.content.parts = [part1]
            yield event1

            event2 = MagicMock()
            part2 = MagicMock()
            part2.text = "元気ですか？"
            event2.content.parts = [part2]
            yield event2

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())
        events = list(
            wrapper.stream_query(
                user_id="u-1",
                session_id="s-1",
                message="テスト",
            )
        )

        assert len(events) == 2
        assert events[0] == {"content": {"parts": [{"text": "こんにちは"}]}}
        assert events[1] == {"content": {"parts": [{"text": "元気ですか？"}]}}


class TestQuery:
    """query のテスト"""

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_returns_joined_response(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """複数パートの応答を結合して返す"""

        async def mock_run_async(**kwargs: object) -> None:  # noqa: ARG001
            event = MagicMock()
            part1 = MagicMock()
            part1.text = "答えは"
            part2 = MagicMock()
            part2.text = "42です"
            event.content.parts = [part1, part2]
            yield event

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())
        result = wrapper.query("テスト")

        assert result == "答えは 42です"

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_skips_events_without_text(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """テキストのないイベントをスキップする"""

        async def mock_run_async(**kwargs: object) -> None:  # noqa: ARG001
            # content が None のイベント
            event1 = MagicMock()
            event1.content = None
            yield event1

            # テキストありのイベント
            event2 = MagicMock()
            part = MagicMock()
            part.text = "応答テキスト"
            event2.content.parts = [part]
            yield event2

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())
        result = wrapper.query("テスト")

        assert result == "応答テキスト"
