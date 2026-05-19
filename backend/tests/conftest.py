import json
import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Use an isolated sqlite file per test session (absolute path to avoid CWD ambiguity)
TEST_DB = BACKEND_DIR / "test_errors.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from app.models import Template, Vocab, Severity  # noqa: E402 — register first
from app.database import Base, engine, SessionLocal  # noqa: E402

# Clean DB before main is imported (so create_app's create_all sees no stale file)
if TEST_DB.exists():
    TEST_DB.unlink()

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    # Tables were created by create_app on import; just ensure they exist.
    Base.metadata.create_all(bind=engine)

    # Seed (only once per session)
    data = json.loads((BACKEND_DIR / "seed_data.json").read_text())
    db = SessionLocal()
    try:
        if db.query(Template).count() > 0:
            yield
            return
        for t in data["templates"]:
            sev = t.get("severity_hint")
            db.add(Template(
                pattern=t["pattern"],
                kind=t.get("kind", "title"),
                severity_hint=Severity(sev) if sev else None,
                weight=t.get("weight", 1),
            ))
        for slot, values in data["vocab"].items():
            for v in values:
                db.add(Vocab(slot=slot, value=v))
        db.commit()
    finally:
        db.close()

    yield

    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    app = create_app()
    return TestClient(app)
