"""Guardrail metrics from the pipeline's own traces.

Answers what the F1 score cannot: did the queries parse, did they use real vocabulary,
how often did a repair fire, and did it help. Reads results/traces.jsonl only,
never the reference answers.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import median


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def percentile(values: list[float], fraction: float) -> float:
    """Nearest-rank percentile. Small samples, so no interpolation games."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(fraction * len(ordered)) - 1))
    return ordered[index]


def summarise(traces: list[dict]) -> dict:
    total = len(traces)
    if not total:
        return {}
    blocked = [t for t in traces if t.get("blocked")]
    first_errors: Counter[str] = Counter()
    repaired_ok = repaired = 0
    clean_first_try = 0

    for trace in traces:
        attempts = trace.get("attempts") or []
        if not attempts:
            continue
        first = attempts[0].get("errors") or []
        if not first:
            clean_first_try += 1
        else:
            repaired += 1
            for error in first:
                first_errors[error.split(":")[0]] += 1
            if not (attempts[-1].get("errors") or []):
                repaired_ok += 1

    seconds = [t["seconds"] for t in traces if "seconds" in t]
    final_clean = sum(1 for t in traces if t.get("attempts") and not (t["attempts"][-1].get("errors") or []))

    return {
        "questions": total,
        "clean_first_try": clean_first_try,
        "needed_repair": repaired,
        "repair_succeeded": repaired_ok,
        "repair_success_rate": round(repaired_ok / repaired, 3) if repaired else None,
        "passing_all_guardrails_at_the_end": final_clean,
        "g1_blocks": len(blocked),
        "first_failure_by_guardrail": dict(first_errors.most_common()),
        "repairs_per_question_median": median([len(t.get("attempts", [])) - 1 for t in traces]) if total else 0,
        "seconds_p50": round(percentile(seconds, 0.5), 1),
        "seconds_p95": round(percentile(seconds, 0.95), 1),
    }


def main(path: str = "results/traces.jsonl") -> int:
    traces = load(Path(path))
    by_config: dict[str, list[dict]] = {}
    for trace in traces:
        by_config.setdefault(trace.get("config", "?"), []).append(trace)

    report = {config: summarise(rows) for config, rows in sorted(by_config.items())}
    print(json.dumps(report, indent=2))
    Path("results/diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
