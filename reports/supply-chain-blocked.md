# Supply Chain Review: checkout-api

- Environment: `production`
- Version: `2026.07.11-2`
- Artifact: `sha256:badc0ffee456`
- Score: `100`
- Decision: `block`

## Findings

- **missing-provenance** (high, +20): Artifact has no build provenance attestation. Evidence: no extra evidence.
- **unverified-signature** (critical, +40): Artifact signature was not verified. Evidence: no extra evidence.
- **critical-vulnerabilities** (critical, +50): Artifact contains critical vulnerabilities. Evidence: critical=1.
- **high-vulnerabilities** (high, +20): Artifact contains high-severity vulnerabilities. Evidence: high=2.
- **denied-licenses** (high, +30): SBOM contains dependencies with denied licenses. Evidence: GPL-3.0-only.

## Required Actions

1. Do not promote this artifact until blocking supply-chain findings are resolved.
1. Sign the artifact and verify the signature against the trusted identity policy.
1. Rebuild with patched dependencies and rerun the vulnerability scan.
