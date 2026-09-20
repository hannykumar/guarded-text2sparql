"""report.py on synthetic metrics: proves the report works before any model has run."""
import json

import pytest

from eval import report


@pytest.fixture
def results(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "RESULTS", tmp_path)
    monkeypatch.chdir(tmp_path)

    def write(config, split, run, f1, exact_ids):
        path = tmp_path / config / split / f"run{run}"
        path.mkdir(parents=True)
        data = {f"ck25:{i}-en": {"set_F": 1.0 if i in exact_ids else 0.0, "set_P": 1.0, "set_recall": 1.0} for i in range(1, 6)}
        data["average"] = {"set_F": f1, "set_P": f1, "set_recall": f1}
        (path / "metrics.json").write_text(json.dumps(data))

    return write


def test_report_shows_every_config_and_the_range_over_runs(results):
    results("A0", "dev", 1, 0.10, {1})
    results("A3", "dev", 1, 0.40, {1, 2})
    results("A3", "dev", 2, 0.50, {1, 2, 3})
    report.main()
    text = (report.RESULTS / "RESULTS.md").read_text()
    assert "| A0 |" in text and "| A3 |" in text
    assert "0.450 (0.400-0.500)" in text  # mean with range when runs disagree
    assert "0.100" in text  # single run, no range
    assert "### test" not in text  # a split that was never measured is simply absent


def test_diagnostics_table_is_included_when_present(results):
    results("A3", "test", 1, 0.3, {1})
    (report.RESULTS / "diagnostics.json").write_text(json.dumps({
        "A3": {"questions": 35, "clean_first_try": 20, "needed_repair": 15, "repair_succeeded": 9,
               "repair_success_rate": 0.6, "passing_all_guardrails_at_the_end": 29, "g1_blocks": 0,
               "first_failure_by_guardrail": {"G4 vocabulary": 9}, "seconds_p50": 40.0, "seconds_p95": 95.0}
    }))
    report.main()
    text = (report.RESULTS / "RESULTS.md").read_text()
    assert "Guardrail diagnostics" in text
    assert "9 (60%)" in text
    assert "G4 vocabulary" in text


def test_no_results_at_all_still_writes_a_report(results):
    report.main()
    assert "_No measurements yet._" in (report.RESULTS / "RESULTS.md").read_text()
