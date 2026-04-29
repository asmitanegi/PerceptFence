# Policy Boundaries — PerceptFence Runtime Mediation Layer

**Source:** Security review for NEE-1242
**Date:** 2026-04-26
**Purpose:** Define what each policy module enforces, what it does NOT enforce, and the trust assumptions. This document should be adapted into the paper repo's `policies/README.md` when M3 (repo scaffold) is built.

---

## Consent Policy Engine

**Enforces:**
- Per-content-category opt-in/opt-out decisions (e.g., "share code but not chat messages")
- Session-level consent state (active/paused/revoked)
- Policy persistence across session restarts (consent state must not silently reset)

**Does NOT enforce:**
- Informed consent in the legal/HCI sense — this is a technical access control, not a substitute for IRB-grade informed consent
- Consent on behalf of third parties (if a screen shows another person's data, the data owner has not consented)
- Cross-session consent transfer (consent in session A does not automatically apply to session B)

**Trust assumption:** The user who sets the policy is the data controller for everything on their screen. This is a simplification — in practice, shared screens show other people's data.

---

## Redaction Engine

**Enforces:**
- Pattern-based detection and masking of known sensitive data categories: credentials (synthetic credential strings), PII (SSN, email, phone, address), and financial data (card numbers, account numbers)
- Configurable sensitivity levels per category
- Redaction BEFORE content enters the LLM context (not post-hoc)

**Does NOT enforce:**
- Detection of novel/unknown credential formats
- Detection of sensitive data that is semantically but not syntactically identifiable (e.g., "the code to the safe is the year I was born" contains no pattern-matchable secret)
- Adversarial evasion resistance (Unicode homoglyphs, character splitting, encoding tricks) — unless specific evasion tests are added to the benchmark
- Redaction of data in images/screenshots embedded within the shared screen (requires OCR + secondary redaction pass)

**Trust assumption:** The redaction engine is only as good as its pattern/model coverage. False negatives are expected and must be reported in the benchmark.

---

## Session Memory Gate

**Enforces:**
- Content exclusion: preventing specific frames/content from entering the LLM context window (strongest mode)
- OR conversation history pruning: removing messages from the chat history after a consent revocation (weaker mode — model may have already encoded the information)

**Does NOT enforce:**
- Erasure of information from the LLM's internal representations (impossible without model retraining or context-window restart)
- Prevention of inferred/summarized references to gated content (the model may say "I recall something about credentials" even after the source message is removed)
- Memory control across model provider boundaries (if the screen-share assistant calls an external API, the memory gate does not control what that API retains)

**Trust assumption:** The LLM is a black box. Memory gating operates at the input level (what goes into the context) and the output level (what the output guard filters), but not at the internal-representation level.

---

## Output Guard

**Enforces:**
- Blocking or sanitizing assistant responses that contain detected sensitive data patterns
- Blocking responses that reference redacted content by category (e.g., "I saw a credential string" is a policy violation even without the key itself)
- Response-level policy enforcement: the assistant's output must comply with the current consent state

**Does NOT enforce:**
- Detection of steganographic or encoded leakage (e.g., first letters of sentences spelling out a secret)
- Detection of all indirect disclosure forms (the assistant can still leak information through implication, contrast, or metadata)
- Protection against prompt injection that targets the output guard itself (if the guard is LLM-based and shares context with the assistant)

**Trust assumption:** The output guard is a best-effort filter. It reduces leakage probability; it does not eliminate it. The benchmark must measure both direct and indirect leakage.

---

## Audit Logger

**Enforces:**
- Recording of all policy decisions: what was shown, what was redacted, what consent state was active, what the assistant said
- Append-only logging within a session (new entries are appended, not overwritten)
- Structured log format for post-hoc analysis

**Does NOT enforce:**
- Tamper evidence or tamper resistance (an attacker with write access can modify logs)
- Confidentiality of log contents (the log itself contains metadata about sensitive data — access control is the deployer's responsibility)
- Real-time alerting on policy violations (the logger records; it does not act)
- Completeness guarantee (if the mediation layer crashes, the last few entries may be lost)

**Trust assumption:** The audit log is trustworthy only if the infrastructure is trustworthy. The paper must NOT claim the log provides accountability without stating this assumption.

---

## Policy Interaction Matrix

| Module A | Module B | Interaction | Risk |
|----------|----------|-------------|------|
| Consent engine | Redaction engine | Consent state determines which categories are active for redaction | If consent is downgraded, redaction categories shrink — the user sees more, but so does the LLM |
| Redaction engine | Memory gate | Redacted content should not enter memory; but if redaction fails (false negative), the memory gate has no second chance to catch it | Single point of failure on the redaction step |
| Memory gate | Output guard | Even if memory gate removes content, the output guard must still filter in case the LLM references residual information | Defense in depth — both layers must operate independently |
| Output guard | Audit logger | Output guard decisions are logged; but if the output guard passes a leak, the logger records it without blocking it | The logger is not a safety control — it is an observability control |
| Consent engine | Audit logger | Consent changes are logged; consent revocation triggers memory gate and redaction updates | Consent revocation must be atomic: if consent is revoked, all downstream modules must update before the next frame is processed |
