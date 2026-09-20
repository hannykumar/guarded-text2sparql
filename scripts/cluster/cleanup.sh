#!/usr/bin/env bash
# Remove everything this project put on the cluster. Run it when the runs are done.
set -euo pipefail
scancel -u "$USER" --name=ollama 2>/dev/null || true
rm -rf "$HOME/ollama" "$HOME/ollama-models" "$HOME"/ollama-*.out
echo "removed: ~/ollama, ~/ollama-models, job logs. Remaining home usage:"
du -sh "$HOME" 2>/dev/null | tail -1
