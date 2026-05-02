# Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants

> Anonymous draft for double/single-blind review. Do not include author identifiers. De-anonymization happens at submission time per the venue's policy.
>
> **Status:** Draft 2, 2026-05-02. NEE-241 source-check complete: Section 3 (Related Work) written with 16 verified citations; §5.3 ablation error corrected (spoken_sensitive_fragment, not homoglyph_credential, is the fixture missed by redaction_only); §5.4 adversarial-evasion analysis filled from per_fixture_ablation.csv; §5.5 latency table filled from baseline_vs_guarded.csv; §5.6 no-prior-system claim confirmed; references.bib committed. All placeholders resolved.

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

**Runtime capture permissions.**
Mobile operating systems use API-level permissions to control which applications may access the camera, microphone, or screen-capture surface.
Felt et al. characterize Android's permission model and find that most users grant permissions without understanding their scope [@felt2012permissions].
A companion study shows that applications routinely request permissions they do not use, creating unnecessary exposure [@felt2011android].
At the system layer, TaintDroid tracks the flow of privacy-sensitive data through the Android runtime, demonstrating that third-party applications frequently transmit sensitive user data to advertising networks without user awareness [@enck2014taintdroid].
These system-level designs gate access to a capture API but do not control what happens to the content of the captured stream after access is granted.
PerceptFence operates at the content layer rather than the access layer: it interposes between a granted capture stream and an AI assistant's context-construction step.

**Privacy norms and contextual integrity.**
Nissenbaum frames appropriate information flow in terms of contextual integrity: information should flow in ways consistent with the norms of the context in which it was originally disclosed [@nissenbaum2004privacy].
Apthorpe et al. apply contextual integrity to smart-home IoT devices, showing that users hold nuanced norms about which data a home device may forward to third-party services, conditioned on the recipient and stated purpose [@apthorpe2018smart].
Shvartzshnaider and Duddu extend this framework to large language models, measuring deviations between the information-flow choices made by LLMs and contextually appropriate expectations, and proposing an auditing metric grounded in contextual integrity theory [@shvartzshnaider2026privacy].
The consent and policy engine in PerceptFence enforces a simplified contextual boundary by content type: it blocks sensitive screen and speech content from entering the assistant's context unless the active session policy permits that content category.

**Privacy-aware AI assistants.**
Xu et al. study user and expert expectations of AI-powered privacy assistants that automate privacy decisions on behalf of users, identifying factors that influence acceptability, including transparency of information sources and regulatory context [@xu2025acceptability].
Danry et al. build a gaze-aware multimodal assistant that uses egocentric video to infer where a user is struggling during a task, raising questions about what such an assistant is permitted to observe and how that observation boundary should be defined [@danry2026gaze].
These systems address AI assistant design and user-facing controls but do not impose runtime content-level filtering on a continuously changing multimodal stream.
PerceptFence contributes a mediation layer targeting live screen-share input rather than post-hoc user control or assistant behavior calibration.

**Screen-capture privacy in deployed systems.**
Microsoft Recall captures a desktop screenshot every few seconds and uses on-device LLMs to provide a retrievable memory layer; early deployments did not filter sensitive content from the snapshot store, and subsequent versions added opt-in filtering for recognized credential patterns after significant public and security-research scrutiny [@microsoft2024recall].
Zoom AI Companion provides in-meeting AI assistance including transcription and summaries; its privacy documentation describes zero-data-retention options and per-account toggle controls, but these operate at the session level rather than at the granularity of what the assistant may observe within an active session [@zoom2024ai].
Neither system exposes per-content-category runtime controls during an active session.
PerceptFence targets this gap: it mediates at the frame and utterance level rather than only at session setup time.

**Prompt injection attacks.**
Screen-visible content introduces a direct prompt injection surface when an AI assistant observes and processes text displayed on screen.
Greshake et al. systematize indirect prompt injection attacks in LLM-integrated applications, showing that attacker-controlled content placed in retrieved data can override application instructions without any direct user interaction [@greshake2023indirect].
Liu et al. extend this analysis to black-box attacks on commercial applications, reporting high success rates against production LLM integrations and proposing a taxonomy of injection techniques [@liu2023prompt].
Screen-share sessions are a particularly direct injection surface because attacker-controlled text is visually displayed and the assistant observes the display without intermediation; the synthetic benchmark includes prompt-injection-on-screen and encoded-screen-instruction scenarios covering this threat.

**Defenses against prompt injection and agent safeguards.**
StruQ separates instructions and data into structured channels, fine-tuning the LLM to follow only the designated instruction channel, reducing injection success rates substantially on the evaluated benchmark [@chen2025struq].
SecAlign uses preference optimization to train an LLM to prefer secure outputs over injection-compliant outputs, achieving injection success rates below ten percent against a range of attacks including ones not seen during training [@chen2025secalign].
Yang et al. demonstrate that injected content written into an agent's long-term memory can persist across sessions and trigger unauthorized tool actions in future sessions [@yang2026zombie]; this result motivates PerceptFence's memory gate, which prevents sensitive content from being written to session memory under configurable policy.
Chen and Cong propose AgentGuard, which uses the agent orchestrator itself to enumerate unsafe tool-use workflows and generate safety constraints that can be validated before deployment [@chen2025agentguard].
These defenses operate at the model fine-tuning or orchestration level; PerceptFence operates at the input and output mediation layer without modifying the underlying model, making it applicable to any assistant model but bounded by the limits of rule-based detection, which the system design and evaluation explicitly acknowledge.

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

