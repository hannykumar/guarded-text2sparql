"""Settings from the environment. The ablations are switched here and nowhere else."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _flag(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_model: str = os.environ.get("LLM_MODEL", "qwen2.5-coder:7b")
    llm_api_key: str = os.environ.get("LLM_API_KEY", "ollama")
    sparql_endpoint: str = os.environ.get("SPARQL_ENDPOINT", "http://localhost:3030/ck/query")
    # ablation switches: A0 none, A1 schema, A2 +linking, A3 +guardrails
    use_schema: bool = _flag("G2S_SCHEMA", True)
    use_linking: bool = _flag("G2S_LINKING", True)
    use_guardrails: bool = _flag("G2S_GUARDRAILS", True)
    config_name: str = os.environ.get("G2S_CONFIG", "A3")


settings = Settings()
