# IUI 2027 Venue Checklist — PerceptFence

**Venue:** ACM IUI 2027 (32nd International Conference on Intelligent User Interfaces), Helsinki, Finland, 2027-02-08 to 2027-02-11.
**Track:** IUI 2027 Papers
**Source:** https://iui.acm.org/2027/call-for-papers/
**Retrieved:** 2026-05-17 by EB1A Case Manager (NEE-199)
**Authoritative ground truth:** the linked CFP page. Re-verify before any submission step; do not act from this checklist alone.

## Key deadlines (AoE)

| Stage | Date (AoE) | Days from 2026-05-17 |
|---|---|---|
| Abstract submission | 2026-08-13 | T-88 |
| Full paper submission | 2026-08-20 | T-95 |
| Initial notifications | 2026-10-29 | — |
| Rebuttal deadline | 2026-11-05 | — |
| Final decisions | 2026-11-26 | — |
| Camera-ready | 2026-12-10 | — |
| Conference dates | 2027-02-08 to 2027-02-11 | — |

All deadlines are Anywhere on Earth (AoE).

## Submission portal

Precision Conference Submission (PCS) Portal: https://new.precisionconference.com/
Path: Submissions → Society "SIGCHI" → Conference "IUI 2027" → Track "IUI 2027 Papers" → Go.

## Anonymization rules (double-blind)

- Author names and affiliations must not appear anywhere in the submission.
- Self-citations must use third person ("Smith et al." not "our previous work").
- Acknowledgements must be anonymized or removed for review.
- Non-compliance is grounds for desk rejection without review.

Local enforcement: `paper/paper.tex` must use `\documentclass[manuscript,review,anonymous]{acmart}`. The de-anonymized `src/paper/cybersecurity_springer/main.tex` is the **non-IUI fallback path** and must not be reused as the IUI source without re-anonymizing.

## GenAI disclosure

A dedicated section before references must disclose all use of GenAI tools across research stages (code, data, writing). LLM-generated text must be clearly marked. Unmarked GenAI use is desk-reject.

## Ethics statement

Submissions with human participants must contextualize ethics review per the author's research environment and comply with the 2021 ACM Publications policy on research involving human participants and subjects. PerceptFence uses only synthetic fixtures and no human-subjects data, so a short statement noting "no human subjects; all inputs are synthetic" is the expected form.

## Concurrent submission policy

If any concurrent or under-review submission is "closely related" (same study, artifact, or dataset), an anonymized version must be included in the concurrent-submissions field. Failure to disclose triggers desk rejection.

**Action item:** the de-anonymized Springer Cybersecurity submission (NEE-245, 2026-05-03) shares the artifact. Before IUI submission, confirm posture: (a) Springer withdrawn pre-IUI, (b) Springer still active and disclosed as anonymized concurrent submission, or (c) IUI deferred to later venue. Neeraj decision required.

## Open access

ACM is 100% Open Access as of 2026-01-01. APCs are waived if the corresponding author is at a participating institution; Parafin's status here is unverified. Do not assume waiver.

## Format

ACM `acmart` document class, manuscript / review / anonymous options for submission. See https://www.acm.org/publications/proceedings-template for the current `acmart` package.

## Submission pack expectations (per PROJECT.md M5)

- `paper/paper.tex` — anonymous acmart source.
- `eval/results/baseline_vs_guarded.csv` — committed (M5 done).
- `docs/figures/headline_ser.svg` — committed (M5 done).
- `supplement/artifact_checklist.md` — committed (M5 done).
- GenAI Usage Disclosure section before references.
- Ethics note (synthetic-fixtures only).
- Anonymized concurrent-submission disclosure for the Springer track if (b) above.

## Pre-submission verification (run before Aug 13)

- Author-leak grep across the review-pack tree against patterns in gitignored `paper/authors.private.md`. Any hit outside that file blocks submission.
- Banned-claim grep across `paper/paper.tex` from `security-threat-model-review.md` §2.1.
- LaTeX compile (or document-class lint if compile tooling absent).
- Re-fetch the IUI 2027 CFP page and diff against this checklist; flag any deadline or rule change.
