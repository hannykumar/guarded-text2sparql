"""error_analysis.py on synthetic results: works before any model has run."""
import json

from eval import error_analysis


def test_only_failures_are_listed_with_their_query_and_guardrail_state(tmp_path):
    run = tmp_path / "A3/test/run1"
    run.mkdir(parents=True)
    (run / "metrics.json").write_text(json.dumps({
        "ck25:1-en": {"set_F": 1.0},
        "ck25:2-en": {"set_F": 0.0},
        "ck25:3-en": {"set_F": 0.5},
        "average": {"set_F": 0.5},
    }))
    (run / "answers.json").write_text(json.dumps([
        {"qname": "ck25:1-en", "question": "fine one", "query": "ASK { ?s ?p ?o }"},
        {"qname": "ck25:2-en", "question": "broken one", "query": "SELECT ?x WHERE { ?x a pv:Nope }"},
        {"qname": "ck25:3-en", "question": "partial one", "query": "SELECT ?x WHERE { ?x a pv:Department }"},
    ]))
    traces = tmp_path / "traces.jsonl"
    traces.write_text(json.dumps({
        "question": "broken one",
        "attempts": [{"attempt": 0, "errors": ["G4 vocabulary: pv:Nope does not exist."]},
                     {"attempt": 1, "errors": ["G4 vocabulary: pv:Nope does not exist."]}],
    }) + "\n")

    error_analysis.main(str(run), str(traces))
    text = (run / "ERRORS.md").read_text()

    assert "ck25:2-en" in text and "ck25:3-en" in text
    assert "ck25:1-en" not in text          # a correct answer is not an error
    assert "pv:Nope does not exist" in text  # the guardrail state is carried over
    assert "**Repairs:** 1" in text
    assert text.count("**Cause:** _________") == 2  # one blank to fill per failure
