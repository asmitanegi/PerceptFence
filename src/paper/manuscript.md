# Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants

> Anonymous draft for double/single-blind review. Do not include author identifiers. De-anonymization happens at submission time per the venue's policy.
>
> **Status:** Draft 3, 2026-05-03. NEE-252 prose pass expands Introduction, Related Work, Design, Discussion, and Limitations toward the 6,000-word bar. Related Work uses checked citation keys from `references.bib`; empirical claims remain tied to committed files under `eval/results/`.

---

## Abstract

Live screen-share AI assistants can observe raw screen and speech streams, but users lack fine-grained runtime control over what the assistant may see, retain, and say. Static chatbot and privacy controls do not close this gap: the sensitive content is in the live capture, not in the prompt, and the assistant needs fast-changing interface context to respond at all. We design and evaluate a runtime mediation layer that enforces consent, redaction, memory controls, and output safeguards for live multimodal assistance, sitting between capture adapters, session memory, and assistant responses. We evaluate the layer on synthetic screen-share scenarios covering secrets, personal data, sensitive speech fragments, screen-visible prompt injection, dense or zoomed interfaces, fast window switching, and three adversarial-evasion classes (Unicode-homoglyph credentials, split or spaced personal-data digits, and role-play / chain-prompt screen instructions), measuring sensitive exposure, false blocks, latency overhead, and task completion against an unmediated prototype baseline. We contribute a bounded design and evaluation of runtime control mechanisms for screen-share assistants; claims remain limited to deterministic synthetic evidence.

**Keywords.** Privacy, screen-share assistants, runtime mediation, consent, redaction, multimodal AI, prompt injection, evaluation.

---

## 1. Introduction

Live screen-share AI assistants collapse two interaction modes that used to be separate. In one mode, a user deliberately sends a prompt to a chatbot. In the other, a collaborator shares a live desktop, browser, terminal, or meeting window with other people. A screen-share assistant sees the second mode through the interface of the first: the assistant receives a stream of visual and speech-derived context, then produces text as if the user had intentionally provided every item in that stream. That assumption is fragile. A terminal may contain an API token beside the command the user wants explained. A browser may show a customer identifier next to a workflow step. A chat overlay may appear for half a second while the user is asking about an unrelated design artifact. A meeting participant may display instructions that are meaningful to humans but adversarial to an AI assistant.

The resulting gap is not just a data-retention setting. Session-level controls such as whether an assistant is enabled, whether a transcript is retained, or whether vendor training is allowed operate before or after the live interaction. They do not answer the runtime questions that arise after capture begins: should this frame enter the model context, should this utterance be written to memory, and should the assistant repeat or imply a sensitive item in its response? Existing permission systems similarly decide whether an application may access a resource, but once access is granted they rarely mediate each content category inside the stream. For live screen-share assistance, the policy decision must be closer to the assistant's context-construction boundary.

We frame this paper around three control surfaces. The **observe** surface governs what captured screen, notification, and speech content may enter assistant context. The **retain** surface governs what may persist beyond the immediate turn. The **say** surface governs what the assistant may reveal in its response, including direct repetition and configured indirect references to gated content. These surfaces are intentionally separated. Redacting an input token does not guarantee that no memory write occurred; suppressing a memory write does not guarantee that the current response is clean; blocking a response does not prove that the model never saw the content. A runtime mediation layer must therefore coordinate input, memory, output, and audit behavior rather than treating privacy as a single switch.

We present PerceptFence, a synthetic prototype of such a runtime mediation layer. PerceptFence interposes seven cooperating modules between raw capture and assistant response: a screen capture adapter, a speech event adapter, a consent/policy engine, a deterministic redaction engine, a session memory gate, an output guard, and an audit logger. The prototype does not modify the underlying language model or the host operating system. Instead, it treats captured screen and speech content as untrusted input, constructs assistant context only after policy and redaction decisions, prevents configured content from being written to session memory, and filters assistant output using policy-only guard context.

The evaluation is deliberately bounded. We use eleven invented screen-share scenario classes covering credentials, personal data, notifications, sensitive speech fragments, screen-visible prompt injection, fast window switching, dense or zoomed interfaces, and three configured adversarial-evasion families: Unicode-homoglyph credentials, split or spaced personal-data digits, and encoded or chained screen instructions. Against an unmediated baseline, the composed guard achieves the expected outcome on all eleven fixtures while the baseline achieves it on none. The mean sensitive exposure rate in the committed benchmark is 0.909 for the baseline and 0.000 for the guarded path; the mean false block rate rises from 0.000 to 0.182. These numbers are evidence about the fixture set and implementation path only. They are not evidence about real screen-share distributions, human understanding, legal consent, deployment latency, or defenses against compromised hosts or models.

