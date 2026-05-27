# Security & Threat-Model Review — PerceptFence

**Reviewer:** Anonymous internal security review
**Date:** 2026-04-26
**Paper:** "Design and evaluation of a consent-aware runtime layer for real-time screen-share assistants"
**Review scope:** Threat-model completeness, adversary coverage, system-design risks, and claim guardrails
**Status of paper:** M1 venue/thesis lock. Abstract, outline, title, venue checklist, non-targets, and source scaffold (`src/`) exist; no LaTeX draft exists yet.

---

## 1. Threat Model

The paper proposes a runtime mediation layer with seven modules: screen capture adapter, speech event adapter, redaction engine, consent/policy engine, session memory gate, output guard, and audit logger. The paper should make the adversary model explicit before describing the design, because the contribution is only meaningful relative to the risks it chooses to handle.

### 1.1 Adversary Models

Section 2 should include a compact table that separates in-scope runtime threats from excluded systems-security threats.

| Adversary | Description | In scope? | Rationale |
|-----------|-------------|-----------|-----------|
| **A1: Malicious screen content** | An attacker controls text or visual content shown on the shared screen, including instructions meant to manipulate the assistant. | Yes — primary | Prompt injection through displayed content is the central screen-share-specific risk. |
| **A2: Malicious meeting participant** | A participant deliberately displays sensitive content or prompts the assistant to reveal content outside another participant’s consent. | Yes | Tests whether consent and output policies hold when another participant is adversarial. |
| **A3: Curious or over-privileged user** | The assistant user tries to lower consent, redaction, or retention settings to expose more data than the policy allows. | Yes | Distinguishes enforceable runtime policy from advisory user preferences. |
| **A4: Assistant output leakage** | The assistant repeats, summarizes, infers, or indirectly references content that should have been redacted or gated. | Yes | Motivates the memory gate and output guard, while forcing precise claims about their limits. |
| **A5: Temporal exposure** | Sensitive content appears briefly during window switches, popups, zoom changes, or small-font rendering. | Yes | Matches the planned synthetic scenarios and tests whether mediation works under changing context. |
| **A6: Compromised infrastructure** | An attacker can read or modify audit logs, session storage, runtime state, or backend services. | No for this paper | Reasonable exclusion for the current prototype, but the paper must avoid tamper-evidence or infrastructure-hardening claims. |
| **A7: Poisoned model or supply chain** | The underlying model, dependency, or capture stack is malicious or backdoored. | No for this paper | This is a broader systems-security problem and should be named as out of scope. |
| **A8: Operating-system compromise** | Malware or an attacker controls the host operating system, display server, microphone stack, or clipboard. | No for this paper | Runtime mediation cannot defend against a compromised host without a different trusted-computing design. |

### 1.2 Attack Surface by Module

#### Screen Capture Adapter

- **Threat:** The adapter is the first trust boundary. A captured frame can contain sensitive data, adversarial instructions, or both.
- **Required design statement:** Captured frames and extracted text should be treated as untrusted input until the policy and redaction stages complete.
- **Evaluation gap:** Synthetic fixtures should include concrete prompt-injection payloads embedded in screen content, not only a broad “prompt-injection text” category.

#### Speech Event Adapter

- **Threat:** Spoken sensitive fragments can conflict with screen permissions, reveal content that is not visible, or cause the assistant to expose gated screen context in response.
- **Required design statement:** The paper should state whether consent is per-session, per-modality, per-speaker, or per-content category.
- **Evaluation gap:** At least one fixture should test audio/screen conflict, such as a permitted screen with a spoken secret or a sensitive screen with benign speech.

#### Redaction Engine

