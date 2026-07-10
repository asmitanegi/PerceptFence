"""Render the headline benchmark figure as a stdlib-only SVG.

Reads ``eval/results/baseline_vs_guarded.csv`` and writes
``docs/figures/headline_ser.svg``: a grouped-bar chart of sensitive exposure
rate (SER) per scenario class for the baseline and guarded paths, with the
overall headline numbers (SER delta, FBR, TSR, latency overhead) annotated.

We hand-build the SVG so the figure has no third-party dependency and is
reproducible bit-for-bit from the same CSV input.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path
from typing import Any

# Layout constants (px).
WIDTH = 920
HEIGHT = 540
MARGIN_LEFT = 90
MARGIN_RIGHT = 30
MARGIN_TOP = 90
MARGIN_BOTTOM = 200  # room for rotated category labels + legend
PLOT_W = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
PLOT_H = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
GROUP_GAP_FRAC = 0.25   # fraction of group width left as gap between groups
BAR_GAP_PX = 4

COLOR_BASELINE = "#c0392b"    # warm red — exposed
COLOR_GUARDED = "#2c7fb8"     # cool blue — mediated
COLOR_GRID = "#dddddd"
COLOR_AXIS = "#333333"
COLOR_TEXT = "#1a1a1a"
COLOR_SUBTLE = "#666666"


def _x_escape(text: str) -> str:
    """Minimal XML escape sufficient for this generator's inputs."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;"))


