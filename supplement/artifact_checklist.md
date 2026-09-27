# PerceptFence Artifact Checklist

This bundle is Additional file 1 for the PerceptFence manuscript
"PerceptFence: Content-Mediation Architecture and Deterministic Coverage for Screen-Share AI Assistants."
It is a self-contained reproducibility archive. The package builder supplies citation,
licence, and target context for the selected review model.

---

## 1. Provenance

| Item | Value |
|---|---|
| Code license | All rights reserved; review and reproducibility inspection only (`LICENSE`). |
| Data provenance | All fixtures are invented and synthetic. No real screen captures, no real personal data, no real notifications, no production telemetry. |
| Author identity | Supplied or withheld by the package builder according to the selected review model. |
| Repository status during review | Self-contained Additional file; public links are supplied only when the selected review model permits them. |
| Third-party dependencies | Core harness: none. Tests: pytest. Presidio comparison and paper-figure regeneration: optional third-party dependencies. |
| Network access required | Package installation only; no network calls during deterministic evaluation. |

---

## 2. Hardware and runtime

| Item | Value |
|---|---|
| Reference platform | macOS / Linux laptop, 2024-vintage |
| Python version (tested) | 3.12.13; package metadata declares Python 3.10+ |
| External services | None |
| Network calls | None for deterministic evaluation |
| GPU | None |
| Memory ceiling observed | < 50 MB |
| Wall-clock budget | < 30 seconds for full reproducibility set on a laptop |

---

## 3. File inventory

```
PerceptFence_review_artifact/
├── README.md                                  ← reviewer quickstart
├── CITATION.cff                               ← review-model-specific citation file
├── LICENSE                                    ← all-rights-reserved review license
├── pyproject.toml  requirements-eval.txt
├── screenshare_mediator/                      ← fixture-driven reference scaffold
│   ├── __init__.py  models.py  capture.py  policy.py  redaction.py
│   ├── memory.py  output_guard.py  audit.py  runtime.py  fixture_loader.py
├── policies/consent_redaction_policy.json     ← action allow-list
├── data/synthetic/                            ← 11 invented fixtures + index.json
├── eval/
│   ├── smoke_test.py  ablation_study.py  benchmark.py  metrics.md
│   ├── render_figure.py  render_coverage_figure.py  render_architecture_figure.py
│   ├── model_in_loop/                         ← harness and tests; no result snapshots
│   ├── heldout/                               ← census, paired Presidio runner, protocol
│   └── results/*.csv                         ← deterministic evidence only
├── tests/                                     ← 42 unit/integration tests
├── artifact_checklist.md                      ← this file
├── SUPPLEMENT_MANIFEST.md
└── ADDITIONAL_FILE_CHECKSUMS.sha256
```

---

## 4. Reproducibility recipe

The deterministic evaluators use only the Python standard library. Running the
test command requires pytest; reproducing the real Presidio baseline requires
the pinned Presidio/spaCy environment documented in `eval/heldout/PROTOCOL.md`.
Exploratory model snapshots are excluded because submission-grade per-case
prompts, replies, identifiers, and repeated runs were not retained.

