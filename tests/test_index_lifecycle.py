import pytest
from rag.index import replace_document, delete_document


class Search:
    index, version = 'demo', 'contract-test'

    def __init__(self):
        self.actions = []
        self.old = [{'id': 'old-1', 'tenant': 'demo', 'document_id': 'policy'},
                    {'id': 'old-2', 'tenant': 'demo', 'document_id': 'policy'}]
        self.partial = False

    def embedding(self, text):
        return [.1, .2]

    def request(self, service, method, path, body):
        self.actions.append(body)
        if path.startswith('/indexes/demo/docs/search'):
            assert body['filter'] == "tenant eq 'demo' and document_id eq 'policy'"
            return {'value': self.old}
        return {'value': [{'key': a['id'], 'status': not self.partial} for a in body['value']]}


def test_shorter_replacement_deletes_all_old_chunks_before_upload():
    client = Search()
    result = replace_document(client, 'demo', {'id': 'policy', 'title': 'Policy',
                                              'text': 'Short revised policy.', 'groups': ['finance']})
    assert result == {'deleted': 2, 'uploaded': 1}
    assert [a['@search.action'] for a in client.actions[1]['value']] == ['delete', 'delete']
    assert client.actions[2]['value'][0]['@search.action'] == 'upload'


def test_cross_tenant_result_never_deleted():
    client = Search()
    client.old[0]['tenant'] = 'other'
    with pytest.raises(RuntimeError, match='scope'):
        delete_document(client, 'demo', 'policy')
    assert len(client.actions) == 1


def test_partial_deletion_blocks_upload():
    client = Search()
    client.partial = True
    with pytest.raises(RuntimeError, match='Incomplete'):
        replace_document(client, 'demo', {'id': 'policy', 'title': 'Policy', 'text': 'Updated', 'groups': ['hr']})
    assert len(client.actions) == 2


def test_empty_delete_and_incomplete_acknowledgement():
    client = Search()
    client.old = []
    assert delete_document(client, 'demo', 'policy') == 0
    assert len(client.actions) == 1
