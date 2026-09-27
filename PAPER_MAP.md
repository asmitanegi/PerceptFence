# PAPER_MAP — PerceptFence

> **Status (2026-09-27):** the v0.3 manuscript was submitted to the *International Journal of Information Security* on 2026-09-07 and declined on 2026-09-09 ("results too premature"). v0.4.0 adds the rendered-screen evaluation in response and is posted as a preprint. IJIS-specific instructions below are kept as a record of that submission.

A five-minute orientation to this repository. If you read nothing else, read this file
first. It tells a human author (or a reviewer) what the paper is, what the code does,
what the numbers prove, and — just as importantly — what they are *not* allowed to claim.

**Paper title:** PerceptFence: Content-Mediation Architecture and Deterministic Coverage for Screen-Share AI Assistants
**Artifact:** `screenshare_mediator` — a standard-library-only, synthetic-fixture reference scaffold
**Status:** deterministic core tested; manuscript blinded by default; no live-assistant integration is claimed

---

## 1. What is this paper about?

Live screen-share AI assistants (think an assistant watching your screen during a call)
may receive raw capture content — terminals with credentials, browsers with personal data,
chat pop-ups, or spoken fragments. The paper proposes a **runtime mediation design**
between capture and assistant boundaries. Its released artifact is narrower: fixture
dictionaries enter a deterministic policy/redaction/memory/output scaffold and a string
stub stands in for the assistant. There is no live screen, audio, OCR, network, or
production-model adapter. The evaluation is deterministic and synthetic only.

## 2. What is the exact research question?

> Can a deterministic, rule-based content mediator measurably reduce recoverable
> sensitive-content exposure
> on a **self-generated deterministic evasion census** — and does *normalization-before-matching*
> beat both a no-normalization baseline and a real production PII tool (Microsoft
> Presidio) on the evasion families the design targets?

The honest answer the paper defends: **yes on the targeted normalization families, with a
characterized coverage boundary** (it deliberately does worse than 1.0 and says where).

## 3. What problem does PerceptFence solve?

Static privacy toggles ("do not log", "do not share") cannot express *"this terminal is
fine but the password manager is not"* or *"summarize the screen but never name the
customer."* The sensitive content is in the **live capture**, not in the prompt, so
chatbot-style controls miss it entirely. PerceptFence introduces an observe / retain / say control decomposition. In the artifact,
the policy step is a hard-coded fixture `scenario_class → action` router; authenticated
consent profiles, category inference, re-consent transitions, and persistent memory are
target-design components rather than implemented controls.

## 4. What is the code artifact?

A standard-library-only Python package (`screenshare_mediator/`, Python ≥ 3.10,
no ML deps, no network, fully deterministic):

- **7 cooperating modules / 8 files:** fixture capture adapter, hard-coded policy router,
  six-family redaction engine, per-invocation memory gate, isolated output guard,
  in-memory SHA-256-chained event list, and a runtime composing baseline vs guarded paths.
- **11 synthetic fixtures** (`data/synthetic/`) across eight ordinary and three
  adversarial-evasion scenario classes. No real captures, data, or credentials.
- **Two evaluation harnesses:** the per-module ablation and the self-generated deterministic
  census (`eval/`), plus a latency micro-benchmark and a figure renderer.
- **42 unit/integration tests** (verified in the release environment on Python 3.12.13).

## 5. What experiments / evaluations exist?

| # | Evaluation | What it is | Headline number |
|---|---|---|---|
| 1 | Per-module ablation (11 fixtures) | **Configuration-consistency check** — *not* robustness; same author wrote fixtures, expected outcomes, and rules | full_guard reaches the configured outcome 11/11; SER 1.000→0.000, FBR 0.143 (unit-weighted) |
| 2 | Deterministic coverage census | 9,600 machine-generated cases (480 × 20 seeds), 11 self-authored evasion families, separately implemented but not independent exposure oracle; baselines = naive, PerceptFence, **real Presidio** | on paired seeds: overall recall **0.398** vs Presidio **0.260** vs naive **0.140** (cross-tool *indicative only*); out-of-coverage Presidio leads (0.238 vs 0.154) |
| 3 | Like-for-like digit-PII control | The family Presidio is *designed* for, isolating normalization from category coverage | paired seeds: PerceptFence **0.828** vs Presidio **0.183** vs naive **0.000** |
| 4 | Full-guarded-path check | Routes the same census through policy→redaction→memory→output guard | identical to redaction-only (**0.398**) → observe/retain/say is a taxonomy, not a measured robustness gain |
| 5 | Threshold sensitivity (0.5/0.7/0.9) | Recoverability-threshold robustness | ranking and magnitude stable (PF 0.392/0.398/0.401) |
| 6 | Dose–response & latency | Family-specific evasion curves; isolated micro-benchmark excluding capture/OCR/network/model time | monotone only for confusable, zero-width, and chained families; median guarded ≈34 µs |

Evidence files: `eval/results/heldout_overall.csv`, `heldout_by_family.csv`,
`heldout_benign_controls.csv`, `heldout_dose_response.csv`, `heldout_sensitivity.csv`, `per_module_ablation.csv`,
`per_fixture_ablation.csv`, `heldout_paired_presidio.csv`, and
`baseline_vs_guarded.csv`. The held-out protocol is documented in
`eval/heldout/PROTOCOL.md`: v1 preceded first results; a disclosed v2 amendment corrected
the bidi operator and regenerated the exact 9,600-case census. It is neither a third-party
pre-registration nor a protocol frozen before every score.

## 6. What claims ARE allowed?

