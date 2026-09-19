"""Fixed dev/test split: 15 dev questions to build on, 35 held back.

Evaluator-only: it reads questions.yml. The pipeline must never import this.
Stratified by query form so dev is not accidentally all easy lookups.
Deterministic (fixed seed) and the result is committed, so every run scores the same set.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import yaml

QUESTIONS = Path("data/ck25/questions.yml")
OUT = Path("eval/split.json")
DEV_SIZE = 15
SEED = 42


def bucket(features: list[str]) -> str:
    """Coarse query form. Order matters most, then aggregation, then ASK, then plain lookups."""
    if "ASK" in features:
        return "ask"
    if {"COUNT", "SUM", "AVG", "MIN", "MAX", "GROUP"} & set(features):
        return "aggregate"
    if "ORDER" in features:
        return "ordered"
    return "plain"


def split(questions: list[dict], dev_size: int = DEV_SIZE, seed: int = SEED) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}
    for question in questions:
        groups.setdefault(bucket(question.get("features", [])), []).append(question["id"])

    rng = random.Random(seed)
    dev: list[int] = []
    # proportional share per bucket, largest bucket first so rounding lands somewhere sensible
    for name in sorted(groups, key=lambda b: -len(groups[b])):
        ids = sorted(groups[name])
        rng.shuffle(ids)
        take = round(dev_size * len(ids) / len(questions))
        dev += ids[:take]
    # fix up rounding against the full pool, still deterministically
    pool = [q["id"] for q in questions if q["id"] not in dev]
    rng.shuffle(pool)
    while len(dev) < dev_size:
        dev.append(pool.pop())
    dev = sorted(dev[:dev_size])
    return {"dev": dev, "test": sorted(q["id"] for q in questions if q["id"] not in dev)}


def write_subset(which: str, destination: str) -> None:
    """A questions file holding only the dev (or test) questions, for the official client."""
    data = yaml.safe_load(QUESTIONS.read_text())
    wanted = set(json.loads(OUT.read_text())[which])
    data["questions"] = [q for q in data["questions"] if q["id"] in wanted]
    Path(destination).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    print(f"{len(data['questions'])} {which} questions -> {destination}")


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "subset":
        write_subset(sys.argv[2], sys.argv[3])
        return 0
    questions = yaml.safe_load(QUESTIONS.read_text())["questions"]
    result = split(questions)
    counts = {b: 0 for b in ("ask", "aggregate", "ordered", "plain")}
    for question in questions:
        if question["id"] in result["dev"]:
            counts[bucket(question.get("features", []))] += 1
    result["seed"], result["dev_forms"] = SEED, counts
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"dev {len(result['dev'])}, test {len(result['test'])}, dev forms {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
