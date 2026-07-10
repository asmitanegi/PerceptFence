"""Render the held-out dose-response figure as a stdlib-only SVG.

Reads ``eval/results/heldout_dose_response.csv`` and writes
``docs/figures/dose_response.svg``: PerceptFence recall vs. evasion intensity for
the normalization families the design targets (Unicode confusable, zero-width,
split-digit). This is the most informative single view of the held-out result —
graceful degradation under stronger evasion, with a characterized boundary.

Hand-built SVG (no third-party dependency) so it is bit-for-bit reproducible from
the same CSV. To embed in the LaTeX manuscript, convert to PDF
(`rsvg-convert -f pdf` / `inkscape` / `cairosvg`) and `\\includegraphics` it.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

WIDTH, HEIGHT = 720, 460
ML, MR, MT, MB = 70, 200, 70, 70
PLOT_W = WIDTH - ML - MR
PLOT_H = HEIGHT - MT - MB

# In/partial-coverage families the design targets (the robustness-relevant signal).
SERIES = [
    ("digit_split", "#2c7fb8", "split-digit PII"),
    ("unicode_confusable", "#d95f02", "Unicode confusable"),
    ("zero_width", "#7570b3", "zero-width insertion"),
]
FONT = '-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif'


def read_curves(csv_path: Path, defense: str):
    curves: dict[str, list[tuple[int, float]]] = {}
    with csv_path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["defense"] != defense:
                continue
            curves.setdefault(r["family"], []).append((int(r["intensity"]), float(r["recall"])))
    for fam in curves:
        curves[fam].sort()
    return curves


def render_svg(curves) -> str:
    intensities = sorted({i for fam in SERIES for i, _ in curves.get(fam[0], [])})
    if not intensities:
        raise SystemExit("no perceptfence dose-response rows found")
    xmin, xmax = min(intensities), max(intensities)

    def px(i):
        return ML + (PLOT_W * (i - xmin) / (xmax - xmin) if xmax > xmin else 0)

    def py(r):
        return MT + PLOT_H * (1.0 - r)

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
         f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
         f'aria-label="PerceptFence held-out recall versus evasion intensity">',
         '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
         f'<text x="{WIDTH/2}" y="34" text-anchor="middle" font-family="{FONT}" '
         f'font-size="18" font-weight="600" fill="#1a1a1a">Held-out recall vs. evasion '
         f'intensity (PerceptFence)</text>',
         f'<text x="{WIDTH/2}" y="55" text-anchor="middle" font-family="{FONT}" '
         f'font-size="12" fill="#666">Graceful degradation on targeted normalization '
         f'families; from heldout_dose_response.csv</text>']

    # y gridlines
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = py(t)
        p.append(f'<line x1="{ML}" y1="{y}" x2="{ML+PLOT_W}" y2="{y}" stroke="#ddd"/>')
        p.append(f'<text x="{ML-8}" y="{y+4}" text-anchor="end" font-family="{FONT}" '
                 f'font-size="11" fill="#333">{t:.2f}</text>')
    p.append(f'<text transform="rotate(-90 {ML-46} {MT+PLOT_H/2})" x="{ML-46}" '
             f'y="{MT+PLOT_H/2}" text-anchor="middle" font-family="{FONT}" font-size="12" '
             f'fill="#1a1a1a">Sensitive-content recall</text>')

    # x ticks
    for i in intensities:
        x = px(i)
        p.append(f'<line x1="{x}" y1="{MT+PLOT_H}" x2="{x}" y2="{MT+PLOT_H+5}" stroke="#333"/>')
        p.append(f'<text x="{x}" y="{MT+PLOT_H+20}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="11" fill="#333">{i}</text>')
    p.append(f'<text x="{ML+PLOT_W/2}" y="{MT+PLOT_H+44}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="12" fill="#1a1a1a">Evasion intensity</text>')
    p.append(f'<line x1="{ML}" y1="{MT+PLOT_H}" x2="{ML+PLOT_W}" y2="{MT+PLOT_H}" stroke="#333"/>')

    # series
    for k, (fam, color, label) in enumerate(SERIES):
        pts = curves.get(fam, [])
        if not pts:
            continue
        poly = " ".join(f"{px(i):.1f},{py(r):.1f}" for i, r in pts)
        p.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for i, r in pts:
            p.append(f'<circle cx="{px(i):.1f}" cy="{py(r):.1f}" r="3.5" fill="{color}"/>')
        ly = MT + 10 + k * 22
        p.append(f'<line x1="{ML+PLOT_W+14}" y1="{ly}" x2="{ML+PLOT_W+34}" y2="{ly}" '
                 f'stroke="{color}" stroke-width="2.5"/>')
        p.append(f'<text x="{ML+PLOT_W+40}" y="{ly+4}" font-family="{FONT}" font-size="12" '
                 f'fill="#1a1a1a">{label}</text>')

    p.append(f'<text x="{WIDTH-20}" y="{HEIGHT-12}" text-anchor="end" font-family="{FONT}" '
             f'font-size="10" fill="#666">Synthetic census; deterministic over 20 seeds</text>')
    p.append('</svg>')
    return "\n".join(p) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Render held-out dose-response SVG (stdlib).")
    ap.add_argument("--csv", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    csv_path = args.csv or (repo / "eval" / "results" / "heldout_dose_response.csv")
    out_path = args.out or (repo / "docs" / "figures" / "dose_response.svg")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_svg(read_curves(csv_path, "perceptfence")), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
