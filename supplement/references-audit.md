# `references.bib` Audit — 2026-05-03

## Scope

- Manuscript checked: `manuscript.md`
- Bibliography checked: `references.bib`
- Acceptance target: every in-text citation resolves to a complete BibTeX entry; unresolved items are listed explicitly.

## Citation Resolution

- In-text citation keys found: 16
- BibTeX entries found: 16
- Missing BibTeX entries: none
- Unused BibTeX entries: none
- Required-field completeness failures among cited entries: none after adding explicit URL fields for non-DOI sources

Resolved citation keys:

```text
apthorpe2018smart
chen2025agentguard
chen2025secalign
chen2025struq
danry2026gaze
enck2014taintdroid
felt2011android
felt2012permissions
greshake2023indirect
liu2023prompt
microsoft2024recall
nissenbaum2004privacy
shvartzshnaider2026privacy
xu2025acceptability
yang2026zombie
zoom2024ai
```

## DOI Spot-Check Results

Checked all five DOI-bearing entries against the Crossref Works API on 2026-05-03.

| Citation key | DOI | Result | Crossref title |
|---|---:|---|---|
| `felt2011android` | `10.1145/2046707.2046779` | OK | Android permissions demystified |
| `felt2012permissions` | `10.1145/2335356.2335360` | OK | Android permissions |
| `enck2014taintdroid` | `10.1145/2619091` | OK | TaintDroid |
| `apthorpe2018smart` | `10.1145/3214262` | OK | Discovering Smart Home Internet of Things Privacy Norms Using Contextual Integrity |
| `chen2025secalign` | `10.1145/3719027.3744836` | OK | SecAlign: Defending Against Prompt Injection with Preference Optimization |

The shorter Crossref titles for `felt2012permissions` and `enck2014taintdroid` are publisher metadata abbreviations, not resolution failures. The local BibTeX titles retain the fuller paper titles.

## Non-DOI URL Completion

Added explicit `url` fields for the cited non-DOI sources so every cited BibTeX entry now has either `doi`, `url`, or both:

```text
nissenbaum2004privacy
shvartzshnaider2026privacy
xu2025acceptability
danry2026gaze
microsoft2024recall
greshake2023indirect
liu2023prompt
chen2025struq
yang2026zombie
chen2025agentguard
```

## Unresolved Items

None for citation resolution or required-field completeness.

## Blind-Review Safety Flags

Separate from citation resolution, a quick blind-safety grep found internal tracking identifiers in package files:

- `manuscript.md`: status/limitations/checklist text mentions `NEE-240`, `NEE-241`, `NEE-243`, and `NEE-245`.

The `references.bib` internal issue comment was removed in this pass.

These identifiers should be removed or moved to non-submission notes before building a blinded review package.

## Verification Commands

```bash
python3 - <<'PY'
# Extracted Pandoc/LaTeX citation keys from manuscript.md and compared them
# with BibTeX entry keys in references.bib.
PY

python3 - <<'PY'
# Queried https://api.crossref.org/works/{doi} for each DOI field in references.bib.
PY

rg -n --ignore-case 'neeraj|patty|parafin|paperclip|openai|claude-skills|/home/|agent://|NEE-[0-9]+|customer|slack|company' manuscript.md references.bib README.md
```
