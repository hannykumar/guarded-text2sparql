"""A stand-in for Ollama that answers instantly, to rehearse the measurement batch.

The whole harness (ablate -> official client -> diagnostics -> report) can then be
proven end to end without loading a model, which on a laptop takes hours.

    uv run python eval/fake_llm_server.py &
    LLM_BASE_URL=http://localhost:11500/v1 eval/ablate.sh dev 90 A3
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# Deliberately imperfect: a real query for the one question it knows, a query with a
# bad property otherwise, so the repair loop and the guardrail diagnostics get exercised.
KNOWN = """PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  <http://ld.company.org/prod-instances/empl-Karen.Brant%40company.org> pv:memberOf ?result .
  ?result a pv:Department .
}"""
FALLBACK = """PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?result WHERE { ?result a pv:Department }"""
BAD = """PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?result WHERE { ?result pv:worksIn ?x }"""


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = body["messages"][-1]["content"]
        if '"mentions"' in prompt:
            reply = '{"mentions": []}'
        elif "What is wrong with it" in prompt:
            reply = FALLBACK  # the "repair": drop the invented property
        elif "department" in prompt.lower() and "brant" in prompt.lower():
            reply = KNOWN
        else:
            reply = BAD
        payload = json.dumps({"choices": [{"message": {"content": reply}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args: object) -> None:
        pass  # quiet


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 11500
    print(f"fake LLM on :{port}", flush=True)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
