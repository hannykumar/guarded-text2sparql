#!/usr/bin/env bash
# The whole measurement, unattended. Start it when you are not using the machine.
#
#   eval/run_all.sh            # full: A0-A3 on dev and test, 3 runs each, plus the model comparison
#   eval/run_all.sh smoke      # a few minutes: one tiny-model run on dev, to prove the plumbing
#
# Resumable: a run whose metrics.json already exists is skipped, so Ctrl-C and restart
# continues where it stopped. One model call at a time; never two API processes at once.
set -euo pipefail
MODE=${1:-full}
MAIN_MODEL=${LLM_MODEL:-qwen2.5-coder:7b}
COMPARISON_MODEL=${COMPARISON_MODEL:-qwen2.5-coder:1.5b}
LOGS=results/logs
mkdir -p "$LOGS"

need() { command -v "$1" >/dev/null || { echo "$1 is required" >&2; exit 1; }; }
need uv; need curl; need ollama

curl -fsS "${SPARQL_ENDPOINT:-http://localhost:3030/ck/query}" --data-urlencode 'query=ASK {}' >/dev/null \
  || { echo "no triple store: run 'make store load' first" >&2; exit 1; }

run_one() {  # config split run model
  local config=$1 split=$2 run=$3 model=$4
  local tag="$config/$split/run$run"
  if [ -f "results/$tag/metrics.json" ]; then
    echo "skip  $tag (already scored)"
    return 0
  fi
  echo "run   $tag  model=$model"
  LLM_MODEL="$model" eval/ablate.sh "$split" "$run" "$config" > "$LOGS/${config}-${split}-run${run}.log" 2>&1 \
    || { echo "FAILED $tag - see $LOGS/${config}-${split}-run${run}.log" >&2; return 1; }
}

if [ "$MODE" = smoke ]; then
  ollama pull "$COMPARISON_MODEL"
  run_one A3 dev 99 "$COMPARISON_MODEL"
  uv run --group eval python eval/diagnostics.py
  echo "smoke done. If this looks right, run: eval/run_all.sh"
  exit 0
fi

# 1. the ablation, three runs each: local inference is not bit-identical even at temperature 0
for run in 1 2 3; do
  for config in A0 A1 A2 A3; do
    for split in dev test; do
      run_one "$config" "$split" "$run" "$MAIN_MODEL" || true   # keep going; failures are logged
    done
  done
done

# 2. model comparison on the full system only
for run in 1 2 3; do
  LLM_MODEL="$COMPARISON_MODEL" run_one A3 test "1${run}" "$COMPARISON_MODEL" || true
done

uv run --group eval python eval/diagnostics.py
uv run --group eval python eval/report.py
echo "done. results/RESULTS.md is written."
