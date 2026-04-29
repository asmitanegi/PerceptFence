# PerceptFence Paper Pack

Private blind-review-only working pack for the IUI 2027 target.

**Article title:** "Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants"

**Project name:** PerceptFence

**Repo / slide-header form:** PerceptFence — Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants

Do not add public repository links, public demos, author identity, organization identity, real user data, non-synthetic screen captures, secrets, or production telemetry.

## Frozen thesis

Problem statement: “Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.”

What we solve: “A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance.”

Article about: “Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants.”

## Target venue

Primary target: ACM IUI 2027 papers track.

Rationale: the official CFP names intelligent user interfaces for generative AI, privacy and security of IUI, human control in daily automations, multimodal AI assistants, user control and steering of LLMs and agents, and reproducibility/evaluation as in-scope topics. The paper must still earn those claims with synthetic prototype evidence before submission.

## Pack status

- Venue/thesis lock: in progress via `paper/venue-checklist.md`, `paper/non-targets.md`, `paper/abstract.md`, and `docs/figures/slide-1.md`.
- Evaluation status: synthetic smoke path plus bounded per-module ablation diagnostics exist in `eval/results/`; final benchmark and paper-result claims remain planned only.
- Review safety: run the blind-review grep before review handoff.
