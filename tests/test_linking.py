"""Linking tests run on a hand-made index, so they need no store and no dataset.

The rows below were written by hand from the graph. They must never be taken from
questions.yml, which holds the reference answers.
"""
import pytest

from g2s.linking import build_index, lookup, normalise
from g2s.schema import build
from g2s.sparql import ENDPOINT, QueryError, run

EMPL = "http://ld.company.org/prod-instances/empl-"
PV = "http://ld.company.org/prod-vocab/"
INDEX = [
    (f"{EMPL}Karen.Brant%40company.org", "Karen Brant", f"{PV}Employee", "karen brant"),
    (f"{EMPL}Karen.Brant%40company.org", "Karen.Brant@company.org", f"{PV}Employee", "karen.brant@company.org"),
    (f"{EMPL}Sylvester.Brant%40company.org", "Sylvester Brant", f"{PV}Employee", "sylvester brant"),
    (f"{EMPL}Heinrich.Hoch%40company.org", "Heinrich Hoch", f"{PV}Employee", "heinrich hoch"),
    ("http://ld.company.org/prod-instances/dept-73191", "Engineering", f"{PV}Department", "engineering"),
]


def test_normalise_drops_titles_and_punctuation():
    assert normalise("Ms. Brant") == "brant"
    assert normalise("  Dr Heinrich   Hoch!") == "heinrich hoch"


def test_full_name_wins_outright():
    top = lookup("Heinrich Hoch", INDEX)[0]
    assert top.iri.endswith("Heinrich.Hoch%40company.org")
    assert top.score == 1.0


def test_surname_finds_every_person_with_that_name():
    """"Ms. Brant" is genuinely ambiguous, so both Brants must survive into the candidates."""
    iris = {c.iri for c in lookup("Ms. Brant", INDEX)}
    assert iris == {f"{EMPL}Karen.Brant%40company.org", f"{EMPL}Sylvester.Brant%40company.org"}


def test_email_is_linkable_and_deduped_per_iri():
    hits = lookup("Karen.Brant@company.org", INDEX)
    assert hits[0].iri == f"{EMPL}Karen.Brant%40company.org"
    assert len({c.iri for c in hits}) == len(hits)  # one entry per resource, not one per label


def test_typo_still_links():
    assert lookup("Engineerng", INDEX)[0].label == "Engineering"


def test_unknown_mention_links_to_nothing():
    assert lookup("Ministry of Silly Walks", INDEX) == []
    assert lookup("   ", INDEX) == []


def test_limit_is_respected():
    assert len(lookup("Brant", INDEX, limit=1)) == 1


# --- live checks: skipped unless the store is up (make store load) -----------------

@pytest.fixture(scope="module")
def live():
    try:
        run("ASK {}")
    except QueryError:
        pytest.skip(f"no store at {ENDPOINT}")


def test_schema_card_covers_the_ontology(live):
    card = build()
    assert "pv:Employee" in card and "pv:memberOf" in card
    assert card.count("\n- ") >= 40  # 13 classes + 30 properties
    assert len(card) < 8000  # stays promptable


def test_real_index_links_ms_brant(live):
    top = lookup("Ms. Brant", build_index())[0]
    assert top.iri == f"{EMPL}Karen.Brant%40company.org" or top.iri.endswith("Brant%40company.org")