- Overall held-out recall **0.398 vs Presidio 0.260 vs naive 0.140** — *indicative only*, not headlined; PerceptFence leads on in-coverage normalization families but Presidio leads on unseen encodings
  cross-tool, because the census includes credential/injection payloads outside Presidio's
  PII design.
- On the **like-for-like digit-PII family**, paired seeds 0–4: PerceptFence **0.828** vs Presidio **0.183**
  vs naive **0.000** — this isolates *normalization*, not category coverage, as the source
  of the gain.
- The advantage concentrates on the normalization families the design targets. Paired
  values are homoglyph **0.650**, split-digit **0.828**, and zero-width **0.526**;
  20-seed values are sensitivity estimates, not cross-tool comparisons.
- Recall is **deliberately below 1.0** with a *characterized coverage boundary*.
- The full guarded path equals redaction-only (**0.398**); ranking is stable across
  recoverability thresholds.
- The ablation is a **configuration-consistency** result on a designer-authored set.
- On the 11-fixture set: unit-weighted SER falls 1.000→0.000; FBR is 0.143 (2 of 14 benign
  units); these are *descriptive* statistics, not inferential estimates.

## 7. What claims are NOT allowed?

- ❌ No formal privacy / differential-privacy guarantee. "For Privacy" in the title is a
  *motivational goal*, not a property claim.
- ❌ No defense against compromised infrastructure (A6), poisoned model/supply chain (A7),
  or OS compromise (A8) — explicitly out of scope.
- ❌ No **model-behavioral injection-defense result**. Exploratory aggregate snapshots
  lacked retained per-case prompts, replies, and stable model identifiers and are excluded
  from the paper's evidence. The reported oracle scores string recoverability only.
- ❌ No live capture, OCR, ASR, authenticated consent state machine, persistent cross-turn
  memory, external model adapter, or end-to-end latency result.
- ❌ No claim that the exposure oracle is independent or categorically stronger than the
  redactor; it shares authorship and some normalization concepts.
- ❌ No real-world generalization. The held-out result is a **census** of a deterministic
  generator, not a sample — so **no confidence intervals or significance tests**.
- ❌ No claim of completeness against unknown evasions; out-of-coverage families are
  reported honestly (Base64 & leetspeak **0.000**, hex **0.143**, ROT13 **0.375**).
- ❌ Banned vocabulary unless backed by a measurement: *safe, secure, privacy-preserving,
  trustworthy, prevents leakage, robust* (without an adversary + metric), *real-time*
  (without latency bounds), standalone *novel/first/verified*. Enforced by a banned-term
  grep in `tools/verify_submission.py`.
- ⚠️ **Residual generative circularity** (generator and redactor share an author) is
  *disclosed and mitigated, not eliminated*.

## 8. What is the target venue and why?

**Springer Nature *International Journal of Information Security*** (journal 10207), **single-blind** review.

Why it fits: the work is a bounded runtime-security/privacy systems study matching IJIS's
published scope for technical work in the theory, applications, and implementation of
information security, including content protection and privacy. IJIS also has an open
Systems Security: Security and Privacy of AI section. The paper has a real third-party
baseline (Presidio), a predeclared self-authored evasion taxonomy, and an explicit
in-/out-of-coverage split. This is a better fit than an HCI/usability venue (no user study)
or a Tier-1 ML venue (no validated model-behavior study; the census is deterministic).
The public repository and single-blind review manuscript
identify both authors as Independent Researchers and disclose the public Zenodo/GitHub
artifact. Submission-process materials and generated upload files remain in the internal
repository's `private/generated-submissions/` control plane and are excluded from the public
projection.

## 9. What files are canonical?

| Concern | Canonical file(s) |
|---|---|
| Manuscript source | `paper/main.tex` (+ `paper/references.bib`) |
| Metric definitions | `eval/metrics.md` |
| Held-out protocol (frozen) | `eval/heldout/PROTOCOL.md` |
| Empirical evidence | `eval/results/*.csv` (and byte-identical copies in `supplement/`) |
| Code | `screenshare_mediator/` |
| Synthetic fixtures | `data/synthetic/` |
| Threat model / claim discipline | `policy-boundaries.md`, `security-threat-model-review.md` |
| Consistency gate | `tools/verify_submission.py` (+ `.github/workflows/`, `tools/hooks/pre-push`) |
| Public overview | `README.md`; this map: `PAPER_MAP.md` |

Every printed empirical number in the manuscript traces to a committed CSV; the verifier
fails closed if a number, the test count, the blinding, or the banned-term list drifts.

## 10. What files can be ignored or deleted?

The repository is already minimal after cleanup — there is nothing stale to delete. The
following are *generated or local* and intentionally untracked (`.gitignore`):

- `.evalvenv/` — local venv carrying real Presidio for the baseline (std-lib defenses run
  without it).
- `__pycache__/`, `.pytest_cache/`, `.DS_Store` — caches/OS cruft.
- `eval/results/*.csv` and `supplement/*.csv` are committed snapshots but are
  *regenerated* deterministically by the eval scripts; never hand-edit them.
- **Submission package** (Snapp PDF/source ZIP, cover letter, declarations, runbook,
  approval gate, checksums) — internal-only under `private/generated-submissions/`; it is
  regenerated from the canonical source and is never projected to the public repository.

---

### How to verify the artifact in one block

```bash
PYTHONPATH=. python3 eval/smoke_test.py
PYTHONPATH=. python3 eval/ablation_study.py
PYTHONPATH=. python3 eval/heldout/sensitivity_and_fullsystem.py
PYTHONPATH=. .evalvenv/bin/python -m pytest tests -q      # 42 passed
.evalvenv/bin/python tools/verify_submission.py            # all consistency gates pass
```
