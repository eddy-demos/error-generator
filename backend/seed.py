"""Seed the database with templates and vocab from seed_data.json.

Idempotent: if the tables already have rows, this is a no-op.
"""
import json
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Template, Vocab, Severity


def main() -> None:
    Base.metadata.create_all(bind=engine)
    data_path = Path(__file__).parent / "seed_data.json"
    data = json.loads(data_path.read_text())

    db = SessionLocal()
    try:
        if db.query(Template).count() == 0:
            for t in data["templates"]:
                sev = t.get("severity_hint")
                db.add(Template(
                    pattern=t["pattern"],
                    kind=t.get("kind", "title"),
                    severity_hint=Severity(sev) if sev else None,
                    weight=t.get("weight", 1),
                ))
            print(f"Inserted {len(data['templates'])} templates")
        else:
            print("Templates already seeded, skipping")

        if db.query(Vocab).count() == 0:
            count = 0
            for slot, values in data["vocab"].items():
                for v in values:
                    db.add(Vocab(slot=slot, value=v))
                    count += 1
            print(f"Inserted {count} vocab entries")
        else:
            print("Vocab already seeded, skipping")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
