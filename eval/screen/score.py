"""Score defenses on OCR'd real-rendered screens.

For every case, each defense receives the identical OCR text. Exposure is judged
by the paper's separately implemented oracle (eval/heldout/oracle.py:is_exposed),
applied to the canonical planted value. A payload is only *eligible* when the
secret survived OCR in the raw text (is_exposed(raw_ocr, secret) is True);
payloads that OCR itself destroyed are reported separately as ocr_lost and are
never counted as defense wins.

Benign utility: fraction of the case's task tokens (error codes, file names,
status strings) still present, compared against their presence in the raw OCR.

Defenses: none, naive, perceptfence (current engine), presidio, gitleaks
(v8 default ruleset; findings -> spans replaced with [REDACTED]).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from eval.heldout import baselines, oracle  # noqa: E402
from eval.screen import corpus  # noqa: E402


def gitleaks_available() -> bool:
    return shutil.which("gitleaks") is not None


def gitleaks_redact(text: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        rep = Path(td) / "r.json"
        subprocess.run(["gitleaks", "stdin", "--no-banner", "--log-level", "error", "--exit-code", "0",
                        "--report-format", "json", "--report-path", str(rep)],
                       input=text, text=True, capture_output=True, timeout=60)
        findings = json.loads(rep.read_text() or "[]") if rep.exists() else []
    out = text
    for f in sorted({f["Secret"] for f in findings if f.get("Secret")}, key=len, reverse=True):
        out = out.replace(f, "[REDACTED]")
    return out


def load_ocr(path: Path) -> dict[str, str]:
    return {r["case_id"]: r["ocr"] for r in map(json.loads, path.read_text().splitlines())}


def defenses(include_presidio: bool, include_gitleaks: bool) -> dict:
    d = {"none": lambda t: t, "naive": baselines.naive_redact,
         "perceptfence_v03": baselines.perceptfence_v03_redact, "perceptfence": baselines.perceptfence_redact}
    if include_presidio and baselines.presidio_available():
        d["presidio"] = baselines.presidio_redact
    if include_gitleaks and gitleaks_available():
        d["gitleaks"] = gitleaks_redact
    return d


def score(cases: list[corpus.ScreenCase], ocr: dict[str, str], defs: dict) -> list[dict]:
    rows = []
    for c in cases:
        raw = ocr[c.case_id]
        outs = {name: fn(raw) for name, fn in defs.items()}
        benign_raw = [t for t in c.benign if oracle._canon(t) in oracle._canon(raw)]
        for i, p in enumerate(c.planted):
            eligible = oracle.is_exposed(raw, p.secret)
            base = {"case_id": c.case_id, "template": c.template, "split": c.split, "seed": c.seed,
                    "theme": c.theme, "font_px": c.font_px, "quality": c.quality, "payload_idx": i,
                    "kind": p.kind, "eligible": int(eligible)}
            for name, out in outs.items():
                kept = sum(1 for t in benign_raw if oracle._canon(t) in oracle._canon(out))
                rows.append({**base, "defense": name,
                             "exposed": int(eligible and oracle.is_exposed(out, p.secret)),
                             "benign_total": len(benign_raw), "benign_kept": kept})
    return rows


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def cluster_bootstrap_diff(rows: list[dict], a: str, b: str, iters: int = 2000, seed: int = 7) -> tuple[float, float, float]:
    """Paired difference in neutralisation (a - b), resampling (seed, template) clusters."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["eligible"] and r["defense"] in (a, b):
            by[(r["seed"], r["template"])][r["defense"]].append(1 - r["exposed"])
    keys = list(by)
    def diff(ks):
        na = sum(sum(by[k][a]) for k in ks); nb = sum(sum(by[k][b]) for k in ks)
        n = sum(len(by[k][a]) for k in ks)
        return (na - nb) / n if n else float("nan")
    point = diff(keys)
    rng = random.Random(seed)
    samples = sorted(diff([rng.choice(keys) for _ in keys]) for _ in range(iters))
    return point, samples[int(0.025 * iters)], samples[int(0.975 * iters)]


def summarise(rows: list[dict]) -> dict:
    out: dict = {"by_defense": {}, "by_defense_kind": {}, "by_defense_quality": {}, "by_defense_split": {}, "ocr": {}}
    elig = [r for r in rows if r["defense"] == "none"]
    out["ocr"] = {"payloads": len(elig), "eligible": sum(r["eligible"] for r in elig),
                  "ocr_lost": sum(1 - r["eligible"] for r in elig)}
    groups = {"by_defense": lambda r: r["defense"],
              "by_defense_kind": lambda r: f'{r["defense"]}|{r["kind"]}',
              "by_defense_quality": lambda r: f'{r["defense"]}|{r["quality"]}',
              "by_defense_split": lambda r: f'{r["defense"]}|{r["split"]}'}
    for gname, key in groups.items():
        acc = defaultdict(lambda: [0, 0, 0, 0])
        seen_case = set()
        for r in rows:
            k = key(r)
            if r["eligible"]:
                acc[k][0] += 1
                acc[k][1] += 1 - r["exposed"]
            ck = (k, r["case_id"])
            if ck not in seen_case:
                seen_case.add(ck)
                acc[k][2] += r["benign_total"]; acc[k][3] += r["benign_kept"]
        for k, (n, neut, bt, bk) in sorted(acc.items()):
            lo, hi = wilson(neut, n)
            out[gname][k] = {"eligible": n, "neutralised": neut, "rate": round(neut / n, 4) if n else None,
                             "wilson95": [round(lo, 4), round(hi, 4)],
                             "benign_retention": round(bk / bt, 4) if bt else None}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=("dev", "test"), required=True)
    ap.add_argument("--ocr", type=Path, required=True)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--no-presidio", action="store_true")
    a = ap.parse_args()
    cases = corpus.dev_cases() if a.split == "dev" else corpus.test_cases()
    defs = defenses(not a.no_presidio, True)
    rows = score(cases, load_ocr(a.ocr), defs)
    a.csv.parent.mkdir(parents=True, exist_ok=True)
    with a.csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    s = summarise(rows)
    s["defenses"] = list(defs)
    pairs = [("perceptfence", d) for d in defs if d not in ("perceptfence", "none")]
    s["paired_diff_bootstrap95"] = {f"{x}-{y}": [round(v, 4) for v in cluster_bootstrap_diff(rows, x, y)] for x, y in pairs}
    a.summary.write_text(json.dumps(s, indent=2))
    print(json.dumps({"ocr": s["ocr"], "by_defense": s["by_defense"], "paired": s["paired_diff_bootstrap95"]}, indent=1))


if __name__ == "__main__":
    main()
