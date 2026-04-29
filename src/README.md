# PerceptFence

**Private / blind-review-only artifact.**

**Article title:** "Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants"

This scaffold is for anonymous review preparation and synthetic smoke testing only. Do not publish it, attach live-session captures, or add identifying author or organization metadata.

## Three-line thesis

Problem statement: "Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say."

What we solve: "A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance."

Article about: "Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants."

## What is included

- `src/` — minimal Python package for loading fixtures and running the synthetic baseline/guarded mediation path.
- `policies/` — local policy definitions used by the smoke test.
- `tests/` — unit tests for fixture coverage and schema checks.
- `eval/` — offline smoke-test and ablation commands plus formal metric definitions in `eval/metrics.md`.
- `data/synthetic/` — synthetic-only scenario fixtures.
- `docs/figures/` — placeholder home for anonymous figures.
- `paper/` — placeholder home for anonymous manuscript materials.

## Synthetic scenario coverage

`data/synthetic/` currently covers eleven classes:

1. terminal secret
2. chat/notification
3. browser PII
4. spoken sensitive fragment
5. prompt injection on screen
6. fast window switching
7. small-font/zoomed UI
8. homoglyph credential
9. split PII
10. mixed sensitivity
11. encoded screen instruction (role-play / chain-prompt evasion)

All fixtures are invented and intentionally small so the full smoke test runs without network access or external data.

## Memory gate scope

The session memory gate uses **mode-a context exclusion** for non-retainable content: once the consent/policy engine chooses `block_memory_write`, the content is removed before the assistant context is built for that turn. This is stronger than telling the assistant to ignore content and stronger than deleting history after the assistant has already seen it.

Limitation: context exclusion does **not** erase information already encoded in an LLM's internal representations from a prior turn. The scaffold's claim is only that excluded synthetic content is absent from the assistant context window for the guarded turn and that each exclusion decision is audit-logged without raw sensitive content.

## Unit tests and offline smoke test

From this directory:

```bash
python3 -m unittest discover -s tests -v
```

Then run the smoke path:

```bash
PYTHONPATH=src python3 eval/smoke_test.py
```

Expected output includes baseline-vs-guarded contrast for terminal redaction, prompt-injection output guarding, and context-exclusion memory gating:

```text
Baseline path: fixture=synthetic-terminal-secret-001 model_context_contains_sentinel=True
Guarded path: fixture=synthetic-terminal-secret-001 action=redact_before_model model_context_contains_sentinel=False audit_events=2
Prompt-injection path: baseline_leaked_instruction=True separate_context_guard_blocked=True output_guard_logged=True
Context-exclusion path: baseline_reproduced_ssn=True guarded_context_contains_ssn=False guarded_output_mentions_phrase=False context_exclusion_logged=True
SMOKE PASS: 11 synthetic scenarios validated; 3 runtime mediation paths exercised
```

The smoke path is intentionally not a benchmark and does not produce final evaluation claims.

Run the per-module ablation from this directory when updating diagnostic measurements:

```bash
PYTHONPATH=src python3 eval/ablation_study.py
```

The ablation writes `eval/results/per_module_ablation.csv` and `eval/results/per_fixture_ablation.csv`. Treat these as bounded synthetic diagnostics, not final paper benchmark claims.
