"""Pack-root smoke-test entrypoint for fresh-clone verification."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys


PACK_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = PACK_ROOT / "src"
sys.path.insert(0, str(CODE_ROOT / "src"))
runpy.run_path(str(CODE_ROOT / "eval" / "smoke_test.py"), run_name="__main__")
