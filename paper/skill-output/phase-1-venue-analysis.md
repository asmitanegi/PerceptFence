# Phase 1 — Context Gathering and Venue Analysis

**Run date:** 2026-04-26 America/Los_Angeles  
**Target:** ACM IUI 2027 papers track  
**Source policy:** venue and ACM policy facts below are from official pages re-checked on the run date.

## Official venue facts

| Requirement | Captured fact | Source |
|---|---|---|
| Abstract deadline | 2026-08-13 AoE | IUI 2027 CFP |
| Full paper deadline | 2026-08-20 AoE | IUI 2027 CFP |
| Initial paper notifications | 2026-10-29 | IUI 2027 CFP |
| Invited rebuttal deadline | 2026-11-05 | IUI 2027 CFP |
| Final decision notification | 2026-11-26 | IUI 2027 CFP |
| Camera-ready deadline | 2026-12-10 | IUI 2027 CFP |
| Conference | 2027-02-08 to 2027-02-11, Helsinki, Finland | IUI 2027 CFP |
| Review model | Double-blind; paper and supplemental materials must be anonymized | IUI 2027 CFP |
| Review format | Single-column ACM manuscript; LaTeX review command `\documentclass[manuscript,review,anonymous]{acmart}` | IUI 2027 CFP |
| Working word budget | Keep the review manuscript at or below 10,000 words; manuscripts over 12,000 words need a length note | IUI 2027 CFP |
| Evidence expectation | Evidence must be rigorous and proportional to the claims, e.g. system evaluation or computational analysis | IUI 2027 CFP |
| Submission system | PCS: SIGCHI → IUI 2027 → IUI 2027 Papers | IUI 2027 CFP |
| Supplement | Optional but encouraged; must be anonymized; related concurrent submissions require anonymized disclosure | IUI 2027 CFP |
| Accessibility | Submissions should be accessible; video supplements require captions | IUI 2027 CFP |

## Topic fit

The project fits IUI only if it remains an HCI+AI systems paper with bounded evidence. Official IUI 2027 topics that directly support the fit are: intelligent user interfaces for generative AI, privacy and security of IUI, human control in daily automations, multimodal AI assistants, end-user interaction with LLMs/agents/multimodal models, user control and steering of LLMs and agents, and reproducibility through benchmarks/datasets/challenges.

## Anonymization constraints

- Remove author names and affiliations from paper, video figures, and all supplemental materials.
- Remove or anonymize acknowledgements during review.
- Write self-citations in the third person.
- Keep public repository/demo links, organization identifiers, non-synthetic operational data, non-synthetic screen captures, and production telemetry out of the review pack.
- Run a blind-review grep before any handoff.

## GenAI disclosure constraints

IUI 2027 points authors to ACM GenAI/authorship policy and requires a `GenAI Usage Disclosure` section before the references. The disclosure must cover use of GenAI tools across research, code/data, and writing. The disclosure section and references do not count toward the word budget.

## Ethics constraints

IUI 2027 requires human-subject research to follow the authors' applicable ethics-review process and asks authors to submit a short note to reviewers with that context. ACM's human-participants policy requires compliance with ethical/legal standards, including minimization of potential harms, privacy and self-determination, relevant regulations, informed consent, and justice. Current PerceptFence scope is synthetic-only; any real participant study remains blocked until an ethics path is cleared.

## ACM template context

ACM author instructions say manuscripts for review should be submitted in single-column format and that LaTeX authors use the ACM Primary Article Template with the `manuscript` option. IUI 2027 further specifies `manuscript,review,anonymous` for anonymous review.

## Scaffold implication

The correct paper pack target before the 2026-06-07 filing gate is: bounded abstract, section outline, anonymous ACM skeleton, synthetic smoke path, criteria/gap analysis, and plan. Benchmark table, figure generation from results, and full section prose are post-gate work.

## Sources re-checked

- IUI 2027 CFP: https://iui.acm.org/2027/call-for-papers/
- ACM author submissions/templates: https://www.acm.org/xpages/publications/authors/submissions
- ACM Policy on Authorship / GenAI disclosure: https://www.acm.org/publications/policies/new-acm-policy-on-authorship
- ACM human-participants policy: https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects
