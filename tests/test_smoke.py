"""The whole pipeline with a FakeLLM: no model, no store, no dataset. This is what CI runs."""
from dataclasses import replace

import pytest

from g2s import pipeline
from tests.test_guardrails import KAREN, PREFIXES, FakeStore

GOOD = PREFIXES + f"SELECT ?result WHERE {{ <{KAREN}> pv:memberOf ?result . ?result a pv:Department }}"
BAD_VOCAB = PREFIXES + f"SELECT ?result WHERE {{ <{KAREN}> pv:worksIn ?result }}"
BAD_SYNTAX = PREFIXES + "SELECT ?result WHERE { ?result a"


class FakeLLM:
    """Returns the given replies in order, then repeats the last one."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []

    def __call__(self, prompt, system="", timeout=180):
        self.prompts.append(prompt)
        return self.replies[min(len(self.prompts) - 1, len(self.replies) - 1)]


@pytest.fixture
def wired(monkeypatch):
    monkeypatch.setattr(pipeline, "schema_card", lambda: "pv:Employee pv:memberOf")
    monkeypatch.setattr(pipeline, "candidates_block", lambda question: "")
    monkeypatch.setattr(pipeline, "store", lambda: FakeStore())
    monkeypatch.setattr(pipeline, "settings", replace(pipeline.settings, use_guardrails=True))

    def use(*replies):
        llm = FakeLLM(*replies)
        monkeypatch.setattr(pipeline, "chat", llm)
        return llm

    return use


def test_a_good_query_is_returned_without_any_repair(wired):
    llm = wired(GOOD)
    assert pipeline.answer("In which department is Ms. Brant?") == GOOD
    assert len(llm.prompts) == 1  # generated once, no repair needed


def test_a_bad_property_is_repaired_and_the_error_reaches_the_model(wired):
    llm = wired(BAD_VOCAB, GOOD)
    assert pipeline.answer("In which department is Ms. Brant?") == GOOD
    assert len(llm.prompts) == 2
    assert "pv:worksIn does not exist" in llm.prompts[1]
    assert "pv:memberOf" in llm.prompts[1]  # the suggestion is handed over


def test_repairs_are_capped_at_two(wired):
    """G8: a model that never fixes its query must not loop forever."""
    llm = wired(BAD_VOCAB)
    pipeline.answer("In which department is Ms. Brant?")
    assert len(llm.prompts) == 3  # one generation plus two repairs, then stop


def test_a_write_query_is_never_returned(wired):
    """G1 is a hard stop: the pipeline returns something harmless instead."""
    wired("DELETE WHERE { ?s ?p ?o }")
    result = pipeline.answer("Delete everything")
    assert "DELETE" not in result.upper()


def test_unparseable_output_falls_back_to_a_query_that_at_least_parses(wired):
    llm = wired(BAD_VOCAB, BAD_SYNTAX, BAD_SYNTAX)
    result = pipeline.answer("In which department is Ms. Brant?")
    assert result == BAD_VOCAB  # the last one that parsed, not the broken one
    assert len(llm.prompts) == 3
