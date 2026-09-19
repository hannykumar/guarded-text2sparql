#!/usr/bin/env bash
# Score one or more ablation configs. Each needs its own API process: settings are read at import.
# Usage: eval/ablate.sh [dev|test|all] [RUN_NUMBER] [CONFIG...]
set -euo pipefail
API=${API_URL:-http://localhost:8000}
SPLIT=${1:-dev}
RUN=${2:-1}
shift 2 || true
CONFIGS=("${@:-A0 A1 A2 A3}")
export PYTHONPATH=src  # the project is not installed; src goes on the path

# One run at a time. Two overlapping runs write to the same result paths and
# silently score one run's answers against another's queries.
if curl -fsS "$API/health" >/dev/null 2>&1; then
  echo "an API is already running on $API - stop it first" >&2
  exit 1
fi

for CONFIG in ${CONFIGS[@]}; do
  echo "=== $CONFIG ($SPLIT, run $RUN)"
  set -a; . "eval/configs/$CONFIG.env"; set +a
  uv run uvicorn g2s.api:app --port 8000 --log-level warning &
  API_PID=$!
  trap 'kill $API_PID 2>/dev/null || true' EXIT
  # wait for the API, but give up if it died: a hanging wait once let a stale run
  # attach itself to the next run's server
  for _ in $(seq 1 60); do
    curl -fsS "$API/health" >/dev/null 2>&1 && break
    kill -0 $API_PID 2>/dev/null || { echo "API process died, see the log above" >&2; exit 1; }
    sleep 1
  done
  curl -fsS "$API/health" >/dev/null 2>&1 || { echo "API did not come up" >&2; exit 1; }
  API_URL="$API" eval/run_official.sh "$CONFIG" "$SPLIT" "$RUN"
  kill $API_PID 2>/dev/null || true
  wait $API_PID 2>/dev/null || true
  trap - EXIT
done
