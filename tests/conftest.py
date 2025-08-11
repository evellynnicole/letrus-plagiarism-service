from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Cliente de teste FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_compare_service():
    """Mock simples do CompareService"""
    service = Mock()
    service.compare_lexical.return_value = [{"index": 0, "similarity": 0.9, "text": "teste"}]
    service.compare_semantic.return_value = [{"id": "doc1", "similarity": 0.8, "text": "teste"}]
    service.compare_hybrid.return_value = [{"id": "doc1", "similarity": 0.85, "text": "teste"}]
    return service
