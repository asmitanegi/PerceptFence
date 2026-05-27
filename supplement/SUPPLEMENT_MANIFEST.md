# PerceptFence — Supplement Bundle Manifest

**Prepared:** 2026-05-03 (NEE-245)
**Target venue:** Cybersecurity (Springer Nature)
**Submission deadline:** 2026-05-16

Upload ALL files in this directory as supplementary material in Springer Editorial Manager.

## Contents

| File | Description | Required? |
|---|---|---|
| `artifact_checklist.md` | Blinded artifact checklist — confirms code + fixture provenance | Yes |
| `qa_audit_2026-05-13.md` | QA audit pass (NEE-243): banned-term grep, claim-to-metric, refiner — all PASS | Yes |
| `references-audit.md` | Source-check pass on all 16 references — provenance verified 2026-05-02 | Yes |
| `per_module_ablation.csv` | Raw ablation results: 7 variants × 11 fixtures | Yes |
| `per_fixture_ablation.csv` | Per-fixture results including 3 adversarial-evasion rows | Yes |
| `baseline_vs_guarded.csv` | 200-iteration latency benchmark (baseline vs full guard per fixture) | Yes |
| `CITATION.cff` | Repository citation metadata | Optional |
| `security-threat-model-review.md` | Full threat model review document | Optional |

## Upload instructions for Editorial Manager

1. In the submission portal, select **"Supplementary Material"** as the file type.
2. Upload each file individually or as a zip archive named `perceptfence_supplement_2026-05-16.zip`.
3. The `per_module_ablation.csv` and `per_fixture_ablation.csv` are referenced from the main text — upload these first.
