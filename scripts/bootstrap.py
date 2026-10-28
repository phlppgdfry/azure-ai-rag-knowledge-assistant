import json
import secrets
from pathlib import Path

path = Path('.env')
if path.exists():
    raise SystemExit('.env already exists; refusing to overwrite')
profiles = {'admin': {'subject': 'synthetic-admin', 'tenant': 'synthetic-firm', 'groups': ['finance', 'hr'], 'admin': True}, 'analyst': {'subject': 'synthetic-analyst', 'tenant': 'synthetic-firm', 'groups': ['finance']}, 'hr': {'subject': 'synthetic-hr', 'tenant': 'synthetic-firm', 'groups': ['hr']}}
keys = {secrets.token_urlsafe(32): profile for profile in profiles.values()}
content = "RAG_PRINCIPALS='" + json.dumps(keys) + "'\n"
with path.open('x') as file:
    file.write(content)
path.chmod(0o600)
print('Created local .env with random keys; inspect it privately for role-specific keys.')
