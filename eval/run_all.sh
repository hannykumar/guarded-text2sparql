#!/usr/bin/env bash
# The measurement, unattended. Start it when you are not using the machine.
#
#   eval/run_all.sh rehearse   # seconds, no model: proves the harness works
#   eval/run_all.sh smoke      # minutes: one real run with the small model
#   eval/run_all.sh dev        # A0-A3 on the 15 dev questions, 3 runs each
#   eval/run_all.sh test       # A0-A3 on the 35 held-back questions + the model comparison
#   eval/run_all.sh ck26       # the paraphrase-robustness run
#
# Run `dev` first, look at the results, freeze the design, and only then run `test`.
# The test questions are meant to be seen once.
#
# Resumable: a run whose metrics.json already exists is skipped, so Ctrl-C and restart
# continues where it stopped. One model call at a time; never two API processes at once.
set -euo pipefail
# No default: a bare `eval/run_all.sh` must never start loading a model by accident.
MODE=${1:-}
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

case "$MODE" in
  rehearse)
    exec eval/rehearse.sh
    ;;
  smoke)
    ollama pull "$COMPARISON_MODEL"
    run_one A3 dev 99 "$COMPARISON_MODEL"
    uv run --group eval python eval/diagnostics.py
    echo "smoke done. If this looks right: eval/run_all.sh dev"
    exit 0
    ;;
  dev|test)
    # three runs each: local inference is not bit-identical even at temperature 0
    for run in 1 2 3; do
      for config in A0 A1 A2 A3; do
        run_one "$config" "$MODE" "$run" "$MAIN_MODEL" || true  # keep going; failures are logged
      done
    done
    # model comparison, full system only, on the held-back questions
    if [ "$MODE" = test ]; then
      for run in 1 2 3; do
        run_one A3 test "1${run}" "$COMPARISON_MODEL" || true
      done
    fi
    ;;
  ck26)
    run_one A3 ck26 1 "$MAIN_MODEL" || true
    ;;
  *)
    echo "usage: eval/run_all.sh rehearse|smoke|dev|test|ck26" >&2
    echo "  rehearse  seconds, no model      smoke  minutes, small model" >&2
    echo "  dev       the 15 dev questions   test   the 35 held-back questions" >&2
    exit 1
    ;;
esac

uv run --group eval python eval/diagnostics.py
uv run --group eval python eval/report.py
echo "done. results/RESULTS.md is written."
