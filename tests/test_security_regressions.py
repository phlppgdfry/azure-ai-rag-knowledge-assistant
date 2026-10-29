from fastapi.testclient import TestClient
from rag.api import app


def test_non_ascii_credential_fails_closed(monkeypatch):
    monkeypatch.setenv('RAG_PRINCIPALS', '{"valid-key":{"subject":"a","tenant":"a","groups":["finance"]}}')
    response = TestClient(app).post('/ask', json={'question': 'policy'}, headers={'X-API-Key': b'\xc3\xa9-invalid'})
    assert response.status_code == 401
