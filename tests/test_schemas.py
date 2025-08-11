from app.schema.compare import CompareMode, CompareRequest, CompareResponse, MatchItem


def test_compare_mode():
    """Testa valores válidos do CompareMode"""
    valid_modes = ["lexical", "semantic", "hybrid", "all"]
    for mode in valid_modes:
        assert CompareMode(mode) == mode


def test_compare_request():
    """Testa request básico"""
    request = CompareRequest(text="teste")
    assert request.text == "teste"
    assert request.mode == "all"
    assert request.top_k == 5


def test_match_item():
    """Testa MatchItem básico"""
    item = MatchItem(score=0.9, text="teste")
    assert item.score == 0.9
    assert item.text == "teste"
    assert item.id is None


def test_compare_response():
    """Testa response básico"""
    response = CompareResponse(
        mode="all",
        lexical=[MatchItem(score=0.9, text="teste")],
        semantic=[MatchItem(score=0.8, text="teste")],
        hybrid=[MatchItem(score=0.85, text="teste")],
    )
    assert response.mode == "all"
    assert len(response.lexical) == 1
    assert len(response.semantic) == 1
    assert len(response.hybrid) == 1
