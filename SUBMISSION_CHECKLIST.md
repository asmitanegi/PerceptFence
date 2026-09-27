# SUBMISSION_CHECKLIST.md — PerceptFence → submission-staged

> **Status (2026-09-27):** the v0.3 manuscript was submitted to the *International Journal of Information Security* on 2026-09-07 and declined on 2026-09-09 ("results too premature"). v0.4.0 adds the rendered-screen evaluation in response and is posted as a preprint. IJIS-specific instructions below are kept as a record of that submission.

Single, canonical, evidence-backed readiness gate for the Springer Nature *International Journal of Information Security*
(single-blind) submission. Every line carries a **status** and the **command that proves it**.
Re-run the commands on a fresh clone; do not trust this file's PASS marks without reproducing them.

**Authoritative gates:** `python3 tools/verify_submission.py` and `python3 -m pytest tools/test_build_submission_package.py -q`.
**Last verified:** flat-tree layout, 42/42 scientific tests, 3/3 packaging regressions, gate 9/9.

---

## 1. Manuscript (`paper/main.tex`)

| Item | Status | Proof command / evidence |
|---|---|---|
| Single-blind IJIS build available | PASS | `tools/build_submission_package.py --review-model single-anonymous --target international-journal-information-security --journal-name "International Journal of Information Security" --date 2026-09-07` exits 0 |
| Author identity and employer boundary | PASS | packaging regression proves both authors + Independent Researcher + public DOI, with zero Parafin references; legacy blinded build remains identity-free |
| Required sections present (9) | PASS | Introduction, Threat Model, Related Work, Design, Evaluation, Discussion, Limitations, Ethics, Conclusion — `grep -c '\\section{' paper/main.tex` |
| Abstract present | PASS | `\abstract{...}`, 219 words — within Springer's 250-word limit |
| Keywords present | PASS | `grep -n '\\keywords' paper/main.tex` |
| Compiles under Springer `sn-jnl` class | PASS | `tectonic -X compile paper/main.tex --outdir /tmp/perceptfence-build --keep-logs --keep-intermediates` exits 0; class and bibliography style are vendored |
| Review formatting present | PASS | double spacing via `setspace`; continuous line numbers via `lineno`; 43-page A4 PDF verified with `pdfinfo` |

## 2. Source (`screenshare_mediator/`)

| Item | Status | Proof command / evidence |
|---|---|---|
| 8 runtime modules at repo root (no `src/src`) | PASS | `ls screenshare_mediator/*.py` |
| Standard-library only (no third-party imports) | PASS | `grep -rEn '^(import\|from) ' screenshare_mediator/ \| grep -vE 'screenshare_mediator\|^.*(import (os\|sys\|re\|json\|hashlib\|dataclasses\|typing\|pathlib\|base64\|unicodedata\|collections\|enum\|datetime))'` → empty |
| Importable from repo root | PASS | `PYTHONPATH=. python3 -c 'import screenshare_mediator'` |

## 3. Policy (`policies/`, `policy-boundaries.md`)

| Item | Status | Proof command / evidence |
|---|---|---|
| Machine-readable policy present | PASS | `python3 -c 'import json; json.load(open("policies/consent_redaction_policy.json"))'` |
| Per-module enforces / does-not-enforce documented | PASS | `policy-boundaries.md` |

## 4. Evaluation (`eval/`)

| Item | Status | Proof command / evidence |
|---|---|---|
| Unit tests pass (flat layout) | PASS | `python3 -m pytest tests/ -q` → **42 passed** |
| Smoke path reproduces | PASS | `PYTHONPATH=. python3 eval/smoke_test.py` → `SMOKE PASS: 11 synthetic scenarios` |
| Per-module ablation reproduces (deterministic) | PASS | `PYTHONPATH=. python3 eval/ablation_study.py` — recall/SER columns byte-stable |
| Std-lib held-out robustness reproduces unchanged | PASS | `PYTHONPATH=. python3 eval/heldout/sensitivity_and_fullsystem.py` → `delta(overall) = +0.000` |
| Full Presidio held-out (optional) | OPTIONAL | needs `.evalvenv`: `PYTHONPATH=.:eval/heldout .evalvenv/bin/python eval/heldout/run_heldout.py` |
| Headline numbers trace to canonical CSV | PASS | `python3 tools/verify_submission.py` → `headline number trace` PASS |
| Metric definitions frozen | PASS | `eval/metrics.md` |
| Held-out protocol committed before results | PASS | `eval/heldout/PROTOCOL.md`; `git log -- eval/heldout/PROTOCOL.md eval/results/heldout_*.csv` |
| Model-in-the-loop evidence excluded | PASS | Unauditable aggregate snapshots and logs were removed from the release tree. The experimental harness remains fail-closed and is not cited as evidence; a future reportable run must retain per-case prompts/replies, stable model identifiers, adjudication provenance, and repeat runs. See `eval/model_in_loop/README.md`. |

