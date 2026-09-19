"""The pipeline must never see reference answers.

Three ways they could leak, one test each:
  1. source code reading the answer files,
  2. a reference query (or its class/property hints) reaching a prompt,
  3. queries.ttl being loaded into the store.
"""
import re
from pathlib import Path

import pytest
import yaml

from g2s import pipeline
from g2s.sparql import ENDPOINT, QueryError, run

ROOT = Path(__file__).parents[1]
ANSWER_FILES = ("queries.ttl", "questions.yml", "questions_ck26.yml")
QUESTIONS = ROOT / "data/ck25/questions.yml"


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def test_pipeline_never_references_answer_files():
    """eval/ may read them. src/ and the store loader may not."""
    files = [*(ROOT / "src").rglob("*.py"), ROOT / "scripts" / "load_store.sh"]
    hits = [
        f"{f.relative_to(ROOT)}: {name}"
        for f in files
        if f.is_file()
        for name in ANSWER_FILES
        if name in f.read_text(errors="ignore")
    ]
    assert not hits, hits


def test_store_loads_only_prod_inst():
    script = (ROOT / "scripts" / "load_store.sh").read_text()
    assert set(re.findall(r"[\w-]+\.ttl", script)) == {"prod-inst.ttl"}


def test_get_data_deletes_the_reference_queries():
    assert "rm -f" in (ROOT / "scripts/get_data.sh").read_text()
    assert "queries.ttl" in (ROOT / "scripts/get_data.sh").read_text()


def test_few_shot_examples_use_the_toy_domain_only():
    """The examples teach form, never CK25 content.

    The prefix block in generate.txt does name the CK25 namespace, which is fine:
    the schema is meant to be in the prompt. The worked examples are what must stay clean.
    """
    examples = (ROOT / "src/g2s/prompts/examples_toy.txt").read_text()
    assert "ld.company.org" not in examples
    assert "example.org" in examples  # the toy domain


# --- these need the dataset, which CI downloads; skipped when it is absent ---------

@pytest.fixture(scope="module")
def reference_queries():
    if not QUESTIONS.exists():
        pytest.skip("dataset not downloaded (make data)")
    return yaml.safe_load(QUESTIONS.read_text())["questions"]


def test_no_reference_query_appears_in_any_rendered_prompt(reference_queries, monkeypatch):
    """Render every prompt the pipeline can produce and search it for the answers."""
    monkeypatch.setattr(pipeline, "schema_card", lambda: "SCHEMA CARD")
    monkeypatch.setattr(pipeline, "candidates_block", lambda question: "CANDIDATES")
    question = reference_queries[0]["question"]["en"]
    rendered = [
        pipeline.fill(
            pipeline.prompt("generate"),
            schema="SCHEMA CARD",
            candidates="CANDIDATES",
            examples=pipeline.prompt("examples_toy"),
            question=question,
        ),
        pipeline.fill(
            pipeline.prompt("repair"),
            schema="SCHEMA CARD",
            candidates="CANDIDATES",
            question=question,
            query="SELECT ?x WHERE { ?x ?y ?z }",
            errors="- G4 vocabulary: pv:nope does not exist.",
        ),
        pipeline.fill(pipeline.prompt("extract"), question=question),
    ]
    haystack = normalise(" ".join(rendered))
    for entry in reference_queries:
        body = normalise(entry["query"]["sparql"])
        assert body not in haystack, f"reference query for ck25:{entry['id']} leaked into a prompt"
        # the classes/properties lists are hints towards the answer, and leak just as badly
        for hint in entry.get("classes", []) + entry.get("properties", []):
            assert f"hint {hint}" not in haystack


def test_reference_query_hints_are_not_used_by_the_pipeline():
    """No module under src/ may read the classes/properties hints."""
    sources = " ".join(f.read_text() for f in (ROOT / "src").rglob("*.py"))
    assert "classes" not in sources or "questions" not in sources


def test_store_holds_no_reference_queries():
    """The query catalog has its own vocabulary; none of it may be in the store."""
    try:
        result = run("ASK { ?s ?p ?o FILTER(CONTAINS(STR(?p), 'sparql')) }")
    except QueryError:
        pytest.skip(f"no store at {ENDPOINT}")
    assert result["boolean"] is False
