from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

HTTP_OK = 200
HTTP_UNPROCESSABLE_ENTITY = 422


def test_health_check():
    """Testa endpoint de saúde"""
    response = client.get("/health")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_compare_endpoint():
    """Testa endpoint de comparação básico"""
    response = client.post("/compare", json={"text": "teste"})
    assert response.status_code == HTTP_OK
    assert "mode" in response.json()


def test_compare_different_modes():
    """Testa diferentes modos de comparação"""
    modes = ["lexical", "semantic", "hybrid", "all"]
    for mode in modes:
        response = client.post("/compare", json={"text": "teste", "mode": mode})
        assert response.status_code == HTTP_OK
        assert response.json()["mode"] == mode


def test_compare_validation():
    """Testa validação de entrada"""
    # Texto vazio
    response = client.post("/compare", json={"text": ""})
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY

    # Sem texto
    response = client.post("/compare", json={})
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY
