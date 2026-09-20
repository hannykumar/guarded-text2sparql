#!/usr/bin/env bash
# Install Ollama into $HOME on the cluster. No root, nothing outside $HOME,
# so scripts/cluster/cleanup.sh can remove every trace afterwards.
set -euo pipefail
VERSION=${1:-v0.12.3}
URL="https://github.com/ollama/ollama/releases/download/$VERSION/ollama-linux-amd64.tgz"

mkdir -p "$HOME/ollama"
if curl -fsSL --connect-timeout 10 "$URL" -o /tmp/ollama.tgz; then
  echo "downloaded on the cluster"
else
  echo "no direct internet on this node." >&2
  echo "On your laptop instead:" >&2
  echo "  curl -fL $URL -o ollama.tgz" >&2
  echo "  scp ollama.tgz $USER@login-1.gpu.cit-ec.net:/tmp/" >&2
  exit 1
fi
tar -xzf /tmp/ollama.tgz -C "$HOME/ollama"
rm -f /tmp/ollama.tgz
"$HOME/ollama/bin/ollama" --version
