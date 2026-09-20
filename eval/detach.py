"""Start a long measurement in its own session, so it survives the terminal closing.

    uv run python eval/detach.py dev        # same as eval/run_all.sh dev, but detached

A batch takes hours; without this it dies with whatever started it.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
log = Path("results/logs") / f"{mode}-batch.log"
log.parent.mkdir(parents=True, exist_ok=True)

os.setsid()  # detach: no longer in the caller's process group
with log.open("ab", buffering=0) as handle:
    process = subprocess.Popen(
        ["eval/run_all.sh", mode],
        stdout=handle,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        env={**os.environ, "PYTHONPATH": "src"},
    )
print(f"{mode} batch detached as pid {process.pid}, logging to {log}")
