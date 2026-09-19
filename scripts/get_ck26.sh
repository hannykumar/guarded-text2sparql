#!/usr/bin/env bash
# Download the CK26 question set (paraphrases of CK25 over the same graph).
# Evaluator-only, and deliberately NOT committed: it is CC-BY-SA-4.0, so a modified
# copy would have to carry that licence. The graph itself stays prod-inst.ttl.
set -euo pipefail
CK26_COMMIT=935cb5a210717a7596a6028740136ac842db7ede  # branch 2026, 2026-07-20
DEST=data/ck26
mkdir -p "$DEST"
curl -fsSL -o "$DEST/questions_ck26.yml" \
  "https://raw.githubusercontent.com/AKSW/text2sparql.aksw.org/$CK26_COMMIT/docs/results/ck26/questions_ck26.yml"
echo "$CK26_COMMIT" > "$DEST/COMMIT"
echo "CK26 @ $CK26_COMMIT -> $DEST/questions_ck26.yml (CC-BY-SA-4.0, AKSW)"
