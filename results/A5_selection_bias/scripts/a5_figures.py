#!/usr/bin/env python3
"""
a5_figures.py -- figures for study A5, drawn from the CSVs a5_analysis.py wrote.

One figure per stratification x partition: four panels (binary / MCQ / date /
FRQ), x = stratum, one line per model with 95% bootstrap CI bars. Suppressed
cells (n < 20) are simply absent -- never drawn as a point.
"""
from __future__ import annotations
import csv, os, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a5_common as C  # noqa: E402

OUT = os.path.dirname(HERE)
FIG = f"{OUT}/figures"
TASKS = ["binary", "mcq", "date", "frq"]
YLAB = {"binary": "balanced accuracy", "mcq": "accuracy",
        "date": "date score", "frq": "FRQ score (0-10)"}
MODEL_ORDER = [p[0] for p in C.PANEL]


def read(dim):
    path = f"{OUT}/by_{dim}/{dim}_cells.csv"
    rows = list(csv.DictReader(open(path)))
    return rows


def draw(dim, part, order_labels, title):
    rows = [r for r in read(dim) if r["partition"] == part and r["suppressed"] == "0"]
    if not rows:
        return None
    strata = [s for s in order_labels if any(r["stratum"] == s for r in rows)]
    if not strata:
        return None
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.6))
    cmap = plt.get_cmap("tab10")
    colors = {m: cmap(i % 10) for i, m in enumerate(MODEL_ORDER)}
    any_drawn = False
    for ax, task in zip(axes, TASKS):
        sub = [r for r in rows if r["task"] == task]
        for mi, m in enumerate(MODEL_ORDER):
            pts = {r["stratum"]: r for r in sub if r["model"] == m}
            xs, ys, lo, hi = [], [], [], []
            for i, s in enumerate(strata):
                if s not in pts:
                    continue
                r = pts[s]
                xs.append(i + (mi - 4.5) * 0.045)
                ys.append(float(r["statistic"]))
                lo.append(float(r["statistic"]) - float(r["ci_lo"]))
                hi.append(float(r["ci_hi"]) - float(r["statistic"]))
            if not xs:
                continue
            any_drawn = True
            ax.errorbar(xs, ys, yerr=[lo, hi], marker="o", ms=4, lw=1.3,
                        capsize=2, color=colors[m], label=m, alpha=0.85)
        ax.set_title(C.TASK_LABEL[task], fontsize=11)
        ax.set_ylabel(YLAB[task], fontsize=9)
        ax.set_xticks(range(len(strata)))
        ax.set_xticklabels(strata, rotation=30, ha="right", fontsize=8)
        ax.grid(alpha=0.25, axis="y")
        if task == "binary":
            ax.axhline(0.5, color="grey", ls=":", lw=1)
    if not any_drawn:
        plt.close(fig)
        return None
    h, l = axes[0].get_legend_handles_labels()
    if not h:
        for ax in axes:
            hh, ll = ax.get_legend_handles_labels()
            if hh:
                h, l = hh, ll
                break
    fig.legend(h, l, loc="lower center", ncol=min(len(l), 5), fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.09))
    fig.suptitle(title, fontsize=12.5, y=1.02)
    fig.tight_layout()
    os.makedirs(FIG, exist_ok=True)
    stem = f"{FIG}/A5_{dim}_{part}"
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return f"{stem}.png"


def main():
    made = []
    labels = {
        "source": [C.SOURCE_LABEL[s] for s in C.SOURCE_ORDER],
        "visibility": None,   # filled from the CSV (edges are numeric)
        "latency": C.LATENCY_ORDER,
    }
    vis_rows = read("visibility")
    seen = []
    for r in vis_rows:
        if r["stratum"] not in seen:
            seen.append(r["stratum"])
    labels["visibility"] = sorted(seen)

    titles = {
        "source": "A5.1  Performance by source / venue",
        "visibility": "A5.2  Performance by citation quartile (481 events, original half)",
        "latency": "A5.3  Performance by publication latency (708 extension events)",
    }
    for dim in ("source", "visibility", "latency"):
        for part in ("pre", "post", "overall"):
            p = draw(dim, part, labels[dim], f"{titles[dim]} — {part.upper()}-cutoff")
            if p:
                made.append(p)
                print("wrote", p)
    if not made:
        print("no figures drawn", file=sys.stderr)


if __name__ == "__main__":
    main()
