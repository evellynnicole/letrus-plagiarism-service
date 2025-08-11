from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Testa endpoint de saúde"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_compare_endpoint():
    """Testa endpoint de comparação básico"""
    response = client.post("/compare", json={"text": "teste"})
    print(response.status_code, response.text)
    assert response.status_code == 200
    assert "mode" in response.json()


def test_compare_validation():
    """Testa validação de entrada"""
    response = client.post("/compare", json={"text": ""})
    assert response.status_code == 422
