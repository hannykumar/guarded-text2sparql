"""Entity linking: question wording -> IRIs that exist in the store.

"Ms. Brant" must become <...empl-Karen.Brant%40company.org>. The LLM cannot guess
that, so code does it: one label index, then exact -> token -> fuzzy matching.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from g2s.schema import short
from g2s.sparql import ENDPOINT, select

TITLES = {"mr", "mrs", "ms", "miss", "dr", "prof", "herr", "frau", "mister"}

INDEX_QUERY = """
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?iri ?text ?type WHERE {
  VALUES ?p { rdfs:label pv:name pv:email }
  ?iri ?p ?text .
  ?iri a ?type .
  # instances only: vocabulary terms are the schema card's job, not the entity index
  FILTER(!STRSTARTS(STR(?iri), "http://ld.company.org/prod-vocab/"))
}
"""


@dataclass(frozen=True)
class Candidate:
    iri: str
    label: str
    type: str
    score: float

    def __str__(self) -> str:
        return f"{self.label} -> <{self.iri}> ({short(self.type)}, score {self.score:.2f})"


def normalise(text: str) -> str:
    """Lowercase, drop honorifics and punctuation, collapse whitespace."""
    words = re.split(r"[^\w@.]+", text.lower())
    kept = [w for w in words if w and w.rstrip(".") not in TITLES]
    return " ".join(kept).strip()


def build_index(endpoint: str = ENDPOINT) -> list[tuple[str, str, str, str]]:
    """(iri, label, type, normalised label) for every named resource. Built once at startup."""
    return [
        (row["iri"], row["text"], row["type"], normalise(row["text"]))
        for row in select(INDEX_QUERY, endpoint)
    ]


def _score(mention: str, label: str) -> float:
    if mention == label:
        return 1.0
    mention_words, label_words = set(mention.split()), set(label.split())
    if mention_words and mention_words <= label_words:
        # "brant" inside "karen brant": a surname or partial name, very likely the one meant
        return 0.9
    return SequenceMatcher(None, mention, label).ratio()


def lookup(
    mention: str,
    index: list[tuple[str, str, str, str]],
    limit: int = 3,
    threshold: float = 0.6,
) -> list[Candidate]:
    """Top candidates for one mention, best first. Empty when nothing is close enough."""
    normalised = normalise(mention)
    if not normalised:
        return []
    best: dict[str, Candidate] = {}
    for iri, label, type_, normalised_label in index:
        score = _score(normalised, normalised_label)
        if score >= threshold and score > best.get(iri, Candidate("", "", "", 0.0)).score:
            best[iri] = Candidate(iri, label, type_, score)
    return sorted(best.values(), key=lambda c: (-c.score, c.label))[:limit]


if __name__ == "__main__":
    index = build_index()
    print(f"{len(index)} indexed names")
    for mention in ("Ms. Brant", "Heinrich Hoch", "Karen.Brant@company.org", "Sales", "Inductor"):
        print(f"\n{mention}:")
        for candidate in lookup(mention, index):
            print(" ", candidate)
