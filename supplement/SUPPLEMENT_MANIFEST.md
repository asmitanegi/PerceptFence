# PerceptFence — Supplement Bundle Manifest

**Prepared:** 2026-06-13 (NEE-2434 repair)
**Target venue:** Cybersecurity (Springer Nature)
**Submission posture:** Springer supplementary material candidate; not a public DOI, Zenodo, or arXiv release.

Upload only after the Editorial Manager file inventory and license/publication posture are confirmed by the corresponding author.

## Contents

| File | Description | Required? |
|---|---|---|
| `artifact_checklist.md` | Artifact checklist confirming code, fixture provenance, and reproducibility posture | Yes |
| `qa_audit_2026-05-13.md` | Internal QA evidence after public-language cleanup; review before external upload | Optional |
| `references-audit.md` | Source-check pass on all 16 references — provenance verified 2026-05-02 | Yes |
| `per_module_ablation.csv` | Raw ablation results: 7 variants × 11 fixtures | Yes |
| `per_fixture_ablation.csv` | Per-fixture results including 3 adversarial-evasion rows | Yes |
| `baseline_vs_guarded.csv` | 200-iteration latency benchmark (baseline vs full guard per fixture) | Yes |
| `CITATION.cff` | Repository citation metadata | Optional |
| `security-threat-model-review.md` | Full threat model review document | Optional |

## Upload instructions for Editorial Manager

1. In the submission portal, select **"Supplementary Material"** as the file type.
2. Upload each file individually or as a zip archive named `perceptfence_supplement_2026-06-13.zip`.
3. The `per_module_ablation.csv` and `per_fixture_ablation.csv` are referenced from the main text — upload these first.
