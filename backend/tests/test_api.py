import re


CODE_RE = re.compile(r"^0x[0-9A-F]{1,6}[A-Z]{0,2}$")


def test_healthz(client):
    r = client.get("/api/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_generate_returns_valid_payload(client):
    r = client.post("/api/generate", json={})
    assert r.status_code == 200
    body = r.json()
    assert CODE_RE.match(body["code"]), body["code"]
    assert body["severity"] in {"INFO", "WARNING", "ERROR", "CRITICAL", "EXISTENTIAL"}
    assert len(body["title"]) <= 120
    assert len(body["description"]) <= 500
    assert body["seed"]


def test_preview_is_deterministic(client):
    a = client.get("/api/preview/abcd1234").json()
    b = client.get("/api/preview/abcd1234").json()
    assert a == b


def test_severity_override(client):
    r = client.post("/api/generate", json={"severity": "EXISTENTIAL"})
    assert r.status_code == 200
    assert r.json()["severity"] == "EXISTENTIAL"


def test_crud_errors(client):
    gen = client.post("/api/generate", json={}).json()
    payload = {
        "code": gen["code"],
        "title": gen["title"],
        "description": gen["description"],
        "severity": gen["severity"],
        "subsystem": gen["subsystem"],
        "tags": gen.get("tags", []),
        "is_favorite": False,
    }
    r = client.post("/api/errors", json=payload)
    assert r.status_code == 201, r.text
    obj = r.json()
    eid = obj["id"]

    r = client.get(f"/api/errors/{eid}")
    assert r.status_code == 200

    r = client.patch(f"/api/errors/{eid}", json={"is_favorite": True})
    assert r.status_code == 200
    assert r.json()["is_favorite"] is True

    r = client.get("/api/errors", params={"favorite": True})
    assert r.status_code == 200
    assert any(item["id"] == eid for item in r.json()["items"])

    r = client.delete(f"/api/errors/{eid}")
    assert r.status_code == 204

    r = client.get(f"/api/errors/{eid}")
    assert r.status_code == 404


def test_invalid_code_returns_422(client):
    r = client.post("/api/errors", json={
        "code": "not-a-code",
        "title": "x",
        "description": "y",
        "severity": "ERROR",
        "subsystem": "kernel.mood",
    })
    assert r.status_code == 422


def test_stats(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    body = r.json()
    assert "total" in body and "by_severity" in body
