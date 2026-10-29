import pytest
from rag.evaluate import ranking_metrics, benchmark


def test_metrics_penalize_rank_and_deduplicate_chunks():
    metrics = ranking_metrics(['wrong', 'policy', 'policy'], ['policy', 'missing'], 3)
    assert metrics['precision_at_k'] == 1 / 3
    assert metrics['recall_at_k'] == .5
    assert metrics['reciprocal_rank'] == .5
    assert metrics['ndcg_at_k'] == pytest.approx((1 / 1.584962500721156) / (1 + 1 / 1.584962500721156))
    assert ranking_metrics([], [], 1)['recall_at_k'] is None


def test_authored_retrieval_baseline():
    for case in benchmark()['results']:
        assert case['permission_pass'] and case['expected_abstention_pass']
        if case['metrics']['recall_at_k'] is not None:
            assert case['metrics']['recall_at_k'] == 1
