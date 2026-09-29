import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_documents():
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_chat_out_of_scope():
    payload = {"query": "How many calories should I eat to lose weight?"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_type"] == "out_of_scope"
    assert "This falls outside what I can help with" in data["answer"]

def test_chat_corpus_refusal():
    payload = {"query": "What is the capital of France?"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["refusal_type"] == "not_in_corpus"
    assert "The dietary guidance documents I searched do not cover this topic" in data["answer"]

def test_chat_nutrition_question():
    payload = {"query": "What does the WHO recommend for daily salt intake?"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    if data["refusal_type"] is None:
        assert data["answer"]
