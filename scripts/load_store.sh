#!/usr/bin/env bash
# Replace the store's default graph with prod-inst.ttl. Nothing else is ever loaded.
set -euo pipefail
STORE=${STORE_URL:-http://localhost:3030/ck}
AUTH="admin:${FUSEKI_PASSWORD:-admin}"

# The store needs a few seconds after `make store` before its dataset exists.
for _ in $(seq 1 60); do
  curl -fs -o /dev/null --data-urlencode 'query=ASK {}' "$STORE/query" 2>/dev/null && break
  sleep 1
done

curl -fsS -u "$AUTH" -X PUT -H 'Content-Type: text/turtle' \
  --data-binary @data/ck25/graphs/prod-inst.ttl "$STORE/data?default" -o /dev/null
curl -fsS -H 'Accept: text/csv' --data-urlencode \
  'query=SELECT (COUNT(*) AS ?triples) WHERE { ?s ?p ?o }' "$STORE/query"
