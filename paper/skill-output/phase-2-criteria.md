# Phase 2 — Dynamic Criteria Framework

**Run date:** 2026-04-26 America/Los_Angeles  
**Top-level categories:** 12  
**Sub-criteria count:** 156  
**Distribution:** 13 sub-criteria per category.  
**Purpose:** scaffold-mode review checklist for PerceptFence before any Phase 5+ generation.

## Grounding coverage

- IUI 2027 CFP: criteria A3, H13, K3, K5, K8.
- ACM `acmart` format: criteria K1–K4.
- Blind-review hygiene: criteria J1–J13.
- GenAI disclosure: criteria K5–K7.
- Ethics note: criteria K8–K9.

## A. Venue fit and contribution framing

**Grounding:** IUI 2027 CFP

1. Explicitly state the paper as an intelligent-interface systems contribution, not a product announcement.
2. Link the problem to live screen and speech observation in real-time assistance.
3. Map the contribution to IUI topics: generative AI interfaces, privacy/security of IUI, multimodal assistants, and user steering.
4. Use the frozen three-line thesis verbatim across abstract, README, and slide 1.
5. Keep the article title aligned with runtime mediation and screen-share assistants.
6. Explain why coarse chatbot settings are insufficient for fast-changing screen context.
7. Separate design contribution from empirical contribution until benchmark outputs exist.
8. Name synthetic-only scope in the introduction and limitations plan.
9. Define the runtime unit of analysis: session, screen event, speech event, memory write, and assistant output.
10. Explain how practical/societal impact is addressed without overstating deployment impact.
11. Avoid claiming real-world deployment benefit before real-user evidence exists.
12. Frame the work as consent-aware policy mediation rather than as a blanket privacy guarantee.
13. Include a clear non-goals paragraph early in the manuscript skeleton.

## B. Runtime mediation problem formulation

**Grounding:** project thesis

1. Define observe, retain, and say as distinct control surfaces.
2. Identify where raw screen frames and speech fragments enter the system.
3. Describe why runtime context changes can invalidate static permissions.
4. State that all captured content is untrusted before mediation.
5. Specify what counts as model context, session memory, and user-visible output.
6. Define consent as runtime policy state rather than validated human consent quality.
7. Clarify whether consent controls apply per session, window, region, modality, and output type.
8. Explain how mediation composes with baseline assistant behavior.
9. Distinguish accidental exposure from adversarial screen content.
10. Name the latency/utility tradeoff created by mediation.
11. Specify failure behavior for policy ambiguity or mediation timeout.
12. Define when content is held, redacted, summarized, blocked, or passed.
13. Make the threat boundary visible before system architecture details.

## C. Consent and policy model

**Grounding:** project thesis

1. List policy fields for allowed observation, retention, and output disclosure.
2. Define default-deny or default-limited behavior for unknown content classes.
3. Support modality-specific policy decisions for screen text and speech transcript events.
4. Support per-window or per-region restrictions in the planned policy model.
5. Capture user overrides without implying that overrides are ergonomically validated.
6. Model retention permissions separately from observation permissions.
7. Model output permissions separately from input redaction decisions.
8. Log policy decisions without logging raw sensitive text.
9. Handle policy downgrade attempts as an adversarial scenario.
10. Define how policy precedence resolves conflicts among session defaults and local overrides.
11. Keep policy examples synthetic and identity-free.
12. Include policy limitations for ambiguous, non-textual, or OCR-imperfect content.
13. Connect each policy action to a planned metric or smoke-test behavior.

## D. Redaction and input-boundary design

**Grounding:** security review

