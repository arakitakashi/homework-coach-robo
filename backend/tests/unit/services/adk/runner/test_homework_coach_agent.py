"""HomeworkCoachAgent のテスト

Agent Engine デプロイ用ラッパークラスのテスト。
インスタンス化とメソッドシグネチャの確認を行う。
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
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

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_AGENT_ENGINE_ID": "test-engine-123",
            "GOOGLE_CLOUD_PROJECT": "test-project",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
        },
    )
    @patch("app.services.adk.runner.homework_coach_agent.InMemoryMemoryService")
    @patch("app.services.adk.runner.homework_coach_agent.InMemorySessionService")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_uses_in_memory_services_when_agent_engine_env_set(
        self,
        mock_runner_cls: MagicMock,
        mock_memory_session_cls: MagicMock,
        mock_memory_memory_cls: MagicMock,
    ) -> None:
        """Agent Engine 環境変数が設定されている場合、InMemory サービスを使用する

        VertexAiSessionService は Agent Engine 内部では session_events.list() API が
        INVALID_ARGUMENT を返すため、InMemorySessionService を使用する。
        """
        mock_agent = MagicMock()
        mock_in_memory_session = MagicMock()
        mock_in_memory_memory = MagicMock()
        mock_memory_session_cls.return_value = mock_in_memory_session
        mock_memory_memory_cls.return_value = mock_in_memory_memory
        mock_runner_instance = MagicMock()
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(mock_agent)
        runner = wrapper._get_runner()

        assert runner is mock_runner_instance
        # InMemorySessionService がパラメータなしで呼ばれたことを確認
        mock_memory_session_cls.assert_called_once_with()
        # InMemoryMemoryService がパラメータなしで呼ばれたことを確認
        mock_memory_memory_cls.assert_called_once_with()
        # Runner に InMemory サービスが渡されたことを確認
        mock_runner_cls.assert_called_once_with(
            app_name="homework-coach-agent-engine",
            agent=mock_agent,
            session_service=mock_in_memory_session,
            memory_service=mock_in_memory_memory,
        )

    @patch.dict(
        "os.environ",
        {
            "GOOGLE_CLOUD_AGENT_ENGINE_ID": "",
        },
        clear=False,
    )
    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_falls_back_to_factory_when_no_agent_engine_env(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,
        mock_memory_factory: MagicMock,
    ) -> None:
        """GOOGLE_CLOUD_AGENT_ENGINE_ID が空の場合、ファクトリ関数にフォールバックする"""
        mock_session = MagicMock()
        mock_memory = MagicMock()
        mock_session_factory.return_value = mock_session
        mock_memory_factory.return_value = mock_memory

        wrapper = HomeworkCoachAgent(MagicMock())
        wrapper._get_runner()

        mock_session_factory.assert_called_once()
        mock_memory_factory.assert_called_once()
        mock_runner_cls.assert_called_once_with(
            app_name="homework-coach-agent-engine",
            agent=wrapper._agent,
            session_service=mock_session,
            memory_service=mock_memory,
        )


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

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_works_inside_running_event_loop(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """既存イベントループ内でもセッション作成が動作する（Agent Engine 環境を模倣）"""
        mock_session = MagicMock()
        mock_session.id = "loop-session"

        mock_runner_instance = MagicMock()
        mock_runner_instance.session_service.create_session = AsyncMock(
            return_value=mock_session,
        )
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())

        # 既存イベントループ内で呼び出す（Agent Engine サーバー環境を模倣）
        async def run_in_loop() -> dict[str, Any]:
            return wrapper.create_session(user_id="loop-user")

        result = asyncio.run(run_in_loop())
        assert result == {"id": "loop-session"}


def _make_stream_runner_mock(
    mock_runner_cls: MagicMock,
    run_async_fn: Any,
) -> MagicMock:
    """stream_query テスト用の Runner モックを作成するヘルパー

    InMemorySessionService 環境ではセッションを事前作成するため、
    session_service.create_session を AsyncMock で設定する。

    Args:
        mock_runner_cls: Runner クラスのモック
        run_async_fn: run_async に設定する非同期ジェネレータ関数

    Returns:
        設定済みの mock_runner_instance
    """
    mock_session = MagicMock()
    mock_session.id = "auto-created-session"

    mock_runner_instance = MagicMock()
    mock_runner_instance.run_async = run_async_fn
    mock_runner_instance.session_service.create_session = AsyncMock(
        return_value=mock_session,
    )
    mock_runner_cls.return_value = mock_runner_instance
    return mock_runner_instance


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
        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:  # noqa: ARG001
            return
            yield  # noqa: B027 - async generator にするため

        _make_stream_runner_mock(mock_runner_cls, mock_run_async)

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
    def test_creates_session_and_passes_id_to_run_async(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """stream_query はセッションを事前作成し、そのIDを run_async に渡す

        InMemorySessionService は session_id=None で自動作成しないため、
        明示的にセッションを作成してから run_async に渡す。
        """
        call_args: dict[str, Any] = {}

        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:
            call_args.update(kwargs)
            return
            yield  # noqa: B027

        mock_runner_instance = _make_stream_runner_mock(mock_runner_cls, mock_run_async)

        wrapper = HomeworkCoachAgent(MagicMock())
        list(
            wrapper.stream_query(
                user_id="u-1",
                session_id="cloud-run-session-id",
                message="テスト",
            )
        )

        # セッションが事前に作成されることを確認
        mock_runner_instance.session_service.create_session.assert_called_once_with(
            app_name="homework-coach-agent-engine",
            user_id="u-1",
        )
        # 作成されたセッションIDが run_async に渡されることを確認（None ではない）
        assert call_args["session_id"] == "auto-created-session"
        assert call_args["user_id"] == "u-1"

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

        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:  # noqa: ARG001
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

        _make_stream_runner_mock(mock_runner_cls, mock_run_async)

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

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_works_inside_running_event_loop(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """既存イベントループ内でも stream_query が動作する（Agent Engine 環境を模倣）"""

        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:  # noqa: ARG001
            event = MagicMock()
            part = MagicMock()
            part.text = "ループ内応答"
            event.content.parts = [part]
            yield event

        _make_stream_runner_mock(mock_runner_cls, mock_run_async)

        wrapper = HomeworkCoachAgent(MagicMock())

        # 既存イベントループ内で呼び出す
        async def run_in_loop() -> list[dict[str, Any]]:
            return list(
                wrapper.stream_query(
                    user_id="u-1",
                    session_id="s-1",
                    message="テスト",
                )
            )

        events = asyncio.run(run_in_loop())
        assert len(events) == 1
        assert events[0] == {"content": {"parts": [{"text": "ループ内応答"}]}}


class TestRegisterOperations:
    """register_operations のテスト"""

    def test_returns_correct_format(self) -> None:
        """正しい形式（辞書）を返す"""
        wrapper = HomeworkCoachAgent(MagicMock())
        operations = wrapper.register_operations()

        assert isinstance(operations, dict)
        assert "" in operations
        assert "stream" in operations

    def test_registers_sync_methods(self) -> None:
        """同期メソッド（query, create_session）を登録する"""
        wrapper = HomeworkCoachAgent(MagicMock())
        operations = wrapper.register_operations()

        sync_methods = operations[""]
        assert "query" in sync_methods
        assert "create_session" in sync_methods

    def test_registers_stream_methods(self) -> None:
        """ストリーミングメソッド（stream_query）を登録する"""
        wrapper = HomeworkCoachAgent(MagicMock())
        operations = wrapper.register_operations()

        stream_methods = operations["stream"]
        assert "stream_query" in stream_methods


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

        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:  # noqa: ARG001
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

        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:  # noqa: ARG001
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

    @patch("app.services.adk.runner.homework_coach_agent.create_memory_service")
    @patch("app.services.adk.runner.homework_coach_agent.create_session_service")
    @patch("app.services.adk.runner.homework_coach_agent.Runner")
    def test_works_inside_running_event_loop(
        self,
        mock_runner_cls: MagicMock,
        mock_session_factory: MagicMock,  # noqa: ARG002
        mock_memory_factory: MagicMock,  # noqa: ARG002
    ) -> None:
        """既存イベントループ内でも query が動作する（Agent Engine 環境を模倣）"""

        async def mock_run_async(**kwargs: object) -> AsyncGenerator[Any, None]:  # noqa: ARG001
            event = MagicMock()
            part = MagicMock()
            part.text = "ループ内応答"
            event.content.parts = [part]
            yield event

        mock_runner_instance = MagicMock()
        mock_runner_instance.run_async = mock_run_async
        mock_runner_cls.return_value = mock_runner_instance

        wrapper = HomeworkCoachAgent(MagicMock())

        async def run_in_loop() -> str:
            return wrapper.query("テスト")

        result = asyncio.run(run_in_loop())
        assert result == "ループ内応答"
