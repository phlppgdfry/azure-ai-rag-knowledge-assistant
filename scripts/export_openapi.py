import argparse
import json
from pathlib import Path
from rag.api import app

parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
path = Path('docs/openapi.json')
content = json.dumps(app.openapi(), indent=2, sort_keys=True) + '\n'
if args.check:
    if not path.exists() or path.read_text() != content:
        raise SystemExit('OpenAPI snapshot differs; run python scripts/export_openapi.py')
else:
    path.parent.mkdir(exist_ok=True)
    path.write_text(content)