## 5. Tools & gates

| Item | Status | Proof command / evidence |
|---|---|---|
| Pre-submission gate green (9 checks) | PASS | `python3 tools/verify_submission.py` exit 0 |
| Latency CSV copies byte-identical (no stale dupes) | PASS | gate `csv no-stale-dupes` PASS (2 canonical copies: `eval/results/` + `supplement/`) |
| Supplement CSVs byte-match canonical source | PASS | gate `supplement sync` PASS (9 CSVs) |
| Banned-claim gate clean | PASS | gate `banned-term` PASS |
| Checksums match committed manifest | PASS | gate `checksums` PASS (`submission_checksums.sha256`) |
| CI workflow uses flat paths | PASS | `.github/workflows/verify.yml` runs `pytest tests/`, `PYTHONPATH="$PWD"`, then the gate |

## 6. Citations & authorship

| Item | Status | Proof command / evidence |
|---|---|---|
| Both authors on every author-bearing surface | PASS | `CITATION.cff`, `paper/authors_identity.tex`, README BibTeX — Asmita Negi & Neeraj Kumar Singh Beshane; blinded supplement metadata remains anonymous |
| Equal contribution + corresponding author marked | PASS | `\equalcont{...}` + `\author*[1]{...Beshane}` (corresponding); corresponding = Neeraj |
| ORCID — both authors present | PASS | `CITATION.cff` and `paper/authors_identity.tex`: Asmita `0009-0005-7566-9555`; Neeraj `0009-0002-2125-1805` |
| Release dates have distinct meanings | PASS | Public `CITATION.cff` uses Zenodo's UTC publication date `2026-07-10`; blinded supplement metadata and `2026-07-09` filenames retain the independently assembled review-snapshot date and contain no Zenodo link |
| No test-count staleness (count synced to suite) | PASS | `grep -rn '29 passed\|29/29\|29 of' --include='*.md' --include='*.tex' .` → none; manuscript + docs state 42, suite has 42 |

## 7. Supplement (`supplement/`)

| Item | Status | Proof command / evidence |
|---|---|---|
| Manifest present | PASS | `supplement/SUPPLEMENT_MANIFEST.md` |
| CSVs byte-identical to `eval/results/` | PASS | gate `supplement sync` PASS |
| Springer additional-file inventory complete | PASS | manifest includes protocol, synthetic fixtures, 9 CSVs, citation file, checklist, and frozen checksums |

## 8. Claim discipline

| Item | Status | Proof command / evidence |
|---|---|---|
| No unguarded banned claims | PASS | gate `banned-term` PASS; list in `security-threat-model-review.md` §2.1 |
| Headline = like-for-like digit-PII (0.828 vs Presidio 0.183) | PASS | `eval/results/heldout_paired_presidio.csv`, traced by gate |
| Recall deliberately < 1.0, coverage boundary disclosed | PASS | manuscript Limitations + README "Headline" section |
| Synthetic-only scope; no real-world generalization claim | PASS | abstract + Ethics + SECURITY.md |

## 9. Public vs private boundary + human-only final steps

These are **out of scope for this repo** and require a human:

- [ ] Asmita approval of the exact IJIS manuscript, author metadata, declarations, preprint disclosure, and cover letter
- [ ] Copyright / license decision (currently all-rights-reserved; resolve for public release)
- [ ] APC / fee confirmation with the venue
- [ ] Reconfirm title-page identity, author order, corresponding author, and declarations before upload
- [ ] Ensure the cover letter uses the final title and bounded evidence claims
- [ ] Final Snapp upload, system-PDF inspection, and Neeraj's submit click

---

### Decision state: `submission-staged`

The artifact and manuscript are internally self-consistent, reproducible from a
fresh extraction, and pass all 9 automated gates once checksums are frozen. The
IJIS single-blind and legacy blinded source builds are locally verified. Remaining work is author/portal control,
not an untested manuscript build. Acceptance probability is still governed by the
science—novelty, synthetic-only evidence, and limited model coverage—not packaging.
