# Phase 3 — IUI Pattern and Gap Analysis

**Run date:** 2026-04-26 America/Los_Angeles  
**Pattern source:** IUI 2025 proceedings metadata/titles via DBLP plus IUI 2027 CFP expectations. This is not reviewer-score data; it is a scaffold-mode pattern read from accepted-paper topics/titles and official venue requirements.

## IUI 2025 pattern signals inspected

Representative IUI 2025 proceedings titles include: `A Design Space for Intelligent Dialogue Augmentation`, `A Design Space of Behavior Change Interventions for Responsible Data Science`, `A Dynamic Bayesian Network Based Framework for Multimodal Context-Aware Interactions`, `A Framework for Efficient Development and Debugging of Role-Playing Agents with Large Language Models`, and `A Prompt Chaining Framework for Long-Term Recall in LLM-Powered Intelligent Assistant`.

## Strong-accept style patterns to aim for

1. **Named system or framework with a precise design space.** IUI papers frequently present a named artifact or framework and make the contribution legible in the title and section structure.
2. **HCI + AI balance.** A credible IUI paper must explain both the interactive user-control problem and the machine-intelligence/system behavior.
3. **Evidence proportional to claims.** IUI 2027 explicitly expects rigorous evidence appropriate to claims; PerceptFence should not claim measured impact until benchmark rows exist.
4. **Concrete artifact and reproducibility path.** The project needs runnable synthetic fixtures, smoke tests, benchmark commands, and clear supplement provenance.
5. **Responsible AI reflection.** The official CFP encourages practical/societal impact and ethical-consideration reflection; this paper's limitations/ethics section should be substantive, not perfunctory.
6. **Clear boundaries.** IUI reviewers should be able to see what the runtime layer handles and what it excludes.

## Strong-reject risk patterns to avoid

1. **Idea-only paper.** A paper with only an abstract and architecture prose will be weak without runnable artifacts or benchmark evidence.
2. **Unsupported broad claims.** Claims about privacy, prevention, user benefit, real-time behavior, robustness, or deployment impact require direct measurement or must be downgraded.
3. **Blind-review leakage.** Author/organization identity, public links, non-synthetic screen captures, or acknowledgements in review files can trigger desk rejection.
4. **Synthetic evidence overreach.** Synthetic fixtures can support scoped system behavior claims, not real-user behavior claims.
5. **Single-layer guard story.** If input redaction, memory control, and output checking are blurred, the contribution will look like generic filtering rather than runtime mediation.
6. **No ethics/GenAI disclosure path.** IUI 2027 requires GenAI disclosure and human-participant context handling; placeholders must exist in the skeleton.

## Required gap check from the scaffold-mode task

| Acceptance gap item | Current pack state | Residual action |
|---|---|---|
| Missing `eval/metrics.md` | `src/eval/metrics.md` exists; pack-root `eval/metrics.md` is missing. | Decide whether to mirror or reference `src/eval/metrics.md` from the paper pack root before Phase 5. |
| Missing `paper/threat-model.md` | `paper/threat-model.md` exists. | Integrate a compact threat table into `paper/paper.tex` and keep detailed version in supplement/notes. |
| Missing `paper/paper.tex` skeleton | `paper/paper.tex` exists and uses anonymous ACM class. | Lint/compile once LaTeX tooling is confirmed; keep it scaffold-only pre-gate. |
| Missing per-section scope paragraphs | `paper/section-scope.md` exists. | Ensure each planned section in `paper/paper.tex` points to the corresponding scope paragraph. |
| Missing adversarial-evasion fixtures | The acceptance phrase `missing adversarial-evasion fixtures` is partially stale: dedicated `homoglyph_credential`, `split_pii`, and `mixed_sensitivity` fixtures now exist, alongside `prompt_injection_on_screen`. | Remaining gap is encoded/role-play screen-instruction evasion plus any benchmark rows using the evasion fixtures. |

## Additional gaps observed

- `PROJECT.md` in the project pack currently appears truncated to late milestone text; preserve the canonical issue/README/venue files as immediate context until the canonical project note is restored or re-copied.
- No `eval/results/` directory exists in the pack, so all benchmark/evaluation claims must remain planned.
- No benchmark CSV or generated figure exists; do not draft result prose.
- Smoke test expectation was stale for the prompt-injection fixture wording; it now checks for the current synthetic `SYSTEM OVERRIDE` text.
- `paper/paper.tex` includes placeholders and planned contribution language; it should not be expanded into full sections in this issue.
- Need a direct blind-review grep record over the review-pack tree excluding `paper/authors.private.md`.

## Sources

- IUI 2025 proceedings metadata: https://dblp.org/db/conf/iui/iui2025.html
- IUI 2027 CFP: https://iui.acm.org/2027/call-for-papers/
- Project pack: `data/eb1a/04_Projects/screen_share_ai_paper/`
