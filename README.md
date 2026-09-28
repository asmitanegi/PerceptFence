# PerceptFence

**PerceptFence: Content-Mediation Architecture and Deterministic Coverage for Screen-Share AI Assistants**

> Public research artifact for a synthetic-only study of runtime mediation in screen-share AI assistants.
> All inputs are synthetic. No real screen captures, no real personal data, no real notifications, no customer data, and no production telemetry are included.

**Start here:** [`PAPER_MAP.md`](PAPER_MAP.md) gives you a five-minute claim/evidence orientation. [`PROJECT_LEARNING_GUIDE.md`](PROJECT_LEARNING_GUIDE.md) then teaches you the architecture, execution path, evaluation, limitations, reproduction flow, and paper-submission path in second person.

---

## Frozen thesis

**Problem.** Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.

**What we build.** A deterministic synthetic-fixture scaffold for a proposed content-layer mediation architecture; it does not integrate live capture, authenticated consent transitions, persistent memory, or an external assistant model.

**Article about.** Evidence-bounded design and synthetic evaluation of content-layer mediation for screen-share assistants.

## Abstract

Live screen-share AI assistants may receive raw screen and speech content, but users have little runtime control over what an assistant may observe, retain, or disclose. PerceptFence proposes a content-layer mediation architecture and releases a deterministic synthetic-fixture scaffold for its content path. The target design has per-modality and per-category consent; the artifact instead routes fixture scenario labels to fixed redaction, memory-gate, output, and in-memory audit actions. It has no live capture, category inference, authenticated re-consent, cross-session state, or external model adapter. The deterministic redaction surface is measured on 9,600 protocol-documented adversarial cases against a separately implemented—but not independent—exposure oracle, a no-normalization matcher, and real Microsoft Presidio. On identical cases from seeds 0–4, split-digit PII recall is 0.828 for PerceptFence and 0.183 for Presidio; outside the target boundary Presidio leads 0.238 to 0.154. The overall 0.398 to 0.260 comparison is therefore indicative only. This is a bounded architecture/evaluation contribution, not evidence of live deployment, formal privacy, novel redaction primitives, or model-behavior robustness.

## Why this exists

A multimodal assistant integrated into a screen-share session sees the same surface the user is explaining by hand: terminals with credentials, browsers with personal data, chat overlays with private notifications, and spoken context that may include sensitive fragments. Static chatbot privacy settings do not cover content that enters through a capture path. PerceptFence decomposes a proposed mediator into *observe*, *retain*, and *say*. The repository implements and measures only the deterministic fixture-driven content path; live adapters and durable session controls remain future work.

## Repository layout

