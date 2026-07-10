# PerceptFence — Supplement Bundle Manifest

**Target venue:** Springer Nature *Cybersecurity*
**Updated:** 2026-07-09
**Posture:** upload as
`perceptfence_additional_file_1_2026-07-09.zip`; do not link the public,
de-anonymized repository during double-anonymous review.

## Contents

| Path | Description | Required? |
|---|---|---|
| `artifact_checklist.md` | Artifact checklist confirming code, fixture provenance, and reproducibility posture | Yes |
| `screenshare_mediator/` | Fixture-driven reference implementation | Yes |
| `data/synthetic/` | Eleven invented fixture JSON files, index, and provenance README | Yes |
| `policies/` | Action allow-list used by the fixture policy scaffold | Yes |
| `eval/` | Deterministic ablation, benchmark, held-out harness, paired Presidio runner, metric notes, and figure generators | Yes |
| `eval/results/*.csv` | Canonical deterministic result tables, including the paired-seed Presidio comparison | Yes |
| `tests/` | Forty-two unit and integration tests | Yes |
| `requirements-eval.txt` | Pinned pytest, Presidio, spaCy, and plotting dependencies | Yes |
| `pyproject.toml` | Package metadata and pytest configuration | Yes |
| `LICENSE` | All-rights-reserved review and reproducibility terms | Yes |
| `README.md` | Anonymous reviewer quickstart and evidence boundaries | Yes |
| `SUPPLEMENT_MANIFEST.md` | This manifest | Yes |
| `ADDITIONAL_FILE_CHECKSUMS.sha256` | SHA-256 hashes for every file in this Additional-file archive | Yes |
| `CITATION.cff` | Anonymous artifact citation metadata | Yes |

The model-run harness and its unit tests are included, but exploratory model-output
snapshots are intentionally excluded: per-case prompts, responses, stable model
identifiers, and repeat runs were not retained. The maintainer runs the repository
verifier before package generation; archive-local checksums are then verified from a
clean extraction.