- **Threat: false negatives.** The detector can miss novel credential formats, obfuscated personal information, non-English text, screenshots-within-screenshots, or low-resolution text.
- **Threat: false positives.** Over-redaction can block legitimate assistance and lower task completion.
- **Threat: adversarial evasion.** Attackers can use Unicode homoglyphs, zero-width characters, spacing, casing, or image rendering to evade pattern checks.
- **Required design statement:** The paper should characterize whether redaction is pattern-based, model-based, or hybrid, then report detection rates by evasion type when benchmark results exist.
- **Claim constraint:** Do not claim complete redaction or leakage prevention. Use measured language such as “reduced sensitive exposure on the synthetic benchmark,” with numbers once available.

#### Consent / Policy Engine

- **Threat: policy downgrade.** A user or participant may try to relax policies during a session to reveal more content.
- **Threat: policy confusion.** Mixed-sensitivity frames can include permitted work content and non-permitted personal content at the same time.
- **Threat: consent fatigue.** Excessive prompts can train users to approve every request.
- **Required design statement:** Define the policy granularity: per-frame, per-region, per-window, per-modality, per-content type, or some combination.
- **Evaluation gap:** Include at least one mixed-sensitivity screen in the synthetic benchmark.

#### Session Memory Gate

- **Threat: context residual.** If sensitive content has already entered the assistant context, later deletion from session memory does not prove the model did not use it in the current response.
- **Threat: indirect leakage.** The assistant can leak the existence, category, length, format, or implications of gated content without repeating it verbatim.
- **Required design statement:** Define “memory control” precisely. The strongest design prevents gated content from entering assistant context; weaker designs only remove it from future turns or instruct the model not to use it.
- **Claim constraint:** Do not claim that the assistant cannot remember redacted content unless the architecture excludes that content before model invocation and the evaluation measures downstream references.

#### Output Guard

- **Threat: indirect disclosure.** The assistant might say that a secret exists, describe its prefix, or reveal enough metadata to reconstruct it.
- **Threat: encoding.** Sensitive content can be embedded in acrostics, code comments, URLs, formatting, or summaries.
- **Threat: shared-context bypass.** If the output guard uses the same model context as the assistant, a screen prompt injection can influence both generation and guarding.
- **Required design statement:** State whether the output guard is rule-based, model-based, or hybrid. If model-based, it should use a separate context from the potentially injected screen content.
- **Evaluation gap:** Test indirect-disclosure cases, not only verbatim repetition.

#### Audit Logger

- **Threat: log as sensitive surface.** Logs can reveal what was shown, where redaction occurred, what policies fired, and what the assistant said.
- **Threat: log integrity.** Without an integrity design, logs can be altered after a leak.
- **Required design statement:** Define whether logs contain raw content, redacted content, coordinates, policy decisions, hashes, or metadata only.
- **Claim constraint:** “Audit logging records policy decisions for post-hoc review” is acceptable. Avoid accountability, forensic, or tamper-evidence claims unless the design adds access-control and integrity guarantees.

### 1.3 Cross-Cutting Threats

| Threat | Description | Mitigation the paper should discuss |
|--------|-------------|-------------------------------------|
| **Latency-induced bypass** | If mediation is slow, the system may fall back to unmediated passthrough for usability. | Measure latency overhead and document whether any bypass mode exists. |
| **Multimodal conflict** | Audio and screen streams can carry different sensitivity levels or contradictory instructions. | Define per-modality policy semantics and report whether evaluation covers conflicts. |
| **Tool-use escalation** | A prompt injection could instruct a tool-enabled assistant to exfiltrate information through files, code execution, or network calls. | State whether tool use is in scope. If not, exclude it explicitly. |
| **Audit-data minimization** | Recording every decision can itself increase retained sensitive metadata. | Specify log retention and content-minimization choices. |

---

## 2. Claim Guardrails

Every claim in the abstract, introduction, and conclusion should map to a planned or completed metric. If the metric does not exist yet, the claim should remain planned rather than achieved.

### 2.1 Banned Terms Unless Backed by Measurement

