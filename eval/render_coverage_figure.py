"""Render the paper's held-out coverage-boundary figure from committed results.

The figure compares PerceptFence with the real Microsoft Presidio baseline on
the identical generated cases from paired seeds 0--4. It separates targeted/partial families
from declared out-of-coverage families so the plot cannot hide the boundary in
an overall average.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path


FAMILY_ORDER = {
    "targeted": ["digit_split", "unicode_confusable", "zero_width", "fullwidth_compat", "chained"],
    "out": ["base64", "hex", "leetspeak", "rot13", "bidi_override", "instruction_paraphrase"],
}
LABELS = {
    "digit_split": "split-digit PII",
    "unicode_confusable": "Unicode confusable",
    "zero_width": "zero-width insertion",
    "fullwidth_compat": "full-width / compatibility",
    "chained": "chained transforms",
    "base64": "Base64",
    "hex": "hex",
    "leetspeak": "leetspeak",
    "rot13": "ROT13",
    "bidi_override": "bidirectional override",
    "instruction_paraphrase": "instruction wrapping*",
}


def read_results(path: Path) -> dict[str, dict[str, float]]:
    data: dict[str, dict[str, float]] = {"perceptfence": {}, "presidio": {}}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            defense = row["defense"]
            if defense in data:
                data[defense][row["family"]] = float(row["recall"])
    missing = [
        f"{defense}:{family}"
        for defense in data
        for family in FAMILY_ORDER["targeted"] + FAMILY_ORDER["out"]
        if family not in data[defense]
    ]
    if missing:
        raise SystemExit("missing result rows: " + ", ".join(missing))
    return data


def render(data: dict[str, dict[str, float]], pdf_path: Path, png_path: Path) -> None:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9.5,
            "legend.fontsize": 9,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(8.2, 4.8),
        sharex=True,
        gridspec_kw={"width_ratios": [1.0, 1.12], "wspace": 0.42},
    )
    colors = {"perceptfence": "#2166AC", "presidio": "#8C8C8C"}
    bar_height = 0.34

    for ax, block, title in zip(
        axes,
        ("targeted", "out"),
        ("Targeted/partial families\npaired seeds 0–4", "Out-of-coverage families\npaired seeds 0–4"),
    ):
        families = FAMILY_ORDER[block]
        y = np.arange(len(families))
        pf = [data["perceptfence"][family] for family in families]
        pr = [data["presidio"][family] for family in families]

        ax.barh(y - bar_height / 2, pf, height=bar_height, color=colors["perceptfence"], label="PerceptFence")
        ax.barh(y + bar_height / 2, pr, height=bar_height, color=colors["presidio"], label="Microsoft Presidio")
        ax.set_yticks(y, [LABELS[family] for family in families])
        ax.invert_yaxis()
        ax.set_xlim(0, 1.0)
        ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
        ax.grid(axis="x", color="#E2E2E2", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.set_title(title, loc="left", fontweight="semibold", pad=8)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel("Recall (fraction of payloads neutralised)")

        for yi, value in zip(y - bar_height / 2, pf):
            ax.text(min(value + 0.018, 0.96), yi, f"{value:.3f}", va="center", ha="left", fontsize=8.5, color="#174A78")
        for yi, value in zip(y + bar_height / 2, pr):
            ax.text(min(value + 0.018, 0.96), yi, f"{value:.3f}", va="center", ha="left", fontsize=8.5, color="#555555")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.005),
    )
    fig.text(
        0.19,
        0.08,
        "* Legacy CSV identifier: instruction_paraphrase; templates retain the instruction verbatim.",
        fontsize=8.0,
        color="#555555",
    )
    fig.subplots_adjust(left=0.21, right=0.975, top=0.92, bottom=0.24)

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "Title": "Held-out recall by evasion family and coverage boundary",
        "Author": "Anonymous",
        "Subject": "Generated from eval/results/heldout_paired_presidio.csv",
        "CreationDate": datetime(2026, 7, 9, tzinfo=timezone.utc),
        "ModDate": datetime(2026, 7, 9, tzinfo=timezone.utc),
    }
    fig.savefig(pdf_path, format="pdf", metadata=metadata)
    fig.savefig(png_path, format="png", dpi=220, facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--png", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    csv_path = args.csv or root / "eval" / "results" / "heldout_paired_presidio.csv"
    pdf_path = args.pdf or root / "paper" / "figures" / "heldout_coverage.pdf"
    png_path = args.png or root / "paper" / "figures" / "heldout_coverage.png"
    render(read_results(csv_path), pdf_path, png_path)
    print(f"Wrote {pdf_path}")
    print(f"Wrote {png_path}")


if __name__ == "__main__":
    main()
