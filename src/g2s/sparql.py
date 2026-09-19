"""Minimal SPARQL client. stdlib only: the store speaks HTTP and returns JSON."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "http://localhost:3030/ck/query")
TIMEOUT = 10


class QueryError(RuntimeError):
    """The store rejected the query. The message is handed to the repair prompt verbatim."""


def run(query: str, endpoint: str = ENDPOINT, timeout: int = TIMEOUT) -> dict:
    """Raw SPARQL results (JSON). Raises QueryError with the store's own message."""
    request = urllib.request.Request(
        endpoint,
        data=urllib.parse.urlencode({"query": query}).encode(),
        headers={"Accept": "application/sparql-results+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise QueryError(error.read().decode(errors="replace").strip()[:500]) from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise QueryError(str(error)) from error


def select(query: str, endpoint: str = ENDPOINT, timeout: int = TIMEOUT) -> list[dict[str, str]]:
    """SELECT rows as plain {variable: value} dicts. Unbound variables are simply absent."""
    results = run(query, endpoint, timeout)
    return [{k: v["value"] for k, v in row.items()} for row in results["results"]["bindings"]]
