# Retrieval evidence and lifecycle

Open `/console` and use a server-configured finance/HR key to inspect responses and source chunks. The local answer is extractive, without an LLM. The UI shows abstention when no matching authorized source exists. Keys stay in page memory and never enter a URL or browser storage.

```bash
.venv/bin/python -m rag.evaluate
```

The six authored queries in `fixtures/retrieval-cases.json` measure unique document rankings. Precision divides relevant retrieved documents by **k** (including unfilled positions); recall divides by the relevant set size; reciprocal rank uses the first relevant document; nDCG uses binary relevance and logarithmic discounting. Empty relevant sets have null recall/nDCG and separate permission/abstention checks. Duplicate chunks cannot inflate document scores. This small lexical benchmark does not measure semantic answer correctness, production recall or cloud latency.

`rag.index` now explicitly replaces each document: validate, compute embeddings, query tenant+parent keys, delete all old chunks, check every acknowledgement, then upload the replacement. It rejects cross-scope keys, incomplete/partial batches, continuation pages and parents near 1,000 chunks. Deletion of a source removed from the fixture file must be explicit:

```bash
.venv/bin/python -m rag.index --tenant demo --delete-document invoice-policy --apply
```

**This is a documented remote mutation, not executed here.** Replacement is not an atomic Azure operation. Pause serving the index during updates/ACL changes, wait for service-side visibility and verify retrieval before reopening it. Embedding failure occurs before deletion; upload failure after deletion can leave the document unavailable. Stop and reconcile, then retry the full replacement. Concurrent indexing requires an external maintenance lock; this CLI does not provide one. No claim of instantaneous Azure permission revocation is made. For production, use index-version/alias rollout and an authorization source checked independently of stale search metadata.

Official lifecycle reference read through Context7: [Azure Search delete documents](https://learn.microsoft.com/en-us/azure/search/search-how-to-delete-documents). Contract tests use injected client responses; no live mutation or Azure deletion guarantee was verified.

The [playbook runner](https://github.com/phlppgdfry/ai-transformation-playbook) starts the local APIs and proves workflow retrieval, finance/HR access separation and evaluation gates. The workflow's finance key does not grant document administration.
