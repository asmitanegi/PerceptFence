# PerceptFence — Project Plan

**Article title:** Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants
**Project name:** PerceptFence
**Primary venue:** ACM IUI 2027 (papers track)
**Submission window:** abstract 2026-08-13 AoE, full paper 2026-08-20 AoE
**Filing gate:** post-2026-06-07 work is unblocked; pre-gate work is bounded by the staging rules below
**Last reviewed:** 2026-04-28

This file is the single canonical project plan. Three-line frozen thesis lives in `README.md`, abstract in `paper/abstract.md`, venue facts in `paper/venue-checklist.md`, threat model in `paper/threat-model.md`, and metric definitions in `src/eval/metrics.md`. Update those source files first, then reflect changes here.

## Frozen thesis

- **Problem:** Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.
- **What we solve:** A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance.
- **Contribution:** Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants.

The wording above is mirrored verbatim across `README.md`, `paper/abstract.md`, and `docs/figures/slide-1.md`. Do not paraphrase without updating all four sites in the same change.

## Staging rules

| Stage | Window | Allowed work | Blocked work |
|---|---|---|---|
| Pre-filing | up to 2026-06-07 | Abstract, outline, section scope, threat model, anonymous ACM skeleton, synthetic fixtures, smoke path, per-module ablation diagnostics, blind-review hygiene, related-work survey | Final benchmark CSV, full Evaluation results prose, generated figures from benchmark data, public submission pack |
| Post-filing | 2026-06-07 onward | M5 work is unblocked: full benchmark, figure generation, results prose, supplement bundle, blinded submission pack | None — venue deadlines apply |
| Submission | 2026-08-13 to 2026-08-20 | PCS upload, GenAI disclosure, ethics note, anonymized supplement | Public repo links, author identity, real data |
| Camera-ready | by 2026-12-10 | De-anonymize, swap real authorship from `paper/authors.private.md`, populate references | n/a |

The pre-filing window's hard rule: do not generate `eval/results/baseline_vs_guarded.csv` or any benchmark figure with achieved-result claims until 2026-06-07 unless the project owner explicitly overrides the gate in writing.

## Milestones

### M0 — Venue and thesis lock

**Goal:** Lock primary venue, frozen thesis wording, and blind-review constraints before any code or paper draft.

**Success criteria:**

- `paper/venue-checklist.md` records IUI 2027 deadlines, format, anonymization, GenAI, ethics, and accessibility requirements with retrieval-dated source citations.
- `paper/non-targets.md` records why UIST 2026, SOUPS 2026, CHI 2027, and NDSS 2027 are not the primary path.
- `paper/title.md` records the chosen title, the project name, and rejected alternatives.
- `paper/abstract.md` and `README.md` contain the frozen three-line thesis verbatim.

**Exit test:** Word-by-word string match of the three-line thesis across `paper/abstract.md`, `README.md`, and `docs/figures/slide-1.md`. Banned-claim grep over `paper/abstract.md` and `paper/outline.md` from `security-threat-model-review.md` §5.

**Status:** Complete.

### M1 — Threat model and policy boundaries

**Goal:** Produce a defendable, scoped threat model and per-module policy boundary document before writing system-design prose.

**Success criteria:**

- `paper/threat-model.md` defines adversaries, trust boundaries, threat catalog, defense-in-depth matrix, trust assumptions, claim guardrails, evaluation mapping, and residual risks.
- `policy-boundaries.md` defines what each module enforces, what it does not enforce, and the underlying trust assumptions.
- `security-threat-model-review.md` enumerates banned terms and the claim-to-metric mapping.

**Exit test:** Every banned term in `security-threat-model-review.md` §2.1 has a corresponding safer phrasing in `paper/threat-model.md` §8 and in `src/eval/metrics.md`. Every threat in `paper/threat-model.md` §4 has a row in §9 mapping it to a metric and a fixture.

**Status:** Complete.

### M2 — Synthetic fixture set and runtime modules

**Goal:** Implement the minimal runnable prototype: capture adapter, consent/policy engine, redaction engine, memory gate, output guard, audit logger, fixture loader.

**Success criteria:**

- `src/src/screenshare_mediator/` contains seven modules with type-annotated dataclasses and rule-based logic; no live capture, no network, no real data.
- `src/data/synthetic/` covers the ten frozen scenario classes: terminal_secret, chat_notification, browser_pii, spoken_sensitive_fragment, prompt_injection_on_screen, fast_window_switching, small_font_zoomed_ui, homoglyph_credential, split_pii, mixed_sensitivity.
- `src/policies/consent_redaction_policy.json` declares the allowed action set used by the policy engine.
- `src/tests/` contains unit tests for each runtime module plus a fixture-coverage test.

**Exit test:** `python3 -m unittest discover -s src/tests -v` reports one or more passing tests per module and confirms the synthetic fixture set covers every expected scenario class.

**Status:** Complete (16/16 tests pass as of 2026-04-28).

### M3 — Anonymous paper skeleton and metric specification

**Goal:** Produce a blind-review-safe paper skeleton, per-section scope paragraphs, and a metric specification before any benchmark generation.

