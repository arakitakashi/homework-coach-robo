"""Pytest fixtures"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI テストクライアント"""
    return TestClient(app)