1. Run redaction before content enters assistant model context.
2. Document the redaction engine inputs, outputs, and metadata side channel.
3. Distinguish deletion, masking, summarization, and hold actions.
4. Preserve enough context for task completion without exposing raw identifiers.
5. Map terminal-secret fixture behavior to redaction action.
6. Map browser-PII fixture behavior to summarization or masking action.
7. Map chat-notification fixture behavior to suppression action.
8. Include expected behavior for small fonts and zoom changes as planned detection constraints.
9. List known regex/pattern limitations without smoothing them away.
10. Avoid claiming full coverage over image-only secrets, handwriting, screenshots, or non-Latin scripts.
11. Attach every redaction claim to code paths or planned benchmark outputs.
12. Define redaction metadata visible to the output guard.
13. Keep raw sensitive sentinels synthetic and non-operational.

## E. Memory-control design

**Grounding:** security review

1. Define session memory as a separate sink from immediate model context.
2. Specify when memory writes are blocked, summarized, or allowed.
3. Ensure memory-gate claims do not rely on prompting a model to forget.
4. Name sensitive speech fragments as a retention-control fixture class.
5. Document residual risk when content reaches immediate context but not memory.
6. Map memory-control decisions to audit events.
7. Define memory expiration or session-boundary assumptions if included.
8. State that long-term personalization effects are outside current evidence.
9. Plan metrics for memory-write count and memory-sensitive-content leakage.
10. Keep memory examples synthetic and review-anonymous.
11. Document whether redacted content can be reconstructed from memory metadata.
12. Include a failure mode for memory gate bypass or policy mismatch.
13. Separate memory policy from output disclosure policy in text and figures.

## F. Output safeguard design

**Grounding:** security review

1. Treat LLM candidate output as untrusted until checked.
2. Keep output guard separated from the same raw or mediated context that influenced generation.
3. Define blocked-output classes such as direct secret repetition and indirect references.
4. Use prompt-injection fixture behavior to test output blocking in smoke mode.
5. Log output decisions with non-sensitive metadata.
6. Define false block rate for benign content.
7. Define indirect disclosure rate for adversarial prompts.
8. Explain residual risk from paraphrase, obfuscation, and multi-turn leakage.
9. Pair output guard behavior with user-visible fallback text.
10. Avoid claiming model alignment; frame the guard as policy-mediated post-processing.
11. Document latency overhead added by output checking as a planned metric.
12. Connect output claims to tests or future benchmark rows.
13. Ensure output examples contain no real secrets or internal strings.

## G. Synthetic fixture coverage

**Grounding:** project scaffold

1. Inventory all fixture classes in `src/data/synthetic/index.json`.
2. Cover terminal secrets with synthetic sentinels only.
3. Cover chat/notification overlays without real Slack/Teams exports.
4. Cover browser personal data using invented names, emails, and record IDs.
5. Cover spoken sensitive fragments using invented transcripts.
6. Cover prompt-injection text displayed on screen.
7. Cover fast window switching and context-stability holds.
8. Cover small-font and zoomed-UI cases as planned visual constraints.
9. Add adversarial evasion cases for Unicode homoglyph credentials.
10. Add adversarial evasion cases for split or spaced personal data.
11. Add adversarial evasion cases for encoded or role-play screen instructions.
12. Include fixture provenance notes confirming synthetic-only generation.
13. Ensure fixture loader can run offline without network or external datasets.

## H. Evaluation and benchmark planning

**Grounding:** IUI 2027 CFP

1. Define sensitive exposure/leakage rate precisely before reporting values.
2. Define false block rate by scenario class.
3. Define latency overhead using median and tail percentiles once benchmark data exists.
4. Define task completion on synthetic tasks without implying real-user utility.
5. Compare baseline and mediated paths for every fixture class.
6. Keep smoke-test output separate from benchmark-result files.
7. Use `eval/results/` as the only location for achieved measurement claims.
8. Record benchmark command, environment, and fixture version.
9. Make benchmark rows reproducible from synthetic fixtures only.
10. Include audit-log completeness as a planned metric.
11. Include prompt-injection success or indirect disclosure rate as a planned metric.
12. Flag any missing metric file at the pack root before drafting results prose.
13. Ensure evaluation claims are proportional to synthetic evidence per IUI CFP.

## I. Threat model and adversarial scenarios

**Grounding:** paper/threat-model.md

