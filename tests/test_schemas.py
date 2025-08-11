import pytest
from pydantic import ValidationError

from app.schema.compare import CompareMode, CompareRequest, CompareResponse, MatchItem

HTTP_OK = 200
TOP_K = 10
EXPECTED_SCORE = 0.9


def test_compare_mode_values():
    """Testa valores válidos do CompareMode"""
    valid_modes = ["lexical", "semantic", "hybrid", "all"]
    for mode in valid_modes:
        assert CompareMode(mode) == mode


def test_compare_mode_invalid():
    """Testa modo inválido"""
    with pytest.raises(ValidationError):
        CompareMode("invalid")


def test_compare_request_basic():
    """Testa request básico"""
    request = CompareRequest(text="teste")
    assert request.text == "teste"
    assert request.mode == "all"
    assert request.top_k == TOP_K


def test_compare_request_custom():
    """Testa request com valores customizados"""
    request = CompareRequest(text="teste", mode="lexical", top_k=TOP_K)
    assert request.text == "teste"
    assert request.mode == "lexical"
    assert request.top_k == TOP_K


def test_compare_request_validation():
    """Testa validação do request"""
    # Texto vazio
    with pytest.raises(ValidationError):
        CompareRequest(text="")

    # top_k muito baixo
    with pytest.raises(ValidationError):
        CompareRequest(text="teste", top_k=0)


def test_match_item_basic():
    """Testa MatchItem básico"""
    item = MatchItem(score=EXPECTED_SCORE, text="teste")
    assert item.score == EXPECTED_SCORE
    assert item.text == "teste"
    assert item.id is None


def test_compare_response_lexical():
    """Testa response no modo lexical"""
    response = CompareResponse(
        mode="lexical", lexical=[MatchItem(score=EXPECTED_SCORE, text="teste")]
    )
    assert response.mode == "lexical"
    assert len(response.lexical) == 1
    assert len(response.semantic) == 0


def test_compare_response_all():
    """Testa response no modo all"""
    response = CompareResponse(
        mode="all",
        lexical=[MatchItem(score=EXPECTED_SCORE, text="teste")],
        semantic=[MatchItem(score=EXPECTED_SCORE, text="teste")],
        hybrid=[MatchItem(score=EXPECTED_SCORE, text="teste")],
    )
    assert response.mode == "all"
    assert len(response.lexical) == 1
    assert len(response.semantic) == 1
    assert len(response.hybrid) == 1
