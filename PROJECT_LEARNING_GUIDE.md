# PerceptFence — Your Project Learning Guide

> **Status (2026-09-27):** the v0.3 manuscript was submitted to the *International Journal of Information Security* on 2026-09-07 and declined on 2026-09-09 ("results too premature"). v0.4.0 adds the rendered-screen evaluation in response and is posted as a preprint. IJIS-specific instructions below are kept as a record of that submission.

## Start here: what you are building

You are building a bounded runtime mediation architecture for AI assistants that can see a shared screen and hear meeting content. The central problem is simple to state but easy to mishandle:

> A screen-share assistant should not receive, retain, or disclose every piece of content that happens to appear during a session.

PerceptFence separates that problem into three controls:

1. **Observe:** what content may enter the assistant's context?
2. **Retain:** what content may be written to session memory?
3. **Say:** what content may leave through the assistant's output?

Your paper's contribution is not a claim that you have built a production screen-sharing product. You have built and evaluated a content-layer mediation architecture plus a deterministic reference scaffold that makes these control boundaries executable, inspectable, and reproducible.

## The one-minute explanation you should be able to give

When someone asks what PerceptFence does, you can say:

> You treat screen and speech content as untrusted input. Before that content reaches an assistant, a policy decision selects a bounded mediation action. The system then sanitizes or excludes content, controls whether it may enter memory, checks the assistant's candidate output in a separate policy-only context, and records content-minimized decision metadata in a hash chain. You evaluate the deterministic redaction surface on synthetic adversarial cases, report where it works, and report where it does not.

That explanation is accurate because it names the real artifact and does not overclaim live deployment, formal privacy, general robustness, or complete leakage prevention.

## Why the problem matters

A live screen can expose sensitive information without the user intentionally giving it to an AI system:

- a terminal can reveal an API key;
- a browser can show names, emails, record identifiers, payment-card data, or an SSN;
- a private notification can appear over a permitted application;
- another participant can display adversarial instructions;
- a secret can be spoken even when the visible screen is benign;
- sensitive content can flash during fast window switching;
- a mixed screen can contain one consented pane and one non-consented pane.

A single on/off permission such as “allow screen access” cannot express these distinctions. Your architecture therefore treats consent as runtime policy state at a finer content boundary.

## The architecture you need to understand

### 1. Capture adapters produce untrusted session content

The synthetic capture path reads a fixture and constructs the raw session context. In the target architecture, screen and speech adapters would sit at this boundary. In the released artifact, there is no live screen capture, microphone integration, OCR service, or production assistant connection.

Your first trust rule is:

> Raw captured content is untrusted until policy and mediation have completed.

### 2. The policy engine chooses an allowed action

`ConsentPolicyEngine` maps each synthetic scenario class to one fixed action. Examples include:

- `redact_before_model`
- `suppress_notification`
- `summarize_without_identifier`
- `block_memory_write`
- `ignore_screen_instruction`
- `require_stable_window`
- `increase_ocr_sensitivity`
- `selective_redact`

The policy file defines which actions are allowed. The engine rejects a mapped action if it is outside that allowlist.

This is an executable policy-routing scaffold. It is not category inference from arbitrary real-world content, an authenticated consent service, or a complete policy language.

### 3. The redaction engine constructs mediated model context

`RedactionEngine` normalizes and sanitizes text before returning model context. Its deterministic controls include:

- credential and bearer-token masking;
- Unicode normalization and selected Cyrillic/Greek confusable folding;
- zero-width and split-digit handling;
- SSN recognition;
- Luhn-validated payment-card recognition;
- email, record, and name summarization;
- prompt-injection line replacement;
- non-consented pane removal;
- stable-window holding behavior.

The important design choice is **normalization before matching**. Attackers can insert spaces, zero-width characters, or visual lookalikes so that a naive regex no longer sees the original token. Normalization reconstructs a comparable representation before deterministic rules run.

The equally important limitation is that the rule set is deliberately incomplete. Base64, hex, ROT13, leetspeak, bidirectional-text attacks, and instruction wrapping are declared out of coverage for the current redactor. You report these misses rather than hiding them.

### 4. The memory gate excludes non-retainable content before the assistant call

