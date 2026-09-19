"""G1-G7: the deterministic checks a generated query must pass before it is returned.

The LLM never decides whether its own output is acceptable. Every failure message is
written to be useful to the repair prompt: what is wrong, and what exists instead.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import get_close_matches

from rdflib.plugins.sparql.parser import parseQuery

from g2s.schema import VOCAB, short
from g2s.sparql import ENDPOINT, STARTUP_TIMEOUT, TIMEOUT, QueryError, run, select

INSTANCES = "http://ld.company.org/prod-instances/"

# G1: anything that writes, deletes, or calls out to another endpoint.
FORBIDDEN = re.compile(
    r"\b(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|ADD|MOVE|COPY|SERVICE)\b", re.IGNORECASE
)
READ_ONLY_START = re.compile(r"(?is)^\s*(?:(?:PREFIX|BASE)\b[^\n]*\n\s*)*(SELECT|ASK)\b")

FIXED_PREFIXES = {
    "pv": VOCAB,
    "prodi": INSTANCES,
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
}

VOCABULARY_QUERY = f"""
SELECT DISTINCT ?term WHERE {{ ?term a ?kind
  FILTER(STRSTARTS(STR(?term), "{VOCAB}")) }}
"""


class Blocked(Exception):
    """G1 failed: not repairable, the query is rejected outright."""


@dataclass
class Store:
    """What the guardrails need from the store. Swapped for fakes in the tests."""

    endpoint: str = ENDPOINT
    vocabulary: set[str] = field(default_factory=set)

    def load_vocabulary(self) -> set[str]:
        if not self.vocabulary:
            self.vocabulary = {
                row["term"] for row in select(VOCABULARY_QUERY, self.endpoint, STARTUP_TIMEOUT)
            }
        return self.vocabulary

    def missing_iris(self, iris: set[str]) -> set[str]:
        """Which of these instance IRIs have no triples at all."""
        if not iris:
            return set()
        values = " ".join(f"<{iri}>" for iri in iris)
        found = {
            row["s"]
            for row in select(
                f"SELECT DISTINCT ?s WHERE {{ VALUES ?s {{ {values} }} {{ ?s ?p ?o }} UNION {{ ?x ?q ?s }} }}",
                self.endpoint,
                STARTUP_TIMEOUT,
            )
        }
        return iris - found

    def execute(self, query: str) -> dict:
        return run(query, self.endpoint, TIMEOUT)


STRING_LITERAL = re.compile(
    r"'''(?:[^\\']|\\.)*'''|\"\"\"(?:[^\\\"]|\\.)*\"\"\"|'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"",
    re.DOTALL,
)
PREFIX_DECLARATION = re.compile(r"(?im)^\s*PREFIX\s+(\w*):\s*<([^>]*)>")
FULL_IRI = re.compile(r"<(https?://[^>\s]+)>")
PREFIXED_NAME = re.compile(r"(?<![\w:<#/])(\w+):([\w.%-]+)")


def code_only(query: str) -> str:
    """The query with string literals and comments blanked out, so scanning it is safe.

    Without this, a label like "pv:NotATerm" inside a FILTER would be read as vocabulary.
    """
    return re.sub(r"#[^\n]*", "", STRING_LITERAL.sub('""', query))


def iris_in(query: str) -> set[str]:
    """Every IRI the query refers to, full or prefixed, expanded using its own declarations."""
    text = code_only(query)
    prefixes = dict(PREFIX_DECLARATION.findall(text))
    # the namespace IRIs in the declarations themselves are not terms the query uses
    iris = set(FULL_IRI.findall(PREFIX_DECLARATION.sub("", text)))
    iris |= {
        prefixes[prefix] + local
        for prefix, local in PREFIXED_NAME.findall(text)
        if prefix in prefixes
    }
    return iris


def g1_read_only(query: str) -> None:
    """Only SELECT and ASK. Update forms and federated calls are rejected, never repaired."""
    if match := FORBIDDEN.search(query):
        raise Blocked(f"G1: {match.group(1).upper()} is not allowed; only read-only SELECT or ASK")
    if not READ_ONLY_START.match(query):
        raise Blocked("G1: query must be a SELECT or an ASK")


def g2_syntax(query: str) -> list[str]:
    try:
        parseQuery(query)
    except Exception as error:  # noqa: BLE001 - rdflib raises several parser types; a guardrail must not crash
        return [f"G2 syntax: {str(error).splitlines()[0][:300]}"]
    return []


def g3_prefixes(query: str) -> tuple[str, list[str]]:
    """Declare any fixed prefix the query uses but forgot. Unknown prefixes are reported."""
    text = code_only(query)
    declared = {p for p, _ in PREFIX_DECLARATION.findall(text)}
    used = {p for p, _ in PREFIXED_NAME.findall(text)}
    missing = {p for p in used - declared if p in FIXED_PREFIXES}
    unknown = {p for p in used - declared if p not in FIXED_PREFIXES}
    if missing:
        header = "\n".join(f"PREFIX {p}: <{FIXED_PREFIXES[p]}>" for p in sorted(missing))
        query = f"{header}\n{query}"
    errors = [f"G3 prefix: '{p}:' is not a known prefix" for p in sorted(unknown)]
    return query, errors


def g4_vocabulary(query: str, store: Store) -> list[str]:
    """Every pv: term must exist in the ontology; suggest the closest ones that do."""
    known = store.load_vocabulary()
    # matched lowercased: the model's mistakes are usually casing or word order
    # (suppliedBy for hasSupplier), which an exact-case comparison misses entirely
    by_lower = {short(term).lower(): short(term) for term in known}
    errors = []
    for iri in sorted(i for i in iris_in(query) if i.startswith(VOCAB)):
        if iri not in known:
            close = get_close_matches(short(iri).lower(), list(by_lower), n=3, cutoff=0.3)
            hint = (
                f" Did you mean {', '.join(by_lower[m] for m in close)}?"
                if close
                else " Use a class or property from the schema above."
            )
            errors.append(f"G4 vocabulary: {short(iri)} does not exist.{hint}")
    return errors


def g5_entities(query: str, store: Store) -> list[str]:
    """Every instance IRI must exist in the store."""
    used = {i for i in iris_in(query) if i.startswith(INSTANCES)}
    return [
        f"G5 entity: <{iri}> is not in the graph. Use only the IRIs given to you."
        for iri in sorted(store.missing_iris(used))
    ]


def g6_execution(query: str, store: Store) -> tuple[dict | None, list[str]]:
    try:
        return store.execute(query), []
    except QueryError as error:
        return None, [f"G6 execution: {error}"]


def g7_plausibility(query: str, result: dict | None) -> list[str]:
    """An empty answer can be correct, so this is a soft signal, capped at one repair."""
    if result is None or "boolean" in result:
        return []
    if re.search(r"(?i)\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", query):
        return []
    if not result.get("results", {}).get("bindings"):
        return ["G7 plausibility: the query is valid but returns nothing. Check entity IRIs and direction of properties."]
    return []


def check(query: str, store: Store) -> tuple[str, list[str], bool]:
    """Run G1-G7. Returns (possibly prefix-fixed query, errors, whether it executed)."""
    g1_read_only(query)  # raises Blocked
    query, errors = g3_prefixes(query)
    if syntax := g2_syntax(query):
        return query, syntax, False
    errors += g4_vocabulary(query, store) + g5_entities(query, store)
    if errors:
        return query, errors, False
    result, execution_errors = g6_execution(query, store)
    return query, execution_errors + g7_plausibility(query, result), result is not None
