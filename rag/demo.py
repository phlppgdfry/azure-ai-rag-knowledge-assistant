import json
import tempfile
from pathlib import Path
from importlib.resources import files
from rag.core import Principal, Store


def main():
    with tempfile.TemporaryDirectory() as directory:
        store = Store(Path(directory) / "demo.sqlite3")
        admin = Principal("seed", "synthetic-firm", ("finance",), True)
        for doc in json.loads(files("rag").joinpath("data/documents.json").read_text()):
            store.upsert(admin, doc)
        result = store.answer(Principal("analyst", "synthetic-firm", ("finance",)), "factuur goedkeuring")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