`SessionMemoryGate` implements the strongest mode used by this artifact: if a policy blocks memory, the mediated content is removed from the current assistant context before generation. This is not a prompt asking a model to “forget,” and it is not post-hoc deletion after the model has already seen the content.

You should remember this distinction:

> Preventing content from entering context is stronger than deleting it from history later.

The artifact is still per-invocation. It does not implement cross-session memory, a durable memory store, retention periods, or authenticated memory administration.

### 5. The output guard controls what the assistant may say

The deterministic assistant stub creates a candidate response. `OutputGuard` then evaluates that candidate using only:

- the candidate output;
- the scenario class;
- the selected policy action;
- policy reason and blocked categories.

It does not receive the raw or mediated screen context. That isolation matters because a screen instruction should not be able to influence both the generator and the guard through a shared context.

The guard blocks known literal sensitive fragments, indirect disclosure patterns, and unstable-window output. This is a deterministic scaffold, not proof that every possible paraphrase, encoding, inference, or side channel is blocked.

### 6. The audit logger records decisions without raw content

`AuditLogger` records policy, context-exclusion, and output-guard metadata. It intentionally does not store raw screen text, speech, model context, or assistant output. Each event includes a SHA-256 chain from the previous event.

The right claim is **crash-evident or edit-detectable within the recorded chain**, not tamper-proof. An attacker with code execution on the host could rewrite events and recompute the chain.

## The end-to-end execution path

For one guarded fixture, follow this sequence:

1. `SyntheticCaptureAdapter.capture()` creates the captured session.
2. `ConsentPolicyEngine.decide()` chooses a permitted action.
3. `RedactionEngine.mediate()` sanitizes or transforms the content.
4. `SessionMemoryGate.exclude_from_context()` removes non-retainable content before the assistant call.
5. `SessionMemoryGate.maybe_write()` records a synthetic session-memory write only when allowed.
6. `AuditLogger` records the policy decision and any context exclusion.
7. `assistant_candidate_output()` creates a deterministic candidate response.
8. `OutputGuard.context_from_policy()` creates an isolated policy-only guard context.
9. `OutputGuard.guard()` decides whether to allow, block, or hold the candidate.
10. `AuditLogger` records the output-guard decision.
11. `RuntimeResult` returns the mediated context, final output, memory writes, and audit metadata.

When you inspect `screenshare_mediator/runtime.py`, this entire path is visible in one method: `RuntimeMediator.run_guarded()`.

## What the evaluation actually proves

You have three different evidence layers. Do not merge them into one headline.

### Layer 1: the 11-fixture configuration-consistency check

The fixture suite verifies that the modules produce the outcomes they were configured to produce. The full guard reaches the configured outcome on 11 of 11 synthetic scenarios. Unit-weighted sensitive-exposure rate falls from 1.000 to 0.000, with a false-block rate of 0.143, or 2 of 14 benign units.

This is useful implementation evidence, but it is not an independent robustness benchmark. You and Asmita authored the fixtures, expected outcomes, and rules.

### Layer 2: the 9,600-case deterministic coverage census

The held-out harness generates 480 payload-bearing cases for each of 20 seeds, producing 9,600 cases across 11 literature-informed evasion families. A separately implemented exposure oracle checks whether the canonical secret, or a recoverable contiguous portion of it, survives after mediation.

The oracle shares no imports with the redactor and adds decoding paths, but it was designed in the same project. Therefore, call it **separately implemented**, not independent or strictly stronger.

Across the paired five seeds used for the real Microsoft Presidio comparison:

- PerceptFence overall recall: **0.398**
- Microsoft Presidio overall recall: **0.260**
- naive no-normalization baseline: **0.140**

This overall comparison is only indicative because the census includes credentials and prompt-injection payloads outside Presidio's PII purpose. In the declared out-of-coverage families, Presidio leads PerceptFence **0.238 to 0.154**.

### Layer 3: the like-for-like digit-PII comparison

Your strongest defensible comparative result is the category both systems are designed to handle:

- PerceptFence: **0.828**
- Microsoft Presidio: **0.183**
- naive matcher: **0.000**

This isolates normalization handling on digit PII. It is the result to lead with because it is category-aligned and uses the same generated cases for all three systems.

You should not turn 0.828 into “complete protection.” The result means the deterministic PerceptFence redactor neutralized 82.8% of payloads under the paper's declared oracle and census for that comparison.