**Success criteria:**

- `paper/paper.tex` uses `\documentclass[manuscript,review,anonymous]{acmart}`, contains anonymous CCS concepts and keywords, and references the threat-model input file.
- `paper/section-scope.md` defines a scope paragraph for every planned section.
- `src/eval/metrics.md` defines sensitive exposure rate (SER), false block rate (FBR), latency overhead, task completion rate (TSR), audit-log completeness, indirect-reference rate, memory-write compliance, and per-evasion-technique detection rate; each metric is mapped to the corresponding claim guardrail.
- `paper/skill-output/` records the four phases of paper-enhancer scaffold-mode analysis: input classification, venue/context, criteria framework with at least 150 sub-criteria, and gap analysis with refiner-handoff packet.

**Exit test:** Frontmatter check on `paper/paper.tex` confirms the LaTeX command and document class. Coverage check confirms every section in `paper/paper.tex` has a matching scope paragraph in `paper/section-scope.md`. Banned-claim grep over `paper/paper.tex` reports zero hits outside guarded contexts.

**Status:** Complete.

### M4 — Smoke path, ablation diagnostics, and adversarial-evasion coverage

**Goal:** A smoke command can run baseline and guarded paths on at least one synthetic scenario without producing final benchmark claims; per-module ablation diagnostics distinguish each module's contribution.

**Success criteria:**

- `eval/smoke_test.py` and `eval/ablation_study.py` are runnable from a fresh clone via `python3 eval/smoke_test.py` and `python3 eval/ablation_study.py`.
- Smoke output exhibits baseline-vs-guarded contrast for terminal redaction, prompt-injection output guarding, and context-exclusion memory gating.
- `eval/results/per_module_ablation.csv` and `eval/results/per_fixture_ablation.csv` enumerate seven module variants (none, policy, redaction, memory_gate, output_guard, audit_log, full_guard) by the ten scenario classes; the files are clearly labeled synthetic diagnostics, not final benchmarks.
- The redaction engine handles the homoglyph, split-PII, and direct prompt-injection adversarial categories. An encoded/role-play screen-instruction adversarial fixture is added with the same coverage discipline.

**Exit test:** Run the unit-test command and the smoke command. Tests must show one passing test per module. Smoke output must show baseline and guarded processing for at least one synthetic scenario. Full benchmark table generation is gated until after 2026-06-07.

**Status:** Largely complete; encoded/role-play instruction fixture is the remaining pre-gate gap.

### M5 — Post-filing benchmark, figure, and blinded submission pack

**Goal of this milestone:** After the 2026-06-07 filing gate, turn the prototype into a reviewable paper pack with evidence-backed claims.

**Success criteria:**

- `eval/results/baseline_vs_guarded.csv` contains sensitive exposure/leakage rate, false block rate, latency overhead, and task success/completion for every synthetic scenario.
- `docs/figures/` contains one figure generated from the benchmark data.
- `paper/paper.tex` uses `\documentclass[manuscript,review,anonymous]{acmart}` and includes placeholders/notes for GenAI Usage Disclosure and ethics handling.
- `supplement/` or `paper/supplement/` contains the blinded artifact checklist and no author/company identifiers.
- Real authorship metadata lives only in `paper/authors.private.md` (gitignored) and is *not* present anywhere in the review pack. Camera-ready swap procedure documented inside that file.

**Exit test:** Run the benchmark and figure-generation commands from a fresh clone. Open the CSV and figure; values must match. Run the blind-review grep from M3 across the final pack. Run the private **author-leak grep** documented in gitignored `paper/authors.private.md` against the review-pack tree before submission; do not copy private author patterns into tracked files.

Any hit outside `paper/authors.private.md` itself is a blocker — the review pack is not blind-safe. Confirm `paper/paper.tex` compiles or, if compilation tooling is not installed, at least lints for the correct document class and required sections.

## Dependencies & risks

- **Agent ownership:** A dedicated Screen-Share AI Paper Lead is needed because existing active agents cover EB1A case management, engineering, and security, but not sustained academic-paper production.
- **Venue drift:** CFP details can change; any plan update after 2026-04-26 must re-check official venue pages before quoting deadlines or rules.
- **Evidence risk:** This paper does not help EB1A if it stays as a vague idea. It needs a measurable artifact, draft, and submission trail.
- **Blind-review risk:** Public links, real data, author identity, or company metadata can invalidate the target venue path.
- **Claim-risk:** The project is safer if claims stay narrow: runtime mediation reduces measured leakage on synthetic scenarios with bounded latency overhead.
- **Time risk:** IUI dates are in August, but EB1A filing pressure is June 7. Pre-filing work is limited to abstract, outline, private skeleton repo, and synthetic prototype smoke path unless Patty explicitly prioritizes more.
- **First-class filing gate:** Post-filing work is blocked through `/NEE/issues/NEE-1248` → `/NEE/issues/NEE-1246` → `/NEE/issues/NEE-1247` → `/NEE/issues/NEE-1245`. Do not close the date blocker before 2026-06-07 unless Patty explicitly overrides; do not start benchmark/table/full-draft work from a status comment alone.
