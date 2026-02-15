"""BigQueryDataServiceのユニットテスト"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.bigquery import (
    DialogueSessionBQ,
    DialogueTurnBQ,
    LearningHistoryBQ,
    LearningProfileSnapshotBQ,
    SubjectUnderstandingBQ,
)
from app.services.bigquery.bigquery_service import BigQueryDataService


@pytest.fixture
def mock_bigquery_client() -> MagicMock:
    """BigQueryクライアントのモック"""
    return MagicMock()


@pytest.fixture
def bigquery_service(mock_bigquery_client: MagicMock) -> BigQueryDataService:
    """BigQueryDataServiceのフィクスチャ"""
    return BigQueryDataService(
        project_id="test-project",
        dataset_id="test_dataset",
        client=mock_bigquery_client,
    )


@pytest.fixture
def sample_session_data() -> DialogueSessionBQ:
    """テスト用セッションデータ"""
    return DialogueSessionBQ(
        session_id="session123",
        user_id="user456",
        problem="1 + 1 = ?",
        start_time=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 2, 15, 10, 10, 0, tzinfo=timezone.utc),
        dialogue_turns=[
            DialogueTurnBQ(
                turn_id=1,
                speaker="user",
                content="2",
                timestamp=datetime(2026, 2, 15, 10, 5, 0, tzinfo=timezone.utc),
            )
        ],
        total_hints_used=1,
        self_solved_count=1,
        total_points=2,
    )


@pytest.fixture
def sample_history_data() -> LearningHistoryBQ:
    """テスト用学習履歴データ"""
    return LearningHistoryBQ(
        id="history123",
        user_id="user456",
        problem_id="problem789",
        subject="math",
        grade_level=2,
        attempted_at=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
        solved_independently=True,
        hints_used=1,
        time_spent_seconds=600,
        points_earned=2,
        session_id="session123",
    )


@pytest.fixture
def sample_snapshot_data() -> LearningProfileSnapshotBQ:
    """テスト用プロファイルスナップショットデータ"""
    return LearningProfileSnapshotBQ(
        id="snapshot123",
        user_id="user456",
        snapshot_at=datetime(2026, 2, 15, 10, 10, 0, tzinfo=timezone.utc),
        persistence_score=0.8,
        independence_score=0.7,
        reflection_quality=0.9,
        hint_dependency=0.3,
        subject_understanding=[
            SubjectUnderstandingBQ(
                subject="math",
                topic="addition",
                level="intermediate",
                trend="improving",
            )
        ],
    )


class TestBigQueryDataServiceInit:
    """BigQueryDataServiceの初期化テスト"""

    def test_init_with_client(self, mock_bigquery_client: MagicMock) -> None:
        """クライアントを指定して初期化"""
        service = BigQueryDataService(
            project_id="test-project",
            dataset_id="test_dataset",
            client=mock_bigquery_client,
        )
        assert service.project_id == "test-project"
        assert service.dataset_id == "test_dataset"
        assert service.client == mock_bigquery_client

    @patch("app.services.bigquery.bigquery_service.bigquery.Client")
    def test_init_without_client(self, mock_client_class: MagicMock) -> None:
        """クライアントを指定せずに初期化（自動作成）"""
        service = BigQueryDataService(
            project_id="test-project",
            dataset_id="test_dataset",
        )
        mock_client_class.assert_called_once_with(project="test-project")
        assert service.project_id == "test-project"
        assert service.dataset_id == "test_dataset"


class TestSaveSessionData:
    """save_session_data メソッドのテスト"""

    async def test_save_session_data_success(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_session_data: DialogueSessionBQ,
    ) -> None:
        """セッションデータ保存成功ケース"""
        mock_bigquery_client.insert_rows_json.return_value = []  # 成功

        await bigquery_service.save_session_data(sample_session_data)

        mock_bigquery_client.insert_rows_json.assert_called_once()
        args = mock_bigquery_client.insert_rows_json.call_args
        assert args[0][0] == "test-project.test_dataset.dialogue_sessions"
        assert len(args[0][1]) == 1
        assert args[0][1][0]["session_id"] == "session123"

    async def test_save_session_data_failure(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_session_data: DialogueSessionBQ,
    ) -> None:
        """セッションデータ保存失敗ケース"""
        mock_bigquery_client.insert_rows_json.return_value = [
            {"index": 0, "errors": [{"reason": "invalid"}]}
        ]

        with pytest.raises(Exception, match="BigQuery insert failed"):
            await bigquery_service.save_session_data(sample_session_data)


class TestSaveLearningHistory:
    """save_learning_history メソッドのテスト"""

    async def test_save_learning_history_success(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_history_data: LearningHistoryBQ,
    ) -> None:
        """学習履歴保存成功ケース"""
        mock_bigquery_client.insert_rows_json.return_value = []

        await bigquery_service.save_learning_history(sample_history_data)

        mock_bigquery_client.insert_rows_json.assert_called_once()
        args = mock_bigquery_client.insert_rows_json.call_args
        assert args[0][0] == "test-project.test_dataset.learning_history"
        assert len(args[0][1]) == 1
        assert args[0][1][0]["id"] == "history123"

    async def test_save_learning_history_failure(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_history_data: LearningHistoryBQ,
    ) -> None:
        """学習履歴保存失敗ケース"""
        mock_bigquery_client.insert_rows_json.return_value = [
            {"index": 0, "errors": [{"reason": "invalid"}]}
        ]

        with pytest.raises(Exception, match="BigQuery insert failed"):
            await bigquery_service.save_learning_history(sample_history_data)


class TestSaveLearningProfileSnapshot:
    """save_learning_profile_snapshot メソッドのテスト"""

    async def test_save_learning_profile_snapshot_success(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_snapshot_data: LearningProfileSnapshotBQ,
    ) -> None:
        """プロファイルスナップショット保存成功ケース"""
        mock_bigquery_client.insert_rows_json.return_value = []

        await bigquery_service.save_learning_profile_snapshot(sample_snapshot_data)

        mock_bigquery_client.insert_rows_json.assert_called_once()
        args = mock_bigquery_client.insert_rows_json.call_args
        assert args[0][0] == "test-project.test_dataset.learning_profile_snapshots"
        assert len(args[0][1]) == 1
        assert args[0][1][0]["id"] == "snapshot123"

    async def test_save_learning_profile_snapshot_failure(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_snapshot_data: LearningProfileSnapshotBQ,
    ) -> None:
        """プロファイルスナップショット保存失敗ケース"""
        mock_bigquery_client.insert_rows_json.return_value = [
            {"index": 0, "errors": [{"reason": "invalid"}]}
        ]

        with pytest.raises(Exception, match="BigQuery insert failed"):
            await bigquery_service.save_learning_profile_snapshot(sample_snapshot_data)


class TestSaveAll:
    """save_all メソッドのテスト"""

    async def test_save_all_success(
        self,
        bigquery_service: BigQueryDataService,
        mock_bigquery_client: MagicMock,
        sample_session_data: DialogueSessionBQ,
        sample_history_data: LearningHistoryBQ,
        sample_snapshot_data: LearningProfileSnapshotBQ,
    ) -> None:
        """一括保存成功ケース"""
        mock_bigquery_client.insert_rows_json.return_value = []

        await bigquery_service.save_all(
            sample_session_data,
            sample_history_data,
            sample_snapshot_data,
        )

        # 3回呼ばれる（session, history, snapshot）
        assert mock_bigquery_client.insert_rows_json.call_count == 3
