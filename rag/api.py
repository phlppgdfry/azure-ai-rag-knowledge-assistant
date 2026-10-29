from .security import install_security
import hmac
import json
import os
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field
from fastapi.responses import HTMLResponse
from importlib.resources import files

from rag.core import Principal, Store

app = FastAPI(title="Knowledge Assistant", version="0.1.0")
key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def principal(key: str | None = Depends(key_header)):
    # Only server configuration grants tenancy, membership and ingestion privilege.
    for secret, profile in json.loads(os.getenv("RAG_PRINCIPALS", "{}")).items():
        if key and hmac.compare_digest(key.encode("utf-8"), secret.encode("utf-8")):
            return Principal(profile["subject"], profile["tenant"], tuple(profile["groups"]), profile.get("admin", False))
    raise HTTPException(401, "Invalid API key")


@lru_cache
def store():
    return Store(os.getenv("RAG_DB", "data/knowledge.sqlite3"))


class Query(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=2000)
    top: int = Field(default=4, ge=1, le=10)


class Document(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=100000)
    groups: list[str] = Field(min_length=1, max_length=30)


@app.get("/health")
def health():
    return {"status": "ok", "provider": os.getenv("RAG_PROVIDER", "local")}


@app.get('/console', response_class=HTMLResponse, include_in_schema=False)
def console():
    return HTMLResponse(files('rag').joinpath('console.html').read_text(),
                        headers={'Cache-Control': 'no-store', 'X-Frame-Options': 'DENY'})


@app.post("/documents", status_code=201)
def ingest(document: Document, user=Depends(principal)):
    if os.getenv("RAG_PROVIDER", "local") != "local":
        raise HTTPException(409, "Azure indexing uses the explicit administrative rag.index CLI")
    try:
        return {"content_hash": store().upsert(user, document.model_dump())}
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except ValueError as e:
        raise HTTPException(422, str(e)) from e


@app.delete("/documents/{document_id}", status_code=204)
def delete(document_id: str, user=Depends(principal)):
    if os.getenv("RAG_PROVIDER", "local") != "local":
        raise HTTPException(409, "Azure document deletion requires dedicated index administration")
    try:
        store().delete(user, document_id)
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e


@app.post("/ask")
def ask(query: Query, user=Depends(principal)):
    provider = os.getenv("RAG_PROVIDER", "local")
    try:
        if provider == "local":
            return store().answer(user, query.question, query.top)
        if provider == "azure":
            from rag.azure import AzureRAG
            return AzureRAG().answer(user, query.question, query.top)
        raise RuntimeError("Unknown provider")
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    except Exception as e:
        # Do not expose service responses, document bodies or credentials to callers.
        raise HTTPException(503, "Retrieval provider unavailable; no fallback was used") from e


install_security(app, max_bytes=524288)
