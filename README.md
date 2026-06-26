# ci-cd-release-risk-scanner

Production-shaped DevOps and platform engineering project for scoring release risk before
a deployment reaches production.

The scanner turns concrete CI/CD evidence into a release gate decision: changed files,
test failures, coverage delta, dependency updates, recent incidents, rollback history,
change size, and production approvals. It ships as a Python CLI and FastAPI service with
Prometheus metrics, Docker packaging, Kubernetes manifests, Terraform scaffolding, tests,
sample reports, and recruiter-readable documentation.

## Problem

Teams often deploy with incomplete context. A release can look green while still carrying
risk from migration files, dependency updates, production config changes, recent incidents,
or missing approvals. This project creates a deterministic gate that helps decide whether
to approve, require manual review, or block a release.

## Architecture

```mermaid
flowchart LR
    A[Release context JSON] --> B[Risk scanner engine]
    B --> C[Rule findings]
    B --> D[Risk score]
    D --> E[approve/manual_review/block]
    C --> F[CLI JSON or Markdown report]
    E --> F
    B --> G[FastAPI /scan]
    G --> H[Prometheus /metrics]
    G --> I[Docker image]
    I --> J[Kubernetes manifests]
    I --> K[AWS ECR and CloudWatch Terraform skeleton]
```

## What It Demonstrates

- CI/CD release gate design
- Deterministic risk scoring suitable for CI
- FastAPI and CLI parity through one shared scanner
- Prometheus counters, gauges, and latency histogram
- Docker, Kubernetes, Terraform, and GitHub Actions template coverage
- Practical DevOps judgment around production approvals, migrations, and rollback risk

## Local Setup

```bash
make setup
```

## Run Checks

```bash
make lint
make test
```

## Generate Sample Reports

```bash
make sample
make sample-markdown
```

The risky sample exits with code `2` because it correctly blocks the release. The Makefile
treats that as expected proof of the gate.

Direct CLI usage:

```bash
release-risk tests/fixtures/risky_release.json --output reports/risky-release.json
release-risk tests/fixtures/risky_release.json --format markdown --output reports/risky-release.md
```

## Run The API

```bash
make run
```

Health:

```bash
curl http://localhost:8080/health
```

Scan:

```bash
curl -X POST http://localhost:8080/scan \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/risky_release.json
```

Metrics:

```bash
curl http://localhost:8080/metrics
```

## Docker

```bash
make docker-build
docker run --rm -p 8080:8080 ci-cd-release-risk-scanner:local
```

Docker Compose:

```bash
docker compose up --build
```

## Kubernetes

```bash
kubectl apply -k infra/k8s
kubectl rollout status deployment/release-risk-scanner
kubectl port-forward service/release-risk-scanner 8080:80
```

The manifests include probes, resource limits, Prometheus scrape annotations, and a
non-root container security context.

## Terraform

`infra/terraform` contains a small AWS deployment skeleton for ECR and CloudWatch logs.

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
```

Local development does not require cloud credentials.

## CI/CD

The GitHub Actions template is stored at `docs/github-actions/ci.yml` because this local
GitHub token does not currently have `workflow` scope. After refreshing the token, copy it
to `.github/workflows/ci.yml`:

```bash
gh auth refresh -h github.com -s workflow
```

## Limitations

- The scoring engine is deterministic and intentionally explainable; it is not a live
  connection to GitHub Actions, Jenkins, Jira, PagerDuty, or Datadog.
- Terraform is a skeleton for deployability, not a full production environment.
- The sample rules should be tuned to a real organization before use in production.

