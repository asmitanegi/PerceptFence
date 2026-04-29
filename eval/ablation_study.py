"""Pack-root ablation entrypoint for fresh-clone verification."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys


PACK_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = PACK_ROOT / "src"
sys.path.insert(0, str(CODE_ROOT / "src"))
sys.argv = [
    str(CODE_ROOT / "eval" / "ablation_study.py"),
    "--repo-root",
    str(CODE_ROOT),
    "--output-dir",
    str(PACK_ROOT / "eval" / "results"),
]
runpy.run_path(str(CODE_ROOT / "eval" / "ablation_study.py"), run_name="__main__")