## What you may claim

You may say that:

- PerceptFence is a content-layer runtime mediation architecture.
- The reference artifact executes policy, redaction, memory gating, output guarding, and content-minimized audit actions deterministically.
- Normalization before matching improves recall on targeted evasion families in the synthetic census.
- PerceptFence reaches 0.828 recall versus Presidio's 0.183 on the like-for-like digit-PII comparison.
- The evaluation explicitly separates in-coverage and out-of-coverage behavior.
- The artifact, tests, protocol, result CSVs, figure generators, and dependency pins support reproduction.

## What you must not claim

Do not claim that the current artifact:

- is a production or live screen-share assistant;
- is formally privacy-preserving;
- prevents every form of leakage;
- is generally robust to unknown attacks;
- performs real-time capture or mediation with measured latency;
- recognizes arbitrary content categories;
- supplies authenticated re-consent;
- protects against a compromised host, poisoned model, or malicious dependency;
- provides cross-session memory governance;
- proves usability or user trust without a user study;
- introduces a novel general-purpose redaction algorithm.

These boundaries make the paper stronger, not weaker. Reviewers can see exactly what was built, tested, and left for future work.

## Your threat model

Keep the adversaries separated:

### In scope

- **A1 — malicious screen content:** displayed content contains instructions intended to manipulate the assistant.
- **A2 — malicious meeting participant:** another participant displays sensitive content or pushes for unauthorized disclosure.
- **A3 — policy downgrade attempt:** a user tries to relax runtime controls beyond the allowed policy.
- **A4 — assistant output leakage:** the assistant repeats or indirectly references gated content.
- **A5 — temporal exposure:** sensitive content appears briefly during popups, zoom changes, or window switching.

### Out of scope for this paper

- **A6 — compromised infrastructure:** an attacker controls logs, runtime state, storage, or backend services.
- **A7 — poisoned model or supply chain:** the model, dependency, or capture stack is malicious.
- **A8 — operating-system compromise:** the host OS, display server, microphone, or clipboard is controlled by an attacker.

## How to reproduce the artifact

From the repository root, your shortest verification path is:

1. Run `./reproduce.sh`.
2. Confirm the unit-test stage reports **42 passed**.
3. Confirm the smoke stage reports **11 synthetic scenarios**.
4. Confirm submission verification reports **9/9 gates passed**.

The core implementation uses the Python standard library. The full Microsoft Presidio comparison uses the pinned optional evaluation environment described in `requirements-eval.txt` and the held-out protocol.

When you read the evidence, start with:

1. `README.md` for orientation and reproduction.
2. `PAPER_MAP.md` for claim-to-evidence mapping.
3. `policy-boundaries.md` for what each module does and does not enforce.
4. `screenshare_mediator/runtime.py` for the complete guarded path.
5. `eval/metrics.md` for metric definitions and evidence interpretation.
6. `eval/heldout/PROTOCOL.md` for the census, oracle, and amendment history.
7. `paper/main.tex` or the frozen blinded PDF for the submission narrative.

## What is already complete for the paper

You already have:

- a 43-page blinded manuscript PDF;
- an identity-bearing title page;
- a cover letter;
- a blinded LaTeX source ZIP;
- an Additional file 1 reproducibility ZIP;
- machine-readable metadata and a portal paste packet;
- SHA-256 checksums;
- both authors and ORCIDs on identity-bearing surfaces;
- equal-contribution language;
- funding, competing-interest, ethics, data-availability, and AI-tool-use disclosures;
- a public GitHub artifact and Zenodo DOI;
- passing tests, reproduction, and submission gates.

This means the technical package is **submission-ready**. It does not mean the article has been submitted, accepted, or published by the journal.

## What you need to do now

Only you and Asmita can complete the authorship and submission decisions below.

### Before the final click

1. Read the frozen IJIS PDF as an author, not as an editor looking for endless improvements.
2. Ask Asmita to approve the exact manuscript and confirm that:
   - she consents to submission;
   - the author order is `Asmita Negi; Neeraj Kumar Singh Beshane`;
   - both authors contributed equally;
   - the contribution statement is accurate;
   - the funding and competing-interest declarations are accurate;
   - her email and ORCID are correct.
