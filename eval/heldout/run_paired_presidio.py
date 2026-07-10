"""Generate the seed-paired three-defense comparison used by the paper.

Naive matching, PerceptFence, and Presidio run on identical generated cases for
seeds 0--4. This file is
separate from the 20-seed PerceptFence census so cross-tool comparisons cannot
silently mix denominators.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from baselines import DEFENSES, presidio_available
from generator import FAMILY_PAYLOADS
from run_heldout import run_seed
from taxonomy import FAMILY_COVERAGE

DEFAULT_PAIRED_SEEDS = list(range(5))


def parse_args() -> argparse.Namespace:
    default_output = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "heldout_paired_presidio.csv"
    )
    parser = argparse.ArgumentParser(
        description="Run naive, PerceptFence, and Presidio on identical generated cases."
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=DEFAULT_PAIRED_SEEDS,
        help="Integer generator seeds (default: 0 1 2 3 4).",
    )
    parser.add_argument("--output", type=Path, default=default_output)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paired_seeds = args.seeds
    if not presidio_available():
        raise SystemExit("Microsoft Presidio is required; run with .evalvenv/bin/python")

    rows: list[dict[str, object]] = []
    families = set(FAMILY_PAYLOADS)
    for defense in ("naive", "perceptfence", "presidio"):
        neutralized: dict[str, int] = defaultdict(int)
        exposed: dict[str, int] = defaultdict(int)
        recalls: dict[str, list[float]] = defaultdict(list)
        for seed in paired_seeds:
            per_family, _, _, _ = run_seed(seed, DEFENSES[defense], families)
            for family, (tp, fn) in per_family.items():
                neutralized[family] += tp
                exposed[family] += fn
                recalls[family].append(tp / (tp + fn))

        for family in sorted(recalls):
            tp = neutralized[family]
            fn = exposed[family]
            per_seed = recalls[family]
            rows.append(
                {
                    "defense": defense,
                    "family": family,
                    "coverage": FAMILY_COVERAGE[family],
                    "n_payload_cases": tp + fn,
                    "seeds": len(paired_seeds),
                    "recall": f"{tp / (tp + fn):.3f}",
                    "recall_min": f"{min(per_seed):.3f}",
                    "recall_max": f"{max(per_seed):.3f}",
                    "neutralized": tp,
                    "exposed": fn,
                }
            )

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {output} ({len(rows)} rows; seeds={paired_seeds})")


if __name__ == "__main__":
    main()
