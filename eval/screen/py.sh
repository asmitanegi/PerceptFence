#!/bin/bash
# Clean-env wrapper for the PerceptFence eval venv (Hermes' PYTHONPATH leaks otherwise).
cd "$(dirname "$0")/../.." || exit 1
exec env -i HOME="$HOME" PATH=/opt/homebrew/bin:/usr/bin:/bin LANG=en_US.UTF-8 \
  PYTHONPATH="$PWD" PF_RENDER_DIR="${PF_RENDER_DIR:-}" \
  .evalvenv/bin/python "$@"
