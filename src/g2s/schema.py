"""Schema card: what the store actually contains, rendered for the prompt.

Built by introspecting the store, never by reading the dataset's own files, so the
LLM only ever sees vocabulary that exists.
"""
from __future__ import annotations

from g2s.sparql import ENDPOINT, select

VOCAB = "http://ld.company.org/prod-vocab/"

CLASSES = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cls ?label ?comment ?parent (COUNT(?i) AS ?instances) WHERE {
  ?cls a owl:Class .
  OPTIONAL { ?cls rdfs:label ?label }
  OPTIONAL { ?cls rdfs:comment ?comment }
  OPTIONAL { ?cls rdfs:subClassOf ?parent }
  OPTIONAL { ?i a ?cls }
} GROUP BY ?cls ?label ?comment ?parent ORDER BY ?cls
"""

PROPERTIES = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?prop ?label ?domain ?range (SAMPLE(?o) AS ?example) WHERE {
  VALUES ?kind { owl:ObjectProperty owl:DatatypeProperty }
  ?prop a ?kind .
  OPTIONAL { ?prop rdfs:label ?label }
  OPTIONAL { ?prop rdfs:domain ?domain }
  OPTIONAL { ?prop rdfs:range ?range }
  OPTIONAL { ?s ?prop ?o }
} GROUP BY ?prop ?label ?domain ?range ORDER BY ?prop
"""


def short(iri: str) -> str:
    """pv:Employee for vocabulary terms, a compact form for anything else."""
    if iri.startswith(VOCAB):
        return "pv:" + iri[len(VOCAB) :]
    if "#" in iri:
        return iri.rsplit("#", 1)[1]
    return iri.rsplit("/", 1)[-1]


def build(endpoint: str = ENDPOINT) -> str:
    """Render the schema card. Called once at startup."""
    lines = [
        "# Schema of the corporate knowledge graph",
        f"PREFIX pv: <{VOCAB}>",
        "",
        "## Classes (with instance counts)",
    ]
    for row in select(CLASSES, endpoint):
        parts = [f"- {short(row['cls'])}"]
        if row.get("label"):
            parts.append(f'"{row["label"]}"')
        if row.get("instances", "0") != "0":
            parts.append(f"({row['instances']} instances)")
        if row.get("parent"):
            parts.append(f"subClassOf {short(row['parent'])}")
        if row.get("comment"):
            parts.append(f"- {row['comment']}")
        lines.append(" ".join(parts))

    lines += ["", "## Properties (domain -> range, example value)"]
    for row in select(PROPERTIES, endpoint):
        arrow = f"{short(row.get('domain', '?'))} -> {short(row.get('range', '?'))}"
        line = f"- {short(row['prop'])} ({arrow})"
        if row.get("label"):
            line += f' "{row["label"]}"'
        if row.get("example"):
            line += f"  e.g. {short(row['example']) if row['example'].startswith('http') else row['example']}"
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    print(build())
