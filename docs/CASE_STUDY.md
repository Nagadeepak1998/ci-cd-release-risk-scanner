# Case Study: CI/CD Release Risk Scanner

## Context

Deployment failures are rarely caused by one obvious signal. Risk usually comes from a
combination of test failures, large change sets, sensitive config changes, migrations,
recent incidents, rollback history, dependency updates, and weak approvals.

## Solution

This project builds deterministic release gates that convert CI/CD evidence into a
score and decision. The pre-release scanner returns `approve`, `manual_review`, or
`block`; the post-deploy evidence review returns `promote`, `watch`, or `rollback`.
Both paths include specific findings, deployment readiness checks, and required actions.
The artifact review adds an `approve`, `manual_review`, or `block` policy decision for
SBOM, provenance, signature, vulnerability, and license evidence.
The change-advisory review adds the same decision model for production change readiness:
freeze windows, CAB approval, business approval, support coverage, rollback rehearsal,
stakeholder notice, runbook, and observability evidence.

## Implementation

- Shared scanner engine in `src/release_risk_scanner/scanner.py`
- CLI entry point for CI usage
- FastAPI service with `/health`, `/scan`, `/evidence`, `/supply-chain`,
  `/change-advisory`, and `/metrics`
- Prometheus metrics for scan count, evidence review count, advisory review count, latest
  scores, and latency
- JSON and Markdown report output
- Deployment readiness checks for rollback plans, monitoring dashboards, and canary rollout
  posture
- Post-deploy evidence scoring for error budget burn, error-rate regression, latency
  regression, synthetic check failures, rollback events, and firing alerts
- Supply-chain artifact policy for SBOM and provenance presence, verified signatures,
  vulnerability severity, and denied licenses
- Change-advisory policy for release-ticket readiness, freeze-window overrides, CAB and
  business approval, support coverage, rollback rehearsal, stakeholder notice, maintenance
  windows, linked incidents, runbooks, and dashboards
- Docker image and Compose configuration
- Kubernetes deployment with probes, resource limits, and scrape annotations
- Terraform skeleton for ECR and CloudWatch logs
- Tests for safe/risky releases, CLI behavior, API contract, and Markdown output

## Production-Shaped Behavior

The risky fixture intentionally blocks deployment because it includes failing tests,
security/config changes, a database migration, infrastructure changes, dependency updates,
recent incidents, rollback history, a large change set, missing production approval,
missing rollback and monitoring references, and an off-hours rollout without canary.

The safe fixture approves deployment because tests pass, the change set is small, recent
incident history is clean, production approvals are present, and rollback, monitoring, and
canary readiness checks pass.

The healthy evidence fixture promotes deployment after the evidence window because burn
rate, error rate, latency, synthetics, alerts, and rollback events stay within threshold.
The rollback evidence fixture stops promotion because the release was already blocked and
post-deploy evidence shows burn-rate, error-rate, latency, synthetic, alert, and rollback
signals.

The supply-chain fixtures make the policy boundary visible: fully attested and signed
artifacts pass, while an unverified artifact with critical vulnerabilities is blocked and
produces a release-ticket-ready Markdown report.

The change-advisory fixtures add a production-support boundary: a clean catalog release
passes with approvals, support coverage, rollback rehearsal, and observability references;
the checkout release blocks because it is inside a freeze window and lacks CAB approval,
business approval, risk acceptance, support roles, rollback rehearsal, stakeholder notice,
runbook, and dashboard evidence.

## Recruiter-Relevant Signals

- CI/CD release gate design
- Production deployment risk analysis
- Release readiness evidence that maps to real deployment review conversations
- Post-deploy evidence review that maps to canary promotion and rollback decisions
- Software-supply-chain security and artifact promotion policy
- Change-management readiness review for production support credibility
- Python API and CLI implementation
- Test automation and deterministic fixtures
- Docker, Kubernetes, Terraform, and observability fundamentals
- Clear operational writing and release-management judgment
