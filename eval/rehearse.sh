#!/usr/bin/env bash
# Rehearse the whole measurement without a model: a stub LLM answers instantly, so the
# harness (ablate -> official client -> diagnostics -> report) is proven end to end in
# seconds instead of hours. Writes to a scratch directory, never into results/.
set -euo pipefail
ROOT=$(mktemp -d)
PORT=11500
trap 'kill %1 2>/dev/null || true; rm -rf "$ROOT"' EXIT

uv run python eval/fake_llm_server.py "$PORT" >/dev/null 2>&1 &
until curl -fsS -X POST "http://localhost:$PORT/v1/chat/completions" -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"ping"}]}' >/dev/null 2>&1; do sleep 0.5; done

RESULTS_ROOT="$ROOT" G2S_TRACE="$ROOT/traces.jsonl" LLM_BASE_URL="http://localhost:$PORT/v1" \
  eval/ablate.sh dev 1 A3 >"$ROOT/run.log" 2>&1

uv run --group eval python eval/diagnostics.py "$ROOT/traces.jsonl" >"$ROOT/diagnostics.json"
test -s "$ROOT/A3/dev/run1/metrics.json"
test -s "$ROOT/diagnostics.json"
echo "rehearsal ok: scored run, traces and diagnostics all produced (results/ untouched)"
