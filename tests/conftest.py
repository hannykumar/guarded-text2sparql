"""Keep the test suite out of results/: traces from tests are not measurements."""
import pytest

from g2s import trace


@pytest.fixture(autouse=True)
def traces_go_to_a_temporary_file(tmp_path, monkeypatch):
    monkeypatch.setattr(trace, "PATH", tmp_path / "traces.jsonl")
