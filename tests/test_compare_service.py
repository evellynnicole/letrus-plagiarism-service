import pytest
from unittest.mock import Mock, patch
from app.services.compare_service import CompareService

@pytest.fixture
def mock_service():
    """Mock simples do CompareService"""
    service = Mock(spec=CompareService)
    service.compare_lexical.return_value = [{"index": 0, "score": 0.9, "text": "teste"}]
    service.compare_semantic.return_value = [{"id": "doc1", "score": 0.8, "text": "teste"}]
    service.compare_hybrid.return_value = [{"id": "doc1", "score": 0.85, "text": "teste"}]
    return service

def test_compare_lexical(mock_service):
    """Testa comparação lexical"""
    result = mock_service.compare_lexical("texto", top_k=3)
    assert len(result) == 1
    assert result[0]["score"] == 0.9

def test_compare_semantic(mock_service):
    """Testa comparação semântica"""
    result = mock_service.compare_semantic("texto", top_k=3)
    assert len(result) == 1
    assert result[0]["id"] == "doc1"

def test_compare_hybrid(mock_service):
    """Testa comparação híbrida"""
    result = mock_service.compare_hybrid("texto", top_k=3)
    assert len(result) == 1
    assert result[0]["score"] == 0.85

def test_compare_all_modes(mock_service):
    """Testa todos os modos de comparação"""
    result = mock_service.compare_all("texto", top_k=3)
    assert "lexical" in result
    assert "semantic" in result
    assert "hybrid" in result
