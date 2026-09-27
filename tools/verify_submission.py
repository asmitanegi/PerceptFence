#!/usr/bin/env python3
"""Pre-submission verification gate — fail loudly on a stale or divergent artifact.

This mechanizes the "are we shipping the current version?" checks that were
previously manual (and therefore skippable). Run it before building the package,
on every push (see tools/hooks/pre-push), and in CI. Exit code 0 = all gates
pass; non-zero = at least one FAIL (do not submit).

The verifier implementation is stdlib-only, but its test gate invokes pytest
through the current Python interpreter and fails closed if pytest is unavailable.

Gates
  1. test-count trace   : "contains N tests" in main.tex == actual `def test_` count
  2. csv no-stale-dupes  : every package copy of baseline_vs_guarded.csv is byte-identical
  3. supplement sync     : shipped result CSVs byte-match their canonical sources
  4. metric schema       : payload recall and benign-token removal use distinct units
  5. headline trace      : paired overall/block/digit-PII recalls in main.tex == paired CSV
  6. tests pass          : pytest 42/42; absence of a runnable pytest is a failure
  7. blind-leak          : author identity appears only in comments or \\else branches
  8. banned-term         : no unguarded banned claim in main.tex
  9. checksums           : (re)generate submission_checksums.sha256 and verify if present

Usage:  python3 tools/verify_submission.py [--write-checksums]
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "main.tex"
TESTS_DIR = ROOT / "tests"
OVERALL = ROOT / "eval" / "results" / "heldout_overall.csv"
BY_FAMILY = ROOT / "eval" / "results" / "heldout_by_family.csv"
PAIRED = ROOT / "eval" / "results" / "heldout_paired_presidio.csv"
BENIGN = ROOT / "eval" / "results" / "heldout_benign_controls.csv"
LATENCY_COPIES = [
    ROOT / "eval" / "results" / "baseline_vs_guarded.csv",
    ROOT / "supplement" / "baseline_vs_guarded.csv",
]
# Files whose bytes define the evidence-bearing submission; checksummed together.
PACK = [
    TEX,
    ROOT / "paper" / "authors_identity.tex",
    ROOT / "paper" / "references.bib",
    ROOT / "paper" / "figures" / "heldout_coverage.pdf",
    ROOT / "paper" / "figures" / "architecture_walkthrough.pdf",
    LATENCY_COPIES[0],
    ROOT / "eval" / "results" / "per_module_ablation.csv",
    ROOT / "eval" / "results" / "per_fixture_ablation.csv",
    OVERALL,
    BY_FAMILY,
    PAIRED,
    BENIGN,
    ROOT / "eval" / "results" / "heldout_dose_response.csv",
    ROOT / "eval" / "results" / "heldout_sensitivity.csv",
    ROOT / "eval" / "heldout" / "PROTOCOL.md",
    ROOT / "eval" / "heldout" / "run_paired_presidio.py",
    ROOT / "eval" / "render_coverage_figure.py",
    ROOT / "eval" / "render_architecture_figure.py",
    ROOT / "tools" / "build_submission_package.py",
    ROOT / "supplement" / "SUPPLEMENT_MANIFEST.md",
    ROOT / "supplement" / "artifact_checklist.md",
    ROOT / "supplement" / "README_REVIEW_ARTIFACT.md",
    ROOT / "supplement" / "CITATION.cff",
]

IDENTITY = ["Parafin", "Negi", "Singh", "Beshane", "Asmita", "Asmitha",
            "0009-0005-7566-9555", "0009-0002-2125-1805",
            "gmail", "asmitanegi07", "neerajkumarsingh", "b.neerajkumarsingh"]
BANNED = [r"\bprivacy-preserving\b", r"\btrustworthy\b", r"\bprevents leakage\b",
          r"\bprovably\b", r"\bbulletproof\b", r"\bguarantees privacy\b"]

results: list[tuple[str, bool, str]] = []


def gate(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "MISSING"


# 1. test-count trace ----------------------------------------------------------------------
def check_test_count() -> None:
    actual = sum(len(re.findall(r"^\s*def test_", f.read_text(), re.M))
                 for f in TESTS_DIR.glob("test_*.py"))
    m = re.search(r"contains\s+(\d+)\s+tests", TEX.read_text())
    stated = int(m.group(1)) if m else -1
    gate("test-count trace", stated == actual,
         f"manuscript says {stated}, suite has {actual}")


# 2. csv no-stale-duplicates ---------------------------------------------------------------
def check_csv_dupes() -> None:
    digs = {p: sha(p) for p in LATENCY_COPIES}
    uniq = set(digs.values())
    gate("csv no-stale-dupes", len(uniq) == 1 and "MISSING" not in uniq,
         "all latency CSV copies identical" if len(uniq) == 1
         else "DIVERGENT copies: " + "; ".join(f"{p.relative_to(ROOT)}={d[:8]}" for p, d in digs.items()))


# 2b. supplement matches canonical source --------------------------------------------------
def check_supplement_sync() -> None:
    """Every result CSV shipped in supplement/ must byte-match the canonical
    eval/results/ copy — so the uploaded bundle can never be a stale version."""
    src_dir = ROOT / "eval" / "results"
    sup_dir = ROOT / "supplement"
    drift = []
    checked = 0
    for sup in sorted(sup_dir.glob("*.csv")):
        canon = src_dir / sup.name
        if not canon.exists():
            drift.append(f"{sup.name}: no canonical source in eval/results")
            continue
        checked += 1
        if sha(sup) != sha(canon):
            drift.append(f"{sup.name}: supplement != source")
    gate("supplement sync", not drift,
         f"{checked} shipped CSV(s) match canonical source" if not drift
         else "; ".join(drift))


# 3. headline number trace -----------------------------------------------------------------
def _csv_rows(path: Path) -> list[dict]:
    import csv
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def check_heldout_metric_schema() -> None:
    """Keep payload-case recall and benign-token removal as separate units."""
    import csv

    expected_overall = {
        "defense", "coverage_block", "n_payload_cases", "recall", "neutralized", "exposed"
    }
    expected_benign = {
        "defense", "seeds", "n_benign_tokens", "benign_tokens_removed",
        "benign_tokens_preserved", "benign_token_removal_rate",
    }
    problems = []
    with OVERALL.open(newline="") as fh:
        overall_fields = set(csv.DictReader(fh).fieldnames or [])
    with BENIGN.open(newline="") as fh:
        benign_fields = set(csv.DictReader(fh).fieldnames or [])
    if overall_fields != expected_overall:
        problems.append(f"heldout_overall fields={sorted(overall_fields)}")
    if benign_fields != expected_benign:
        problems.append(f"heldout_benign_controls fields={sorted(benign_fields)}")
    for row in _csv_rows(BENIGN):
        total = int(row["n_benign_tokens"])
        removed = int(row["benign_tokens_removed"])
        preserved = int(row["benign_tokens_preserved"])
        if removed + preserved != total:
            problems.append(f"{row['defense']} benign counts do not sum")
        expected_rate = f"{removed / total:.3f}" if total else "0.000"
        if row["benign_token_removal_rate"] != expected_rate:
            problems.append(f"{row['defense']} benign rate mismatch")
    gate("heldout metric schema", not problems,
         "payload recall and benign-token removal use separate valid schemas"
         if not problems else "; ".join(problems))


def check_headline_trace() -> None:
    tex = TEX.read_text()
    missing = []
    paired = _csv_rows(PAIRED)
    defenses = {row["defense"] for row in paired}
    expected_defenses = {"naive", "perceptfence", "presidio"}
    if defenses != expected_defenses:
        missing.append(f"paired defenses {sorted(defenses)} != {sorted(expected_defenses)}")
    # Every cross-tool headline must come from the same seed-paired case set.
    for defense in ("naive", "perceptfence", "presidio"):
        defense_rows = [r for r in paired if r["defense"] == defense]
        for label, rows in (
            ("overall", defense_rows),
            ("in-coverage", [r for r in defense_rows if r["coverage"] == "in"]),
            ("partial", [r for r in defense_rows if r["coverage"] == "partial"]),
            ("out-of-coverage", [r for r in defense_rows if r["coverage"] == "out"]),
        ):
            neutralized = sum(int(r["neutralized"]) for r in rows)
            total = sum(int(r["n_payload_cases"]) for r in rows)
            val = f"{neutralized / total:.3f}"
            if val not in tex:
                missing.append(f"{defense} paired {label} {val}")
    # Digit-PII like-for-like control on the paired Presidio seed subset.
    for r in paired:
        if r["family"] == "digit_split":
            if r["recall"] not in tex:
                missing.append(f"{r['defense']} digit_split {r['recall']}")
    gate("headline number trace", not missing,
         "every printed headline number matches the canonical CSV" if not missing
         else "printed-but-untraceable / stale: " + ", ".join(missing))


# 4. tests pass ----------------------------------------------------------------------------
def check_tests() -> None:
    p = subprocess.run([sys.executable, "-m", "pytest", str(TESTS_DIR), "-q"],
                       capture_output=True, text=True, cwd=ROOT)
    last = ((p.stdout + p.stderr).strip().splitlines() or ["(no output)"])[-1]
    gate("tests pass", p.returncode == 0, last)


# 5. blind-leak ----------------------------------------------------------------------------
def check_blind_leak() -> None:
    """When the review build is active (\\blindtrue), no author identity may sit on a
    RENDERED line: identity is allowed only in comments or inside an \\else...\\fi branch."""
    text = TEX.read_text()
    blind_active = bool(re.search(r"^\s*\\blindtrue", text, re.M))
    leaks = []
    in_blind = False        # inside \ifblind ... \else
    in_else = False         # inside \else ... \fi  (the de-anon branch — allowed)
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith(r"\ifblind"):
            in_blind, in_else = True, False
            continue
        if in_blind and line.startswith(r"\else"):
            in_else = True
            continue
        if in_blind and line.startswith(r"\fi"):
            in_blind = in_else = False
            continue
        code = line.split("%", 1)[0]          # drop comment portion
        if not code.strip():
            continue                          # pure comment / blank → never rendered
        if in_else:
            continue                          # de-anon branch, not in the blind PDF
        for tok in IDENTITY:
            if tok in code:
                leaks.append(f"L{i}: '{tok}' in rendered text")
    # Only a hard FAIL when the blind build is the one selected.
    ok = (not leaks) or (not blind_active)
    detail = ("no identity on rendered lines" if not leaks
              else ("LEAKS (blind build active): " + "; ".join(leaks[:4]) if blind_active
                    else "identity on rendered lines but \\blindfalse (de-anon build) — OK"))
    gate("blind-leak", ok, detail)


# 6. banned-term ---------------------------------------------------------------------------
def check_banned() -> None:
    text = "\n".join(l.split("%", 1)[0] for l in TEX.read_text().splitlines())
    hits = [pat for pat in BANNED if re.search(pat, text, re.I)]
    gate("banned-term", not hits, "clean" if not hits else "hits: " + ", ".join(hits))


# 7. checksums -----------------------------------------------------------------------------
def check_checksums(write: bool) -> None:
    manifest = ROOT / "submission_checksums.sha256"
    missing = [p.relative_to(ROOT) for p in PACK if not p.exists()]
    if missing:
        gate("checksums", False,
             "required PACK file(s) missing: " + ", ".join(map(str, missing)))
        return
    current = "".join(f"{sha(p)}  {p.relative_to(ROOT)}\n" for p in PACK)
    if write or not manifest.exists():
        manifest.write_text(current)
        gate("checksums", True, f"{'wrote' if write else 'initialized'} {manifest.name}")
        return
    gate("checksums", manifest.read_text() == current,
         "submission pack matches committed checksums"
         if manifest.read_text() == current
         else f"PACK CHANGED since checksums were written — rerun with --write-checksums after intentional edits")


def main() -> int:
    write = "--write-checksums" in sys.argv
    for fn in (check_test_count, check_csv_dupes, check_supplement_sync,
               check_heldout_metric_schema, check_headline_trace, check_tests,
               check_blind_leak, check_banned):
        fn()
    check_checksums(write)

    print("\nPre-submission verification gate\n" + "=" * 34)
    failed = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"  [{mark}] {name:22} {detail}")
    print("=" * 34)
    if failed:
        print(f"{failed} gate(s) FAILED — do NOT submit until resolved.")
        return 1
    print("All gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
