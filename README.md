# PerceptFence

**Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants**

> Anonymous-review research artifact targeting **ACM IUI 2027** (papers track).
> All inputs are synthetic. No real screen captures, no real personal data, no real notifications. Authorship metadata is intentionally absent during double-blind review.

---

## Frozen thesis

**Problem.** Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say.

**What we solve.** A runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance.

**Article about.** Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants.

## Abstract

Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say. Static chatbot and privacy controls do not close this gap: the sensitive content is in the live capture, not in the prompt, and the assistant needs fast-changing interface context to respond at all. We study a runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance, sitting between capture adapters, session memory, and assistant responses. We will evaluate the layer on synthetic screen-share scenarios covering secrets, personal data, sensitive speech fragments, screen-visible prompt injection, dense or zoomed interfaces, fast window switching, and three adversarial-evasion classes (Unicode-homoglyph credentials, split or spaced personal-data digits, and role-play / chain-prompt screen instructions), measuring sensitive exposure, false blocks, latency overhead, and task completion against an unmediated prototype baseline. We contribute a bounded design and evaluation of runtime control mechanisms for screen-share assistants; claims remain limited to synthetic evidence until benchmark results are available.

## Why this exists

A multimodal assistant integrated into a screen-share session sees the same surface the user is explaining by hand: terminals with credentials, browsers with personal data, chat overlays with private notifications, and spoken context that may include sensitive fragments. Static chatbot privacy settings address none of this because the sensitive content is not in the user's prompt; it is in the live capture. PerceptFence interposes a deterministic runtime layer between raw capture and the assistant, with three control surfaces — *observe*, *retain*, and *say* — and reports per-module ablation diagnostics on a synthetic fixture set spanning eleven scenario classes.

## Repository layout

```
PerceptFence/
├── README.md                  ← you are here
├── PROJECT.md                 ← canonical project plan, M0–M5 milestones, gating rules
├── policy-boundaries.md       ← per-module enforces / does-not-enforce / trust assumptions
├── security-threat-model-review.md  ← banned-term list + claim-to-metric mapping
├── eval/
│   ├── smoke_test.py          ← fresh-clone smoke entry point
│   ├── ablation_study.py      ← fresh-clone ablation entry point
│   ├── metrics.md             ← formal metric specification (canonical at src/eval/metrics.md)
│   └── results/
│       ├── per_module_ablation.csv   ← synthetic diagnostics, per-variant
│       └── per_fixture_ablation.csv  ← synthetic diagnostics, per-variant × per-fixture
└── src/                       ← code artifact (review-pack subtree)
    ├── README.md              ← reproducibility quickstart for the artifact track
    ├── CITATION.cff           ← anonymous citation file
    ├── LICENSE                ← review-only license
    ├── SECURITY.md            ← allowed/disallowed inputs
    ├── pyproject.toml         ← stdlib-only, Python ≥ 3.10
    ├── policies/
    │   └── consent_redaction_policy.json
    ├── data/synthetic/        ← 11 invented fixtures + index
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
    ├── eval/
    │   ├── metrics.md         ← canonical metric spec
    │   ├── smoke_test.py
    │   ├── ablation_study.py
    │   └── results/           ← regenerated each ablation run
    ├── src/
    │   └── screenshare_mediator/
    │       ├── __init__.py
    │       ├── models.py          ← typed dataclasses across module boundaries
    │       ├── capture.py         ← synthetic capture adapter
    │       ├── policy.py          ← consent / policy engine
    │       ├── redaction.py       ← six-family deterministic redaction
    │       ├── memory.py          ← session memory gate (mode-A context exclusion)
    │       ├── output_guard.py    ← rule-based filter, isolated policy-only context
    │       ├── audit.py           ← append-only decision logger
    │       ├── runtime.py         ← baseline + guarded path composition
    │       └── fixture_loader.py  ← offline fixture loading + validation
    └── tests/
        ├── test_runtime_modules.py    ← 21 module + integration tests
        └── test_synthetic_fixtures.py ← 6 fixture-coverage tests
```

> Paper sources (`paper/`, `docs/`) are intentionally outside the public repo
> per blind-review hygiene; the canonical metric spec, threat model, and
> policy boundaries are mirrored here at the pack root.

## Reproducibility quickstart

The reference implementation is **standard-library-only Python ≥ 3.10**. No network, no machine-learning dependencies, no model providers. Every transform is deterministic so runs are bit-exact reproducible from the synthetic fixture set.

### Run the unit tests

```bash
cd src
python3 -m pytest tests/ -v
```

Expected: **27 passed in ~0.03s** (Python 3.14 on a 2024 laptop).

### Run the smoke test

