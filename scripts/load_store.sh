#!/usr/bin/env bash
# Replace the store's default graph with prod-inst.ttl. Nothing else is ever loaded.
set -euo pipefail
STORE=${OXIGRAPH_URL:-http://localhost:7878}
curl -fsS -X PUT -H 'Content-Type: text/turtle' \
  --data-binary @data/ck25/graphs/prod-inst.ttl "$STORE/store?default"
curl -fsS -H 'Accept: text/csv' --data-urlencode 'query=SELECT (COUNT(*) AS ?triples) WHERE { ?s ?p ?o }' "$STORE/query"
