.PHONY: setup lint test sample sample-markdown run smoke docker-build docker-run clean

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install -e '.[dev]'

lint:
	.venv/bin/ruff check src tests

test:
	.venv/bin/pytest

sample:
	.venv/bin/release-risk tests/fixtures/risky_release.json --output reports/risky-release.json || test $$? -eq 2
	.venv/bin/release-risk tests/fixtures/safe_release.json --output reports/safe-release.json

sample-markdown:
	.venv/bin/release-risk tests/fixtures/risky_release.json --format markdown --output reports/risky-release.md || test $$? -eq 2

run:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080

smoke:
	.venv/bin/python scripts/smoke_api.py

docker-build:
	docker build -f infra/docker/Dockerfile -t ci-cd-release-risk-scanner:local .

docker-run:
	docker run --rm -p 8080:8080 ci-cd-release-risk-scanner:local

clean:
	rm -rf .venv .pytest_cache .ruff_cache src/*.egg-info

