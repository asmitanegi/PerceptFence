"""Pack-root figure renderer entrypoint for fresh-clone verification."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys


PACK_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = PACK_ROOT / "src"
sys.path.insert(0, str(CODE_ROOT / "src"))
sys.argv = [
    str(CODE_ROOT / "eval" / "render_figure.py"),
    "--csv",
    str(PACK_ROOT / "eval" / "results" / "baseline_vs_guarded.csv"),
    "--out",
    str(PACK_ROOT / "docs" / "figures" / "headline_ser.svg"),
]
runpy.run_path(str(CODE_ROOT / "eval" / "render_figure.py"), run_name="__main__")
