.PHONY: data store load truth truth-official test

data:          ## download CK25 at the pinned commit
	scripts/get_data.sh

store:         ## start Oxigraph on :7878
	docker compose up -d fuseki

load:          ## load prod-inst.ttl (and nothing else) into the store
	scripts/load_store.sh

truth:         ## sanity check: all 50 reference queries return results locally
	uv run --group eval python eval/check_truth.py

truth-official: ## official ground truth (holds the answers, so it is not committed)
	rm -f results/true.json
	uv run --group eval text2sparql query data/ck25/questions.yml -e $${SPARQL_ENDPOINT:-http://localhost:3030/ck/query} -o results/true.json

test:
	uv run pytest -q
