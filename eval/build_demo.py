"""Build the data for the demo page: schema map, saved questions, and a small graph per question.

Everything is baked in here so the page needs no server and no model. It shows what the
system actually produced on the held-back test questions.

Never embeds reference answers: only our own query, our own result, and the score the
official client gave it.

    uv run --group eval python eval/build_demo.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from g2s.guardrails import INSTANCES, iris_in
from g2s.schema import VOCAB, short
from g2s.sparql import STARTUP_TIMEOUT, QueryError, run, select

RUN = Path("results/A3/test/run1")
TRACES = Path("results/traces.jsonl")
OUT = Path("docs/demo_data.json")
MAX_EDGES = 28  # a picture stops being readable past roughly this many


def schema() -> dict:
    """The 13 classes and 30 properties, as the picture of the domain."""
    classes = select(
        """PREFIX owl: <http://www.w3.org/2002/07/owl#>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           SELECT ?cls ?label ?comment (COUNT(?i) AS ?n) WHERE {
             ?cls a owl:Class OPTIONAL { ?cls rdfs:label ?label }
             OPTIONAL { ?cls rdfs:comment ?comment } OPTIONAL { ?i a ?cls }
           } GROUP BY ?cls ?label ?comment ORDER BY DESC(?n)""",
        timeout=STARTUP_TIMEOUT,
    )
    properties = select(
        """PREFIX owl: <http://www.w3.org/2002/07/owl#>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           SELECT ?p ?domain ?range WHERE {
             VALUES ?k { owl:ObjectProperty owl:DatatypeProperty } ?p a ?k
             OPTIONAL { ?p rdfs:domain ?domain } OPTIONAL { ?p rdfs:range ?range }
           } ORDER BY ?p""",
        timeout=STARTUP_TIMEOUT,
    )
    return {
        "classes": [
            {
                "id": short(c["cls"]),
                "label": c.get("label", short(c["cls"])),
                "comment": c.get("comment", ""),
                "instances": int(c.get("n", 0)),
            }
            for c in classes
            if c["cls"].startswith(VOCAB)
        ],
        "properties": [
            {
                "id": short(p["p"]),
                "from": short(p.get("domain", "?")),
                "to": short(p.get("range", "?")),
                "object": p.get("range", "").startswith(VOCAB) or "dbpedia" in p.get("range", ""),
            }
            for p in properties
        ],
    }


def label_of(iri: str) -> str:
    try:
        rows = select(
            f"""PREFIX pv: <{VOCAB}> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?l WHERE {{ <{iri}> rdfs:label|pv:name ?l }} LIMIT 1"""
        )
    except QueryError:
        return short(iri)
    return rows[0]["l"] if rows else short(iri)


def neighbourhood(iris: list[str]) -> dict:
    """The facts around a handful of resources: what the question is actually about."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def add_node(iri: str, focus: bool = False) -> None:
        if iri not in nodes:
            nodes[iri] = {"id": iri, "label": label_of(iri), "type": "", "focus": focus}
        elif focus:
            nodes[iri]["focus"] = True

    for iri in iris[:6]:
        add_node(iri, focus=True)
        try:
            rows = select(
                f"""PREFIX pv: <{VOCAB}>
                    SELECT ?p ?o ?type WHERE {{
                      <{iri}> ?p ?o . OPTIONAL {{ ?o a ?type }}
                      FILTER(?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
                    }} LIMIT 12"""
            )
            types = select(f"SELECT ?t WHERE {{ <{iri}> a ?t }} LIMIT 1")
        except QueryError:
            continue
        if types:
            nodes[iri]["type"] = short(types[0]["t"])
        for row in rows:
            if len(edges) >= MAX_EDGES:
                break
            target, predicate = row["o"], short(row["p"])
            is_iri = target.startswith("http")
            key = (iri, predicate, target)
            if key in seen:
                continue
            seen.add(key)
            if is_iri:
                add_node(target)
                if row.get("type"):
                    nodes[target]["type"] = short(row["type"])
            else:
                nodes[target] = {"id": target, "label": target[:40], "type": "value", "focus": False}
            edges.append({"from": iri, "to": target, "label": predicate})
    return {"nodes": list(nodes.values()), "edges": edges}


def our_result(query: str) -> tuple[list[str], list[str]]:
    """What our query returns, as plain rows, plus any IRIs in the answer."""
    try:
        result = run(query)
    except QueryError as error:
        return [f"error: {error}"[:160]], []
    if "boolean" in result:
        return [str(result["boolean"])], []
    rows, iris = [], []
    for binding in result["results"]["bindings"][:8]:
        cells = []
        for value in binding.values():
            text = value["value"]
            if text.startswith(INSTANCES):
                iris.append(text)
                text = label_of(text)
            cells.append(text)
        rows.append(" · ".join(cells))
    return rows or ["(no results)"], iris


def main() -> int:
    metrics = json.loads((RUN / "metrics.json").read_text())
    answers = {a["qname"]: a for a in json.loads((RUN / "answers.json").read_text()) if "qname" in a}
    traces = {}
    for line in TRACES.read_text().splitlines():
        record = json.loads(line)
        if record.get("config") == "A3" and record.get("question"):
            traces[record["question"]] = record

    questions = []
    for qname, scores in sorted(answers.items(), key=lambda kv: int(re.search(r"\d+", kv[0]).group())):
        query = answers[qname].get("query", "")
        question = answers[qname].get("question", "")
        trace = traces.get(question, {})
        attempts = trace.get("attempts") or []
        rows, answer_iris = our_result(query)
        focus = [i for i in sorted(iris_in(query)) if i.startswith(INSTANCES)] or answer_iris
        questions.append(
            {
                "id": qname,
                "question": question,
                "query": query.strip(),
                "f1": round(scores.get("set_F", 0.0), 3) if (scores := metrics.get(qname, {})) else 0.0,
                "rows": rows,
                "repairs": max(len(attempts) - 1, 0),
                "checks": [
                    {"attempt": a["attempt"], "errors": a.get("errors") or []} for a in attempts
                ],
                "graph": neighbourhood(focus + answer_iris),
            }
        )
        print(f"  {qname}: {len(questions[-1]['graph']['nodes'])} nodes", file=sys.stderr)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "schema": schema(),
                "questions": questions,
                "scores": {
                    "A0": 0.029, "A1": 0.084, "A2": 0.170, "A3": 0.170,
                },
            },
            indent=1,
        )
    )
    print(f"wrote {OUT}: {len(questions)} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