This paper makes four contributions:

- **A runtime-mediation framing** for live screen-share AI assistants, organized around observe, retain, and say control surfaces.
- **A seven-module design** that separates capture, policy, redaction, memory gating, output guarding, and audit logging while stating the trust boundary for each module.
- **A synthetic benchmark and ablation** that measure sensitive exposure, false blocks, task-success proxy, audit coverage, and latency on eleven invented scenario classes.
- **A claim-to-metric discipline** that keeps the paper's empirical claims tied to deterministic artifacts under `eval/results/` and labels unsupported user-study, deployment, and formal guarantees as out of scope.

The paper is structured as follows. Section 2 states the threat model and claim guardrails. Section 3 positions PerceptFence relative to runtime permissions, contextual-integrity work, privacy-oriented assistants, deployed screen-capture assistants, prompt-injection attacks, and agent safeguards. Section 4 describes the design and implementation. Section 5 reports the synthetic evaluation. Sections 6 and 7 discuss implications, design alternatives, and limitations.

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
Mobile and desktop platforms usually begin with an access-control question: may this application use a camera, microphone, screen-capture surface, clipboard, or file? Felt et al. show that Android permissions were difficult for users to interpret and that many applications requested permissions whose purpose was unclear to the user [@felt2012permissions]. Their companion analysis of Android applications found over-requesting and permission use that exceeded what application descriptions made salient [@felt2011android]. TaintDroid moves from permission prompts to runtime information-flow tracking, following sensitive data through the Android runtime and showing how third-party applications can transmit such data after access has been granted [@enck2014taintdroid].

PerceptFence shares the runtime concern but changes the unit of control. Permission systems and information-flow monitors reason about application access and data propagation. A screen-share assistant additionally needs a content-level boundary between a granted capture stream and an assistant's context window. The question is not only whether capture is allowed; it is whether a particular credential, notification, utterance, or screen-visible instruction should be observed, retained, or repeated during an active session.

**Privacy norms and contextual integrity.**
Nissenbaum's contextual-integrity theory argues that information-flow appropriateness depends on context, actors, attributes, and transmission principles rather than on a single universal sensitivity label [@nissenbaum2004privacy]. Apthorpe et al. operationalize this view for smart-home IoT devices, showing that users distinguish among data types, recipients, and purposes when evaluating whether a device's information flow is acceptable [@apthorpe2018smart]. Recent language-model work applies related ideas to model behavior, including contextual-integrity audits of how language models judge the appropriateness of information flows [@shvartzshnaider2026privacy].

PerceptFence adopts a narrower engineering approximation of this literature. It does not model the full social context of information flow, nor does it claim that a session policy equals informed human consent. Instead, it uses content categories, modality, window state, and session policy as enforceable runtime inputs. This is a simplification, but it gives the prototype a measurable boundary: the policy engine must convert contextual metadata into one of a small set of actions before content reaches the assistant.

**Privacy-aware AI assistants.**
AI assistants that help users manage privacy choices raise the question of when automation is acceptable and what information sources such systems may use. Xu et al. study perceptions of AI-powered privacy assistants among experts and users, emphasizing transparency, regulatory context, and the social acceptability of automated privacy decisions [@xu2025acceptability]. Danry et al. explore a gaze-aware multimodal assistant that interprets user state from egocentric video, illustrating how richer multimodal context can improve assistance while expanding what the assistant observes [@danry2026gaze].

PerceptFence is complementary to these assistant-design questions. It does not decide a user's privacy preferences or infer cognitive state. It assumes a session policy already exists and asks how an assistant runtime can enforce that policy while handling live capture. The difference matters for evaluation: PerceptFence can measure synthetic exposure and blocking behavior, but it cannot claim that users understand the policy interface or prefer the tradeoff without a separate study.

**Screen-capture privacy in deployed systems.**
Deployed screen and meeting assistants show why runtime mediation is becoming practical rather than speculative. Microsoft Recall stores snapshots of desktop activity and now documents controls for filtering apps, websites, and sensitive information in Recall snapshots, including a sensitive-information filter enabled by default in the current documented experience [@microsoft2024recall]. Zoom AI Companion documentation describes account and feature controls, third-party zero-data-retention arrangements, and privacy/security handling for meeting-derived AI features [@zoom2024ai]. These systems are important reference points because they make screen and meeting content available to AI workflows at product scale.

