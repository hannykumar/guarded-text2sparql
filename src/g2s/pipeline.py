"""Question in, SPARQL out. The LLM proposes; everything around it is deterministic.

Ablations are switched by config: A0 bare question, A1 + schema card,
A2 + linked entity IRIs, A3 + guardrails and repair (added in the guardrails work item).
"""
from __future__ import annotations

import json
import time
from functools import cache
from pathlib import Path

from g2s import guardrails, linking, schema, trace
from g2s.config import settings
from g2s.llm import chat, extract_sparql

PROMPTS = Path(__file__).parent / "prompts"


@cache
def prompt(name: str) -> str:
    return (PROMPTS / f"{name}.txt").read_text()


def fill(template: str, **values: str) -> str:
    """Placeholder substitution. Not str.format: prompts contain literal { } from SPARQL and JSON."""
    for key, value in values.items():
        template = template.replace("{" + key + "}", value)
    return template


@cache
def schema_card() -> str:
    return schema.build(settings.sparql_endpoint)


@cache
def label_index() -> tuple:
    return tuple(linking.build_index(settings.sparql_endpoint))


def mentions(question: str) -> list[str]:
    """LLM call 1: what in the question has to be looked up. Malformed JSON means no mentions."""
    reply = chat(fill(prompt("extract"), question=question))
    try:
        found = json.loads(reply[reply.index("{") : reply.rindex("}") + 1])["mentions"]
    except (ValueError, KeyError, TypeError):
        return []
    return [m for m in found if isinstance(m, str)][:8]


def candidates_block(question: str) -> str:
    """Deterministic: every mention resolved to IRIs that exist in the store."""
    index = list(label_index())
    lines = []
    for mention in mentions(question):
        for candidate in linking.lookup(mention, index):
            lines.append(f'- "{mention}" -> <{candidate.iri}> ({schema.short(candidate.type)}, {candidate.label})')
    if not lines:
        return ""
    return "Entity IRIs found in the graph (use these exactly, do not invent others):\n" + "\n".join(lines) + "\n"


def generate(question: str) -> str:
    """LLM call 2: the candidate query."""
    filled = fill(
        prompt("generate"),
        schema=schema_card() + "\n" if settings.use_schema else "",
        candidates=candidates_block(question) if settings.use_linking else "",
        examples=prompt("examples_toy") + "\n",
        question=question,
    )
    return extract_sparql(chat(filled))


MAX_REPAIRS = 2  # G8


@cache
def store() -> guardrails.Store:
    return guardrails.Store(settings.sparql_endpoint)


def repair(question: str, query: str, errors: list[str]) -> str:
    """LLM call 3: the model sees its own query and the exact messages the checks produced."""
    filled = fill(
        prompt("repair"),
        schema=schema_card() + "\n" if settings.use_schema else "",
        candidates=candidates_block(question) if settings.use_linking else "",
        question=question,
        query=query,
        errors="\n".join(f"- {e}" for e in errors),
    )
    return extract_sparql(chat(filled))


def answer(question: str) -> str:
    """The whole flow: generate, check, repair at most twice, return the best we have."""
    started = time.perf_counter()
    query = generate(question)
    if not settings.use_guardrails:
        trace.record(question=question, query=query, seconds=round(time.perf_counter() - started, 2))
        return query

    attempts: list[dict] = []
    fallback = query  # the last query that at least parsed, in case nothing passes
    for attempt in range(MAX_REPAIRS + 1):
        try:
            query, errors, executed = guardrails.check(query, store())
        except guardrails.Blocked as blocked:
            # G1: not repairable. Return something harmless rather than a write query.
            attempts.append({"attempt": attempt, "blocked": str(blocked)})
            trace.record(question=question, query="", blocked=str(blocked), attempts=attempts,
                         seconds=round(time.perf_counter() - started, 2))
            return "SELECT ?result WHERE { ?result ?p ?o } LIMIT 0"
        attempts.append({"attempt": attempt, "errors": errors, "executed": executed, "query": query})
        if not errors:
            break
        if executed:
            fallback = query  # ran, but looked implausible (G7): better than a broken query
        elif not any(e.startswith("G2") for e in errors):
            fallback = query
        if attempt == MAX_REPAIRS:
            query = fallback
            break
        query = repair(question, query, errors)

    trace.record(
        question=question,
        query=query,
        attempts=attempts,
        repairs=len(attempts) - 1,
        seconds=round(time.perf_counter() - started, 2),
        schema=settings.use_schema,
        linking=settings.use_linking,
    )
    return query
