"""Run the held-out adversarial census and write results.

Outputs (eval/results/):
  heldout_by_family.csv      per family x defense: recall + across-seed spread
  heldout_overall.csv        per defense x coverage-block (in/partial/out/all)
  heldout_dose_response.csv  per family x defense x intensity: recall
  heldout_benign_controls.csv  benign sentinel-token removal, reported separately

Std-lib defenses (naive, perceptfence) run on all SEEDS; the real-Presidio baseline runs
on PRESIDIO_SEEDS (subset) because spaCy NER is the cost bottleneck — documented in
PROTOCOL.md. Reporting is a deterministic census: counts + across-seed min-max spread, no
population CIs.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

from generator import generate, generate_benign, FAMILY_PAYLOADS
from taxonomy import FAMILY_COVERAGE
from oracle import is_exposed, benign_blocked
from baselines import DEFENSES, presidio_available

SEEDS = list(range(20))
PRESIDIO_SEEDS = list(range(5))


def run_seed(seed: int, defense_fn, families: set[str]):
    """Return payload neutralization and benign-token removal counts."""
    per_family = defaultdict(lambda: [0, 0])      # family -> [neutralized(TP), exposed(FN)]
    per_family_intensity = defaultdict(lambda: [0, 0])  # (family,intensity)->[TP,FN]
    benign_removed = benign_preserved = 0
    for case in generate(seed):
        out = defense_fn(case.rendered)
        exposed = is_exposed(out, case.raw_payload)
        cell = per_family[case.family]
        cell[1 if exposed else 0] += 1
        ci = per_family_intensity[(case.family, case.intensity)]
        ci[1 if exposed else 0] += 1
        blocked = benign_blocked(out, case.benign_tokens)
        benign_removed += blocked
        benign_preserved += len(case.benign_tokens) - blocked
    for case in generate_benign(seed):
        out = defense_fn(case.rendered)
        blocked = benign_blocked(out, case.benign_tokens)
        benign_removed += blocked
        benign_preserved += len(case.benign_tokens) - blocked
    return per_family, per_family_intensity, benign_removed, benign_preserved


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    families = set(FAMILY_PAYLOADS)

    active = {"naive": DEFENSES["naive"], "perceptfence": DEFENSES["perceptfence"]}
    if presidio_available():
        active["presidio"] = DEFENSES["presidio"]
        print("Presidio: AVAILABLE (real tool, offline) — running on seeds", PRESIDIO_SEEDS)
    else:
        print("Presidio: NOT available in this interpreter — skipping (run with .evalvenv)")

    # accumulate per defense
    by_family_rows = []
    dose_rows = []
    overall_rows = []
    benign_rows = []

    for dname, dfn in active.items():
        seeds = PRESIDIO_SEEDS if dname == "presidio" else SEEDS
        # family -> list of per-seed recall; and summed tp/fn over seeds (from seed0 counts*?)
        fam_recalls = defaultdict(list)
        fam_tp = defaultdict(int)
        fam_fn = defaultdict(int)
        intensity_tp = defaultdict(int)
        intensity_fn = defaultdict(int)
        total_benign_removed = total_benign_preserved = 0
        for seed in seeds:
            pf, pfi, benign_removed, benign_preserved = run_seed(seed, dfn, families)
            total_benign_removed += benign_removed
            total_benign_preserved += benign_preserved
            for fam, (tp, fn) in pf.items():
                r = tp / (tp + fn) if (tp + fn) else 0.0
                fam_recalls[fam].append(r)
                fam_tp[fam] += tp
                fam_fn[fam] += fn
            for key, (tp, fn) in pfi.items():
                intensity_tp[key] += tp
                intensity_fn[key] += fn

        for fam in sorted(fam_recalls):
            rs = fam_recalls[fam]
            tp, fn = fam_tp[fam], fam_fn[fam]
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            by_family_rows.append({
                "defense": dname, "family": fam, "coverage": FAMILY_COVERAGE[fam],
                "n_payload_cases": tp + fn, "seeds": len(seeds),
                "recall": f"{recall:.3f}",
                "recall_min": f"{min(rs):.3f}", "recall_max": f"{max(rs):.3f}",
                "recall_seed_spread": f"{(max(rs) - min(rs)):.3f}",
                "neutralized": tp, "exposed": fn,
            })

        for (fam, inten) in sorted(intensity_tp):
            tp, fn = intensity_tp[(fam, inten)], intensity_fn[(fam, inten)]
            dose_rows.append({
                "defense": dname, "family": fam, "intensity": inten,
                "recall": f"{tp/(tp+fn):.3f}" if (tp+fn) else "0.000",
                "n": tp + fn,
            })

        # coverage-block aggregates
        for block in ("in", "partial", "out", "all"):
            tp = sum(fam_tp[f] for f in fam_tp if block == "all" or FAMILY_COVERAGE[f] == block)
            fn = sum(fam_fn[f] for f in fam_fn if block == "all" or FAMILY_COVERAGE[f] == block)
            if tp + fn == 0:
                continue
            recall = tp / (tp + fn)
            overall_rows.append({
                "defense": dname, "coverage_block": block,
                "n_payload_cases": tp + fn,
                "recall": f"{recall:.3f}",
                "neutralized": tp, "exposed": fn,
            })

        benign_total = total_benign_removed + total_benign_preserved
        benign_rows.append({
            "defense": dname,
            "seeds": len(seeds),
            "n_benign_tokens": benign_total,
            "benign_tokens_removed": total_benign_removed,
            "benign_tokens_preserved": total_benign_preserved,
            "benign_token_removal_rate": f"{total_benign_removed / benign_total:.3f}" if benign_total else "0.000",
        })

    # Merge-preserve: keep committed rows for any defense NOT run this invocation
    # (e.g. real Presidio when running without .evalvenv) so the public repro
    # command never silently deletes the Presidio baseline from the committed CSVs.
    active_names = set(active)
    _write(out_dir / "heldout_by_family.csv", _merge_preserve(out_dir / "heldout_by_family.csv", by_family_rows, active_names))
    _write(out_dir / "heldout_overall.csv", _merge_preserve(out_dir / "heldout_overall.csv", overall_rows, active_names))
    _write(out_dir / "heldout_dose_response.csv", _merge_preserve(out_dir / "heldout_dose_response.csv", dose_rows, active_names))
    _write(out_dir / "heldout_benign_controls.csv", _merge_preserve(out_dir / "heldout_benign_controls.csv", benign_rows, active_names))
    if "presidio" not in active_names:
        print("NOTE: preserved committed Presidio rows (not recomputed without .evalvenv).")

    print("\n=== HELD-OUT OVERALL (recall by coverage block) ===")
    for row in overall_rows:
        print(f"  {row['defense']:13} {row['coverage_block']:8} "
              f"recall={row['recall']} (n={row['n_payload_cases']}, exposed={row['exposed']})")
    print("\n=== HELD-OUT BENIGN-TOKEN REMOVAL (separate unit) ===")
    for row in benign_rows:
        print(f"  {row['defense']:13} removal_rate={row['benign_token_removal_rate']} "
              f"(removed={row['benign_tokens_removed']}, n={row['n_benign_tokens']})")
    print(f"\nWrote 4 CSVs to {out_dir}")


def _merge_preserve(path: Path, new_rows: list[dict], active_defenses: set) -> list[dict]:
    """Combine freshly-computed rows with committed rows for defenses not run now.

    Rows for any defense in active_defenses are taken from new_rows; rows for
    other defenses (e.g. presidio when skipped) are preserved from the existing
    file so a partial rerun never deletes them. Ordering: naive, perceptfence,
    presidio (stable), else file order.
    """
    preserved: list[dict] = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("defense") not in active_defenses:
                    preserved.append(row)
    combined = new_rows + preserved
    if new_rows:
        fields = list(new_rows[0])
        combined = [{key: row.get(key, "") for key in fields} for row in combined]
    order = {"naive": 0, "perceptfence": 1, "presidio": 2}
    return sorted(combined, key=lambda r: order.get(r.get("defense", ""), 9))


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
