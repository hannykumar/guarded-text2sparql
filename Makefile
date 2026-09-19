.PHONY: data store load truth test

data:          ## download CK25 at the pinned commit
	scripts/get_data.sh

store:         ## start Oxigraph on :7878
	docker compose up -d fuseki

load:          ## load prod-inst.ttl (and nothing else) into the store
	scripts/load_store.sh

truth:         ## sanity check: all 50 reference queries return results locally
	uv run --group eval python eval/check_truth.py

test:
	uv run pytest -q