1. Include an adversary table before system details.
2. Cover accidental exposure from sensitive screen content.
3. Cover malicious screen content attempting prompt injection.
4. Cover malicious meeting participant behavior within screen-share context.
5. Cover rapid context switching and attribution confusion.
6. Cover retention overshoot through memory writes.
7. Cover output leakage through direct or indirect assistant responses.
8. Exclude OS compromise, malicious capture drivers, provider logs, and model training unless evidence is added.
9. Name residual risks for pattern-based redaction.
10. Name residual risks for OCR errors, visual ambiguity, and non-text content.
11. Name residual risks for multi-turn references and paraphrases.
12. Tie each threat to one or more fixture classes.
13. Tie each threat to at least one planned metric or smoke-test assertion.

## J. Blind-review and artifact hygiene

**Grounding:** IUI 2027 CFP

1. Keep paper, supplement, figure captions, README, and source metadata anonymous.
2. Remove or anonymize acknowledgements during review.
3. Write self-citations in third person if needed.
4. Do not include public repository links before blind review.
5. Do not include author names, affiliations, organization names, end-user names, or internal project names.
6. Keep real authorship notes only in `paper/authors.private.md` and exclude that file from review scans.
7. Run author-leak grep across markdown, TeX, BibTeX, CFF, and text files.
8. Run banned-claim grep across paper and supplement before review handoff.
9. Ensure CITATION metadata is anonymous during review.
10. Ensure screenshots/figures are synthetic or schematic only.
11. Ensure supplemental videos, if any, contain no voice/name/desktop identifiers.
12. Ensure README states synthetic-only data provenance.
13. Record the grep command and output in handoff notes.

## K. ACM/IUI format, GenAI, ethics, accessibility compliance

**Grounding:** ACM + IUI policies

1. Use `\documentclass[manuscript,review,anonymous]{{acmart}}` in `paper/paper.tex`.
2. Keep review manuscript single-column per IUI/ACM instructions.
3. Target a manuscript budget at or below 10,000 words before references and excluded sections.
4. Add a note if a future draft exceeds 12,000 words.
5. Place `GenAI Usage Disclosure` before references.
6. Disclose GenAI use across research, code/data, and writing where applicable.
7. Keep references and GenAI disclosure outside the word-count budget per IUI CFP.
8. Add an ethics note explaining synthetic-only data and no human-subject study in current scope.
9. If a human-subject study is later added, clear the applicable ethics review path first.
10. Add figure descriptions or alt text for accessibility.
11. Caption any video supplement if one is later created.
12. Check related-concurrent-submission requirements before submission.
13. Re-check official pages before quoting deadlines or policies in a final handoff.

## L. Writing, limitations, and claim discipline

**Grounding:** paper-enhancer guardrails

1. Use planned-language markers until result files exist.
2. Avoid absolute prevention claims.
3. Avoid exhaustive novelty claims without a related-work audit.
4. Avoid social/user-experience claims without a user study.
5. Keep limitations visible in abstract, evaluation, and conclusion plan.
6. State synthetic-only generalization limits explicitly.
7. Downgrade any unsupported metric, citation, or deployment claim.
8. Map each strong claim to an artifact path or planned metric.
9. Keep section-scope paragraphs separate from full prose generation in scaffold mode.
10. Prepare refiner handoff only for grounded text, not for inventing missing evidence.
11. Preserve exact thesis wording across core artifacts.
12. Record unresolved blockers rather than smoothing them away.
13. Never label the pack as final for submission before all gates pass.

## Sources

- IUI 2027 CFP: https://iui.acm.org/2027/call-for-papers/
- ACM author submissions/templates: https://www.acm.org/xpages/publications/authors/submissions
- ACM Policy on Authorship / GenAI disclosure: https://www.acm.org/publications/policies/new-acm-policy-on-authorship
- ACM human-participants policy: https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects
- Project pack: `data/eb1a/04_Projects/screen_share_ai_paper/`
