# PerceptFence submission-readiness and cleanup checklist

Last updated: 2026-06-13
Target paper: **Consent-Aware Runtime Mediation for Privacy in Real-Time Screen-Share AI Assistants**
Primary target: **Springer Nature _Cybersecurity_** via Editorial Manager (`https://www.editorialmanager.com/cyse/default.aspx`)

## 0. Current status

- [x] **Public repository exists:** `https://github.com/asmitanegi/PerceptFence`
- [x] **Repository visibility:** public
- [x] **No real data in artifact:** synthetic fixtures only; no real screen captures, customer data, production telemetry, or human-subject data.
- [x] **Public attribution added:** root and `src/` citation metadata identify Neeraj Kumar Singh and ORCID.
- [x] **Root license added:** public visibility is all-rights-reserved; no implied open-source grant.
- [x] **Root pytest collection cleaned:** `pytest.ini` restricts pytest discovery to `src/tests` so root-level helper scripts are not collected as duplicate tests.

## 1. Repository cleanup gate

- [x] Add/refresh `.gitignore` for Python caches, virtualenvs, local env files, `uv.lock`, and generated local submission bundles.
- [x] Keep generated `submission/` upload bundles local-only; do not commit large DOCX/PDF/ZIP portal packages to the public source repo.
- [x] Replace outdated "private / blind-review-only / do not publish" wording in public README files.
- [x] Add root `LICENSE` so GitHub and archive readers do not infer an unstated open-source license.
- [x] Add root `SUBMISSION_READY_CHECKLIST.md` as the public checklist of remaining paper/package gates.
- [ ] If an open-source release is desired later, replace the all-rights-reserved license with an explicit OSI license and update `CITATION.cff`, README, manuscript data/code-availability text, and Zenodo metadata in one commit.
- [ ] If an anonymous IUI/ACM route is revived later, create a separate anonymized branch/archive; do not mix it with the de-anonymized Springer route.

## 2. Code and reproducibility gate

Run from the repository root:

- [x] `python3 -m pytest -q` → expected: `29 passed`.
- [x] `cd src && python3 -m pytest -q` → expected: `29 passed`.
- [x] `cd src && PYTHONPATH=src python3 eval/smoke_test.py` → expected: `SMOKE PASS: 11 synthetic scenarios validated; 3 runtime mediation paths exercised`.
- [x] `cd src && PYTHONPATH=src python3 eval/ablation_study.py` → expected: full-guard outcome rate `1.000`.
- [x] Verify no generated caches are tracked: `git status --short --ignored` should show caches ignored, not staged.
- [ ] Re-run smoke + ablation after any fixture, policy, or manuscript claim change.
- [ ] Re-render figures only when the underlying committed CSV changes; avoid replacing latency-sensitive artifacts from a different machine without a reason.

## 3. Public-language and evidence-safety gate

Search upload-facing/public files before each push:

- [x] No EB1A / USCIS / immigration / attorney / petition language in public artifact files.
- [x] No stale `neeraj@parafin.com` or `parafin.com` contact string in public artifact files.
- [x] No overclaim phrases such as `first ever`, `formally verified`, `deployment ready`, `production ready`, or `prevents leakage`.
- [x] Claims are bounded to synthetic evidence.
- [ ] Before submission, re-check that negative declarations mention excluded data types only as exclusions, not as claims of real-data use.

## 4. Springer _Cybersecurity_ manuscript gate

- [x] Target portal corrected to `https://www.editorialmanager.com/cyse/default.aspx`.
- [x] Corresponding author email updated to `b.neerajkumarsingh@gmail.com`.
- [x] ORCID included: `https://orcid.org/0009-0002-2125-1805`.
- [x] Declarations added to Springer source: funding, competing interests, ethics/consent, data availability, code availability, author contribution, and AI/tool-use disclosure.
- [x] Cover letter updated for Springer and bounded synthetic claims.
- [ ] Human review required before final portal submit: exclusivity/originality certification, publication agreement, AI-use disclosure, conflict/funding statements, data/code availability wording, and APC/license selections.
- [ ] If the portal requires LaTeX source rather than DOCX/PDF upload, install/use a TeX environment with Springer `sn-jnl.cls`, generate `main.pdf` and `main.bbl`, and verify the PDF was built from the current `src/paper/cybersecurity_springer/main.tex`.
- [ ] If uploading DOCX/PDF is allowed, use the local `submission/springer/` package and verify the portal's converted proof before final submit.

## 5. Local submission package gate

Local-only package path: `submission/` (ignored by Git).

- [x] `submission/README.md` exists with Springer and Zenodo package inventory.
- [x] `submission/springer/checksums.sha256` verifies from the `submission/` directory.
- [x] `submission/checksums.sha256` verifies from the `submission/` directory.
- [ ] Do not claim `submitted` until Editorial Manager returns a manuscript ID, confirmation page, or confirmation email.
- [ ] Do not claim Zenodo DOI until Zenodo returns a DOI/reserved DOI or a confirmed deposit URL.
- [ ] Rebuild local ZIP/DOCX/PDF packages after any manuscript, cover-letter, metadata, license, declaration, or supplement change.

## 6. Editorial Manager account / portal gate

- [x] Create or verify an Editorial Manager account for Springer _Cybersecurity_.
- [x] Save the final verified credentials to Neeraj's local credentials file and Bitwarden handoff message.
- [x] Verify login by reaching the author dashboard, not merely by seeing a registration form.
- [ ] Stage upload fields/files up to the final human certification gate.
- [x] Capture exact portal state: account email, role, journal title, manuscript title, uploaded files, and next required click. Current verified state: author dashboard reached, journal is _Cybersecurity_, account email is `b.neerajkumarsingh@gmail.com`, no manuscripts started yet.

## 7. Final submission gate

The paper is **submission-ready** only when all of these are true:

- [ ] Public repo is clean and pushed.
- [ ] Local tests/smoke/ablation pass after the final commit.
- [ ] Public-language and private-case leak scans pass.
- [ ] Local upload package checksums pass after final rebuild.
- [x] Editorial Manager account login is verified.
- [ ] Portal has the manuscript metadata and files staged.
- [ ] Neeraj explicitly clears final author/legal declarations and final submit click.
- [ ] External receipt is captured after submit.

## 8. Completion labels

- `repo_published_clean`: public GitHub repo is pushed, tests pass, public-language scans pass, and no local generated bundles are staged.
- `submission_package_ready`: local upload package exists, checksums pass, and checklist names remaining human gates.
- `upload_staged`: Editorial Manager form is filled and files are uploaded up to the final human certification/submit gate.
- `submitted`: Editorial Manager returned a manuscript ID, confirmation page, or confirmation email.
