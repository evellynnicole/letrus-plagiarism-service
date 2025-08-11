import pytest
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
    assert response.status_code == 200
    assert "mode" in response.json()

def test_compare_different_modes():
    """Testa diferentes modos de comparação"""
    modes = ["lexical", "semantic", "hybrid", "all"]
    for mode in modes:
        response = client.post("/compare", json={"text": "teste", "mode": mode})
        assert response.status_code == 200
        assert response.json()["mode"] == mode

def test_compare_validation():
    """Testa validação de entrada"""
    # Texto vazio
    response = client.post("/compare", json={"text": ""})
    assert response.status_code == 422
    
    # Sem texto
    response = client.post("/compare", json={})
    assert response.status_code == 422