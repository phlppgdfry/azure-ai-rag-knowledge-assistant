from importlib.resources import files
from pathlib import Path
import json


def test_packaged_demo_data_matches_preserved_repository_fixtures():
    for name in ('documents.json', 'retrieval-cases.json'):
        assert json.loads(files('rag').joinpath('data', name).read_text()) == json.loads(
            (Path('fixtures') / name).read_text())
