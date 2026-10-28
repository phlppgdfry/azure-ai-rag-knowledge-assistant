import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from rag.core import Principal, Store, chunks
from rag.api import app, store


@pytest.fixture
def corpus(tmp_path):
    db = Store(tmp_path / "rag.db")
    admin = Principal("admin", "a", ("finance",), True)
    for doc in json.loads(Path("fixtures/documents.json").read_text()):
        db.upsert(admin, doc)
    return db


def test_acl_before_ranking(corpus):
    finance = Principal("alice", "a", ("finance",))
    assert corpus.answer(finance, "7312 HR opleidingsbudget")["abstained"]
    assert not corpus.answer(Principal("bob", "a", ("hr",)), "7312")["abstained"]
    assert corpus.answer(Principal("other", "b", ("finance",)), "factuur")["abstained"]
    assert corpus.answer(Principal("none", "a", ()), "factuur")["abstained"]


def test_citation_is_actual_chunk(corpus):
    answer = corpus.answer(Principal("alice", "a", ("finance",)), "factuur goedkeuring")
    assert answer["mode"] == "local-extractive"
    assert "invoice-policy" == answer["citations"][0]["document_id"]
    assert all(c["text"] in answer["answer"] and c["id"] in answer["answer"] for c in answer["citations"])


def test_upsert_revokes_access_and_deletion(corpus):
    admin = Principal("admin", "a", (), True)
    corpus.upsert(admin, {"id":"invoice-policy","title":"New", "text":"factuur gewijzigd", "groups":["hr"]})
    assert corpus.answer(Principal("a", "a", ("finance",)), "factuur")["abstained"]
    corpus.delete(admin, "invoice-policy")
    assert corpus.answer(Principal("b", "a", ("hr",)), "factuur")["abstained"]


def test_write_privilege_and_chunking(corpus):
    with pytest.raises(PermissionError):
        corpus.delete(Principal("a", "a", ("finance",)), "invoice-policy")
    assert len(list(chunks(" ".join(["x"] * 300)))) == 3
    with pytest.raises(ValueError):
        list(chunks("x", 3, 4))


def test_concurrent_query(corpus):
    with ThreadPoolExecutor(max_workers=4) as pool:
        answers = list(pool.map(lambda _: corpus.answer(Principal("a", "a", ("finance",)), "factuur"), range(12)))
    assert all(not a["abstained"] for a in answers)


def test_api_rejects_identity_spoofing(corpus, monkeypatch):
    monkeypatch.setenv("RAG_PRINCIPALS", json.dumps({"test-key":{"subject":"alice","tenant":"a","groups":["finance"]}}))
    app.dependency_overrides[store] = lambda: corpus
    try:
        client = TestClient(app)
        assert client.post("/ask", json={"question":"factuur"}).status_code == 401
        headers = {"X-API-Key":"test-key"}
        assert client.post("/ask", json={"question":"factuur","tenant":"b"}, headers=headers).status_code == 422
        assert client.post("/ask", json={"question":"factuur"}, headers=headers).status_code == 200
        assert client.delete("/documents/invoice-policy", headers=headers).status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_provider_errors_never_fallback(corpus, monkeypatch):
    monkeypatch.setenv("RAG_PRINCIPALS", json.dumps({"test-key":{"subject":"alice","tenant":"a","groups":["finance"]}}))
    monkeypatch.setenv("RAG_PROVIDER", "invalid")
    app.dependency_overrides[store] = lambda: corpus
    try:
        response = TestClient(app).post("/ask", json={"question":"factuur"}, headers={"X-API-Key":"test-key"})
        assert response.status_code == 503
        assert "fallback" in response.text
    finally:
        app.dependency_overrides.clear()
