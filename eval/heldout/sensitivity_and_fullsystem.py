"""Diagnostic runs that turn two reviewer concerns from assertion into measurement.

(1) 0.7-threshold sensitivity: re-score the held-out census at recoverability
    thresholds 0.5 / 0.7 / 0.9 and report overall recall per defense, so the
    PerceptFence > Presidio > naive ordering can be shown stable (or not).

(2) Full-system held-out probe: route the held-out payloads through the FULL
    guarded path (policy -> redaction -> memory gate -> output guard, via
    RuntimeMediator.run_guarded) and score the union of the model-context and
    assistant-output surfaces with the same separately implemented oracle, then compare to
    the redaction-only number. Answers "does the system, not just redaction.py,
    neutralize the held-out payloads?"

Std-lib only (naive + perceptfence + full-system). Presidio is excluded here
because it needs .evalvenv; the committed 0.7 Presidio numbers stand as-is.
Does NOT overwrite any committed CSV — prints a report and writes one new file
(heldout_sensitivity.csv) under eval/results/.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

from generator import generate
from taxonomy import FAMILY_COVERAGE
from oracle import maximal_forms, _canon, _leet_variant
from baselines import naive_redact, perceptfence_redact

SEEDS = list(range(20))


def is_exposed_at(defense_output: str, canonical_secret: str, frac: float) -> bool:
    """is_exposed with a parameterized recoverability threshold (oracle uses 0.7)."""
    if not canonical_secret:
        return False
    base = _canon(canonical_secret)
    if not base:
        return False
    targets = {base, _leet_variant(base)}
    forms = maximal_forms(defense_output)
    for target in targets:
        thresh = math.ceil(frac * len(target))
        for form in forms:
            if target in form:
                return True
            for start in range(0, len(target) - thresh + 1):
                if target[start:start + thresh] in form:
                    return True
    return False


# --- (2) full-system defense -------------------------------------------------------------
_mediator = None


def fullsystem_redact(text: str) -> str:
    """Route text through the full guarded path; return the union of the surfaces
    an exposure oracle should police (model context + assistant output)."""
    global _mediator
    if _mediator is None:
        import sys
        src_pkg = Path(__file__).resolve().parents[2]
        if str(src_pkg) not in sys.path:
            sys.path.insert(0, str(src_pkg))
        from screenshare_mediator.runtime import RuntimeMediator
        policy = Path(__file__).resolve().parents[2] / "policies" / "consent_redaction_policy.json"
        _mediator = RuntimeMediator(policy)
    fixture = {
        "id": "heldout",
        "scenario_class": "terminal_secret",
        "modality": ["screen_text"],
        "input": {"window_title": "", "visible_text": text},
    }
    res = _mediator.run_guarded(fixture)
    # The oracle scores recoverability anywhere the assistant could leak it.
    return f"{res.model_context}\n{res.assistant_output}"


def overall_recall(defense_fn, frac: float):
    """Return (overall_recall, by_block dict) over all seeds at threshold frac."""
    tp = defaultdict(int)
    fn = defaultdict(int)
    for seed in SEEDS:
        for case in generate(seed):
            exposed = is_exposed_at(defense_fn(case.rendered), case.raw_payload, frac)
            block = FAMILY_COVERAGE[case.family]
            key = block
            if exposed:
                fn[key] += 1
            else:
                tp[key] += 1
    blocks = {}
    tot_tp = tot_fn = 0
    for b in ("in", "partial", "out"):
        t, f = tp[b], fn[b]
        tot_tp += t
        tot_fn += f
        blocks[b] = t / (t + f) if (t + f) else 0.0
    blocks["all"] = tot_tp / (tot_tp + tot_fn) if (tot_tp + tot_fn) else 0.0
    return blocks


def main() -> None:
    defenses = {"naive": naive_redact, "perceptfence": perceptfence_redact,
                "fullsystem": fullsystem_redact}

    print("=== (1) THRESHOLD SENSITIVITY — overall recall (20 seeds) ===")
    rows = []
    for frac in (0.5, 0.7, 0.9):
        line = []
        for dname, dfn in defenses.items():
            blocks = overall_recall(dfn, frac)
            line.append(f"{dname}={blocks['all']:.3f}")
            rows.append({"threshold": frac, "defense": dname,
                         "recall_in": f"{blocks['in']:.3f}",
                         "recall_partial": f"{blocks['partial']:.3f}",
                         "recall_out": f"{blocks['out']:.3f}",
                         "recall_overall": f"{blocks['all']:.3f}"})
        print(f"  thresh={frac}: " + "  ".join(line))

    print("\n=== (2) FULL-SYSTEM vs REDACTION-ONLY @ 0.7 (20 seeds) ===")
    pf = overall_recall(perceptfence_redact, 0.7)
    fs = overall_recall(fullsystem_redact, 0.7)
    print(f"  redaction-only: in={pf['in']:.3f} partial={pf['partial']:.3f} "
          f"out={pf['out']:.3f} overall={pf['all']:.3f}")
    print(f"  full guarded  : in={fs['in']:.3f} partial={fs['partial']:.3f} "
          f"out={fs['out']:.3f} overall={fs['all']:.3f}")
    delta = fs['all'] - pf['all']
    print(f"  delta(overall) = {delta:+.3f}  "
          f"({'identical' if abs(delta) < 1e-9 else 'differs'})")

    out_dir = Path(__file__).resolve().parents[1] / "results"
    out_path = out_dir / "heldout_sensitivity.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