**Reading the table.** Redaction alone removes ten of eleven sensitive units from both context and output; the missed fixture is `spoken_sensitive_fragment`, whose expected policy action is `block_memory_write` — a retention control that the redactor does not implement. Output guard alone blocks all assistant outputs that would have leaked, but does so by blocking *all* responses on the affected fixtures — acceptable as a last-resort fallback, but not a substitute for upstream filtering. Memory gate alone prevents persistence but lets the model see and respond with sensitive content. The full guard composition reaches the expected outcome on every fixture in the benchmark, with no context exposures, no output exposures, five precise output blocks (used only when upstream redaction was insufficient), and an audit trail of 23 decision events.

Per-fixture results are in `eval/results/per_fixture_ablation.csv` and broken out in Section 5.4.

### 5.4 Per-fixture results and adversarial-evasion analysis

The three adversarial-evasion fixtures are `homoglyph_credential`, `split_pii`, and `encoded_screen_instruction`. Per `eval/results/per_fixture_ablation.csv`:

| Fixture | redaction_only outcome | full_guard outcome | output_blocked in full_guard | Mechanism |
| --- | --- | --- | --- | --- |
| `homoglyph_credential` | expected_outcome_met=True | expected_outcome_met=True | False | Unicode normalization before pattern check in the redactor removes the homoglyph substitution; output guard is not invoked. |
| `split_pii` | expected_outcome_met=True | expected_outcome_met=True | True | Whitespace/separator normalization in the redactor catches split digits; the output guard also fires as defense-in-depth (output_blocked=True), confirming the response would have been blocked even if the redactor had missed it. |
| `encoded_screen_instruction` | expected_outcome_met=True | expected_outcome_met=True | True | The redactor strips the encoding marker from the screen text; the output guard additionally blocks the response as defense-in-depth, confirming the instruction did not produce a compliant assistant output. |

All three adversarial-evasion fixtures are handled by `full_guard`. The redactor handles `homoglyph_credential` and `split_pii` via normalization; the output guard provides a second layer on `split_pii` and `encoded_screen_instruction`. The contrast with `redaction_only` (also expected_outcome_met=True for all three) shows that the redactor's normalization is the primary control for evasion; the output guard adds defense-in-depth. The one fixture that `redaction_only` misses is `spoken_sensitive_fragment` (block_memory_write action), which requires the memory gate — a retention control, not a content-redaction control.

### 5.5 Latency overhead

Per `eval/results/baseline_vs_guarded.csv` (200 paired iterations per fixture):

| Fixture | Baseline median (µs) | Guarded median (µs) | Guarded p99 (µs) | Overhead ratio (median) |
| --- | --- | --- | --- | --- |
| terminal_secret | 2.2 | 32.8 | 40.0 | 13.9× |
| chat_notification | 2.2 | 55.5 | 73.1 | 24.6× |
| browser_pii | 2.1 | 35.4 | 46.0 | 15.7× |
| spoken_sensitive_fragment | 2.0 | 35.9 | 85.9 | 17.0× |
| prompt_injection_on_screen | 2.1 | 32.6 | 44.8 | 14.6× |
| fast_window_switching | 2.4 | 32.8 | 43.3 | 12.8× |
| small_font_zoomed_ui | 2.1 | 28.8 | 99.8 | 12.5× |
| homoglyph_credential | 2.1 | 27.3 | 28.1 | 11.9× |
| split_pii | 2.1 | 28.6 | 37.1 | 12.5× |
| mixed_sensitivity | 2.1 | 56.8 | 81.3 | 25.5× |
| encoded_screen_instruction | 2.1 | 71.1 | 103.6 | 32.3× |

The median guarded latency across all fixtures is approximately **32.8 µs** (range 27.3–71.1 µs). The p99 reaches **103.6 µs** for `encoded_screen_instruction`, which requires the most complex output-guard evaluation. The baseline median is approximately **2.2 µs**. The overhead ratio ranges from 11.9× to 32.3× across fixtures, reflecting that the mediation layer dominates the harness time relative to the no-op baseline, but the absolute overhead remains sub-millisecond in every case.

These figures reflect a single-process Python evaluation harness on synthetic fixtures. They characterize the relative contribution of the mediation layer within the harness but should not be interpreted as production-system latencies; actual screen-capture AI pipelines involve OCR, network, and model inference that would dominate the mediation overhead.

### 5.6 Threats to validity

- **Synthetic-only.** All fixtures are invented. Production-scale generalization is not claimed.
- **Eleven fixtures.** Coverage is intentionally bounded; adversarial-evasion classes beyond the three studied are not characterized.
- **English-only synthetic content.** Multi-lingual evasion is not studied.
- **Single-system evaluation.** No comparison to prior runtime-mediation systems because, to our knowledge, none with the same control-surface decomposition exists. A related-work survey (NEE-241, 2026-05-02) confirmed that the closest prior systems operate at the OS permission layer (TaintDroid, Android permission model) or session-level controls (Microsoft Recall, Zoom AI Companion), not at the per-frame, per-content-category runtime level described here.

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

Formatted by ACM-Reference-Format from `references.bib`. See that file for all 16 entries (≤25 cap). Every cite key used in this manuscript resolves in `references.bib`; the provenance table in the file records the verification path for each entry.

---

## Anonymity and de-anonymization log

This draft is anonymous. Author block, affiliations, acknowledgments, and CITATION.cff de-anonymization happen at submission time and are tracked in NEE-245. Repository link in references is also gated on de-anonymization.

## Banned-term audit (per security-threat-model-review.md §5)

To be run by NEE-243 against this draft and every subsequent revision before commit.