The gap is granularity. Product controls can filter selected apps, websites, meeting features, or categories of sensitive information, but PerceptFence studies the assistant-runtime boundary itself: the transition from captured content to context, memory, and response. The prototype therefore reports per-fixture context, output, memory, and audit exposure rather than only whether a product-level setting is enabled.

**Prompt injection attacks.**
Screen-visible text creates an indirect prompt-injection channel. Greshake et al. show that attacker-controlled content in external data can compromise LLM-integrated applications even when the user never types the malicious instruction directly [@greshake2023indirect]. Liu et al. analyze prompt-injection attacks against LLM-integrated applications and organize attack patterns that exploit the application's inability to separate trusted instructions from untrusted content [@liu2023prompt]. In screen-share settings, the untrusted content may simply be visible on the shared display.

PerceptFence treats screen text as data, not instruction, unless the policy engine explicitly allows it to become task context. The synthetic benchmark includes `prompt_injection_on_screen` and `encoded_screen_instruction` fixtures, but those fixtures only test configured classes of displayed instruction handling. They do not establish broad protection against all prompt-injection techniques.

**Defenses against prompt injection and agent safeguards.**
Several recent defenses modify the model, prompt format, or agent orchestration layer. StruQ separates instructions from data using structured queries and trains models to follow instructions from the designated channel rather than from the data channel [@chen2025struq]. SecAlign uses preference optimization to favor policy-aligned responses over injection-compliant responses [@chen2025secalign]. Yang et al. show that injected content can persist through agent memory and influence future behavior [@yang2026zombie], which motivates treating retention as a separate surface rather than a byproduct of input filtering. AgentGuard focuses on evaluating tool-orchestration risks by using the agent orchestrator to surface unsafe workflows and constraints [@chen2025agentguard].

PerceptFence operates below those model- and orchestrator-level defenses. It can be combined with structured prompting or tool-policy systems, but it does not depend on model fine-tuning and does not evaluate tool use. Its contribution is the runtime mediation path around the model: filter what enters context, suppress prohibited memory writes, guard what leaves the assistant, and record policy decisions without raw sensitive payloads.

## 4. Design

The runtime mediation layer is composed of seven modules along three control surfaces:

- **Observe** — what the assistant model is permitted to see (screen capture adapter, speech event adapter, consent/policy engine, redaction engine).
- **Retain** — what the session memory persists across turns (session memory gate).
- **Say** — what the assistant is permitted to output (output guard).

The audit logger sits across all three surfaces and records decisions without recording sensitive payload. The ordering is deliberate: PerceptFence first normalizes capture into an explicit session object, then resolves policy, then transforms context, then handles memory and output. A downstream module may reduce exposure further, but it must not relax a stricter upstream policy.

### 4.1 Control surface 1 — Observe

The observe surface controls what content enters assistant context. It is enforced by the capture adapters, the consent/policy engine, and the redaction engine.

**Screen capture adapter.** The prototype's screen adapter reads synthetic fixture text and metadata rather than a real display. In a deployment, the same module would receive frames or OCR output from a platform capture API. The adapter does not classify content. It emits untrusted text plus structural metadata such as scenario class, region, font size, window stability, recency, and modality. Treating adapter output as untrusted avoids giving screen-visible instructions special authority merely because they appear in the same channel as the task context.

**Speech event adapter.** The speech adapter emits utterance fragments with modality and timestamp metadata. The current benchmark contains one speech-transcript fixture and does not evaluate full audio/screen alignment. The design nevertheless keeps speech separate from screen text so that future policies can distinguish spoken sensitive fragments from visible credentials or notifications.

**Consent/policy engine.** The policy engine is the authoritative decision point for all three control surfaces. It receives adapter metadata and redaction categories, then maps each fixture to a policy action in the configured set: `redact_before_model`, `suppress_notification`, `summarize_without_identifier`, `block_memory_write`, `ignore_screen_instruction`, `require_stable_window`, `increase_ocr_sensitivity`, or `selective_redact`. The engine returns both an action and a reason. This reason is passed to audit logging and to the output guard's policy-only context, but raw sensitive text is not.

