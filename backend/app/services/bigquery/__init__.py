"""BigQueryサービスモジュール

このモジュールは、BigQueryへの学習データ永続化機能を提供します。
"""

from app.services.bigquery.bigquery_service import BigQueryDataService

__all__ = ["BigQueryDataService"]
