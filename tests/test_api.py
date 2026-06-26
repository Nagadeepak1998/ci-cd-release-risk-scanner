import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_api_scan_returns_release_decision() -> None:
    client = TestClient(app)
    payload = json.loads(Path("tests/fixtures/risky_release.json").read_text())

    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    assert response.json()["decision"] == "block"


def test_metrics_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "release_risk_scans_total" in response.text