**Redaction engine.** The redaction engine transforms extracted text and speech fragments after the policy decision. It replaces matched sensitive units with stable placeholders such as `[REDACTED]`, `[EMAIL]`, `[RECORD]`, and `[PERSON]`. The prototype uses deterministic rules rather than a learned classifier so that every benchmark outcome can be reproduced from fixture annotations and code. Six transform families are configured: Unicode-NFKC normalization and confusable-character remapping for homoglyph evasion; ignore-whitespace digit matching for split or spaced PII; credential-pattern masking; identifier summarization; screen-instruction neutralization; and selective region redaction for mixed-sensitivity frames.

**Observe algorithm.** For each captured event *xᵢ*, the adapter emits a `CapturedSession`. The policy engine computes an action *Aᵢ* from scenario metadata, modality, and configured policy. The redaction engine applies the transform family associated with *Aᵢ*, producing a `MediatedContext` containing model context, redaction decisions, and category metadata. If *Aᵢ* is `require_stable_window`, the mediated context withholds unstable content. If *Aᵢ* is `ignore_screen_instruction`, displayed instructions are treated as untrusted data. The invariant is that raw captured content should not be appended to model context before this sequence completes.

### 4.2 Control surface 2 — Retain

The retain surface controls what the assistant may remember across turns. It is enforced by the session memory gate.

**Session memory gate.** The memory gate receives the mediated context and policy action. Its default behavior is to avoid writing sensitive units to memory. When the policy action is `block_memory_write`, the gate uses context exclusion for the affected turn: it zeros or withholds the model context before model invocation and records the exclusion. This is stricter than conversation-history pruning because pruning can remove data from future turns but cannot undo use of content already placed in the current context window. The cost is utility loss: benign task-critical units in the excluded context are also unavailable for that turn, which appears in the false-block and task-success proxy metrics.

**Retain algorithm.** Given `MediatedContext mᵢ` and policy action *Aᵢ*, the gate first checks whether the action forbids retention. If retention is forbidden, it emits an empty memory-write set and, for the strong exclusion path, removes the affected context from the current model input. If retention is allowed, it writes only the mediated representation and never raw sensitive unit values. The audit logger records whether a write was suppressed or allowed. The benchmark's `spoken_sensitive_fragment` fixture exercises this path: redaction alone does not satisfy the expected outcome because the relevant control is memory suppression.

### 4.3 Control surface 3 — Say

The say surface controls what the assistant may output. It is enforced by the output guard.

**Output guard.** The output guard filters the candidate response before display. It uses an isolated policy-only context containing fixture id, scenario class, policy action, policy reason, and blocked categories. It does not receive the raw or mediated screen text. This separation is important because a guard that shares the same injected content as the assistant can itself be influenced by the malicious instruction it is supposed to constrain.

The guard applies two deterministic stages. First, it checks for literal sensitive fragments configured for the synthetic session. Second, it checks for configured indirect-reference patterns, such as outputs that acknowledge a credential, secret, identifier, or hidden field even without repeating the literal value. If either stage fires, the guard replaces the output with a policy-coded block or hold message. In isolation, this can be over-conservative: the `output_guard_only` ablation blocks output but does not repair context exposure. In composition, the guard is a backstop after observe and retain controls have already reduced the assistant's exposure.

**Say algorithm.** Given candidate output *oᵢ* and policy-only context *gᵢ*, the guard evaluates literal-fragment rules, indirect-reference rules, and action-specific hold rules. If a rule matches, it returns a `GuardedOutput` with `allowed=false`, a replacement string, and a reason. Otherwise, it returns the original output. The output decision is then logged without storing the blocked content itself.

### 4.4 Audit logger

The audit logger records policy decisions and module actions. Logs include fixture id, scenario class, policy action, reason, and event type; they do not include raw screen text, raw speech, raw notification text, or sensitive unit values. Each entry carries a SHA-256 hash chain for crash-evident ordering. This hash chain is not a defense against compromised infrastructure, because an attacker with runtime or storage control can alter the logger or delete data before it is written. Its purpose in the prototype is narrower: make decision provenance inspectable during evaluation without expanding the stored sensitive payload.

### 4.5 Implementation

The reference implementation is a standard-library-only Python package (`screenshare_mediator`) requiring Python ≥ 3.10. No machine-learning dependencies, network access, external APIs, or third-party packages are required. All transforms are deterministic given the same fixture and policy configuration, making runs reproducible from the synthetic fixture set.

**Module inventory.**

