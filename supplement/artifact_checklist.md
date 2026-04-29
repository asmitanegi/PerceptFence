# PerceptFence Artifact Checklist

**Anonymous review — do not include author identity, organization, or public links beyond what is already in this checklist.**

This supplement bundle accompanies the anonymous-review manuscript "Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants." It is intended for IUI 2027 reviewers and (when applicable) artifact-evaluation reviewers.

---

## 1. Provenance

| Item | Value |
|---|---|
| Code license | Review-only research scaffold (`src/LICENSE`) |
| Data provenance | All fixtures are invented and synthetic. No real screen captures, no real personal data, no real notifications, no production telemetry. |
| Author identity | Withheld for double-blind review (lives in gitignored `paper/authors.private.md`) |
| Repository status during review | Public; commit attribution under personal-account email; no organizational identifier visible in the review pack |
| Third-party dependencies | None (Python ≥ 3.10 standard library only) |
| Network access required | None for any reproducibility step |

---

## 2. Hardware and runtime

| Item | Value |
|---|---|
| Reference platform | macOS / Linux laptop, 2024-vintage |
| Python version (tested) | 3.14 (also runs on 3.10+) |
| External services | None |
| Network calls | None |
| GPU | None |
| Memory ceiling observed | < 50 MB |
| Wall-clock budget | < 30 seconds for full reproducibility set on a laptop |

---

## 3. File inventory

```
PerceptFence/
├── README.md                                  ← landing page for reviewers
├── PROJECT.md                                 ← M0–M5 milestones + staging rules
├── CITATION.cff                               ← anonymous citation file
├── LICENSE                                    ← see src/LICENSE
├── SECURITY.md                                ← allowed/disallowed inputs + grep gates
├── supplement/
│   └── artifact_checklist.md                  ← this file
├── policy-boundaries.md                       ← per-module enforces / does-not
├── security-threat-model-review.md            ← banned-term list + claim mapping
├── eval/                                      ← pack-root entry points
│   ├── smoke_test.py
│   ├── ablation_study.py
│   ├── benchmark.py                           ← M5 paired baseline-vs-guarded CSV
│   ├── render_figure.py                       ← M5 stdlib-only SVG renderer
│   ├── metrics.md                             ← canonical metric specification
│   └── results/
│       ├── per_module_ablation.csv            ← per-variant synthetic diagnostics
│       ├── per_fixture_ablation.csv           ← per-variant × per-fixture diagnostics
│       └── baseline_vs_guarded.csv            ← M5 benchmark, per scenario class × path
├── docs/figures/
│   ├── README.md
│   └── headline_ser.svg                       ← M5 headline figure
└── src/                                       ← code artifact (review-pack subtree)
    ├── README.md                              ← reproducibility quickstart
    ├── CITATION.cff
    ├── LICENSE
    ├── SECURITY.md
    ├── pyproject.toml                         ← stdlib-only, requires-python = ">=3.10"
    ├── policies/consent_redaction_policy.json
    ├── data/synthetic/                         ← 11 invented fixtures + index.json
    ├── eval/                                   ← canonical metric spec + entry points
    └── src/screenshare_mediator/               ← 8 runtime modules + composition
```

---

## 4. Reproducibility recipe

Every step uses only the Python standard library. No `pip install` is required.

### 4.1 Unit tests

```bash
cd src
python3 -m pytest tests/ -v
```

**Expected:** `29 passed in ~0.03s`. The suite covers fixture-set coverage, runtime-module behaviour (capture, policy, redaction including all four adversarial-evasion paths, memory gate, output guard, audit logger with hash-chain verification), benchmark metric helpers, and the TB3 trust-boundary regression.

### 4.2 Smoke test

```bash
python3 eval/smoke_test.py            # from pack root
# or, equivalently, from src/:
PYTHONPATH=src python3 eval/smoke_test.py
```

**Expected tail:**
```
SMOKE PASS: 11 synthetic scenarios validated; 3 runtime mediation paths exercised
```

### 4.3 Per-module ablation diagnostics

```bash
python3 eval/ablation_study.py
```

**Expected:** writes `eval/results/per_module_ablation.csv` and `eval/results/per_fixture_ablation.csv`. The `full_guard` variant achieves expected outcome on 11 of 11 fixtures; the `baseline` variant achieves 0 of 11.

### 4.4 M5 benchmark

```bash
python3 eval/benchmark.py
```

**Expected headline (synthetic, 11 fixtures × 200 paired iterations):**
```
SER baseline -> guarded:  1.000 -> 0.000  (delta 1.000)
FBR baseline -> guarded:  0.000 -> 0.143
TSR baseline -> guarded:  0.091 -> 1.000
median latency overhead:  ~32 µs (p95 ~70 µs, p99 ~78 µs)
```

Writes `eval/results/baseline_vs_guarded.csv` (22 data rows = 11 scenario classes × 2 paths). Microsecond-level latency carries run-to-run variance; the SER, FBR, and TSR columns are deterministic.

### 4.5 M5 figure

```bash
python3 eval/render_figure.py
```

**Expected:** writes `docs/figures/headline_ser.svg`, a deterministic stdlib-only SVG rendering of the per-class SER baseline-vs-guarded chart with the headline summary inlined as the subtitle.

