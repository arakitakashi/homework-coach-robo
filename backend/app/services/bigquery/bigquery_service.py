"""BigQueryデータサービス

このモジュールは、BigQueryへの学習データ永続化を担当する
BigQueryDataServiceクラスを定義します。
"""

import structlog
from google.cloud import bigquery
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.bigquery import (
    DialogueSessionBQ,
    LearningHistoryBQ,
    LearningProfileSnapshotBQ,
)

logger = structlog.get_logger()


class BigQueryDataService:
    """BigQueryへの学習データ永続化サービス

    セッション終了時に、Firestoreの一時データをBigQueryに永続化します。
    """

    def __init__(
        self,
        project_id: str,
        dataset_id: str = "homework_coach",
        client: bigquery.Client | None = None,
    ):
        """BigQueryDataServiceの初期化

        Args:
            project_id: GCPプロジェクトID
            dataset_id: BigQueryデータセットID（デフォルト: homework_coach）
            client: BigQueryクライアント（テスト用にモック可能）
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = client or bigquery.Client(project=project_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def save_session_data(self, session_data: DialogueSessionBQ) -> None:
        """セッションデータをBigQueryに保存

        Args:
            session_data: セッションデータ

        Raises:
            Exception: BigQuery保存失敗時
        """
        table_id = f"{self.project_id}.{self.dataset_id}.dialogue_sessions"
        rows_to_insert = [session_data.model_dump(mode="json")]

        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error(
                "bigquery_insert_failed",
                table="dialogue_sessions",
                session_id=session_data.session_id,
                errors=errors,
            )
            raise Exception(f"BigQuery insert failed: {errors}")

        logger.info(
            "bigquery_insert_success",
            table="dialogue_sessions",
            session_id=session_data.session_id,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def save_learning_history(self, history_data: LearningHistoryBQ) -> None:
        """学習履歴をBigQueryに保存

        Args:
            history_data: 学習履歴データ

        Raises:
            Exception: BigQuery保存失敗時
        """
        table_id = f"{self.project_id}.{self.dataset_id}.learning_history"
        rows_to_insert = [history_data.model_dump(mode="json")]

        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error(
                "bigquery_insert_failed",
                table="learning_history",
                history_id=history_data.id,
                errors=errors,
            )
            raise Exception(f"BigQuery insert failed: {errors}")

        logger.info(
            "bigquery_insert_success",
            table="learning_history",
            history_id=history_data.id,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def save_learning_profile_snapshot(
        self, snapshot_data: LearningProfileSnapshotBQ
    ) -> None:
        """学習プロファイルスナップショットをBigQueryに保存

        Args:
            snapshot_data: プロファイルスナップショットデータ

        Raises:
            Exception: BigQuery保存失敗時
        """
        table_id = f"{self.project_id}.{self.dataset_id}.learning_profile_snapshots"
        rows_to_insert = [snapshot_data.model_dump(mode="json")]

        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error(
                "bigquery_insert_failed",
                table="learning_profile_snapshots",
                snapshot_id=snapshot_data.id,
                errors=errors,
            )
            raise Exception(f"BigQuery insert failed: {errors}")

        logger.info(
            "bigquery_insert_success",
            table="learning_profile_snapshots",
            snapshot_id=snapshot_data.id,
        )

    async def save_all(
        self,
        session_data: DialogueSessionBQ,
        history_data: LearningHistoryBQ,
        snapshot_data: LearningProfileSnapshotBQ,
    ) -> None:
        """セッション終了時の全データを一括保存

        Args:
            session_data: セッションデータ
            history_data: 学習履歴データ
            snapshot_data: プロファイルスナップショットデータ
        """
        await self.save_session_data(session_data)
        await self.save_learning_history(history_data)
        await self.save_learning_profile_snapshot(snapshot_data)