```bash
python3 eval/smoke_test.py            # from pack root
# or, from src/:
PYTHONPATH=src python3 eval/smoke_test.py
```

Expected tail:

```
SMOKE PASS: 11 synthetic scenarios validated; 3 runtime mediation paths exercised
```

The smoke path exercises three contrasts: terminal redaction, prompt-injection output guarding, and context-exclusion memory gating, and prints the baseline-vs-guarded result for each.

### Run the per-module ablation

```bash
python3 eval/ablation_study.py
```

Writes `eval/results/per_module_ablation.csv` and `eval/results/per_fixture_ablation.csv`. Treat these as **bounded synthetic diagnostics, not the M5 benchmark**.

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

PerceptFence interposes between raw capture and the assistant. A thin synthetic capture adapter normalizes a fixture into a typed `CapturedSession`. The consent / policy engine maps the session to one of eight policy actions and emits a `PolicyDecision` four-tuple. The redaction engine applies six deterministic transform families (Unicode-homoglyph normalization, split-digit personal-data redaction, credential redaction, identifier summarization, prompt-injection neutralization, selective region redaction) before any content reaches model context. The session memory gate uses *mode-A context exclusion*: when policy selects `block_memory_write`, the gate zeros the model context for that turn before the model is invoked. The output guard operates over an isolated policy-only context and never receives raw screen text, raw speech text, or the mediated model context. The audit logger records policy decisions, context-exclusion events, and output-guard decisions with a fixed schema and never stores raw content. Four trust boundaries (TB1–TB4) and seven trust assumptions (TA1–TA7) condition every claim.

## Status

| Milestone | State |
|---|---|
| **M0** Venue and thesis lock | ✅ Complete |
| **M1** Threat model and policy boundaries | ✅ Complete |
| **M2** Synthetic fixture set + runtime modules | ✅ Complete (27/27 tests pass, 11 scenario classes) |
| **M3** Anonymous paper skeleton + metric specification | ✅ Complete |
| **M4** Smoke path + ablation diagnostics + adversarial-evasion coverage | ✅ Complete (full_guard 11/11 on synthetic diagnostics) |
| **M5** Post-filing benchmark, figure, blinded submission pack | 🚧 Gated until **2026-06-07** (see `PROJECT.md`) |

> **Pre-filing-gate discipline.** Until 2026-06-07, no `eval/results/baseline_vs_guarded.csv` is generated and no figure is produced from benchmark data. The project deliberately publishes only ablation diagnostics that are explicitly labeled as synthetic and bounded. Full benchmark CSV, generated architecture figure, and blinded submission pack land after the gate.

## Claim discipline

The article-title phrase **"for Privacy"** is a motivational goal, not a property claim. Every paper claim maps to a measured metric in `src/eval/metrics.md`. The banned-term list in `security-threat-model-review.md` §2.1 enumerates phrases (*safe*, *secure*, *privacy-preserving*, *trustworthy*, *prevents leakage*, *first*, standalone *novel*, *verified*, *useful*, *usable*, *comprehensive*, *complete*, *robust* without an adversary and metric, *real-time* without latency bounds) that are deliberately avoided unless backed by a measurement; we run a banned-term grep before every push.

## Threat model summary

Six in-scope adversaries (A1 accidental exposure, A2 screen-visible prompt injection, A3 context confusion, A4 retention overshoot, A5 output leakage, A6 multi-actor cross-channel) and five out-of-scope adversaries (X1 OS-level attacker, X2 malicious provider, X3 side channels, X4 colluding user, X5 cross-session inference) frame nine threats T1–T9. Three single points of failure are explicitly named: T3 (notification leakage) depends on the redaction stage alone, T4 (sensitive speech retention) depends on the memory gate alone, and T9 (audit incompleteness) depends on the audit logger alone. The compact in-paper threat model lives in the manuscript; the full narrative is mirrored in `policy-boundaries.md` and `security-threat-model-review.md`.

## Citation

```bibtex
@misc{anon-perceptfence-2027,
  author = {Anonymous Authors},
  title  = {Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants},
  year   = {2027},
  note   = {Anonymous-review manuscript; cite the submitted version}
}
```

The anonymous CFF metadata lives at `src/CITATION.cff`.

## License

See `src/LICENSE`. This is a review-only research scaffold; redistribution outside the review context is not permitted until the camera-ready window.

## Blind-review safety note

This repository is intentionally free of author identity, organization names, public demo links, real screen captures, and production telemetry. Real authorship metadata, when added at camera-ready, lives in a gitignored `paper/authors.private.md`. Banned-term and author-leak greps are run before each push; their commands are documented inside `PROJECT.md` and `security-threat-model-review.md`.