---

## 5. Claim-to-evidence mapping

| Manuscript claim pattern | Permitted by | Evidence in this artifact |
|---|---|---|
| "Reduced sensitive exposure" | metrics.md SER | `eval/results/baseline_vs_guarded.csv` SER columns; `docs/figures/headline_ser.svg` |
| "Low false block rate" | metrics.md FBR | `eval/results/baseline_vs_guarded.csv` FBR column |
| "Bounded latency overhead" | metrics.md latency | `baseline_vs_guarded.csv` `median_dt_ms`, `p95_dt_ms`, `p99_dt_ms`, `median_rho`, `p95_rho`, `p99_rho` columns |
| "Maintained task completion" | metrics.md TSR | `baseline_vs_guarded.csv` TSR column |
| "Detection of N sensitive-content categories" | metrics.md `DR_k` | `eval/results/per_fixture_ablation.csv` per-class outcomes |
| "Logged policy decisions for review" | metrics.md `ALC` | per-fixture audit_event_count column in `per_fixture_ablation.csv`; `AuditLogger.verify_chain` returns true on every recorded chain |
| "Reduced indirect disclosure" | metrics.md `IRR` | `OutputGuard._INDIRECT_DISCLOSURE_RE` block path exercised in `eval/results/per_fixture_ablation.csv` |

Every claim in the manuscript maps to one of these patterns. The banned-term list in `security-threat-model-review.md` §2.1 enumerates phrasings deliberately avoided in the prose.

---

## 6. Anonymity confirmation

| Check | Command | Result on this commit |
|---|---|---|
| Author-leak grep | `grep -rinE '<author-name-pattern>' --include="*.md" --include="*.tex" --include="*.py" --include="*.json" --include="*.cff" --include="*.toml" --exclude-dir=.git` excluding `**/authors.private.md`. The pattern set lives in `paper/authors.private.md` (gitignored) and covers author surname variants, organization identifiers, personal-email substrings, and known commit-author handles. | Zero hits |
| Banned-term grep | `grep -inE '(^\|[^-])\b(safe\|secure\|trustworthy\|prevents? leakage\|first.ever\|novel \|verified\|useful\|usable\|comprehensive\|robust)\b'` over README, PROJECT, paper artifacts | Only file-comment hits (e.g., "Anonymous-review safe" in `threat-model.tex` header) |
| Acknowledgements grep | `grep -rinE 'acknowledg\|thanks to\|funded by\|supported by'` excluding `**/*.private.md` | Zero hits |
| Email/URL grep (excluding known venue domains) | `grep -rinE '@[a-z0-9.-]+\.(com\|net\|org\|io\|edu)\|https?://[a-z0-9.-]+'` | Zero hits |

A reviewer can re-run all four greps from a fresh clone in seconds. The commands are also documented inside `PROJECT.md` and `SECURITY.md`.

---

## 7. Threat model summary

Six in-scope adversaries (A1 accidental exposure, A2 screen-visible prompt injection, A3 context confusion, A4 retention overshoot, A5 output leakage, A6 multi-actor cross-channel) and five out-of-scope adversaries (X1 OS-level, X2 malicious provider, X3 side channels, X4 colluding user, X5 cross-session inference) frame nine threats T1–T9. Three single points of failure are explicitly named: T3 (notification leakage) on the redaction stage, T4 (sensitive speech retention) on the memory gate, and T9 (audit incompleteness) on the audit logger.

The audit chain is **crash-evident, not tamper-proof**: each event carries a SHA-256 hash chained from the previous event's hash, and `AuditLogger.verify_chain()` detects any post-hoc edit; an attacker with code-execution access on the host can re-chain forgeries (TA7).

---

## 8. Known limitations (synthetic scope)

- **Generalization.** Eleven invented fixtures cover the categories an IUI reviewer would expect; they do not estimate effect sizes against real screen-share traffic, real attack distributions, or real user behaviour.
- **Detector ceiling.** The redaction engine is rule-based; a learned detector is a natural extension that composes upstream of the same trust boundaries.
- **Multi-line prompt injection.** The detector is non-DOTALL by design (so detection and per-line redaction agree); cross-line attacks within the configured 100-character window are residual risk.
- **Evaluation-harness sentinel list.** The output guard's literal-fragment denylist is fixture-aware bookkeeping rather than a deployment-grade detector; the indirect-disclosure regex is the generalizable filter.
- **No human-subject study.** Future work that adds a participant study will require an applicable ethics-review path; the current artifact does not invoke any.

---

## 9. Fresh-clone exit test (M5)

Runs end-to-end on a fresh clone with only Python ≥ 3.10:

```bash
git clone <anonymous-url>
cd PerceptFence
cd src && python3 -m pytest tests/ -v       # 29 passed
cd .. && python3 eval/smoke_test.py         # SMOKE PASS
python3 eval/ablation_study.py              # full_guard 1.000 over 11
python3 eval/benchmark.py                   # SER 1.000 -> 0.000
python3 eval/render_figure.py               # writes docs/figures/headline_ser.svg
```

No additional setup, no environment variables, no network, no model providers. If any step fails on a fresh clone, that is itself a bug.
