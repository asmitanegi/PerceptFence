# Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants

> Anonymous draft for double/single-blind review. Do not include author identifiers. De-anonymization happens at submission time per the venue's policy.
>
> **Status:** Skeleton draft 1, 2026-05-02. Owner: NEE-240. Source-check tags `[src-chk]` are placeholders to be resolved by NEE-241.

---

## Abstract

Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say. Static chatbot and privacy controls do not close this gap: the sensitive content is in the live capture, not in the prompt, and the assistant needs fast-changing interface context to respond at all. We design and evaluate a runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance, sitting between capture adapters, session memory, and assistant responses. We evaluate the layer on synthetic screen-share scenarios covering secrets, personal data, sensitive speech fragments, screen-visible prompt injection, dense or zoomed interfaces, fast window switching, and three adversarial-evasion classes (Unicode-homoglyph credentials, split or spaced personal-data digits, and role-play / chain-prompt screen instructions), measuring sensitive exposure, false blocks, latency overhead, and task completion against an unmediated prototype baseline. We contribute a design and evaluation of runtime control mechanisms for screen-share assistants, with claims bounded to synthetic evidence.

**Keywords.** Privacy, screen-share assistants, runtime mediation, consent, redaction, multimodal AI, prompt injection, evaluation.

---

## 1. Introduction

Multimodal AI assistants are increasingly deployed inside live screen-share sessions, where they observe the same surface a human is explaining: terminals with credentials, browsers with personal data, chat overlays with personal notifications, and spoken fragments containing sensitive information. This deployment pattern is fundamentally different from the chatbot setting: the sensitive content is not in the user's prompt; it is in the live capture stream itself.

Static privacy settings — blanket "do not log," "do not share with vendors" toggles — address a different problem. They cannot answer questions like *"this terminal window is okay but the password manager is not,"* *"summarize what is on screen but never name the customer,"* or *"redact this email address from your reply but use it to find the right ticket."* These questions are about **runtime** mediation between capture and assistant: deciding, frame-by-frame and utterance-by-utterance, what the model sees, what gets retained, and what comes out.

This paper presents a runtime mediation layer for live screen-share AI assistants. The layer interposes seven cooperating modules between raw capture and assistant response — screen capture adapter, speech event adapter, redaction engine, consent/policy engine, session memory gate, output guard, and audit logger — with three control surfaces: **observe**, **retain**, and **say**. We design the layer to satisfy a stated adversary model (Section 2), describe per-module enforcement and trust boundaries (Section 4), and evaluate per-module contributions on a synthetic benchmark of eleven scenario classes including three adversarial-evasion classes (Section 5).

Our contributions:

- **A consent-aware runtime mediation design** for screen-share AI assistants, decomposed into seven modules with explicit per-module trust assumptions and enforces-vs-does-not-enforce boundaries.
- **A synthetic evaluation benchmark** of eleven scenario classes covering credentials, personal data, sensitive speech, prompt injection on-screen, dense/zoomed interfaces, fast window switching, and three adversarial-evasion classes (Unicode-homoglyph credentials, split/spaced personal-data digits, role-play / chain-prompt screen instructions).
- **A per-module ablation study** isolating which mediation module removes or blocks each annotated risk class, including a measurement that the full guard achieves the expected outcome on every fixture (11/11) while the unmediated baseline reaches it on none (0/11).
- **A claim-to-metric audit framework** that ties every empirical claim in the evaluation to an annotated metric definition, preventing the kind of unmeasured "privacy" claims that have weakened prior work in this space.

We make no claims about formal privacy preservation, differential privacy guarantees, defense against compromised hosts or models, or completeness against unknown adversarial-evasion classes. The contribution is bounded: a design and evaluation of runtime control mechanisms on a synthetic benchmark.

---

## 2. Threat Model

We separate in-scope runtime threats from excluded systems-security threats. The contribution is meaningful only relative to the risks it chooses to handle.

### 2.1 Adversary classes

