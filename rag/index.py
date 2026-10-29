"""Explicit administrative CLI: creates/updates index and uploads synthetic chunks.

Run only against a dedicated demo index; does not provision Azure resources.
"""
import argparse
import hashlib
import json
from pathlib import Path
from rag.azure import AzureRAG, odata
from rag.core import chunks, Store, Principal
import tempfile


def checked_batch(client, actions):
    if not actions:
        return
    if len(actions) > 1000 or len(json.dumps({"value": actions}).encode()) > 15_000_000:
        raise ValueError("Index batch exceeds bounded demo limits")
    result = client.request("search", "POST", f"/indexes/{client.index}/docs/index?api-version={client.version}",
                            {"value": actions})
    rows = result.get("value", [])
    if (len(rows) != len(actions) or {r.get("key") for r in rows} != {a["id"] for a in actions}
            or any(r.get("status") is not True for r in rows)):
        raise RuntimeError("Incomplete indexing batch; stop and reconcile before retry")


def delete_document(client, tenant, document_id):
    """Tenant + parent filter; never follow an untrusted continuation URL."""
    result = client.request("search", "POST", f"/indexes/{client.index}/docs/search?api-version={client.version}", {
        "search": "*", "filter": f"tenant eq {odata(tenant)} and document_id eq {odata(document_id)}",
        "select": "id,tenant,document_id", "top": 1000})
    rows = result["value"]
    if result.get("@odata.nextLink") or result.get("@search.nextPageParameters") or len(rows) >= 1000:
        raise RuntimeError("Parent exceeds bounded lifecycle limit; use dedicated migration tooling")
    if any(r["tenant"] != tenant or r["document_id"] != document_id for r in rows):
        raise RuntimeError("Index returned keys outside the requested parent scope")
    checked_batch(client, [{"@search.action": "delete", "id": r["id"]} for r in rows])
    return len(rows)


def replace_document(client, tenant, document):
    # Reuse local validation before any remote mutation.
    with tempfile.TemporaryDirectory() as tmp:
        Store(Path(tmp) / "validate.db").upsert(Principal("indexer", tenant, (), True), document)
    upload = []
    for n, text in enumerate(chunks(document["text"])):
        upload.append({"@search.action": "upload", "id": hashlib.sha256(
            f"{tenant}:{document['id']}:{n}".encode()).hexdigest(), "document_id": document["id"],
            "tenant": tenant, "title": document["title"], "text": text, "group_ids": document["groups"],
            "content_vector": client.embedding(text)})
    if len(json.dumps({"value": upload}).encode()) > 15_000_000 or len(upload) > 1000:
        raise ValueError("Parent exceeds bounded upload limit")
    # Compute/validate embeddings before deleting; deletion failure blocks upload.
    deleted = delete_document(client, tenant, document["id"])
    checked_batch(client, upload)
    return {"uploaded": len(upload), "deleted": deleted}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--apply", action="store_true", help="Required explicit remote mutation consent")
    parser.add_argument("--delete-document", help="Delete all chunks of one explicitly named tenant document")
    args = parser.parse_args()
    if not args.apply:
        parser.error("Pass --apply to create/update the dedicated Azure demo index and upload fixtures")
    client = AzureRAG()
    if args.delete_document:
        print(json.dumps({"deleted": delete_document(client, args.tenant, args.delete_document)}))
        return
    dimension = len(client.embedding("synthetic index dimension probe"))
    fields = [{"name":name,"type":"Edm.String","key":name=="id","searchable":name in {"text","title"},"filterable":name in {"tenant","document_id"}} for name in ("id","document_id","tenant","title","text")]
    fields += [
        {"name":"group_ids","type":"Collection(Edm.String)","filterable":True},
        {"name":"content_vector","type":"Collection(Edm.Single)","searchable":True,"dimensions":dimension,"vectorSearchProfile":"hybrid-profile"}
    ]
    client.request("search", "PUT", f"/indexes/{client.index}?api-version={client.version}", {"name":client.index,"fields":fields,"vectorSearch":{"algorithms":[{"name":"hnsw-default","kind":"hnsw"}],"profiles":[{"name":"hybrid-profile","algorithm":"hnsw-default"}]}})
    counts = []
    for doc in json.loads(Path("fixtures/documents.json").read_text()):
        counts.append(replace_document(client, args.tenant, doc))
    print(json.dumps({"uploaded": sum(c["uploaded"] for c in counts),
                      "deleted": sum(c["deleted"] for c in counts), "dimensions":dimension,"tenant":args.tenant}))


if __name__ == "__main__":
    main()
