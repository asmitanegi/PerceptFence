# Security and Data Handling

This repository is a synthetic-only research artifact. Its International Journal of Information Security package (declined 2026-09-09) was single-blind; the reusable identity-hidden build remains available for venues that require it.

## Allowed inputs

- Invented screen text, invented speech fragments, invented event timing, and invented notification content.
- Synthetic JSON fixtures under `data/synthetic/`.
- Standard-library Python >= 3.10 for the artifact path.
- Optional evaluation dependencies only for reproducing the Presidio comparison baseline.

## Disallowed inputs

- Real screen captures, microphone audio, notifications, or meeting recordings.
- Production logs, customer data, organizational telemetry, private links, credentials, access tokens, or live user identifiers.
- Employer identity in the single-blind manuscript or any author identity in rendered identity-hidden review output.

## Required gates

Before submission or push:

```bash
python3 tools/verify_submission.py
```

This gate checks test-count traceability, CSV drift, headline-number traceability, unit tests, blind identity leaks, banned claims, and checksum drift. `python3 -m pytest tools/test_build_submission_package.py -q` separately proves both review-model packages.

## Audit log integrity

The runtime audit logger (`screenshare_mediator/audit.py`) records policy and output-guard decisions with a SHA-256 chain. The chain is crash-evident, not a defense against a host attacker with code execution.

## Retention

The synthetic fixture set is the only persistent input the system reads. The prototype audit log is in-process by default; production deployments would need a durable append-only store and a corresponding integrity model.
