"""memory_factory のテスト

環境変数に応じて適切なメモリサービスを返すファクトリ関数をテストする。
"""

from unittest.mock import MagicMock, patch

from google.adk.memory import BaseMemoryService, VertexAiMemoryBankService

from app.services.adk.memory.firestore_memory_service import FirestoreMemoryService
from app.services.adk.memory.memory_factory import create_memory_service


class TestCreateMemoryServiceWithoutAgentEngine:
    """AGENT_ENGINE_ID 未設定時のテスト"""

    @patch("google.cloud.firestore.AsyncClient", return_value=MagicMock())
    @patch.dict("os.environ", {}, clear=True)
    def test_returns_firestore_when_no_env(self, _mock_client: MagicMock) -> None:
        """環境変数未設定時は FirestoreMemoryService を返す"""
        service = create_memory_service()
        assert isinstance(service, FirestoreMemoryService)

    @patch("google.cloud.firestore.AsyncClient", return_value=MagicMock())
    @patch.dict("os.environ", {"AGENT_ENGINE_ID": ""}, clear=True)
    def test_returns_firestore_when_empty_string(self, _mock_client: MagicMock) -> None:
        """AGENT_ENGINE_ID が空文字の場合は FirestoreMemoryService を返す"""
        service = create_memory_service()
        assert isinstance(service, FirestoreMemoryService)


class TestCreateMemoryServiceWithAgentEngine:
    """AGENT_ENGINE_ID 設定時のテスト"""

    @patch.dict(
        "os.environ",
        {"AGENT_ENGINE_ID": "123456"},
        clear=True,
    )
    def test_returns_memory_bank_service(self) -> None:
        """AGENT_ENGINE_ID 設定時は VertexAiMemoryBankService を返す"""
        service = create_memory_service()
        assert isinstance(service, VertexAiMemoryBankService)

    @patch.dict(
        "os.environ",
        {"AGENT_ENGINE_ID": "123456"},
        clear=True,
    )
    def test_passes_agent_engine_id(self) -> None:
        """agent_engine_id が正しく渡される"""
        service = create_memory_service()
        assert isinstance(service, VertexAiMemoryBankService)
        assert service._agent_engine_id == "123456"

    @patch.dict(
        "os.environ",
        {
            "AGENT_ENGINE_ID": "789",
            "GCP_PROJECT_ID": "my-project",
            "GCP_LOCATION": "asia-northeast1",
        },
        clear=True,
    )
    def test_passes_project_and_location(self) -> None:
        """GCP_PROJECT_ID と GCP_LOCATION が正しく渡される"""
        service = create_memory_service()
        assert isinstance(service, VertexAiMemoryBankService)
        assert service._project == "my-project"
        assert service._location == "asia-northeast1"

    @patch.dict(
        "os.environ",
        {"AGENT_ENGINE_ID": "456"},
        clear=True,
    )
    def test_default_location_is_none(self) -> None:
        """GCP_LOCATION 未設定時は None"""
        service = create_memory_service()
        assert isinstance(service, VertexAiMemoryBankService)
        assert service._location is None


class TestCreateMemoryServiceReturnType:
    """戻り値の型テスト"""

    @patch("google.cloud.firestore.AsyncClient", return_value=MagicMock())
    @patch.dict("os.environ", {}, clear=True)
    def test_returns_base_memory_service(self, _mock_client: MagicMock) -> None:
        """戻り値は BaseMemoryService のサブクラス"""
        service = create_memory_service()
        assert isinstance(service, BaseMemoryService)

    @patch.dict(
        "os.environ",
        {"AGENT_ENGINE_ID": "123"},
        clear=True,
    )
    def test_returns_base_memory_service_with_agent_engine(self) -> None:
        """AGENT_ENGINE_ID 設定時も BaseMemoryService のサブクラス"""
        service = create_memory_service()
        assert isinstance(service, BaseMemoryService)
