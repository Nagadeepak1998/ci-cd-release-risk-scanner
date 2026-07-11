from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

SCANS = Counter("release_risk_scans_total", "Release risk scans", ["decision"])
EVIDENCE_REVIEWS = Counter(
    "release_risk_evidence_reviews_total", "Release evidence reviews", ["decision"]
)
SUPPLY_CHAIN_REVIEWS = Counter(
    "release_risk_supply_chain_reviews_total", "Supply-chain evidence reviews", ["decision"]
)
LATEST_SCORE = Gauge("release_risk_latest_score", "Latest release risk score")
LATEST_EVIDENCE_SCORE = Gauge("release_risk_latest_evidence_score", "Latest release evidence score")
LATENCY = Histogram("release_risk_scan_seconds", "Release risk scan latency")