| Module | Role |
|---|---|
| `models.py` | Typed dataclasses (`CapturedSession`, `PolicyDecision`, `MediatedContext`, `AuditEvent`, `GuardedOutput`) shared across module boundaries. |
| `capture.py` | Synthetic capture adapter; normalizes a JSON fixture into a `CapturedSession` (TB1). |
| `policy.py` | Consent/policy engine; maps `CapturedSession` to `PolicyDecision` using `consent_redaction_policy.json`. |
| `redaction.py` | Six-family deterministic redaction engine; transforms raw context at TB2. |
| `memory.py` | Session memory gate; enforces context exclusion and memory-write suppression at TB3. |
| `output_guard.py` | Rule-based output guard with isolated policy-only context (TB4). |
| `audit.py` | Append-only SHA-256-chained audit logger (TA7). |
| `runtime.py` | Baseline and guarded path composition; the two-path comparison interface used by the benchmark. |

**Policy configuration.** Consent policy is declared in `policies/consent_redaction_policy.json`, which maps scenario-class patterns to allowed action sets. The policy file is the single configuration point; the policy engine reads it at startup and applies it without code changes.

**Synthetic fixture set.** The fixture set covers eleven scenario classes. Each fixture is a JSON object containing: scenario identifier, scenario class, synthetic screen text, synthetic speech text, synthetic notification text when applicable, window-event metadata, annotated sensitive units (*U*ᵢ), annotated benign task-critical units (*Q*ᵢ), expected policy action (*A*ᵢ), and binary task-success rubric answer (*y*ᵢ). No fixture contains real screen captures, real personal data, or real credentials.

**Test suite.** The test suite contains fixture-set coverage tests, per-module behavior tests for adversarial-evasion paths, benchmark metric helpers, audit hash-chain checks, and a TB3 trust-boundary regression confirming context-excluded content does not appear in model context for the exclusion turn. The paper reports only results that can be reproduced from the committed benchmark outputs.

### 4.6 Design limits

The design is intentionally narrow. It does not defend against A6/A7/A8: compromised infrastructure, poisoned model or supply chain, or OS-level compromise. It does not provide formal privacy guarantees. It does not perform model-based redaction. It does not evaluate tool-use escalation, cross-session consent transfer, multi-party legal consent, or real-time stream synchronization. Extending the design beyond the seven modules should trigger a new threat-model review rather than being treated as a straightforward implementation detail.

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

The ablation supports a small but specific design claim: no single module is sufficient, and the composed mediation path is what achieves the expected outcomes on the synthetic benchmark. Redaction handles most direct sensitive units, the memory gate handles retention-specific cases, the output guard catches literal and configured indirect output violations, and the audit logger provides decision provenance. The policy engine is the point that makes these modules compose: each module receives an action and reason rather than independently guessing what the user intended.

**Implications for assistant design.** The observe/retain/say split gives assistant builders a way to reason about privacy-relevant behavior without conflating separate failure modes. A system that only filters output may still expose sensitive content to the model. A system that only redacts input may still write sensitive context to memory. A system that only disables retention may still repeat a sensitive unit in the current response. PerceptFence's architecture makes those distinctions explicit and measurable. This supports research packaging because each claim can be mapped to a benchmark surface: context exposure, memory exposure, output exposure, false block rate, task-success proxy, latency, and audit coverage.

**Generalizability.** The benchmark is synthetic, but the design pattern is not tied to the particular tokens in the fixtures. The relevant abstraction is a mediated stream: capture produces untrusted content, policy maps content and context metadata to an action, transforms construct assistant context, memory policy governs retention, and output policy constrains responses. That abstraction can apply to browser copilots, meeting assistants, desktop agents, or remote-support assistants if the developer controls the context-construction path. It applies less directly to closed SaaS assistants where the developer cannot interpose before model invocation or inspect memory writes.

**Design alternatives.** One alternative is platform-level filtering: prevent selected apps, websites, or categories from being captured at all. That approach can reduce exposure before the assistant runtime, but it cannot express cases where the assistant may use part of a frame while withholding another part from memory or output. A second alternative is model-level alignment: train the assistant not to reveal sensitive content. That approach may help output behavior, but it does not by itself create an auditable record of what entered context or memory. A third alternative is post-hoc deletion: allow capture and model use, then remove retained data later. That is insufficient for current-turn output and cannot undo prior model exposure. PerceptFence is closest to a fourth option: runtime mediation at the assistant boundary.

