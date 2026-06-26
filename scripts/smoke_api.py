from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def main() -> int:
    client = TestClient(app)
    payload = json.loads(Path("tests/fixtures/risky_release.json").read_text(encoding="utf-8"))
    health = client.get("/health")
    scan = client.post("/scan", json=payload)
    metrics = client.get("/metrics")
    if health.status_code != 200 or scan.status_code != 200 or metrics.status_code != 200:
        print("API smoke failed")
        return 1
    body = scan.json()
    print(f"{body['decision']}: score={body['score']} findings={len(body['findings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

