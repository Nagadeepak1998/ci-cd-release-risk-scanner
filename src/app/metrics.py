from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

SCANS = Counter("release_risk_scans_total", "Release risk scans", ["decision"])
LATEST_SCORE = Gauge("release_risk_latest_score", "Latest release risk score")
LATENCY = Histogram("release_risk_scan_seconds", "Release risk scan latency")

