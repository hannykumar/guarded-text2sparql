"""Diagnostics on hand-made traces: no model, no runs needed."""
import json
from pathlib import Path

from eval.diagnostics import summarise


def trace(errors_per_attempt, seconds=1.0, blocked=None):
    if blocked:
        return {"config": "A3", "blocked": blocked, "attempts": [{"attempt": 0, "blocked": blocked}], "seconds": seconds}
    return {
        "config": "A3",
        "attempts": [{"attempt": i, "errors": e, "executed": not e} for i, e in enumerate(errors_per_attempt)],
        "seconds": seconds,
    }


def test_counts_clean_repaired_and_failed():
    summary = summarise([
        trace([[]]),                                             # clean first try
        trace([["G4 vocabulary: pv:x does not exist."], []]),    # repaired successfully
        trace([["G2 syntax: boom"], ["G2 syntax: boom"], ["G2 syntax: boom"]]),  # never fixed
    ])
    assert summary["questions"] == 3
    assert summary["clean_first_try"] == 1
    assert summary["needed_repair"] == 2
    assert summary["repair_succeeded"] == 1
    assert summary["repair_success_rate"] == 0.5
    assert summary["passing_all_guardrails_at_the_end"] == 2
    assert summary["first_failure_by_guardrail"] == {"G4 vocabulary": 1, "G2 syntax": 1}


def test_counts_g1_blocks_and_latency():
    summary = summarise([trace([[]], seconds=2.0), trace([], blocked="G1: DELETE is not allowed")])
    assert summary["g1_blocks"] == 1
    assert summary["seconds_p50"] > 0


def test_empty_traces_do_not_crash():
    assert summarise([]) == {}


def test_report_is_valid_json(tmp_path: Path):
    """The report must be machine-readable: results/ is committed and read by report.py."""
    assert json.dumps(summarise([trace([[]])]))
