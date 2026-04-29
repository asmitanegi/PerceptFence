# Security and Data Handling

This repository is a **synthetic-only, anonymous-review research artifact** targeting ACM IUI 2027.

## Allowed inputs

- Invented screen text, invented speech fragments, invented event timing, and invented notification content.
- Small JSON fixtures under `src/data/synthetic/` (eleven scenario classes including three adversarial-evasion classes).
- Standard-library Python ≥ 3.10. No model providers, no network calls.

## Disallowed inputs

- Live-session captures (real screens, real microphone audio, real notifications).
- Production logs or exports.
- Real user identifiers, access tokens, credentials, or internal links.
- Author or organization metadata while the submission is under anonymous review.
- Any non-synthetic data of any kind.

## Reporting issues

For the anonymous-review version, record issues in the private review-pack issue tracker. Do not include live data in any report. Do not attach screenshots that include author identity, organization names, or third-party content.

## Blind-review hygiene

Before every push, the project runs:
- A banned-term grep over `paper/`, `eval/metrics.md`, and the pack-root markdown set, drawn from `security-threat-model-review.md` §2.1.
- An author-leak grep that excludes the gitignored `paper/authors.private.md` and looks for author / organization / contact / public-repo identifiers.
- A structural lint over `paper/paper.tex` and `paper/threat-model.tex` (label / ref consistency, balanced environments).

Failures of any of these gates block a push.

## Audit log integrity

The runtime audit logger (`src/src/screenshare_mediator/audit.py`) records each policy and output-guard decision with a SHA-256 hash chained from the previous event. The chain is *crash-evident*: a post-hoc edit to any recorded field is detected by `AuditLogger.verify_chain()`. The chain does **not** defend against an attacker with code-execution access on the host, who can re-chain forgeries; this assumption is recorded as TA7 in the threat model.

## Retention

The synthetic fixture set is the only persistent input the system reads. The audit logger is in-process and append-only; on process exit, recorded events are not flushed to disk by default. Production deployments would replace this with a durable append-only store and would need a corresponding integrity model.

## Disclosure

This artifact is review-only (see `src/LICENSE`). Redistribution, public posting beyond the anonymous review preparation context, or reuse outside that context is not permitted without explicit written permission until the camera-ready window.
