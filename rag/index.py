"""Explicit administrative CLI: creates/updates index and uploads synthetic chunks.

Run only against a dedicated demo index; does not provision Azure resources.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from rag.azure import AzureRAG, required
from rag.core import chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--apply", action="store_true", help="Required explicit remote mutation consent")
    args = parser.parse_args()
    if not args.apply:
        parser.error("Pass --apply to create/update the dedicated Azure demo index and upload fixtures")
    client = AzureRAG()
    dimension = len(client.embedding("synthetic index dimension probe"))
    fields = [{"name":name,"type":"Edm.String","key":name=="id","searchable":name in {"text","title"},"filterable":name in {"tenant","document_id"}} for name in ("id","document_id","tenant","title","text")]
    fields += [
        {"name":"group_ids","type":"Collection(Edm.String)","filterable":True},
        {"name":"content_vector","type":"Collection(Edm.Single)","searchable":True,"dimensions":dimension,"vectorSearchProfile":"hybrid-profile"}
    ]
    client.request("search", "PUT", f"/indexes/{client.index}?api-version={client.version}", {"name":client.index,"fields":fields,"vectorSearch":{"algorithms":[{"name":"hnsw-default","kind":"hnsw"}],"profiles":[{"name":"hybrid-profile","algorithm":"hnsw-default"}]}})
    upload = []
    for doc in json.loads(Path("fixtures/documents.json").read_text()):
        for n, text in enumerate(chunks(doc["text"])):
            upload.append({"@search.action":"mergeOrUpload", "id":hashlib.sha256(f"{args.tenant}:{doc['id']}:{n}".encode()).hexdigest(),"document_id":doc["id"],"tenant":args.tenant,"title":doc["title"],"text":text,"group_ids":doc["groups"],"content_vector":client.embedding(text)})
    result = client.request("search", "POST", f"/indexes/{client.index}/docs/index?api-version={client.version}", {"value":upload})
    if not all(item["status"] for item in result["value"]):
        raise RuntimeError("Some chunks failed indexing; inspect Azure indexer diagnostics")
    print(json.dumps({"uploaded":len(upload),"dimensions":dimension,"tenant":args.tenant}))


if __name__ == "__main__":
    main()
