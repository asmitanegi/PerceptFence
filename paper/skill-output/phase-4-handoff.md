# Phase 4 — Enhancement Plan and Refiner-Handoff Packet

**Run date:** 2026-04-26 America/Los_Angeles  
**Scope:** scaffold-mode plan only; stop before section generation, visual generation, final critique, or DOCX generation.

## Enhancement plan

### 1. Restore/normalize project source of truth

- Restore or re-copy the canonical project plan because `PROJECT.md` in the pack currently appears truncated to late milestone text.
- Keep the frozen thesis identical across `README.md`, `paper/abstract.md`, and `docs/figures/slide-1.md` before any section work.
- Keep `paper/authors.private.md` excluded from review materials.

### 2. Close scaffold gaps before Phase 5

- Decide whether to create pack-root `eval/metrics.md` or cross-link to `src/eval/metrics.md` from paper artifacts.
- Integrate the existing detailed `paper/threat-model.md` into a compact table in `paper/paper.tex`.
- Wire `paper/section-scope.md` into the manuscript skeleton so each section has a scope paragraph before prose generation.
- Add the remaining adversarial-evasion fixture class for encoded or role-play screen instructions; homoglyph, split/spaced personal data, mixed-sensitivity, and direct prompt-injection fixtures already exist.
- Keep all benchmark/table/figure work blocked until the 2026-06-07 filing gate or explicit override.

### 3. Evidence-gated Phase 5 readiness conditions

Phase 5 may start only when all of the following exist:

- `eval/results/` with benchmark outputs generated from synthetic fixtures.
- A command log showing unit tests, smoke path, and benchmark command output.
- Blind-review grep output over paper/source/supplement paths.
- Updated venue check if any deadline/format/policy language is quoted in new prose.
- Refiner packet below reviewed and narrowed to the section being polished.

### 4. Child-issue recommendation

Create a child issue for the remaining encoded/role-play evasion fixture plus Phase 5 benchmark wiring rather than hiding it inside prose work. Suggested title: `PerceptFence: add remaining adversarial-evasion fixture and benchmark wiring`.

## Refiner-handoff packet

```json
{
  "handoff_version": "1.0",
  "paper_id": "perceptfence-iui-2027",
  "section_id": "scaffold-pack",
  "section_type": "paper-scaffold",
  "target_venue": "ACM IUI 2027",
  "stage": "scaffold-pre-phase-5",
  "source_format": "markdown-plus-latex-skeleton",
  "editing_mode": "light-polish-only",
  "source_text": "Use existing paper/abstract.md, paper/outline.md, paper/section-scope.md, and paper/paper.tex placeholders only. Do not generate full section prose in the scaffold-mode task.",
  "desired_outcome": "A later refiner may tighten grounded wording without adding metrics, citations, experiment outcomes, or deployment claims.",
  "author_voice": {
    "style": "direct, precise, HCI/systems academic prose",
    "confidence": "bounded; planned language unless evidence files exist",
    "preserve_phrases": [
      "runtime mediation layer",
      "consent, redaction, memory controls, and output safeguards",
      "live multimodal assistance",
      "synthetic screen-share scenarios"
    ],
    "avoid_phrases": [
      "blanket guarantees",
      "absolute prevention claims",
      "exhaustive novelty claims"
    ]
  },
  "allowed_claims": [
    "The project studies a consent-aware runtime mediation layer for live screen-share assistants.",
    "The current artifacts are synthetic-only and scaffold-stage.",
    "The planned evaluation measures sensitive exposure, false blocks, latency overhead, audit-log completeness, and task completion on synthetic fixtures.",
    "The anonymous ACM skeleton and threat-model notes exist in the project pack."
  ],
  "blocked_claims": [
    "Any achieved leakage reduction, false-block rate, latency number, or task-completion result before eval/results exists.",
    "Any real-user or human-subject finding before ethics clearance and study execution.",
    "Any public release, external submission, or author/organization identity disclosure before explicit approval.",
    "Any claim that the system eliminates all leakage or covers all possible screen-share risks."
  ],
  "evidence_bundle": [
    {
      "path": "paper/abstract.md",
      "role": "frozen abstract and thesis text"
    },
    {
      "path": "paper/outline.md",
      "role": "one-page section outline"
    },
    {
      "path": "paper/venue-checklist.md",
      "role": "official IUI 2027 compliance notes, retrieved 2026-04-26"
    },
    {
      "path": "paper/paper.tex",
      "role": "anonymous ACM skeleton"
    },
    {
      "path": "paper/threat-model.md",
      "role": "detailed threat model notes"
    },
    {
      "path": "paper/section-scope.md",
      "role": "per-section scope paragraphs"
    },
    {
      "path": "src/eval/smoke_test.py",
      "role": "offline synthetic smoke path"
    },
    {
      "path": "src/eval/metrics.md",
      "role": "metric definitions; not benchmark results"
    },
    {
      "path": "src/data/synthetic/index.json",
      "role": "synthetic fixture index"
    }
  ],
  "open_gaps": [
    "No eval/results directory or benchmark CSV exists.",
    "Pack-root eval/metrics.md is absent even though src/eval/metrics.md exists.",
    "Dedicated encoded/role-play screen-instruction evasion fixture and benchmark rows are absent; homoglyph and split-PII fixtures exist.",
    "Project-pack PROJECT.md appears truncated and should be restored from canonical source before later milestones.",
    "No figure generated from benchmark data exists.",
    "No blinded supplement/checklist bundle exists."
  ],
  "formatting_constraints": {
    "latex_class": "\\documentclass[manuscript,review,anonymous]{acmart}",
    "word_budget": "<=10000 words target before references/excluded sections",
    "blind_review": "remove author names, affiliations, acknowledgements, public links, organization identifiers, and real data",
    "genai_section": "GenAI Usage Disclosure before references",
    "ethics_note": "synthetic-only note now; ethics-review path required before human-subject work"
  },
  "artifact_links": [
    "paper/skill-output/phase-0-input-analysis.md",
    "paper/skill-output/phase-1-venue-analysis.md",
    "paper/skill-output/phase-2-criteria.md",
    "paper/skill-output/phase-3-gap-analysis.md"
  ],
  "acceptance_checks": [
    "Phase 2 has at least 150 sub-criteria across at least 10 top-level categories.",
    "No unsupported metrics or experiment results are introduced.",
    "Banned claim grep over paper/skill-output has zero hits for the the scaffold-mode task banned terms.",
    "Blind-review grep records no author/organization identifier hits outside authors.private.md.",
    "Phase 5+ generation remains unstarted in this issue."
  ]
}
```

## Do-not-cross lines for a refiner

- Do not add or strengthen numerical results.
- Do not add citations that have not been source-checked.
- Do not convert planned evaluation language into achieved findings.
- Do not add author/organization identity or public repository links.
- Do not soften open gaps into implicit claims.

## Sources

- Editorial handoff contract: `skills/paper-enhancer/reference/editorial-handoff.md`
- IUI 2027 CFP: https://iui.acm.org/2027/call-for-papers/
- ACM author submissions/templates: https://www.acm.org/xpages/publications/authors/submissions
- ACM Policy on Authorship / GenAI disclosure: https://www.acm.org/publications/policies/new-acm-policy-on-authorship
- ACM human-participants policy: https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects
