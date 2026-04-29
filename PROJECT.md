- A smoke command can run baseline and guarded paths on at least one synthetic scenario without producing final benchmark claims.

**Exit test:** Run the unit-test command and the smoke command. Tests must show one passing test per module. Smoke output must show baseline and guarded processing for at least one synthetic scenario. Full benchmark table generation is gated until after 2026-06-07.

### M5 — Post-filing benchmark, figure, and blinded submission pack

**Goal of this milestone:** After the 2026-06-07 filing gate, turn the prototype into a reviewable paper pack with evidence-backed claims.

**Success criteria:**

- `eval/results/baseline_vs_guarded.csv` contains sensitive exposure/leakage rate, false block rate, latency overhead, and task success/completion for every synthetic scenario.
- `docs/figures/` contains one figure generated from the benchmark data.
- `paper/paper.tex` uses `\documentclass[manuscript,review,anonymous]{acmart}` and includes placeholders/notes for GenAI Usage Disclosure and ethics handling.
- `supplement/` or `paper/supplement/` contains the blinded artifact checklist and no author/company identifiers.
- Real authorship metadata lives only in `paper/authors.private.md` (gitignored) and is *not* present anywhere in the review pack. Camera-ready swap procedure documented inside that file.

**Exit test:** Run the benchmark and figure-generation commands from a fresh clone. Open the CSV and figure; values must match. Run the blind-review grep from M3 across the final pack. Run the private **author-leak grep** documented in gitignored `paper/authors.private.md` against the review-pack tree before submission; do not copy private author patterns into tracked files.

Any hit outside `paper/authors.private.md` itself is a blocker — the review pack is not blind-safe. Confirm `paper/paper.tex` compiles or, if compilation tooling is not installed, at least lints for the correct document class and required sections.

## Dependencies & risks

- **Agent ownership:** A dedicated Screen-Share AI Paper Lead is needed because existing active agents cover EB1A case management, engineering, and security, but not sustained academic-paper production.
- **Venue drift:** CFP details can change; any plan update after 2026-04-26 must re-check official venue pages before quoting deadlines or rules.
- **Evidence risk:** This paper does not help EB1A if it stays as a vague idea. It needs a measurable artifact, draft, and submission trail.
- **Blind-review risk:** Public links, real data, author identity, or company metadata can invalidate the target venue path.
- **Claim-risk:** The project is safer if claims stay narrow: runtime mediation reduces measured leakage on synthetic scenarios with bounded latency overhead.
- **Time risk:** IUI dates are in August, but EB1A filing pressure is June 7. Pre-filing work is limited to abstract, outline, private skeleton repo, and synthetic prototype smoke path unless Patty explicitly prioritizes more.
- **First-class filing gate:** Post-filing work is blocked through `/NEE/issues/NEE-1248` → `/NEE/issues/NEE-1246` → `/NEE/issues/NEE-1247` → `/NEE/issues/NEE-1245`. Do not close the date blocker before 2026-06-07 unless Patty explicitly overrides; do not start benchmark/table/full-draft work from a status comment alone.