3. Confirm your corresponding-author email and ORCID.
4. Confirm the manuscript's public Zenodo/GitHub disclosure and Independent Researcher affiliations.

### In Springer Nature Snapp

1. Open `https://submission.nature.com/new-submission/10207/3`.
2. Select **International Journal of Information Security → Regular Contribution**.
3. Use the prepared metadata packet; do not rewrite the abstract in the portal.
4. Add Asmita first and you second; mark yourself as corresponding author.
5. Upload the single-blind source ZIP as the main manuscript.
6. Upload Additional file 1 as supplementary material.
7. Paste the held cover letter only after both authors approve it.
8. Preview the assembled submission and require both author identities, Independent Researcher, the public DOI, all figures/tables/references, and zero employer identity.
9. Make the final legal/ethical declarations yourself, then submit.
10. Record the manuscript number and submission date in `private/STATUS.md`.

### After submission

To become a published paper, the manuscript must still pass:

1. editorial scope and format screening;
2. peer review;
3. author revisions and response-to-reviewers rounds;
4. acceptance;
5. publisher proof review, licensing, and any publication-charge decision;
6. online publication with a journal DOI.

Do not confuse the current Zenodo artifact DOI with a journal-article DOI. Zenodo archives the research artifact; the journal DOI exists only after publication.

## Your learning path

### In 20 minutes

- Read this guide through “What the evaluation actually proves.”
- Open `runtime.py` and trace `run_guarded()` once.
- Memorize the strongest result: **0.828 vs 0.183 on like-for-like digit PII**.

### In 60 minutes

- Read `PAPER_MAP.md`.
- Read `policy-boundaries.md`.
- Inspect one fixture from each major scenario class.
- Run `./reproduce.sh` and watch the three validation stages.

### In 90–120 minutes

- Read the IJIS manuscript.
- Compare the abstract's claims with the limitations section.
- Inspect `generator.py`, `oracle.py`, and the committed result CSVs.
- Practice explaining why the overall 0.398 vs 0.260 comparison is indicative while 0.828 vs 0.183 is the defensible headline.

## Questions to ask this NotebookLM notebook

Use these prompts to learn actively:

1. “Teach me the PerceptFence execution path from raw fixture to final assistant output, and cite each source.”
2. “Why is observe/retain/say more precise than a single screen-access permission?”
3. “Explain the difference between the 11-fixture check and the 9,600-case census.”
4. “Why is 0.828 vs 0.183 the headline, while 0.398 vs 0.260 is only indicative?”
5. “Show me every explicit non-claim and the evidence boundary behind it.”
6. “Quiz me on the threat model and tell me when my answer overclaims.”
7. “Walk me through the exact files uploaded to Springer Nature Snapp.”
8. “Role-play a skeptical reviewer and make me defend the oracle, protocol amendment, and Presidio comparison.”
9. “Give me a five-minute author explanation of PerceptFence in second person.”
10. “Ask me ten questions that I should be able to answer before I approve submission.”

## Glossary

- **Content-layer mediation:** controls applied to captured content before it reaches or leaves an assistant.
- **Observe:** permission for content to enter assistant context.
- **Retain:** permission for content to enter session memory.
- **Say:** permission for content to appear in assistant output.
- **Normalization:** transforming evasive representations into a comparable form before matching.
- **Sensitive exposure rate:** the fraction of sensitive evaluation units that remain exposed.
- **Recall / neutralization rate:** the fraction of payloads the defense neutralizes under the declared oracle.
- **False-block rate:** the fraction of benign task-critical units removed or blocked.
- **In coverage:** an evasion family for which the current redactor declares a corresponding rule.
- **Out of coverage:** a declared evasion family with no corresponding current rule.
- **Separately implemented oracle:** an evaluator that shares no implementation imports with the redactor but was still designed by the same project authors.
- **Single-blind manuscript:** the current review PDF with author identity visible to reviewers; the repository-safe default build remains identity-hidden.
- **Additional file 1:** the reproducibility artifact submitted alongside the manuscript.

## The sentence to keep

> You are not claiming that PerceptFence solves screen-share privacy. You are showing how observe, retain, and say can be separated into enforceable runtime boundaries, then measuring one deterministic implementation honestly enough that readers can see both its gain and its failure surface.
