#!/bin/bash
# Run Ollama on a cluster GPU node. The pipeline stays on the laptop and talks to it
# over an SSH tunnel, so only inference happens here.
#
#   sbatch scripts/cluster/ollama.sbatch
#   squeue -u $USER              # find the node it landed on
#   cat ollama-<jobid>.out       # prints the node and port to tunnel to
#
#SBATCH --job-name=ollama
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=04:00:00
#SBATCH --output=ollama-%j.out

set -euo pipefail
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_MODELS=$HOME/ollama-models      # everything we add lives here, easy to delete
export OLLAMA_KEEP_ALIVE=30m
export OLLAMA_NUM_PARALLEL=1

echo "node: $(hostname)"
echo "gpu:  $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || echo unknown)"
echo "tunnel from the laptop with:"
echo "  ssh -N -J $USER@login-1.gpu.cit-ec.net $USER@$(hostname) -L 11434:localhost:11434"

"$HOME/ollama/bin/ollama" serve &
OLLAMA_PID=$!
trap 'kill $OLLAMA_PID 2>/dev/null || true' EXIT

until "$HOME/ollama/bin/ollama" list >/dev/null 2>&1; do sleep 2; done
"$HOME/ollama/bin/ollama" pull "${MODEL:-qwen2.5-coder:7b}"
echo "ready: $("$HOME/ollama/bin/ollama" list | tail -n +2 | awk '{print $1}' | tr '\n' ' ')"

wait $OLLAMA_PID