| Term | Risk | Safer phrasing |
|------|------|----------------|
| “safe” | Implies no residual risk. | “reduces measured exposure” |
| “secure” | Implies adversary-proof behavior without formal evidence. | “enforces policy-mediated controls” |
| “private” / “privacy-preserving” | Implies absence of leakage through content, metadata, and side channels. | “privacy-mediating” or “consent-aware” |
| “trustworthy” | Makes a social and user-study claim. | “policy-transparent” or “auditable” if measured |
| “prevents leakage” | Makes an absolute prevention claim. | “reduces measured leakage rate by X on Y” |
| “first” / “first-ever” / standalone “novel” | Requires exhaustive related-work support. | “To our knowledge, among the first to evaluate...” only after citation review |
| “verified” | Implies formal verification. | “evaluated on synthetic benchmarks” |
| “useful” / “usable” | Requires user-study evidence. | “maintains task completion rate of X on synthetic tasks” |
| “comprehensive” / “complete” | Implies full coverage. | “covers N categories of sensitive content” |
| “real-time” without latency bounds | Reviewers need an operational definition. | “with median latency overhead of X ms and p95 of Y ms” |
| “robust” without an adversary and metric | Leaves the threat model unspecified. | “reduces leakage under N evasion scenarios” |

### 2.2 Claim-to-Metric Mapping

| Permitted claim pattern | Required metric |
|-------------------------|-----------------|
| Reduced sensitive exposure | Sensitive exposure or leakage rate, baseline versus mediated condition |
| Low false block rate | False block rate by scenario category |
| Bounded latency overhead | Median, p95, and p99 latency overhead |
| Maintained task completion | Task completion rate, baseline versus mediated condition |
| Detection of N sensitive-content categories | Per-category detection rate |
| Logged policy decisions for review | Audit-log completeness: percentage of decisions recorded |
| Reduced indirect disclosure | Indirect-reference rate under adversarial prompts |

### 2.3 Specific Claim Risks

1. **“Consent-aware” is defensible** if the paper defines consent as policy state, not as a validated model of informed human consent.
2. **“Runtime mediation” is defensible** because it describes the architecture.
3. **“Multimodal” needs modality evidence.** If the prototype only evaluates screen frames, call the evaluation visual-only and reserve multimodal language for design intent.
4. **Synthetic-only evaluation should be explicit.** The paper can state that synthetic scenarios represent selected risk categories, while generalization to production screen-share environments remains a limitation.

---

## 3. Architectural Security Recommendations

These recommendations apply to the prototype and paper structure.

1. **Treat screen and speech content as untrusted input.** Redaction and policy checks should run before content enters assistant context.
2. **Separate output guarding from assistant generation.** A guard that shares the same injected context as the assistant should not be presented as an independent safeguard.
3. **Prefer context exclusion for memory gating.** Prompting a model to forget is not equivalent to preventing content from entering context.
4. **Define the audit-log access model.** State who can read logs, what logs contain, and whether logs can reconstruct redacted content.
5. **Add adversarial evasion fixtures.** Include prompt injection embedded in screen text, Unicode homoglyph credentials, and split or spaced personal data.
6. **Document fallback behavior.** If mediation fails or times out, state whether the assistant blocks, degrades, or passes content through.

---

## 4. Verdict

The project is well-scoped for a synthetic, blind-review-safe research paper. No threat-model issue blocks M1. The main follow-up is to incorporate the adversary table, memory-gate precision, prompt-injection emphasis, and claim-to-metric mapping into the outline, prototype design, and benchmark plan.

**Risk rating:** No M1 blocker. Incorporate the review before M2 and M4 exit tests.

---

## 5. Exit-Test Additions

Add this claim-language check to the M2 exit test:

```bash
grep -iE '(^|[^-])\b(safe|secure|private|privacy.preserving|trustworthy|prevents? leakage|first.ever|novel |verified|useful|usable|comprehensive|complete|robust)\b' paper/abstract.md paper/outline.md
```

Any hit should either map to a metric in `eval/metrics.md` or be removed.

Add the same check to the M5 paper draft once `paper/paper.tex` exists.
