"""Render the evidence-bounded PerceptFence architecture walkthrough.

Solid boxes are implemented in the released synthetic-fixture scaffold; dashed
boxes are target-design components not implemented or evaluated in this paper.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def render(pdf_path: Path, png_path: Path) -> None:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.8))
    ax.set_xlim(0, 8.4)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    def box(x, y, w, h, title, body, color, dashed=False, fontsize=9.2):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            linewidth=1.4,
            edgecolor=color,
            facecolor="#FFFFFF" if dashed else color + "16",
            linestyle="--" if dashed else "-",
        )
        ax.add_patch(patch)
        ax.text(x + 0.10, y + h - 0.14, title, va="top", ha="left", weight="bold", color=color, fontsize=10.0)
        ax.text(x + 0.10, y + h - 0.52, body, va="top", ha="left", color="#222222", fontsize=fontsize, linespacing=1.12)
        return patch

    def arrow(x1, y1, x2, y2, color="#4A4A4A", dashed=False, label=None, label_y=0.1):
        a = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.2,
            color=color,
            linestyle="--" if dashed else "-",
            shrinkA=2,
            shrinkB=2,
        )
        ax.add_patch(a)
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + label_y, label, ha="center", va="bottom", fontsize=8.5, color=color)

    # Target boundary — deliberately dashed and visually separated.
    ax.text(0.20, 5.55, "TARGET LIVE PIPELINE — not implemented or evaluated", weight="bold", color="#8B5A2B", fontsize=11.2)
    box(0.20, 4.43, 1.45, 0.82, "Live capture", "screen · audio\nOCR · ASR", "#8B5A2B", dashed=True, fontsize=8.7)
    box(1.95, 4.43, 1.45, 0.82, "Consent state", "authenticate\nre-consent · revoke", "#8B5A2B", dashed=True, fontsize=8.7)
    box(3.70, 4.43, 1.45, 0.82, "Persistent memory", "cross-turn and\nsession store", "#8B5A2B", dashed=True, fontsize=8.7)
    box(5.45, 4.43, 1.45, 0.82, "External model", "named, pinned\nassistant adapter", "#8B5A2B", dashed=True, fontsize=8.7)
    arrow(1.65, 4.84, 1.95, 4.84, color="#8B5A2B", dashed=True)
    arrow(3.40, 4.84, 3.70, 4.84, color="#8B5A2B", dashed=True)
    arrow(5.15, 4.84, 5.45, 4.84, color="#8B5A2B", dashed=True)

    ax.text(0.20, 3.95, "IMPLEMENTED FIXTURE SCAFFOLD — one terminal-secret event", weight="bold", color="#174A78", fontsize=11.2)

    # Implemented end-to-end event path.
    box(0.20, 2.35, 1.38, 1.20, "1  Fixture", 'terminal_secret\napi_key=SKDEMO…', "#B33A3A")
    box(1.82, 2.35, 1.38, 1.20, "2  Route", "class → action\nredact_before_model", "#2166AC", fontsize=8.7)
    box(3.44, 2.35, 1.38, 1.20, "3  Redact", "normalise + patterns\n→ [REDACTED]", "#2166AC")
    box(5.06, 2.35, 1.38, 1.20, "4  Stub", "deterministic assistant\nmediated text only", "#4E7D4A", fontsize=8.8)
    box(6.68, 2.35, 1.38, 1.20, "5  Guard", "deny/ref checks\n→ allow or hold", "#4E7D4A")

    for x in (1.58, 3.20, 4.82, 6.44):
        arrow(x, 2.95, x + 0.24, 2.95)

    # Retain and audit branches.
    box(2.15, 0.55, 2.05, 1.05, "RETAIN  Per-invocation", "current-turn exclusion\nno persistent store", "#6A4C93")
    box(4.80, 0.55, 2.20, 1.05, "AUDIT  In-memory chain", "detects retained-entry edits\nnot append-only/crash-evident", "#6A4C93", fontsize=8.8)
    arrow(4.13, 2.35, 3.18, 1.60, color="#6A4C93", label="block_memory_write only", label_y=0.03)
    arrow(5.75, 2.35, 5.90, 1.60, color="#6A4C93", label="decision metadata", label_y=0.03)

    # Boundary labels.
    ax.text(1.82, 2.07, "OBSERVE", color="#2166AC", weight="bold", fontsize=9.2)
    ax.text(2.15, 0.25, "RETAIN", color="#6A4C93", weight="bold", fontsize=9.2)
    ax.text(6.68, 2.07, "SAY", color="#4E7D4A", weight="bold", fontsize=9.2)
    ax.text(
        6.90,
        4.92,
        "Dashed: target only",
        fontsize=8.5,
        color="#8B5A2B",
        ha="left",
        va="center",
    )
    ax.text(6.90, 4.65, "Solid: released artifact", fontsize=8.5, color="#174A78", ha="left", va="center")

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.02)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "Title": "PerceptFence implemented scaffold and target live pipeline",
        "Author": "Anonymous",
        "Subject": "Evidence-bounded architecture walkthrough",
        "CreationDate": datetime(2026, 7, 9, tzinfo=timezone.utc),
        "ModDate": datetime(2026, 7, 9, tzinfo=timezone.utc),
    }
    fig.savefig(pdf_path, format="pdf", metadata=metadata)
    fig.savefig(png_path, format="png", dpi=220, facecolor="white")
    plt.close(fig)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    render(
        root / "paper" / "figures" / "architecture_walkthrough.pdf",
        root / "paper" / "figures" / "architecture_walkthrough.png",
    )


if __name__ == "__main__":
    main()