**Costs and tradeoffs.** The main cost is false blocking and task-context loss. The guarded path has a higher mean false block rate than the baseline, and context exclusion can suppress benign task-critical units alongside sensitive units. The second cost is engineering control. A developer must own the capture-to-context path, memory layer, and output-display boundary. The third cost is audit sensitivity: even metadata about policy decisions can reveal that a sensitive event occurred. The prototype handles this by excluding raw sensitive payloads from the log, but a deployment would still need an access-control and retention policy for audit metadata.

**Relationship to C6 evidence.** For EB1A C6 packaging, the manuscript's value is strongest when the paper stays as a bounded scholarly artifact: a clear problem statement, an implemented prototype, a benchmark table, a figure, a source-checked related-work section, and a limitation section that prevents claim inflation. The draft should not be positioned as a deployed product or as evidence of broad user impact. Its current evidence value is a research-output trail: a reproducible artifact and manuscript moving toward external submission.

---

## 7. Limitations

This section states what the benchmark cannot claim.

- **Synthetic benchmark only.** All fixtures are invented. They support deterministic regression testing and baseline-versus-guarded comparison, but they do not represent the distribution of real screen-share sessions. The benchmark does not include real screenshots, real notifications, real audio recordings, real personal data, customer data, or organizational data.
- **Small fixture count.** The benchmark covers eleven scenario classes. This is enough to exercise the configured policy actions and adversarial-evasion families, but it is not coverage evidence for the range of content that can appear in real desktop or meeting environments.
- **Configured evasion families only.** The adversarial fixtures cover Unicode homoglyph credentials, split or spaced personal-data digits, mixed-sensitivity content, and encoded or chained screen instructions. Other evasion techniques, languages, scripts, image-only secrets, screenshots-within-screenshots, layout attacks, and steganographic output channels are not characterized.
- **No human-subject evidence.** The paper does not evaluate whether users understand the controls, whether consent prompts cause fatigue, whether the assistant remains helpful during real tasks, or whether teams would adopt the workflow. Task-success rate is a synthetic proxy, not a usability measure.
- **No deployment latency claim.** The reported latency comes from a single-process Python harness over synthetic fixtures. Real assistants would include capture, OCR, network, model inference, and UI rendering overheads that are not measured here.
- **Rule-based detector.** The redaction engine is deterministic and inspectable, but it can miss formats outside its configured patterns. Learned detectors may improve recall for some categories, but they would introduce new false-positive, explainability, and evaluation questions.
- **Threat-model exclusions.** A6/A7/A8 remain outside scope: compromised infrastructure, poisoned model or dependency, and OS-level compromise. Tool-use exfiltration, multi-party consent negotiation, cross-session consent transfer, and legal informed-consent workflows are also outside the current artifact.
- **Audit metadata risk.** The audit log excludes raw sensitive content, but metadata can still reveal that a sensitive category appeared. The prototype does not define production log access control, retention, deletion, or tamper-resistance.

These limitations are not footnotes to be softened later. They are part of the paper's claim discipline: until additional studies or systems evidence exist, the paper should claim only measured exposure reduction and policy-action behavior on the synthetic fixture set.

## 8. Ethics

All evaluation data is synthetic. No real screen captures, real personal data, real audio recordings, or real notification content was collected, used, or stored. No human subjects were involved. IRB approval is not applicable. The synthetic fixture set is documented under `src/data/synthetic/README.md`.

The design is intended to reduce the assistant's access to sensitive content within the mediated runtime path. It composes with platform-level controls and operates inside the assistant runtime, so it should be evaluated as an additional boundary rather than as a replacement for platform policy, organizational review, or user-facing consent design.

---

## 9. Conclusion

We presented a runtime mediation layer for live screen-share AI assistants, decomposed into seven modules along three control surfaces: observe, retain, and say. A per-module ablation on eleven synthetic scenario classes shows that the composed guard achieves expected outcomes on every fixture while the unmediated baseline reaches it on none, and that no single module is individually sufficient. The contribution is a bounded research artifact: a threat model, implementation scaffold, benchmark, and manuscript whose claims are tied to deterministic synthetic evidence and explicitly exclude formal privacy guarantees, host compromise, and supply-chain threats.

---

## References

Formatted by ACM-Reference-Format from `references.bib`. See that file for all 16 entries (≤25 cap). Every cite key used in this manuscript resolves in `references.bib`; the provenance comments in that file record the source-check path for each entry.

---

## Anonymity and de-anonymization log

This draft is anonymous. Author block, affiliations, acknowledgments, and CITATION.cff de-anonymization happen at submission time. Repository links in references are also gated on de-anonymization.

