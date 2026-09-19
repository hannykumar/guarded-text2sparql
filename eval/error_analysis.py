"""Worksheet for labelling every failed question by cause.

Prints a markdown table of the failures with our query and what the guardrails said,
so the causes can be labelled by hand. A machine cannot tell "wrong property" from
"wrong direction" reliably; a person can, and that table convinces a reviewer more
than the headline score.

Evaluator-only: reads metrics (which come from the reference answers).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CAUSES = [
    "wrong entity",
    "wrong property",
    "wrong direction",
    "missing aggregation",
    "wrong ORDER BY / LIMIT",
    "wrong answer shape",
    "other",
]


def traces_by_question(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    index = {}
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            index[record.get("question", "")] = record
    return index


def main(run_dir: str = "results/A3/test/run1", traces: str = "results/traces.jsonl") -> int:
    directory = Path(run_dir)
    metrics = json.loads((directory / "metrics.json").read_text())
    answers = {a["qname"]: a for a in json.loads((directory / "answers.json").read_text()) if "qname" in a}
    by_question = traces_by_question(Path(traces))

    failed = sorted(
        (qname, scores)
        for qname, scores in metrics.items()
        if qname.startswith(("ck25:", "ck26:")) and scores.get("set_F", 0) < 0.99
    )

    lines = [
        f"# Error analysis: {run_dir}",
        "",
        f"{len(failed)} of {len(metrics) - 1} questions scored below 1.0. Label the cause of each by hand.",
        "",
        "Causes: " + ", ".join(f"`{c}`" for c in CAUSES),
        "",
    ]
    for qname, scores in failed:
        answer = answers.get(qname, {})
        trace = by_question.get(answer.get("question", ""), {})
        attempts = trace.get("attempts") or []
        last_errors = (attempts[-1].get("errors") if attempts else []) or []
        lines += [
            f"## {qname} (F1 {scores.get('set_F', 0):.2f})",
            "",
            f"**Question:** {answer.get('question', '?')}",
            "",
            "```sparql",
            (answer.get("query") or "(no query)").strip(),
            "```",
            "",
            f"**Guardrails at the end:** {'; '.join(last_errors) if last_errors else 'all passed'}",
            f"**Repairs:** {max(len(attempts) - 1, 0)}",
            "",
            "**Cause:** _________",
            "",
        ]
    output = directory / "ERRORS.md"
    output.write_text("\n".join(lines))
    print(f"wrote {output}: {len(failed)} failures to label")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
