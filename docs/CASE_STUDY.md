# Case Study: CI/CD Release Risk Scanner

## Context

Deployment failures are rarely caused by one obvious signal. Risk usually comes from a
combination of test failures, large change sets, sensitive config changes, migrations,
recent incidents, rollback history, dependency updates, and weak approvals.

## Solution

This project builds a deterministic release gate that converts CI/CD evidence into a
score and decision. The scanner returns `approve`, `manual_review`, or `block` with
specific findings and required actions.

## Implementation

- Shared scanner engine in `src/release_risk_scanner/scanner.py`
- CLI entry point for CI usage
- FastAPI service with `/health`, `/scan`, and `/metrics`
- Prometheus metrics for scan count, latest score, and latency
- JSON and Markdown report output
- Docker image and Compose configuration
- Kubernetes deployment with probes, resource limits, and scrape annotations
- Terraform skeleton for ECR and CloudWatch logs
- Tests for safe/risky releases, CLI behavior, API contract, and Markdown output

## Production-Shaped Behavior

The risky fixture intentionally blocks deployment because it includes failing tests,
security/config changes, a database migration, infrastructure changes, dependency updates,
recent incidents, rollback history, a large change set, and missing production approval.

The safe fixture approves deployment because tests pass, the change set is small, recent
incident history is clean, and production approvals are present.

## Recruiter-Relevant Signals

- CI/CD release gate design
- Production deployment risk analysis
- Python API and CLI implementation
- Test automation and deterministic fixtures
- Docker, Kubernetes, Terraform, and observability fundamentals
- Clear operational writing and release-management judgment

