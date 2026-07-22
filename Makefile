.PHONY: setup lint test sample sample-markdown sample-evidence sample-supply-chain sample-change-advisory run smoke docker-build docker-run clean

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install -e '.[dev]'

lint:
	.venv/bin/ruff check src tests

test:
	.venv/bin/pytest

sample:
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli tests/fixtures/risky_release.json --output reports/risky-release.json || test $$? -eq 2
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli tests/fixtures/safe_release.json --output reports/safe-release.json

sample-markdown:
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli tests/fixtures/risky_release.json --format markdown --output reports/risky-release.md || test $$? -eq 2

sample-evidence:
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli --evidence tests/fixtures/healthy_evidence.json --output reports/healthy-evidence.json
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli --evidence tests/fixtures/rollback_evidence.json --format markdown --output reports/rollback-evidence.md --fail-on rollback || test $$? -eq 2

sample-supply-chain:
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli --supply-chain tests/fixtures/supply_chain_safe.json --output reports/supply-chain-safe.json
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli --supply-chain tests/fixtures/supply_chain_blocked.json --format markdown --output reports/supply-chain-blocked.md || test $$? -eq 2

sample-change-advisory:
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli --change-advisory tests/fixtures/change_advisory_safe.json --output reports/change-advisory-safe.json
	PYTHONPATH=src .venv/bin/python -m release_risk_scanner.cli --change-advisory tests/fixtures/change_advisory_blocked.json --format markdown --output reports/change-advisory-blocked.md || test $$? -eq 2

run:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080

smoke:
	PYTHONPATH=src .venv/bin/python scripts/smoke_api.py

docker-build:
	docker build -f infra/docker/Dockerfile -t ci-cd-release-risk-scanner:local .

docker-run:
	docker run --rm -p 8080:8080 ci-cd-release-risk-scanner:local

clean:
	rm -rf .venv .pytest_cache .ruff_cache src/*.egg-info
