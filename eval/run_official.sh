#!/usr/bin/env bash
# One official scoring run: ask our API, execute both sides, score.
# Usage: eval/run_official.sh [CONFIG] [dev|test|all] [RUN_NUMBER]
set -euo pipefail
CONFIG=${1:-A3}
SPLIT=${2:-dev}
RUN=${3:-1}
API=${API_URL:-http://localhost:8000}
STORE=${SPARQL_ENDPOINT:-http://localhost:3030/ck/query}

OUT="results/$CONFIG/$SPLIT/run$RUN"
mkdir -p "$OUT"
rm -f "$OUT"/{true,answers,pred,metrics}.json "$OUT/responses.db"

if [ "$SPLIT" = all ]; then
  QUESTIONS=data/ck25/questions.yml
elif [ "$SPLIT" = ck26 ]; then
  # paraphrase-robustness check: same graph, reworded questions
  [ -f data/ck26/questions_ck26.yml ] || scripts/get_ck26.sh
  QUESTIONS=data/ck26/questions_ck26.yml
else
  QUESTIONS="data/ck25/questions-$SPLIT.yml"
  uv run --group eval python eval/split.py subset "$SPLIT" "$QUESTIONS"
fi

# 1. ground truth: the reference queries on our store
uv run --group eval text2sparql query "$QUESTIONS" -e "$STORE" -o "$OUT/true.json"
# 2. our system's queries. --no-cache, or a rerun would silently reuse another config's answers
uv run --group eval text2sparql ask "$QUESTIONS" "$API" --no-cache --answers-db "$OUT/responses.db" -o "$OUT/answers.json"
# 3. run our queries
uv run --group eval text2sparql query "$QUESTIONS" -a "$OUT/answers.json" -e "$STORE" -o "$OUT/pred.json"
# 4. score
uv run --group eval text2sparql evaluate "$CONFIG" "$OUT/true.json" "$OUT/pred.json" -o "$OUT/metrics.json"

echo "metrics: $OUT/metrics.json"
