#!/usr/bin/env python3
"""Fail closed if internal-only material reaches the public repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PREFIX = "private/"
INTERNAL_ONLY_NAMES = {
    "DECISION_MEMO.md",
    "EXPERIMENT_AND_RELEASE_RUNBOOK.md",
    "FINAL_SUBMISSION_SPEC.md",
    "PRODUCTION_PLAN.md",
    "SCIENCE_HARDENING_SPEC.md",
    "SUBMISSION_INSTRUCTIONS.md",
    "WEAK_MODEL_GOAL.md",
}


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    problems: list[str] = []

    if (ROOT / "private").exists():
        problems.append("private/ exists in the public working tree")

    tracked = git_lines("ls-files")
    private_tracked = [path for path in tracked if path == "private" or path.startswith(PRIVATE_PREFIX)]
    if private_tracked:
        problems.append(f"private paths are tracked: {private_tracked[:5]}")

    internal_names = [path for path in tracked if Path(path).name in INTERNAL_ONLY_NAMES]
    if internal_names:
        problems.append(f"internal-only filenames are tracked: {internal_names[:5]}")

    history_objects = git_lines("rev-list", "--objects", "--all")
    historical_private = []
    for line in history_objects:
        _, separator, path = line.partition(" ")
        if separator and (path == "private" or path.startswith(PRIVATE_PREFIX)):
            historical_private.append(path)
    if historical_private:
        problems.append(f"private paths exist in reachable public history: {historical_private[:5]}")

    ignore_lines = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if "/private/" not in ignore_lines:
        problems.append("public .gitignore is missing the /private/ guard")

    if problems:
        print("PUBLIC TREE GUARD: FAIL")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("PUBLIC TREE GUARD: PASS — no private tree, filenames, or history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
