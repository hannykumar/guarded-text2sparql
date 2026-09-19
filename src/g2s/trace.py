"""One JSONL record per question: what the pipeline did, for the diagnostics.

Never contains reference answers; only the question, our own steps and our own query.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from g2s.config import settings

PATH = Path(os.environ.get("G2S_TRACE", "results/traces.jsonl"))


def record(**fields: object) -> None:
    """Append one trace line. Tracing must never break a request, so failures are swallowed."""
    line = {"time": time.time(), "config": settings.config_name, "model": settings.llm_model, **fields}
    try:
        PATH.parent.mkdir(parents=True, exist_ok=True)
        with PATH.open("a") as handle:
            handle.write(json.dumps(line, default=str) + "\n")
    except OSError:
        pass
