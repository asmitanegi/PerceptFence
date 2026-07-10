# Exploratory model snapshots — excluded from paper evidence

The deterministic held-out census in `eval/heldout/` measures whether an
injected string remains recoverable after mediation. It does **not** measure
whether a downstream model obeys an instruction or emits a secret.

## Evidence status

Historical aggregate files formerly stored as `eval/results/model_in_loop*.csv`
and matching run logs were removed from the release tree. The manuscript does
not cite or interpret them. A July 2026 artifact audit found that they were not
submission-grade:

- only aggregate rows were retained—no case IDs, prompts, raw replies, per-case
  scores, transitions, or judge outputs;
- the exact version behind the generic `gpt-3.5-turbo` alias was not preserved;
- the aligned arm was dispatched through a different assistant route rather
  than the released API harness;
- the released weak-model harness asks for a summary and next step, while the
  aligned-arm log describes an exact-readback task;
- ambiguous A1 cases can be judged by the same configured endpoint, which is
  not an independent judge;
- no repeated runs establish model-output stability.

Those historical fractions therefore must not be described as paired,
repeatable, family-level, cross-model, or model-behavior evidence. No aggregate
model snapshot is included in the repository release, blinded reproducibility
supplement, or submission checksum set.

## Requirements for a future model study

A reportable rerun must predeclare the task and sampling plan, pin exact model
versions/endpoints/scorers, retain prompts and raw replies for both guarded and
unguarded arms, record per-case IDs and scores, use an independent or manual
adjudication protocol for ambiguous cases, and repeat each model/arm enough to
show output variability. Until then, the paper's model-behavior claim is:
**not evaluated**.

The existing harness still refuses to fabricate scores: without a configured
endpoint and credential it exits non-zero and writes no result CSV.
