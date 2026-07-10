#!/usr/bin/env bash
# reproduce.sh — one-command verification of the PerceptFence artifact.
#
# Default (no args): read-only verification — unit tests, smoke test, and the
# pre-submission gate. Does NOT rewrite any committed CSV.
#
#   bash reproduce.sh
#
# Full regeneration (rewrites eval/results/*.csv): the ablation/benchmark paths
# carry machine-dependent latency columns, so regenerated CSVs will differ from
# the committed ones in timing fields (outcome fields are deterministic).
# Regenerate only if you intend to re-baseline, then re-run the gate:
#
#   bash reproduce.sh --regenerate
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/3 unit tests (42 expected) =="
if [[ -x .evalvenv/bin/python ]] && .evalvenv/bin/python -c "import pytest" 2>/dev/null; then
  PYTHON=.evalvenv/bin/python
elif python3 -c "import pytest" 2>/dev/null; then
  PYTHON=python3
else
  python3 -m venv /tmp/pf-test >/dev/null
  /tmp/pf-test/bin/pip install -q pytest
  PYTHON=/tmp/pf-test/bin/python
fi
"$PYTHON" -m pytest tests/ -q

echo "== 2/3 smoke test =="
PYTHONPATH=. python3 eval/smoke_test.py | tail -1

if [[ "${1:-}" == "--regenerate" ]]; then
  echo "== regenerating eval CSVs (latency columns are machine-dependent) =="
  PYTHONPATH=. python3 eval/ablation_study.py
  PYTHONPATH=. python3 eval/benchmark.py
fi

echo "== 3/3 pre-submission gate =="
"$PYTHON" tools/verify_submission.py