```
PerceptFence/
├── README.md                  ← you are here
├── PAPER_MAP.md               ← five-minute orientation map (read this first)
├── PROJECT_LEARNING_GUIDE.md  ← second-person project and paper learning path
├── SUBMISSION_CHECKLIST.md    ← evidence-backed submission readiness gate
├── LICENSE                    ← all-rights-reserved public artifact license
├── CITATION.cff               ← citation metadata for the public artifact
├── pyproject.toml             ← stdlib-only package + pytest config (Python ≥ 3.10)
├── requirements-eval.txt      ← optional Presidio baseline deps (eval only)
├── policy-boundaries.md       ← per-module enforces / does-not-enforce / trust assumptions
├── security-threat-model-review.md  ← banned-term list + claim-to-metric mapping
├── SECURITY.md                ← allowed/disallowed inputs
├── paper/
│   ├── main.tex               ← manuscript source, blinded by default (\blindtrue)
│   ├── references.bib
│   └── references-audit.md
├── screenshare_mediator/      ← 8 runtime modules + composition
│   ├── __init__.py
│   ├── models.py              ← typed dataclasses across module boundaries
│   ├── capture.py             ← synthetic capture adapter
│   ├── policy.py              ← consent / policy engine
│   ├── redaction.py           ← six-family deterministic redaction
│   ├── memory.py              ← session memory gate (mode-A context exclusion)
│   ├── output_guard.py        ← rule-based filter, isolated policy-only context
│   ├── audit.py               ← in-memory hash-chained event list
│   ├── runtime.py             ← baseline + guarded path composition
│   └── fixture_loader.py      ← offline fixture loading + validation
├── data/synthetic/            ← 11 invented fixtures + index
│   ├── index.json
│   ├── terminal_secret.json
│   ├── chat_notification.json
│   ├── browser_pii.json
│   ├── spoken_sensitive_fragment.json
│   ├── prompt_injection_on_screen.json
│   ├── fast_window_switching.json
│   ├── small_font_zoomed_ui.json
│   ├── homoglyph_credential.json     ← adversarial evasion
│   ├── split_pii.json                 ← adversarial evasion
│   ├── mixed_sensitivity.json
│   └── encoded_screen_instruction.json  ← adversarial evasion
├── policies/
│   ├── consent_redaction_policy.json
│   └── README.md
├── eval/
│   ├── metrics.md             ← formal metric specification (canonical)
│   ├── smoke_test.py          ← fresh-clone smoke entry point
│   ├── ablation_study.py      ← fresh-clone ablation entry point
│   ├── benchmark.py           ← M5 latency micro-benchmark
│   ├── render_figure.py       ← deterministic SVG figure renderer
│   ├── render_dose_response.py
│   ├── heldout/               ← deterministic coverage-census harness
│   │   ├── PROTOCOL.md        ← v1 protocol + disclosed v2 amendment history
│   │   ├── generator.py  oracle.py  taxonomy.py  baselines.py
│   │   ├── run_heldout.py     ← full census (needs .evalvenv for Presidio baseline)
│   │   └── sensitivity_and_fullsystem.py  ← std-lib-only robustness checks
│   └── results/              ← committed result CSVs (mirrored byte-identical in supplement/)
├── tests/
│   ├── test_runtime_modules.py    ← 21 module + integration tests
│   ├── test_synthetic_fixtures.py ← 6 fixture-coverage tests
│   └── test_heldout.py            ← 10 held-out harness tests
├── docs/figures/              ← headline_ser + dose_response figures
├── supplement/               ← uploadable supplement bundle (CSVs + manifest)
├── tools/                    ← verify_submission.py + git hooks
└── .github/workflows/        ← CI: tests + held-out repro + verification gate
```

> The manuscript source ships in `paper/` (blinded by default — `\blindtrue`
> in `main.tex`, so the default build renders no author identity); the canonical
> metric spec, threat model, and policy boundaries live at the repository root.

## Usage — reproducibility quickstart

The reference implementation is **standard-library-only Python ≥ 3.10**. No network, no machine-learning dependencies, no model providers. Every transform is deterministic so runs are bit-exact reproducible from the synthetic fixture set.

### Run the unit tests

The tests are standard-library-only but need a `pytest` runner. The repository's
`.evalvenv` contains the pinned evaluation stack and pytest:

```bash
.evalvenv/bin/python -m pytest tests/ -q
```

Expected: **42 passed** (verified in the release environment on Python 3.12.13). The
implementation imports run on the system interpreter alone; the pinned evaluation and
Presidio dependencies live in `requirements-eval.txt`.

### Run the smoke test

```bash
PYTHONPATH=. python3 eval/smoke_test.py
```

Expected tail:

```
SMOKE PASS: 11 synthetic scenarios validated; 3 runtime mediation paths exercised
```

The smoke path exercises three contrasts: terminal redaction, prompt-injection output guarding, and context-exclusion memory gating, and prints the baseline-vs-guarded result for each.

### Run the per-module ablation

```bash
PYTHONPATH=. python3 eval/ablation_study.py
```

Writes `eval/results/per_module_ablation.csv` and `eval/results/per_fixture_ablation.csv`. These are bounded synthetic diagnostics; see [`eval/metrics.md`](eval/metrics.md) for the formal definitions.

### Run the M5 benchmark

