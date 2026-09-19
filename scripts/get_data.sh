#!/usr/bin/env bash
# Download CK25 (CC-BY-4.0, eccenca GmbH) at a pinned commit into data/ck25.
set -euo pipefail
CK25_COMMIT=cb928b2f201e4bdbbde9a1cd0653152779736395  # v1.2.0, 2026-06-23
DEST=data/ck25

rm -rf "$DEST" && mkdir -p "$DEST"
curl -fsSL "https://github.com/eccenca/ck25-dataset/archive/$CK25_COMMIT.tar.gz" \
  | tar -xz -C "$DEST" --strip-components=1
echo "$CK25_COMMIT" > "$DEST/COMMIT"

# queries.ttl holds all 50 reference answers. Delete it so nothing can ever load it.
rm -f "$DEST/graphs/queries.ttl" "$DEST/graphs/queries.ttl.graph"

echo "CK25 @ $CK25_COMMIT -> $DEST"