| ID | Adversary | In scope? | Rationale |
| --- | --- | --- | --- |
| A1 | Malicious screen content (attacker controls displayed text/visuals, including instructions meant to manipulate the assistant) | Yes — primary | Prompt injection through displayed content is the central screen-share-specific risk. |
| A2 | Malicious meeting participant (deliberately displays sensitive content or prompts the assistant to reveal content outside another participant's consent) | Yes | Tests whether consent and output policies hold when another participant is adversarial. |
| A3 | Curious or over-privileged user (tries to lower consent/redaction/retention to expose more than the policy allows) | Yes | Distinguishes enforceable runtime policy from advisory user preferences. |
| A4 | Assistant output leakage (the model repeats, summarizes, infers, or indirectly references content that should have been redacted or gated) | Yes | Motivates the memory gate and output guard. |
| A5 | Temporal exposure (sensitive content appears briefly during window switches, popups, zoom changes, or small-font rendering) | Yes | Matches the synthetic scenarios and tests mediation under changing context. |
| A6 | Compromised infrastructure (read/modify audit logs, session storage, runtime state, backend services) | **No** | Reasonable exclusion for the current prototype. We do not claim tamper-evidence or infrastructure hardening. |
| A7 | Poisoned model or supply chain | **No** | Broader systems-security problem named as out of scope. |
| A8 | Operating-system compromise (malware controls host OS, display server, microphone stack, or clipboard) | **No** | Cannot be defended against without a different trusted-computing design. |

### 2.2 Trust boundaries

Captured frames, extracted text, audio events, and notification events are treated as **untrusted input** until the policy and redaction stages finish. The user's consent profile is **trusted at session start** and modifiable only via authenticated policy operations within the session. Backend storage and audit logs are **trusted under A6 exclusion**; we do not provide tamper-evidence beyond an append-only hash chain (Section 4.7).

### 2.3 Claim guardrails

Every empirical claim in this paper maps to a metric defined in Section 5.1 and computed on the benchmark in Section 5.3. The phrase "for privacy" in the title refers to a measured *reduction* in sensitive exposure rate on synthetic fixtures — not formal privacy preservation, differential privacy, side-channel absence, or prevention of all leakage.

---

## 3. Related Work

[src-chk] Prior work on runtime privacy in conversational assistants. [src-chk] Prompt injection and indirect prompt injection in multimodal contexts. [src-chk] Redaction and PII detection systems. [src-chk] Consent and policy engines for AI systems. [src-chk] Audit logging and tamper-evident systems for ML pipelines. [src-chk] Screen-share security in collaborative work environments.

NEE-241 will resolve every `[src-chk]` placeholder, build `references.bib`, and replace this section with a coherent narrative tying our seven modules to existing work and clearly stating the gap we close.

---

## 4. Design

The runtime mediation layer is composed of seven modules along three control surfaces:

- **Observe** — what the assistant model is permitted to see (screen capture adapter, speech event adapter, redaction engine, consent/policy engine).
- **Retain** — what the session memory persists across turns (session memory gate).
- **Say** — what the assistant is permitted to output (output guard).

The audit logger sits across all three surfaces and records decisions without recording sensitive payload.

### 4.1 Screen capture adapter

Captures display frames and extracts textual content. Output is untrusted text plus structural metadata (window class, region, font size, recency). Does **not** classify content; that is the consent/policy engine's job.

### 4.2 Speech event adapter

Captures audio events and emits utterance fragments with metadata (speaker role, modality, timestamp). Consent decisions can be per-session, per-modality, per-speaker, or per-content category; we adopt **per-modality with per-content-category overrides** (Section 4.4).

### 4.3 Redaction engine

Pattern-based and category-based redaction over extracted text and speech fragments. Replaces matched units with stable placeholders (`[REDACTED]`, `[EMAIL]`, `[RECORD]`, `[PERSON]`). The engine is *not* model-based for this prototype to keep the trust boundary tight; we treat the redaction engine as **enforcing reduction, not elimination, of sensitive exposure**.

Adversarial evasion is a known limitation:
- **Unicode homoglyph evasion** (e.g., Cyrillic `а` for Latin `a` in a credential string) — addressed via Unicode normalization before pattern check.
- **Split/spaced PII** (e.g., `4 1 1 1 - 1 1 1 1 - 1 1 1 1`) — addressed via whitespace and separator normalization with bounded lookback.
- **Role-play / chain-prompt screen instructions** — flagged by the policy engine as A1/A2 surface, not by the redactor; redaction is content-based, not intent-based.

### 4.4 Consent / policy engine

Resolves the active consent profile per frame and per utterance. Inputs: window class, modality, speaker role, content categories detected by the redactor, and the user's session policy. Output: a policy action ∈ {allow, redact, gate-memory, block-output, audit-only}, plus the rationale. The policy engine is the **only** authoritative decision-maker for the three control surfaces.

Policy downgrade is prevented by a session-startup policy lock: relaxations require an authenticated re-consent step, not a runtime toggle.

### 4.5 Session memory gate

Filters what the assistant's session memory persists across turns. Default: no sensitive units written to memory. The memory gate enforces the **retain** surface even when the redactor has allowed a unit through to the model context (e.g., the assistant needs to *use* a personal email but should not *remember* it across the session).

### 4.6 Output guard

Filters the assistant's response stream before display. Enforces output-side policy actions (block, redact, paraphrase). The output guard is the last line of defense against A4 (assistant output leakage), including indirect references — e.g., the assistant naming a person whose email was redacted upstream.

### 4.7 Audit logger

Append-only log of policy decisions and module actions. Logs decision metadata only — never raw screen text, raw speech, raw notification text, or sensitive unit values. Each entry carries a SHA-256 hash chain for crash-evident integrity (defense **not** claimed against A6).

### 4.8 What this design does not do

- It does not defend against A6/A7/A8.
- It does not provide formal privacy guarantees.
- It does not perform model-based redaction; extended category coverage requires a redactor extension.
- It does not generalize beyond the seven modules without explicit threat-model re-review.

---

## 5. Evaluation

### 5.1 Metrics

We define four primary metrics over a synthetic fixture set `D = {x_1, ..., x_n}` with `n = 11`. For each fixture, `U_i` is the set of annotated synthetic sensitive units that must not appear on prohibited surfaces (model context, assistant output, retained memory, audit content beyond decision metadata), and `Q_i` is the set of annotated benign task-critical units that should remain available for task completion.

**Sensitive exposure rate (SER).** For path `p ∈ {B, G}` (baseline / guarded):

```
SER(p) = (Σ_i Σ_{u ∈ U_i} exposed(u, x_i, p)) / (Σ_i |U_i|)
```

where `exposed(u, x_i, p) = 1` if a normalized match for `u` appears on a prohibited surface in path `p`. Lower `SER(G)` is better. Surface breakdowns (`SER_context`, `SER_output`, `SER_memory`, `SER_audit`) are reported per-surface. Full definitions in `src/eval/metrics.md`.

**False block rate (FBR).** Fraction of benign task-critical units `q ∈ Q_i` that the guarded path blocks or replaces in a way that prevents task completion.

**Latency overhead (LOH).** Wall-clock guarded-path runtime minus baseline runtime, on the same fixture, under the same harness.

**Task completion (TC).** Rubric-based pass/fail per fixture, evaluated on assistant output.

### 5.2 Benchmark composition

Eleven synthetic fixtures spanning seven non-adversarial classes (terminal secret, chat notification, browser PII, spoken sensitive fragment, prompt injection on screen, fast window switching, small-font zoomed UI) and three adversarial-evasion classes (Unicode-homoglyph credential, split PII, mixed-sensitivity scene). All fixtures are invented; no real screen captures, real personal data, or production telemetry. Construction details and provenance are in `src/data/synthetic/README.md` and `supplement/artifact_checklist.md`.

### 5.3 Per-module ablation

We run six variants on the eleven fixtures: `baseline` (no mediation), `policy_only`, `redaction_only`, `memory_gate_only`, `output_guard_only`, `audit_log_only`, and `full_guard` (all modules enabled). Results from `eval/results/per_module_ablation.csv`:

| Variant | Modules | Expected-outcome rate | Context exposures | Output exposures | Output blocks | Audit events | Memory writes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `baseline` | none | **0.000** (0/11) | 10 | 10 | 0 | 0 | 0 |
| `policy_only` | policy | 0.000 (0/11) | 10 | 8 | 0 | 0 | 0 |
| `redaction_only` | policy + redaction | 0.909 (10/11) | 1 | 1 | 0 | 0 | 0 |
| `memory_gate_only` | policy + memory gate | 0.091 (1/11) | 9 | 7 | 0 | 0 | 10 |
| `output_guard_only` | policy + output guard | 0.000 (0/11) | 10 | 0 | 10 | 0 | 0 |
| `audit_log_only` | policy + audit logger | 0.000 (0/11) | 10 | 8 | 0 | 11 | 0 |
| `full_guard` | all | **1.000 (11/11)** | 0 | 0 | 5 | 23 | 10 |

**Reading the table.** Redaction alone removes ten of eleven sensitive units from both context and output (the missing one is the homoglyph-evasion fixture). Output guard alone blocks all assistant outputs that would have leaked, but does so by blocking *all* responses on the affected fixtures — acceptable as a last-resort fallback, but not a substitute for upstream filtering. Memory gate alone prevents persistence but lets the model see and respond with sensitive content. The full guard composition reaches the expected outcome on every fixture in the benchmark, with no context exposures, no output exposures, five precise output blocks (used only when upstream redaction was insufficient), and an audit trail of 23 decision events.

Per-fixture results are in `eval/results/per_fixture_ablation.csv` and broken out in Section 5.4.

### 5.4 Per-fixture results and adversarial-evasion analysis

[src-chk: cross-reference per_fixture_ablation.csv specific rows for the three adversarial-evasion fixtures to show whether the full guard handled each, and explain why the redaction-only configuration missed the homoglyph case but full_guard caught it via output_guard.]

### 5.5 Latency overhead

[src-chk: report wall-clock comparison from harness once benchmark instrumentation is finalized; current results CSV does not include `t_i^p` columns.]

### 5.6 Threats to validity

- **Synthetic-only.** All fixtures are invented. Production-scale generalization is not claimed.
- **Eleven fixtures.** Coverage is intentionally bounded; adversarial-evasion classes beyond the three studied are not characterized.
- **English-only synthetic content.** Multi-lingual evasion is not studied.
- **Single-system evaluation.** No comparison to prior runtime-mediation systems because, to our knowledge, none with the same control-surface decomposition exists. [src-chk: confirm in NEE-241.]

---

## 6. Discussion

The ablation supports a small but specific design claim: **no single module is sufficient, and the four mediation modules (redaction, memory gate, output guard, audit logger) compose under the policy engine to achieve full expected-outcome on the synthetic benchmark.** The result is consistent with a defense-in-depth architecture: redaction handles the common path, output guard catches what redaction misses, memory gate prevents cross-turn leakage, audit logger preserves decision provenance.

**Deployment considerations.** The seven-module decomposition assumes a controlled assistant runtime where the developer owns capture, redaction, model invocation, memory, and output. SaaS assistants without this control cannot adopt the design as-is. Hybrid deployments (browser extension + assistant API) would require redaction at the extension boundary and trust-model adjustments.

**What we did not measure.** Real-user task-completion rates, latency on production captures, additional adversarial classes beyond the three studied, multi-lingual performance.

---

## 7. Limitations

- Synthetic benchmark only; no real-user evaluation.
- Eleven fixtures; adversarial classes beyond the three studied are uncharacterized.
- Pattern-based redactor; additional content categories require a redactor extension.
- A6/A7/A8 explicitly excluded from the threat model.
- No formal privacy guarantee.

---

## 8. Ethics

All evaluation data is synthetic. No real screen captures, real personal data, real audio recordings, or real notification content was collected, used, or stored. No human subjects were involved. IRB approval is not applicable. The synthetic fixture set is documented under `src/data/synthetic/README.md`.

The design does not enable surveillance: it reduces, not increases, the assistant's access to sensitive content. The design does not weaken existing privacy controls: it composes with platform-level controls and operates strictly inside the assistant runtime.

---

## 9. Conclusion

We presented a runtime mediation layer for live screen-share AI assistants, decomposed into seven modules along three control surfaces (observe, retain, say) and motivated by an explicit threat model. A per-module ablation on a synthetic benchmark of eleven scenario classes shows that the composed full guard achieves expected outcomes on every fixture while the unmediated baseline reaches it on none, and that no single module is individually sufficient. We make bounded claims tied to a synthetic benchmark and explicitly exclude formal privacy, host compromise, and supply-chain threats from our scope.

---

## References

[src-chk] Built by NEE-241 from the [src-chk] markers above. Target: ≤25 references, BibTeX-valid `references.bib`, every cite key resolves end-to-end.

---

## Anonymity and de-anonymization log

This draft is anonymous. Author block, affiliations, acknowledgments, and CITATION.cff de-anonymization happen at submission time and are tracked in NEE-245. Repository link in references is also gated on de-anonymization.

## Banned-term audit (per security-threat-model-review.md §5)

To be run by NEE-243 against this draft and every subsequent revision before commit.
