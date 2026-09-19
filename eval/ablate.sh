#!/usr/bin/env bash
# Score one or more ablation configs. Each needs its own API process: settings are read at import.
# Usage: eval/ablate.sh [dev|test|all] [RUN_NUMBER] [CONFIG...]
set -euo pipefail
SPLIT=${1:-dev}
RUN=${2:-1}
shift 2 || true
CONFIGS=("${@:-A0 A1 A2 A3}")

for CONFIG in ${CONFIGS[@]}; do
  echo "=== $CONFIG ($SPLIT, run $RUN)"
  set -a; . "eval/configs/$CONFIG.env"; set +a
  uv run uvicorn g2s.api:app --port 8000 --log-level warning &
  API_PID=$!
  trap 'kill $API_PID 2>/dev/null || true' EXIT
  until curl -fsS http://localhost:8000/health >/dev/null 2>&1; do sleep 1; done
  eval/run_official.sh "$CONFIG" "$SPLIT" "$RUN"
  kill $API_PID 2>/dev/null || true
  wait $API_PID 2>/dev/null || true
  trap - EXIT
done
