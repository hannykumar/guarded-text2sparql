"""The pipeline must never see reference answers: queries.ttl, or questions.yml (queries and class/property hints)."""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
FORBIDDEN = ("queries.ttl", "questions.yml", "questions_ck26.yml")


def test_pipeline_never_references_answer_files():
    files = [*(ROOT / "src").rglob("*.py"), ROOT / "scripts" / "load_store.sh"]
    hits = [
        f"{f.relative_to(ROOT)}: {name}"
        for f in files
        if f.is_file()
        for name in FORBIDDEN
        if name in f.read_text(errors="ignore")
    ]
    assert not hits, hits


def test_store_loads_only_prod_inst():
    script = (ROOT / "scripts" / "load_store.sh").read_text()
    assert set(re.findall(r"[\w-]+\.ttl", script)) == {"prod-inst.ttl"}
