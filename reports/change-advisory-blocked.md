# Change Advisory Review: checkout-api

- Environment: `production`
- Version: `2026.06.26-1`
- Change ticket: `CHG-2026-1043`
- Score: `100`
- Decision: `block`

## Summary

checkout-api 2026.06.26-1 change advisory CHG-2026-1043 is block with advisory score 100.

## Findings

- **pre-release-gate-not-approved** (high, +35): Pre-release risk gate is not approved. Evidence: pre_release_decision=block; pre_release_score=100.
- **freeze-window-active** (critical, +45): Change is scheduled during an active freeze window without emergency override. Evidence: CHG-2026-1043.
- **missing-cab-approval** (high, +20): CAB approval is required but not recorded. Evidence: CHG-2026-1043.
- **missing-business-approval** (medium, +12): Business owner approval is missing. Evidence: no extra evidence.
- **missing-risk-acceptance** (high, +18): High-impact change has no named risk acceptance owner. Evidence: customer_impact=high.
- **missing-support-coverage** (high, +18): On-call engineer and incident commander must both be named. Evidence: no extra evidence.
- **rollback-not-rehearsed** (medium, +12): Rollback has not been rehearsed for this release. Evidence: no extra evidence.
- **missing-stakeholder-notice** (medium, +10): Stakeholder notification has not been sent. Evidence: no extra evidence.
- **short-maintenance-window** (medium, +10): Maintenance window is too short for deploy, validation, and rollback. Evidence: minutes=20.
- **missing-observability-or-runbook** (medium, +12): Change lacks an observability dashboard or runbook reference. Evidence: no extra evidence.
- **recent-related-incidents** (medium, +10): Change is linked to multiple recent incidents. Evidence: INC-9182; INC-9211.

## Required Actions

1. Do not start the change until advisory findings are resolved or explicitly accepted.
1. Move the deployment outside the freeze window or record emergency approval.
1. Name the on-call engineer and incident commander before execution.
1. Run and record a rollback rehearsal before the maintenance window.