```bash
PYTHONPATH=. python3 eval/benchmark.py        # writes eval/results/baseline_vs_guarded.csv
python3 eval/render_figure.py    # writes docs/figures/headline_ser.svg
```

The benchmark runs 200 paired baseline-vs-guarded iterations per fixture (10 warmup discarded) and reports SER (with surface decomposition), FBR, TSR, and latency overhead per scenario class. The figure renderer is hand-built SVG with no third-party dependency.

Current diagnostic table (committed snapshot):

| Variant | Outcome rate | Ctx exposures | Output exposures | Output blocks | Audit events |
|---|---:|---:|---:|---:|---:|
| baseline | 0.000 | 10 | 10 | 0 | 0 |
| policy_only | 0.000 | 10 | 8 | 0 | 0 |
| redaction_only | 0.909 | 1 | 1 | 0 | 0 |
| memory_gate_only | 0.091 | 9 | 7 | 0 | 0 |
| output_guard_only | 0.000 | 10 | 0 | 10 | 0 |
| audit_log_only | 0.000 | 10 | 8 | 0 | 11 |
| **full_guard** | **1.000** | **0** | **0** | **5** | **23** |

(Eleven fixtures total. The `small_font_zoomed_ui` fixture annotates only a required marker rather than a forbidden fragment, so baseline counts read 10/11.)

## Architecture in one paragraph

The released artifact begins at a typed synthetic fixture, not raw live capture. A hard-coded `scenario_class → action` router emits a `PolicyDecision`; there is no content-category classifier or authenticated consent state machine. The redactor applies six deterministic transform families (plus four rendered-screen families T7–T10 in v0.4) before content reaches a deterministic assistant stub. A per-invocation memory gate can exclude the current turn's context; there is no persistent cross-turn store. The output guard uses isolated policy-only context. The in-memory SHA-256 chain detects edits to retained events but accepts empty or valid truncated prefixes, so it is not append-only, complete, durable, or crash-evident. Four trust boundaries (TB1–TB4) and seven trust assumptions (TA1–TA7) condition every claim.

## Status

| Milestone | State |
|---|---|
| **M0** Venue and thesis lock | ✅ Complete |
| **M1** Threat model and policy boundaries | ✅ Complete |
| **M2** Synthetic fixture set + runtime modules | ✅ Complete (42/42 v0.3 tests; 50/50 with v0.4) |
| **M3** Anonymous paper skeleton + metric specification | ✅ Complete |
| **M4** Smoke path + ablation diagnostics + adversarial-evasion coverage | ✅ Complete (full_guard 11/11 on synthetic diagnostics) |
| **M5** Benchmark, headline figure, deterministic coverage census | ✅ Complete |
| **M6** Rendered-screen evaluation (Chrome + OCR, frozen split, held-out templates) | ✅ Complete (v0.4) |

## v0.4 — rendered-screen evaluation (developer-support use case)

**Use case.** A developer or support engineer shares a screen with an AI assistant to debug a failure. The assistant needs the error text; it should not receive the AWS keys, GitHub/Stripe/Slack/OpenAI tokens, database passwords, private keys, or customer PII that are also on that screen.

**What is measured.** 480 synthetic screens across 8 templates (terminal `env` dump, `.env` editor, CI log, support-console customer record, chat notification, `kubectl` secret YAML, `cat` of an SSH key, notebook with a customer table), each rendered by headless Chrome at 1280×720 in 12 conditions (dark/light × 13/16/20 px × lossless/compressed), then read by Tesseract OCR. Every defense gets the identical OCR text; the unchanged v0.3 exposure oracle decides whether each planted value is still recoverable. Split rules were frozen and hashed before testing ([`eval/screen/PROTOCOL.md`](eval/screen/PROTOCOL.md), [`supplement/screen_eval/FREEZE.sha256`](supplement/screen_eval/FREEZE.sha256)); three of the eight templates were never rendered during development.

