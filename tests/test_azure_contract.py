import json
import httpx
import pytest
from rag.azure import AzureRAG
from rag.core import Principal


@pytest.fixture
def config(monkeypatch):
    for k,v in {"AZURE_SEARCH_ENDPOINT":"https://synthetic.search.windows.net", "AZURE_OPENAI_ENDPOINT":"https://synthetic.openai.azure.com", "AZURE_SEARCH_INDEX":"demo-index", "AZURE_SEARCH_API_KEY":"fake-search-key", "AZURE_OPENAI_API_KEY":"fake-model-key", "AZURE_EMBEDDING_DEPLOYMENT":"embedding", "AZURE_CHAT_DEPLOYMENT":"chat"}.items():
        monkeypatch.setenv(k,v)


def transport(calls, *, tenant="a", cited="chunk-1"):
    def handle(request):
        body = json.loads(request.content)
        calls.append((request.url.path, body))
        if request.url.path.endswith("embeddings"):
            data = {"data":[{"embedding":[.1,.2,.3]}]}
        elif request.url.path.endswith("/docs/search"):
            data = {"value":[{"id":"chunk-1","document_id":"policy","title":"Policy","text":"Human approval required.","tenant":tenant,"group_ids":["finance"]}]}
        else:
            data = {"choices":[{"message":{"content":json.dumps({"answer":"Human approval required.","citation_ids":[cited],"abstained":False})}}]}
        return httpx.Response(200, json=data)
    return httpx.MockTransport(handle)


def test_hybrid_filter_and_citations(config):
    calls = []
    with httpx.Client(transport=transport(calls)) as client:
        result = AzureRAG(client).answer(Principal("alice","a",("finance",)), "approval?", 3)
    assert result["mode"] == "azure-hybrid"
    query = calls[1][1]
    assert query["search"] == "approval?"
    assert query["vectorFilterMode"] == "preFilter"
    assert "tenant eq 'a'" in query["filter"]
    assert "group_ids/any(g:g eq 'finance')" in query["filter"]
    assert query["vectorQueries"][0]["kind"] == "vector"
    assert result["citations"][0]["id"] == "chunk-1"


def test_defense_against_cross_tenant_result(config):
    with httpx.Client(transport=transport([], tenant="other")) as client:
        with pytest.raises(RuntimeError, match="authorized scope"):
            AzureRAG(client).answer(Principal("a","a",("finance",)), "approval", 3)


def test_hallucinated_citation_rejected(config):
    with httpx.Client(transport=transport([], cited="hidden-source")) as client:
        with pytest.raises(RuntimeError, match="citation"):
            AzureRAG(client).answer(Principal("a","a",("finance",)), "approval", 3)


def test_no_groups_no_remote_call(config):
    calls = []
    with httpx.Client(transport=transport(calls)) as client:
        assert AzureRAG(client).answer(Principal("a","a",()), "approval", 3)["abstained"]
    assert calls == []


def test_missing_credentials_fail_closed(config, monkeypatch):
    monkeypatch.delenv("AZURE_SEARCH_API_KEY")
    monkeypatch.delenv("AZURE_SEARCH_TOKEN", raising=False)
    with httpx.Client(transport=transport([])) as client:
        with pytest.raises(RuntimeError, match="Configure AZURE_SEARCH"):
            AzureRAG(client).answer(Principal("a","a",("finance",)), "approval", 3)