def read_per_class(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def render_svg(rows: list[dict[str, Any]]) -> str:
    # Pivot per-class rows into baseline/guarded pairs in fixture index order.
    categories: list[str] = []
    baseline_ser: dict[str, float] = {}
    guarded_ser: dict[str, float] = {}
    baseline_lat: dict[str, float] = {}
    guarded_lat: dict[str, float] = {}
    for row in rows:
        cat = row["category"]
        if cat not in categories:
            categories.append(cat)
        ser = float(row["SER"])
        med = float(row["median_dt_ms"])
        if row["path"] == "baseline":
            baseline_ser[cat] = ser
            baseline_lat[cat] = med
        else:
            guarded_ser[cat] = ser
            guarded_lat[cat] = med

    n = len(categories)
    group_w = PLOT_W / n
    bar_w = (group_w * (1.0 - GROUP_GAP_FRAC) - BAR_GAP_PX) / 2

    # Aggregates for headline annotation (recompute from rows so the figure is
    # self-consistent with the CSV that produced it).
    n_units_baseline = sum(1.0 for v in baseline_ser.values() if v > 0.0)
    n_units_guarded = sum(1.0 for v in guarded_ser.values() if v > 0.0)
    avg_baseline = statistics.mean(baseline_ser.values()) if baseline_ser else 0.0
    avg_guarded = statistics.mean(guarded_ser.values()) if guarded_ser else 0.0
    overhead_ms = (statistics.median(list(guarded_lat.values()))
                   - statistics.median(list(baseline_lat.values())))

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'role="img" aria-label="Sensitive exposure rate per scenario class, baseline vs guarded">'
    )
    parts.append(
        '<title>PerceptFence sensitive exposure rate per scenario class, '
        'baseline vs guarded (synthetic fixture set)</title>'
    )
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')

    # Title and subtitle.
    parts.append(
        f'<text x="{WIDTH/2}" y="36" text-anchor="middle" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
        f'font-size="20" font-weight="600" fill="{COLOR_TEXT}">'
        f'Sensitive exposure rate per scenario class &#x2014; baseline vs guarded</text>'
    )
    subtitle = (
        f"Synthetic fixture set, n = {n} scenario classes. "
        f"Mean SER {avg_baseline:.2f} &#x2192; {avg_guarded:.2f}. "
        f"Median latency overhead {overhead_ms*1000:.1f} &#xb5;s."
    )
    parts.append(
        f'<text x="{WIDTH/2}" y="60" text-anchor="middle" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
        f'font-size="13" fill="{COLOR_SUBTLE}">{subtitle}</text>'
    )

    # Y-axis gridlines and labels (0.0, 0.25, 0.5, 0.75, 1.0).
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = MARGIN_TOP + PLOT_H * (1.0 - tick)
        parts.append(
            f'<line x1="{MARGIN_LEFT}" y1="{y}" x2="{MARGIN_LEFT + PLOT_W}" y2="{y}" '
            f'stroke="{COLOR_GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{MARGIN_LEFT - 8}" y="{y + 4}" text-anchor="end" '
            f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
            f'font-size="11" fill="{COLOR_AXIS}">{tick:.2f}</text>'
        )

    # Y-axis title.
    parts.append(
        f'<text transform="rotate(-90 {MARGIN_LEFT - 50} {MARGIN_TOP + PLOT_H/2})" '
        f'x="{MARGIN_LEFT - 50}" y="{MARGIN_TOP + PLOT_H/2}" text-anchor="middle" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
        f'font-size="12" fill="{COLOR_TEXT}">Sensitive exposure rate (SER)</text>'
    )

    # Bars per category.
    for idx, cat in enumerate(categories):
        x_group = MARGIN_LEFT + idx * group_w + (group_w * GROUP_GAP_FRAC) / 2
        b_ser = baseline_ser.get(cat, 0.0)
        g_ser = guarded_ser.get(cat, 0.0)
        # baseline bar
        b_h = b_ser * PLOT_H
        parts.append(
            f'<rect x="{x_group}" y="{MARGIN_TOP + PLOT_H - b_h}" '
            f'width="{bar_w}" height="{b_h}" fill="{COLOR_BASELINE}" '
            f'aria-label="{_x_escape(cat)} baseline SER {b_ser:.2f}"/>'
        )
        # guarded bar
        g_h = g_ser * PLOT_H
        parts.append(
            f'<rect x="{x_group + bar_w + BAR_GAP_PX}" y="{MARGIN_TOP + PLOT_H - g_h}" '
            f'width="{bar_w}" height="{g_h}" fill="{COLOR_GUARDED}" '
            f'aria-label="{_x_escape(cat)} guarded SER {g_ser:.2f}"/>'
        )
        # value label above each bar (tiny font)
        parts.append(
            f'<text x="{x_group + bar_w/2}" y="{MARGIN_TOP + PLOT_H - b_h - 4}" '
            f'text-anchor="middle" '
            f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
            f'font-size="10" fill="{COLOR_AXIS}">{b_ser:.2f}</text>'
        )
        parts.append(
            f'<text x="{x_group + bar_w + BAR_GAP_PX + bar_w/2}" '
            f'y="{MARGIN_TOP + PLOT_H - g_h - 4}" text-anchor="middle" '
            f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
            f'font-size="10" fill="{COLOR_AXIS}">{g_ser:.2f}</text>'
        )
        # category label, rotated -45 deg
        cx = x_group + group_w * (1 - GROUP_GAP_FRAC) / 2
        cy = MARGIN_TOP + PLOT_H + 14
        parts.append(
            f'<text x="{cx}" y="{cy}" text-anchor="end" '
            f'transform="rotate(-35 {cx} {cy})" '
            f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
            f'font-size="11" fill="{COLOR_AXIS}">{_x_escape(cat)}</text>'
        )

    # X-axis line.
    parts.append(
        f'<line x1="{MARGIN_LEFT}" y1="{MARGIN_TOP + PLOT_H}" '
        f'x2="{MARGIN_LEFT + PLOT_W}" y2="{MARGIN_TOP + PLOT_H}" '
        f'stroke="{COLOR_AXIS}" stroke-width="1"/>'
    )

    # Legend (bottom right).
    legend_y = HEIGHT - 30
    legend_x = MARGIN_LEFT + 10
    parts.append(
        f'<rect x="{legend_x}" y="{legend_y - 12}" width="14" height="14" fill="{COLOR_BASELINE}"/>'
    )
    parts.append(
        f'<text x="{legend_x + 20}" y="{legend_y}" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
        f'font-size="12" fill="{COLOR_TEXT}">baseline (unmediated)</text>'
    )
    parts.append(
        f'<rect x="{legend_x + 180}" y="{legend_y - 12}" width="14" height="14" fill="{COLOR_GUARDED}"/>'
    )
    parts.append(
        f'<text x="{legend_x + 200}" y="{legend_y}" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
        f'font-size="12" fill="{COLOR_TEXT}">guarded (full mediation)</text>'
    )

    # Footer note.
    parts.append(
        f'<text x="{WIDTH - 20}" y="{HEIGHT - 12}" text-anchor="end" '
        f'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{COLOR_SUBTLE}">'
        f'Synthetic fixtures only; rendered from baseline_vs_guarded.csv'
        f'</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the headline SER figure as stdlib-only SVG."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Path to baseline_vs_guarded.csv (default: ../eval/results from this script).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Path to output SVG (default: ../docs/figures/headline_ser.svg).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    csv_path = args.csv or (repo_root / "eval" / "results" / "baseline_vs_guarded.csv")
    out_path = args.out or (repo_root / "docs" / "figures" / "headline_ser.svg")

    rows = read_per_class(csv_path)
    if not rows:
        raise SystemExit(f"No rows in {csv_path}; run benchmark.py first.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_svg(rows), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
