"""G1-G7 on hand-written good and bad queries. No store, no model, no dataset."""
import pytest

from g2s import guardrails as g
from g2s.sparql import QueryError

PV = "http://ld.company.org/prod-vocab/"
PRODI = "http://ld.company.org/prod-instances/"
PREFIXES = f"PREFIX pv: <{PV}>\nPREFIX prodi: <{PRODI}>\n"
KAREN = f"{PRODI}empl-Karen.Brant%40company.org"


class FakeStore(g.Store):
    """Knows two classes, two properties and one employee. Nothing else exists."""

    def __init__(self, result=None, error=None):
        super().__init__(endpoint="fake", vocabulary={f"{PV}{t}" for t in ("Employee", "Department", "memberOf", "name")})
        self.result = result if result is not None else {"results": {"bindings": [{"result": {"value": "x"}}]}}
        self.error = error

    def missing_iris(self, iris):
        return {i for i in iris if i != KAREN}

    def execute(self, query):
        if self.error:
            raise QueryError(self.error)
        return self.result


GOOD = PREFIXES + "SELECT ?result WHERE { <" + KAREN + "> pv:memberOf ?result . ?result a pv:Department }"


# --- G1 read-only: rejected outright, never repaired ------------------------------

@pytest.mark.parametrize(
    "query",
    [
        "DELETE WHERE { ?s ?p ?o }",
        "INSERT DATA { <urn:a> <urn:b> <urn:c> }",
        "DROP GRAPH <urn:g>",
        "LOAD <http://elsewhere/data.ttl>",
        "SELECT * WHERE { SERVICE <http://elsewhere/sparql> { ?s ?p ?o } }",
        "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
    ],
)
def test_g1_blocks_writes_and_federation(query):
    with pytest.raises(g.Blocked):
        g.g1_read_only(query)


@pytest.mark.parametrize("query", [GOOD, PREFIXES + "ASK { <" + KAREN + "> a pv:Employee }"])
def test_g1_allows_select_and_ask(query):
    g.g1_read_only(query)  # must not raise


# --- G2 syntax --------------------------------------------------------------------

def test_g2_accepts_valid_and_reports_invalid():
    assert g.g2_syntax(GOOD) == []
    errors = g.g2_syntax(PREFIXES + "SELECT ?x WHERE { ?x a")
    assert errors and errors[0].startswith("G2 syntax")


# --- G3 prefixes ------------------------------------------------------------------

def test_g3_adds_a_forgotten_prefix():
    """The 7B model omits prefixes constantly, so this auto-fix carries real weight."""
    fixed, errors = g.g3_prefixes("SELECT ?x WHERE { ?x a pv:Department }")
    assert errors == []
    assert fixed.startswith(f"PREFIX pv: <{PV}>")
    assert g.g2_syntax(fixed) == []


def test_g3_reports_an_unknown_prefix():
    _, errors = g.g3_prefixes(PREFIXES + "SELECT ?x WHERE { ?x a zz:Thing }")
    assert errors == ["G3 prefix: 'zz:' is not a known prefix"]


# --- term extraction --------------------------------------------------------------

def test_strings_and_comments_are_not_mistaken_for_terms():
    query = PREFIXES + '# pv:InAComment\nSELECT ?x WHERE { ?x pv:name "pv:InAString" }'
    assert g.iris_in(query) == {f"{PV}name"}


# --- G4 vocabulary ----------------------------------------------------------------

def test_g4_accepts_known_terms():
    assert g.g4_vocabulary(GOOD, FakeStore()) == []


def test_g4_names_the_bad_term_and_suggests_a_real_one():
    errors = g.g4_vocabulary(PREFIXES + "SELECT ?x WHERE { ?x pv:memberOff ?y }", FakeStore())
    assert len(errors) == 1
    assert "pv:memberOff does not exist" in errors[0]
    assert "pv:memberOf" in errors[0]  # the suggestion is what makes the repair work


# --- G5 entity existence ----------------------------------------------------------

def test_g5_accepts_a_real_iri_and_rejects_an_invented_one():
    assert g.g5_entities(GOOD, FakeStore()) == []
    errors = g.g5_entities(PREFIXES + "SELECT ?d WHERE { prodi:empl-Made.Up ?p ?d }", FakeStore())
    assert len(errors) == 1 and "is not in the graph" in errors[0]


# --- G6 execution and G7 plausibility ---------------------------------------------

def test_g6_passes_the_stores_own_message_to_the_repair():
    result, errors = g.g6_execution(GOOD, FakeStore(error="Unresolved prefixed name: pv:zzz"))
    assert result is None
    assert errors == ["G6 execution: Unresolved prefixed name: pv:zzz"]


def test_g7_flags_an_empty_answer_but_not_an_ask_or_a_count():
    empty = {"results": {"bindings": []}}
    assert g.g7_plausibility("SELECT ?x WHERE { ?x a pv:Department }", empty)
    assert g.g7_plausibility("ASK { ?s ?p ?o }", {"boolean": False}) == []
    assert g.g7_plausibility("SELECT (COUNT(?x) AS ?n) WHERE { ?x a pv:Department }", empty) == []


# --- the whole check --------------------------------------------------------------

def test_check_passes_a_good_query_and_keeps_the_prefix_fix():
    query, errors, executed = g.check("SELECT ?result WHERE { <" + KAREN + "> pv:memberOf ?result }", FakeStore())
    assert errors == [] and executed
    assert query.startswith("PREFIX pv:")


def test_check_stops_at_syntax_before_touching_the_store():
    _, errors, executed = g.check(PREFIXES + "SELECT ?x WHERE { ?x a", FakeStore())
    assert not executed and errors[0].startswith("G2 syntax")


# --- regressions found by the first real run --------------------------------------

@pytest.mark.parametrize(
    "query",
    [
        PREFIXES + "SELECT ?result WHERE { ?result a pv:Service }",
        PREFIXES + "SELECT ?service WHERE { ?service a pv:Service ; pv:name ?n }",
        PREFIXES + 'SELECT ?x WHERE { ?x pv:name "DELETE ME" }',
        PREFIXES + "# INSERT is only mentioned in this comment\nSELECT ?x WHERE { ?x a pv:Employee }",
    ],
)
def test_g1_does_not_block_ordinary_names_that_contain_a_keyword(query):
    """pv:Service is a class in this graph. G1 blocked every question about services."""
    g.g1_read_only(query)


def test_g4_lists_the_real_properties_and_mentions_direction():
    """An invented property is often a relation modelled the other way round."""
    errors = g.g4_vocabulary(PREFIXES + "SELECT ?x WHERE { ?x pv:hasProduct ?p }", FakeStore())
    assert len(errors) == 1
    assert "The only properties that exist are" in errors[0]
    assert "pv:memberOf" in errors[0] and "pv:name" in errors[0]
    assert "opposite direction" in errors[0]


def test_g4_does_not_list_properties_for_a_missing_class():
    errors = g.g4_vocabulary(PREFIXES + "SELECT ?x WHERE { ?x a pv:Machine }", FakeStore())
    assert "The only properties that exist are" not in errors[0]


def test_g1_still_blocks_the_real_service_keyword():
    with pytest.raises(g.Blocked):
        g.g1_read_only(PREFIXES + "SELECT * WHERE { SERVICE <http://elsewhere/sparql> { ?s ?p ?o } }")
    with pytest.raises(g.Blocked):
        g.g1_read_only(PREFIXES + "select * where { service <http://elsewhere/sparql> { ?s ?p ?o } }")
