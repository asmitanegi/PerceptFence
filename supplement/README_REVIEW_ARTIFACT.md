# PerceptFence review artifact

This Additional file supports the deterministic claims in the accompanying
manuscript. It is not a live screen-share assistant integration. The package
builder supplies citation and licence metadata for the selected review model.

## Evidence boundary

Implemented and included:

- synthetic fixture dictionaries and typed fixture adapter;
- hard-coded `scenario_class → action` policy routing;
- deterministic redaction, per-invocation context exclusion, output checks, and
  an in-memory hash-chained event list;
- designer-authored configuration checks;
- a self-generated deterministic 9,600-case coverage census;
- a seed-paired naive/PerceptFence/Presidio comparison on seeds 0–4;
- 42 unit and integration tests.

Not implemented or claimed:

- live screen/audio capture, OCR, ASR, network, or external model adapters;
- content-category inference, authenticated consent changes, or re-consent;
- persistent cross-turn/session memory;
- append-only, complete, durable, or crash-evident logging;
- real-user, deployment, production-latency, or model-behavior evidence;
- an independent or categorically stronger evaluation oracle.

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-eval.txt
.venv/bin/python -m pytest tests/ -q
PYTHONPATH=. .venv/bin/python eval/smoke_test.py
PYTHONPATH=. .venv/bin/python eval/ablation_study.py \
  --output-dir /tmp/perceptfence-ablation
PYTHONPATH=. .venv/bin/python eval/benchmark.py \
  --output-dir /tmp/perceptfence-benchmark
```

Expected test result: `42 passed`. The deterministic coverage and paired
Presidio commands, environment pins, protocol history, and disclosed v2
amendment are documented in `eval/heldout/PROTOCOL.md`.

## Result provenance

Canonical result CSVs are in `eval/results/`. The manuscript's cross-tool
comparisons use `heldout_paired_presidio.csv`, whose three defence rows were
produced on identical generated cases from seeds 0–4. The 20-seed
PerceptFence-only tables are sensitivity results, not cross-tool comparisons.
Payload-case recall is reported separately from the benign-token removal proxy
in `heldout_benign_controls.csv`; the artifact reports no precision or F-score.

Exploratory aggregate model snapshots are deliberately absent because per-case
prompts, replies, stable model identifiers, and repeated runs were not retained.
No model-behavior result is claimed.

Verify every file against `ADDITIONAL_FILE_CHECKSUMS.sha256` before running the
artifact. The bundled `LICENSE` permits review and reproducibility inspection;
it is not an MIT license.
