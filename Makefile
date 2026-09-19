.PHONY: data store load truth truth-official serve rehearse smoke evaluate evaluate-test report test

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

serve:         ## run the API on :8000
	PYTHONPATH=src uv run uvicorn g2s.api:app --port 8000

rehearse:      ## seconds: prove the whole measurement harness with a stub LLM, no model
	eval/rehearse.sh

smoke:         ## a few minutes: prove the measurement plumbing with a tiny model
	eval/run_all.sh smoke

evaluate:      ## the dev measurement, unattended and resumable (hours; the machine will be slow)
	eval/run_all.sh dev

evaluate-test: ## the held-back 35 questions. Only after the design is frozen
	eval/run_all.sh test

report:        ## rebuild results/RESULTS.md and diagnostics from whatever has been measured
	uv run --group eval python eval/diagnostics.py
	uv run --group eval python eval/report.py

test:
	uv run pytest -q
