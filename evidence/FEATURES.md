# Feature evidence matrix — 29 October 2026

Status vocabulary: **VERIFIED** means the stated local behavior was executed; **IMPLEMENTED BUT NOT VERIFIED** means code/artifacts exist without live acceptance; **MOCKED** means a deliberately substituted external effect; **DOCUMENTED ONLY** is a design/runbook; **PLANNED** is future work. Local tests do not prove production safety, real customer use or legal compliance.

Verification commands and results are in [verification-2026-10-29.json](verification-2026-10-29.json). Original 28 October evidence is retained as historical evidence. The pinned dependency audit reports no known advisories at scan time, not absence of all vulnerabilities. Request logs omit bodies, query strings and credentials.

| Feature | Status | Evidence / limitation |
|---|---|---|
| ACL-filtered lexical retrieval, replace/delete, citations | VERIFIED | tests/test_retrieval.py |
| Knowledge UI and finance/HR abstention | VERIFIED | playbook portfolio/browser-qa.json; screenshots/desktop.png |
| Precision/recall/MRR/nDCG definitions and six-case benchmark | VERIFIED | rag/evaluate.py; tests/test_metrics.py; retrieval-2026-10-29.json |
| Azure embeddings/hybrid search/generation | IMPLEMENTED BUT NOT VERIFIED | mock HTTP contract tests only; no live cloud call |
| Azure parent replacement/deletion | IMPLEMENTED BUT NOT VERIFIED | lifecycle contract tests pass; atomic cloud update not claimed |
| Live Azure quality, managed identity token refresh, index-alias rollout | PLANNED | docs/azure.md; docs/portfolio-integration.md |
