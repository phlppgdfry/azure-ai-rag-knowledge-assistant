"""Reproducible lexical retrieval benchmark; not a semantic answer-quality claim."""
import json
import math
import tempfile
from pathlib import Path

from .core import Principal, Store


def ranking_metrics(retrieved, relevant, k):
    if k < 1:
        raise ValueError('k must be positive')
    # Document-level ranking; duplicate chunks cannot inflate relevance.
    ranked = list(dict.fromkeys(retrieved))[:k]
    relevant = set(relevant)
    hits = [index + 1 for index, item in enumerate(ranked) if item in relevant]
    dcg = sum(1 / math.log2(rank + 1) for rank in hits)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
    return {'precision_at_k': len(hits) / k, 'recall_at_k': len(hits) / len(relevant) if relevant else None,
            'reciprocal_rank': 1 / hits[0] if hits else 0, 'ndcg_at_k': dcg / ideal if ideal else None}


def benchmark():
    root = Path(__file__).resolve().parents[1]
    cases = json.loads((root / 'fixtures/retrieval-cases.json').read_text())
    rows = []
    with tempfile.TemporaryDirectory() as folder:
        store = Store(Path(folder) / 'eval.db')
        for doc in json.loads((root / 'fixtures/documents.json').read_text()):
            store.upsert(Principal('admin', 'demo', (), True), doc)
        for case in cases:
            user = Principal('eval', case['tenant'], tuple(case['groups']))
            hits = store.retrieve(user, case['query'], case['k'])
            ids = list(dict.fromkeys(h['document_id'] for h in hits))
            rows.append({'id': case['id'], 'retrieved': ids,
                         'metrics': ranking_metrics(ids, case['relevant'], case['k']),
                         'permission_pass': not bool(set(ids) & set(case.get('forbidden', []))),
                         'expected_abstention_pass': (not ids) if not case['relevant'] else bool(ids)})
    return {'mode': 'local-extractive', 'synthetic': True, 'k_definition': 'unique documents; precision denominator is k',
            'limitations': 'Small authored lexical dataset, no LLM answer correctness or cloud benchmark', 'results': rows}


if __name__ == '__main__':
    print(json.dumps(benchmark(), indent=2))