| Defense (frozen test split, 968 OCR-surviving payloads) | Neutralised | Rate | Wilson 95% | Benign kept |
|---|---:|---:|---:|---:|
| gitleaks 8.30.1 (default rules) | 173 | 0.179 | 0.156–0.204 | 1.000 |
| naive regex | 373 | 0.385 | 0.355–0.416 | 0.938 |
| PerceptFence v0.3 (as submitted) | 462 | 0.477 | 0.446–0.509 | 0.938 |
| Microsoft Presidio 2.2.359 | 562 | 0.581 | 0.549–0.611 | 0.822 |
| **PerceptFence v0.4** | **889** | **0.918** | 0.899–0.934 | 0.932 |
| PerceptFence v0.4, held-out templates only (423) | 412 | 0.974 | 0.954–0.985 | **0.763** |

**Where it loses.** Presidio is better on person names in free text (0.733 vs 0.492). On held-out templates v0.4 removed the Kubernetes secret name and the SSH host in every occurrence — the objects a support engineer would be asking about — so benign retention there is 0.763. 592 of 1,560 planted values were destroyed by OCR itself and are excluded, not counted as wins. Screens are synthetic HTML, OCR is one engine, and no real user session is involved.

**Reproduce** (needs Google Chrome, `tesseract`, `gitleaks`, and the eval venv):

```bash
eval/screen/py.sh eval/screen/render_ocr.py --split test --out /tmp/ocr-test.jsonl
eval/screen/py.sh eval/screen/score.py --split test --ocr /tmp/ocr-test.jsonl \
  --csv /tmp/test.csv --summary /tmp/test.json
```

Committed outputs: [`supplement/screen_eval/test_summary.json`](supplement/screen_eval/test_summary.json), per-payload [`test_payloads.csv`](supplement/screen_eval/test_payloads.csv). No screenshot or generated credential is committed; values are regenerated from the seed.

## Headline: self-generated deterministic coverage census

The primary deterministic result. A generator produces exactly 9,600 payload-bearing cases (480 × 20 seeds) from a documented evasion taxonomy. Protocol v1 preceded the first results; a disclosed v2 amendment corrected the bidirectional-override operator and regenerated the exact census. A separately implemented exposure oracle scores recoverability, but it shares authorship and some normalization concepts with the defense and is not called independent or categorically stronger. Reproduce with `PYTHONPATH=.:eval/heldout .evalvenv/bin/python eval/heldout/run_heldout.py`. Cross-tool results use identical cases from seeds 0–4; the 20-seed PerceptFence pool is sensitivity only.

| Defense | overall recall | in-coverage | out-of-coverage |
|---|---:|---:|---:|
| `naive` (no normalization) | 0.140 | 0.207 | 0.073 |
| real Microsoft Presidio (`en_core_web_sm`) | 0.260 | 0.294 | **0.238** |
| **PerceptFence** | **0.398** | **0.635** | 0.154 |

Recall is deliberately **below 1.0**. On paired seeds, PerceptFence leads where it targets normalization (homoglyph 0.650, split-digit 0.828, zero-width 0.526) and Presidio leads once cases leave that boundary (0.238 vs 0.154 overall out-of-coverage). Full tables: [`eval/results/heldout_paired_presidio.csv`](eval/results/heldout_paired_presidio.csv), [`heldout_by_family.csv`](eval/results/heldout_by_family.csv), [`heldout_benign_controls.csv`](eval/results/heldout_benign_controls.csv), and [`heldout_dose_response.csv`](eval/results/heldout_dose_response.csv). These are a deterministic generator census, not a sample from a real-world distribution; no confidence intervals, real-world generalization, or model-behavior defense are claimed.

## Secondary: designer-authored configuration-consistency check (11 fixtures × 200 paired iterations)

This ablation is reported as a *consistency* check, **not** robustness: the same author wrote the fixtures, expected outcomes, and rules.

