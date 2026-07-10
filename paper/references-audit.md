# References audit — regenerated 2026-07-09

Automated key-resolution check of `paper/main.tex` against `paper/references.bib`
(the previous audit predated the repo flatten and covered only 16 entries).

- Unique `\cite` keys used in main.tex: **36**
- Entries in references.bib: **36**
- Cited but missing from the bib: **none**
- In the bib but never cited: **none**

Every entry in references.bib carries an inline `% provenance:` line naming the
source (arXiv/ACM/publisher page) and the date it was verified. Entries touched
on 2026-07-02 (verified against live sources that day):

- `shvartzshnaider2026privacy` — retitled to the current arXiv v-Dec-2025 title
  ("Privacy Bias in Language Models: A Contextual Integrity-based Auditing
  Metric"), year set to 2026, venue PETS 2026 (accepted). arXiv:2409.03735.
- `alneyadi2016dlp` — added (endpoint-DLP survey; JNCA 62:137--152, 2016,
  doi:10.1016/j.jnca.2016.01.008) to ground the previously uncited DLP
  competitor class in Related Work.


Re-run this audit after any citation change:
`python3 - <<'PY'` (see git history of this file for the snippet) or simply
grep `\cite{...}` keys against `@...{key,` entries.
