# Figures

This directory holds figures rendered from the M5 benchmark CSV.

## Files

| File | Source | Renderer |
|---|---|---|
| `headline_ser.svg` | `eval/results/baseline_vs_guarded.csv` | `eval/render_figure.py` |

## Reproducibility

```bash
# From the pack root, after running the benchmark:
python3 eval/benchmark.py
python3 eval/render_figure.py
```

The renderer is stdlib-only Python (no matplotlib dependency); it hand-builds the SVG so the output is deterministic given the input CSV. Run-to-run variance in the source CSV's microsecond-level latency measurements is the only source of figure variance between independent benchmark runs.

## What the headline figure shows

`headline_ser.svg` is a grouped bar chart of sensitive exposure rate (SER) for each of the eleven synthetic scenario classes, contrasting the baseline (unmediated) path against the guarded (full-mediation) path. The subtitle line states the mean SER delta across classes and the median latency overhead in microseconds. The legend distinguishes baseline (warm red) from guarded (cool blue).

The figure is read by reviewers in conjunction with `eval/results/baseline_vs_guarded.csv`, which carries the full per-class breakdown including SER surface decomposition (context, output, memory, audit), false block rate, task success rate, and latency percentiles.
