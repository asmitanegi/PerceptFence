# PerceptFence — IUI 2027 Abstract (canonical)

**Status:** Draft locked from `src/paper/manuscript.md` (Draft 3, 2026-05-03), reconciled with `README.md` and `PROJECT.md` frozen thesis.
**Venue:** ACM IUI 2027 papers track (see `venue-checklist.md`).
**Anonymization:** No author identifiers. This file mirrors what goes into the anonymous PCS submission.
**Last updated:** 2026-05-17 (NEE-199).
**Word target:** Current draft is ~290 words. IUI does not publish a strict abstract word cap; confirm against the PCS submission form before final paste.

## Frozen three-line thesis

- **Problem:** Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.
- **What we solve:** A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance.
- **Contribution:** Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants.

These three lines are mirrored verbatim in `README.md`, `manuscript.md`, and `docs/figures/slide-1.md`. Do not paraphrase here without updating the other three sites in the same change.

## Abstract (anonymous, submission-ready)

Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say. Static chatbot and privacy controls do not close this gap: the sensitive content is in the live capture, not in the prompt, and the assistant needs fast-changing interface context to respond at all. We design and evaluate a runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance, sitting between capture adapters, session memory, and assistant responses. We evaluate the layer on synthetic screen-share scenarios covering secrets, personal data, sensitive speech fragments, screen-visible prompt injection, dense or zoomed interfaces, fast window switching, and three adversarial-evasion classes (Unicode-homoglyph credentials, split or spaced personal-data digits, and role-play / chain-prompt screen instructions), measuring sensitive exposure, false blocks, latency overhead, and task completion against an unmediated prototype baseline. We contribute a bounded design and evaluation of runtime control mechanisms for screen-share assistants; claims remain limited to deterministic synthetic evidence.

## Keywords

privacy, screen-share assistants, runtime mediation, consent, redaction, multimodal AI, prompt injection, evaluation

## Headline numbers (synthetic, 11 fixtures × 200 paired iterations)

- SER baseline → guarded: **1.000 → 0.000** (delta 1.000)
- FBR baseline → guarded: 0.000 → 0.143
- TSR baseline → guarded: 0.091 → 1.000
- Median latency overhead: ~32 µs (p95 ~70 µs, p99 ~78 µs)

Source: `eval/results/baseline_vs_guarded.csv`. The abstract does not quote these numbers verbatim because IUI reviewers see them in the Results section; keeping the abstract phrasing claim-bounded protects against a desk-reject over numeric over-claim.

## Pre-submission checks (before 2026-08-13 AoE)

- Re-run word count against final PCS form word cap.
- Banned-claim grep from `security-threat-model-review.md` §2.1.
- Author-leak grep against gitignored `paper/authors.private.md`.
- Confirm concurrent-submission posture vs. Springer Cybersecurity track (see venue-checklist).
- Diff this abstract against `manuscript.md` §Abstract — strings must match.
