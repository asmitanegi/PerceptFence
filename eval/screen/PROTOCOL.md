# Rendered-screen evaluation protocol (frozen before the test run)

Use case: a developer or support engineer shares their screen with an AI
assistant to debug a failure (terminal, `.env` editor, CI log, notebook,
support-console record, chat toast). The assistant needs the error text; it
must not receive the credentials and customer PII that are also on screen.

Pipeline: HTML screen -> headless Chrome 1280x720 screenshot -> optional
degradation (0.75x downscale, JPEG q55, upscale) -> Tesseract 5 OCR (eng,
psm 6) -> defense -> exposure oracle (`eval/heldout/oracle.py`, unchanged
from v0.3) on the canonical planted value.

Splits (fixed in `eval/screen/corpus.py` before any measurement):
- dev: seeds 0-1 x 5 templates x 12 render conditions = 120 screens. The v0.4
  families (T7-T10) were written against this split only.
- test-seen-template: seeds 2-6 x the same 5 templates x 12 conditions = 300
  screens, fresh values.
- test-heldout-template: seeds 2-6 x 3 templates never rendered during
  development (kubectl secret YAML with base64 values, OpenSSH private key,
  notebook with a customer table) x 12 conditions = 180 screens.

Scoring rules:
- A payload is eligible only if the oracle recovers it from raw OCR. Payloads
  destroyed by OCR are reported as `ocr_lost`, never as defense wins.
- Neutralisation = eligible payloads the oracle can no longer recover.
- Benign retention = task tokens present in raw OCR that survive the defense.
- Intervals: Wilson 95% per rate; paired differences use a cluster bootstrap
  over (seed, template), 2,000 resamples, fixed seed 7.
- Defenses: none, naive regex, PerceptFence v0.3 (six families, as submitted),
  PerceptFence v0.4 (+T7-T10), Microsoft Presidio 2.2 (spaCy en_core_web_sm),
  gitleaks 8 default rules.

Freeze: after this file is committed, `screenshare_mediator/redaction.py` and
`eval/screen/*.py` are not edited before the test split is scored. SHA-256 of
the frozen files is recorded in `supplement/screen_eval/FREEZE.sha256`. Any
post-test change must be reported as a separate, labelled result.
