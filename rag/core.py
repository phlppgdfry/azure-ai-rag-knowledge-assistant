"""Small-corpus lexical baseline. Authorization happens before scoring."""
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str
    groups: tuple[str, ...]
    admin: bool = False


def tokens(text):
    return re.findall(r"[\w-]+", text.casefold())


def chunks(text, size=120, overlap=25):
    words = text.split()
    if size <= overlap or overlap < 0:
        raise ValueError("Chunk overlap must be smaller than chunk size")
    for start in range(0, len(words), size - overlap):
        yield " ".join(words[start:start + size])
        if start + size >= len(words):
            break


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
              id TEXT, tenant TEXT, title TEXT, body TEXT, groups_json TEXT,
              content_hash TEXT, PRIMARY KEY (id, tenant));
            CREATE TABLE IF NOT EXISTS chunks (
              id TEXT PRIMARY KEY, document_id TEXT, tenant TEXT, body TEXT);
            CREATE TABLE IF NOT EXISTS audit (
              seq INTEGER PRIMARY KEY, subject TEXT, tenant TEXT, action TEXT,
              count INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP);
            """)

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def upsert(self, principal, document):
        if not principal.admin:
            raise PermissionError("Document administration required")
        doc = dict(document)
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", doc["id"]):
            raise ValueError("Invalid document id")
        if not doc["groups"] or not all(re.fullmatch(r"[\w-]{1,80}", g) for g in doc["groups"]):
            raise ValueError("Explicit safe group identifiers required")
        if not doc["text"].strip() or len(doc["text"]) > 100_000:
            raise ValueError("Document must contain 1..100000 characters")
        digest = hashlib.sha256(doc["text"].encode()).hexdigest()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)", (
                doc["id"], principal.tenant, doc["title"], doc["text"], json.dumps(doc["groups"]), digest))
            db.execute("DELETE FROM chunks WHERE document_id=? AND tenant=?", (doc["id"], principal.tenant))
            for n, body in enumerate(chunks(doc["text"])):
                cid = hashlib.sha256(f"{principal.tenant}:{doc['id']}:{digest}:{n}".encode()).hexdigest()
                db.execute("INSERT INTO chunks VALUES (?,?,?,?)", (cid, doc["id"], principal.tenant, body))
            db.execute("INSERT INTO audit(subject,tenant,action,count) VALUES (?,?,?,?)", (principal.subject, principal.tenant, "upsert", 1))
        return digest

    def delete(self, principal, doc_id):
        if not principal.admin:
            raise PermissionError("Document administration required")
        with self.connect() as db:
            db.execute("DELETE FROM chunks WHERE tenant=? AND document_id=?", (principal.tenant, doc_id))
            cur = db.execute("DELETE FROM documents WHERE tenant=? AND id=?", (principal.tenant, doc_id))
            db.execute("INSERT INTO audit(subject,tenant,action,count) VALUES (?,?,?,?)", (principal.subject, principal.tenant, "delete", cur.rowcount))

    def retrieve(self, principal, query, top=4):
        if not query.strip() or len(query) > 2000:
            raise ValueError("Query must contain 1..2000 characters")
        with self.connect() as db:
            rows = db.execute("SELECT c.id,c.document_id,d.title,c.body,d.groups_json FROM chunks c JOIN documents d ON d.id=c.document_id AND d.tenant=c.tenant WHERE c.tenant=?", (principal.tenant,)).fetchall()
        # The complete lexical corpus and its IDF statistics are already ACL trimmed.
        allowed = [r for r in rows if set(json.loads(r[4])) & set(principal.groups)]
        bags = [Counter(tokens(r[3])) for r in allowed]
        avg_len = sum(sum(b.values()) for b in bags) / max(1, len(bags))
        results = []
        for row, bag in zip(allowed, bags):
            score = 0.0
            for term in set(tokens(query)):
                freq = bag[term]
                df = sum(term in b for b in bags)
                idf = math.log(1 + (len(bags) - df + .5) / (df + .5))
                score += idf * freq * 2.2 / (freq + 1.2 * (.25 + .75 * sum(bag.values()) / max(1, avg_len)))
            if score > 0:
                results.append(dict(id=row[0], document_id=row[1], title=row[2], text=row[3], score=round(score, 6)))
        results.sort(key=lambda r: (-r["score"], r["id"]))
        with self.connect() as db:
            db.execute("INSERT INTO audit(subject,tenant,action,count) VALUES (?,?,?,?)", (principal.subject, principal.tenant, "retrieve", min(len(results), top)))
        return results[:top]

    def answer(self, principal, query, top=4):
        hits = self.retrieve(principal, query, top)
        return {"mode": "local-extractive", "answer": "\n\n".join(f"{h['text']} [{h['id']}]" for h in hits) if hits else "Geen toegankelijke bron gevonden. Vraag een dossierbeheerder om hulp.", "abstained": not bool(hits), "citations": hits}