### 4.1 Unit tests

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-eval.txt
.venv/bin/python -m pytest tests/ -q
```

**Expected:** `42 passed`. The suite covers fixture-set coverage, runtime-module behaviour (capture, policy, redaction including all four adversarial-evasion paths, memory gate, output guard, audit logger with hash-chain verification), benchmark metric helpers, and the TB3 trust-boundary regression.

### 4.2 Smoke test

```bash
python3 eval/smoke_test.py            # from pack root
PYTHONPATH=. python3 eval/smoke_test.py
```

**Expected tail:**
```
SMOKE PASS: 11 synthetic scenarios validated; 3 runtime mediation paths exercised
```

### 4.3 Per-module ablation diagnostics

```bash
PYTHONPATH=. python3 eval/ablation_study.py --output-dir /tmp/perceptfence-ablation
```

**Expected:** writes the two ablation CSVs under `/tmp/perceptfence-ablation`. The `full_guard` variant achieves expected outcome on 11 of 11 fixtures; the `baseline` variant achieves 0 of 11.

### 4.4 M5 benchmark

```bash
PYTHONPATH=. python3 eval/benchmark.py --output-dir /tmp/perceptfence-benchmark
```

**Expected headline (synthetic, 11 fixtures × 200 paired iterations):**
```
SER baseline -> guarded:  1.000 -> 0.000  (delta 1.000)
FBR baseline -> guarded:  0.000 -> 0.143
TSR baseline -> guarded:  0.091 -> 1.000
```

Writes `/tmp/perceptfence-benchmark/baseline_vs_guarded.csv` (22 data rows = 11 scenario classes × 2 paths). Microsecond-level latency is machine- and run-dependent; the SER, FBR, and TSR columns are deterministic.

### 4.5 M5 figure

```bash
python3 eval/render_figure.py --out /tmp/perceptfence-headline-ser.svg
```

**Expected:** writes `/tmp/perceptfence-headline-ser.svg`, a deterministic stdlib-only SVG rendering of the per-class SER baseline-vs-guarded chart with the headline summary inlined as the subtitle.

---

## 5. Claim-to-evidence mapping

| Manuscript claim pattern | Permitted by | Evidence in this artifact |
|---|---|---|
| "Reduced sensitive exposure" | metrics.md SER | `eval/results/baseline_vs_guarded.csv` SER columns; reproducible with `eval/render_figure.py` |
| "Literal benign-token removal proxy" | metrics.md FBR | `eval/results/baseline_vs_guarded.csv` FBR column; not detector precision |
| "Bounded latency overhead" | metrics.md latency | `baseline_vs_guarded.csv` `median_dt_ms`, `p95_dt_ms`, `p99_dt_ms`, `median_rho`, `p95_rho`, `p99_rho` columns |
| "Structural completion proxy" | metrics.md TSR | `baseline_vs_guarded.csv` output-presence/configured-block column; not a semantic task rubric |
| "Detection of N sensitive-content categories" | metrics.md `DR_k` | `eval/results/per_fixture_ablation.csv` per-class outcomes |
| "Retained audit entries form a valid hash chain" | metrics.md `ALC` | per-fixture audit-event count and `AuditLogger.verify_chain`; no completeness or durability claim |
| "Indirect-disclosure rule path exercised" | metrics.md `IRR` | `OutputGuard._INDIRECT_DISCLOSURE_RE` block path exercised in `eval/results/per_fixture_ablation.csv`; no separate reduction estimate is claimed |

These patterns cover the deterministic artifact claims. Broader architectural and threat-model claims are scoped in the manuscript rather than treated as measured effects.

---

## 6. Public-language confirmation

| Check | Command | Result on this commit |
|---|---|---|
| Banned-claim grep | `rg -n -i -e '\bfirst ever\b' -e '\bformally verified\b' -e '\bprivacy-preserving\b' -e '\bdeployment ready\b' -e '\bproduction ready\b' README.md SUPPLEMENT_MANIFEST.md eval screenshare_mediator tests policies data` | Zero expected hits in reviewer-facing files. |
| Synthetic-data grep | `rg -n -i -e '\breal screen captures\b' -e '\bcustomer data\b' -e '\bproduction telemetry\b' -e '\bhuman subjects?\b' README.md SUPPLEMENT_MANIFEST.md eval screenshare_mediator tests policies data` | Expected only in negative declarations and scope limitations. |

A reviewer can re-run these checks from a fresh clone in seconds. The result should be interpreted with the scope notes above; negative declarations intentionally mention excluded data types.

---

## 7. Threat model summary

The manuscript defines eight adversaries. A1 (malicious screen content) and A5
(temporal exposure) are in scope. A2 (malicious participant via displayed
content) and A4 (assistant output leakage) are partially exercised. A3
(policy-downgrade attempt) is a design assumption, not an evaluated fixture.
A6 (infrastructure compromise), A7 (poisoned model or supply chain), and A8
(operating-system compromise) are excluded. The full decisions and rationales
are in manuscript Table 1; this summary must not be used to widen the claims.

The audit list is **neither crash-evident nor append-only**. Each retained event
carries a SHA-256 link, and `AuditLogger.verify_chain()` detects edits or
reordering among retained entries. It accepts an empty list and a valid
truncated prefix, so it does not prove completeness, durability, or tail
retention.

---

## 8. Known limitations (synthetic scope)

- **Generalization.** Eleven invented fixtures exercise configured categories; they do not estimate effect sizes against real screen-share traffic, real attack distributions, or real user behaviour.
- **Detector ceiling.** The redaction engine is rule-based; a learned detector is a natural extension that composes upstream of the same trust boundaries.
- **Multi-line prompt injection.** The detector is non-DOTALL by design (so detection and per-line redaction agree); cross-line attacks within the configured 100-character window are residual risk.
- **Evaluation-harness sentinel list.** The output guard's literal-fragment denylist is fixture-aware bookkeeping rather than a deployment-grade detector; the indirect-disclosure regex is the generalizable filter.
- **No human-subject study.** Future work that adds a participant study will require an applicable ethics-review path; the current artifact does not invoke any.

---

## 9. Fresh-clone exit test

Runs end-to-end on a fresh extraction with Python ≥ 3.10 and the pinned dependencies:

```bash
cd PerceptFence_review_artifact
python3 -m venv .venv
.venv/bin/pip install -r requirements-eval.txt
.venv/bin/python -m pytest tests/ -q                  # 42 passed
PYTHONPATH=. .venv/bin/python eval/smoke_test.py      # SMOKE PASS
PYTHONPATH=. .venv/bin/python eval/ablation_study.py \
  --output-dir /tmp/perceptfence-ablation             # full_guard 1.000 over 11
PYTHONPATH=. .venv/bin/python eval/benchmark.py \
  --output-dir /tmp/perceptfence-benchmark            # SER 1.000 -> 0.000
```

These commands verify the deterministic core. The paired Presidio runner is
documented in `eval/heldout/PROTOCOL.md`; no model-behavior result is claimed.
If a deterministic step fails on a fresh extraction, that is itself a bug.