| Metric | Baseline | Guarded | Delta |
|---|---:|---:|---:|
| **SER** (sensitive exposure rate) | **1.000** | **0.000** | −1.000 |
| **FBR** (false block rate) | 0.000 | 0.143 | +0.143 |
| **TSR** (task success rate) | 0.091 | 1.000 | +0.909 |
| Median latency | 2.2 µs | 33.8 µs | +31.6 µs |
| p99 latency | 5.0 µs | 83.2 µs | +78.2 µs |

Per-class breakdown: [`eval/results/baseline_vs_guarded.csv`](eval/results/baseline_vs_guarded.csv). The full_guard 11/11 vs baseline 0/11 expected-outcome result is configuration-consistency on a closed set; it does not estimate effect sizes against unseen attacks. See `supplement/artifact_checklist.md` §8 for the full known-limitations enumeration.

## Claim discipline

The article-title phrase **"for Privacy"** is a motivational goal, not a property claim. Every paper claim maps to a measured metric in `eval/metrics.md`. The banned-term list in `security-threat-model-review.md` §2.1 enumerates phrases (*safe*, *secure*, *privacy-preserving*, *trustworthy*, *prevents leakage*, *first*, standalone *novel*, *verified*, *useful*, *usable*, *comprehensive*, *complete*, *robust* without an adversary and metric, *real-time* without latency bounds) that are deliberately avoided unless backed by a measurement; we run a banned-term grep before every push.

## Threat model summary

The canonical threat model is the eight-adversary table in the manuscript (Threat Model section). **In scope:** A1 malicious screen content / screen-visible prompt injection (primary), A2 malicious meeting participant (partial, via A1/A5 displayed-content fixtures), A3 curious or over-privileged user (design-time policy lock; not exercised by a fixture), A4 assistant output leakage (partial — literal exposure and configured output blocks), and A5 temporal exposure (brief appearance during window switches, popups, zoom, small-font rendering). **Out of scope:** A6 compromised infrastructure, A7 poisoned model / supply chain, and A8 operating-system compromise. Three single points of failure are explicitly named: notification leakage depends on the redaction stage alone, sensitive-speech retention depends on the memory gate alone, and audit incompleteness depends on the audit logger alone. The compact in-paper threat model lives in the manuscript; the full narrative is mirrored in `policy-boundaries.md` and `security-threat-model-review.md`.

## Citation

```bibtex
@misc{negi-singh-perceptfence-2026,
  author = {Negi, Asmita and Beshane, Neeraj Kumar Singh},
  title  = {PerceptFence: Content-Mediation Architecture and Deterministic Coverage for Screen-Share AI Assistants},
  year   = {2026},
  version = {0.4.0},
  doi    = {10.5281/zenodo.23004093},
  url    = {https://doi.org/10.5281/zenodo.23004093},
  note   = {Research artifact and manuscript, v0.4.0 adds the rendered-screen evaluation. Concept DOI: 10.5281/zenodo.21150725.}
}
```

Structured citation metadata lives at `CITATION.cff`. Use concept DOI
`10.5281/zenodo.21150725` when citing the evolving artifact, version DOI
`10.5281/zenodo.23004093` for this v0.4.0 release, and
`10.5281/zenodo.21289219` for the earlier v0.3.0 snapshot.

## License

See `LICENSE`. This is a review-only research scaffold; redistribution outside the review context is not permitted until the camera-ready window.

## Artifact identity and safety note

This public artifact is de-anonymized, and the International Journal of Information Security package (declined 2026-09-09) was single-blind. `CITATION.cff` names both authors as independent researchers: Asmita Negi and Neeraj Kumar Singh Beshane. The package builder still produces an identity-free source and PDF for any future venue that requires double-anonymous review.

The following safety facts hold regardless of route: this repository contains no real screen captures, no real personal data, no real notifications, no customer data, and no production telemetry. Every fixture is synthetic. Banned-term and blind-leak gates run through `tools/verify_submission.py` (also wired into CI via `.github/workflows/` and the local pre-push hook); the claim-to-metric mapping lives in `security-threat-model-review.md`.
