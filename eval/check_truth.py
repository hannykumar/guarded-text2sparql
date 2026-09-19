"""Day-1 sanity check: every CK25 reference query must return a non-empty result on the local store.

Evaluator-only file: it reads the reference queries, so the pipeline (src/) must never import it.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "http://localhost:3030/ck/query")


def run(query: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT,
        data=urllib.parse.urlencode({"query": query}).encode(),
        headers={"Accept": "application/sparql-results+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def is_empty(res: dict) -> bool:
    return "boolean" not in res and not res["results"]["bindings"]  # ASK always answers


def main(path: str = "data/ck25/questions.yml") -> int:
    questions = yaml.safe_load(Path(path).read_text())["questions"]
    bad = []
    for q in questions:
        try:
            if is_empty(run(q["query"]["sparql"])):
                bad.append((q["id"], "empty"))
        except (OSError, ValueError) as e:  # HTTP/connection errors and bad JSON; report all, not just the first
            bad.append((q["id"], str(e)))
    for qid, why in bad:
        print(f"FAIL ck25:{qid}: {why}")
    print(f"{len(questions) - len(bad)}/{len(questions)} reference queries return results")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
