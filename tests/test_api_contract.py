"""The challenge contract: GET /?question=&dataset= returns exactly dataset, question, query.

Runs against a FakeLLM, so it needs no model, no store and no dataset.
"""
import pytest
from fastapi.testclient import TestClient

from g2s import api, pipeline

CK25 = "https://text2sparql.aksw.org/2025/corporate/"
FAKE_QUERY = "SELECT ?result WHERE { ?result a <http://ld.company.org/prod-vocab/Department> }"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(pipeline, "chat", lambda *a, **k: f"```sparql\n{FAKE_QUERY}\n```")
    monkeypatch.setattr(pipeline, "schema_card", lambda: "pv:Department")
    return TestClient(api.app)


def test_response_has_exactly_the_three_contract_keys(client):
    body = client.get("/", params={"question": "Which departments exist?", "dataset": CK25}).json()
    assert set(body) == {"dataset", "question", "query"}
    assert body["dataset"] == CK25
    assert body["question"] == "Which departments exist?"
    assert body["query"] == FAKE_QUERY  # fences stripped


def test_unknown_dataset_is_rejected(client):
    assert client.get("/", params={"question": "x", "dataset": "http://evil.example/"}).status_code == 400


def test_missing_parameters_are_rejected(client):
    assert client.get("/", params={"question": "x"}).status_code == 422


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
