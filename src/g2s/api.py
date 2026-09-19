"""TEXT2SPARQL contract: GET /?question=...&dataset=... -> {dataset, question, query}."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from g2s import pipeline

# The corporate datasets this system serves. Anything else is rejected.
KNOWN_DATASETS = {
    "https://text2sparql.aksw.org/2025/corporate/",
    "https://text2sparql.aksw.org/2026/corporate/",
}

app = FastAPI(title="guarded-text2sparql")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def ask(question: str, dataset: str) -> dict[str, str]:
    if dataset not in KNOWN_DATASETS:
        raise HTTPException(status_code=400, detail=f"unknown dataset: {dataset}")
    return {"dataset": dataset, "question": question, "query": pipeline.answer(question)}
