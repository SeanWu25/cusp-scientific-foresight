#!/usr/bin/env python3
"""
make_si_overview_overleaf.py - Supplementary Figure S1 (Figures/CUSP_Overview_rev.png) on the FULL corpus
(original Jan 2024-Mar 2026 + extension Apr-Aug 2026 = 5,575 events). Same layout and style as the submitted
CUSP_Overview.png: A source donut, B questions per domain by task type, C events per month, D sub-category sunburst.
Re-uses the plotting functions of archive/scripts/analyze_results/cusp_figures.py (the script that made the original).
"""
import json, os, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
sys.path.insert(0, str(ROOT / "archive/scripts/analyze_results")); import cusp_figures as F
OUT = ROOT / "manuscript_updates"
TASKS = [("Binary", "binary_question"), ("Perturbed Binary", "binary_question_perturbed"), ("MCQ", "mcq_question"),
         ("FRQ", "frq_prompt"), ("Date Prediction", "date_prediction_prompt")]
ok = lambda v: v is not None and not (isinstance(v, float) and np.isnan(v)) and str(v).strip() != ""

rows = []
for b in T.BENCH:
    for l in open(ROOT / b):
        if l.strip():
            r = json.loads(l); r["publication_date"] = str(r["publication_date"])[:7]; rows.append(r)
tmp = Path(tempfile.mkdtemp()) / "cusp_full.jsonl"
with open(tmp, "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
F.setup_style(); df = F.load_data(str(tmp))
# task presence = non-empty field (the archived stacked bar used notna(), which counts empty strings)
for name, col in TASKS: df[col] = df[col].apply(lambda v: v if ok(v) else None)
df["binary_perturbation_detail"] = None
tot = {name: int(df[col].notna().sum()) for name, col in TASKS}
print("events", len(df), "tasks", tot, "sum", sum(tot.values()))

# panel D sunburst rendered by the original function, then placed as an image
sb = tmp.parent / "sunburst.png"; F.plot_sunburst(df, str(sb))
fig = plt.figure(figsize=(19, 15), dpi=200)
gs = GridSpec(2, 2, figure=fig, hspace=0.36, wspace=0.16, width_ratios=[1, 1.3], height_ratios=[1, 1.15])
ax_a = fig.add_subplot(gs[0, 0]); F.plot_source_donut(df, ax=ax_a)
for t in ax_a.texts:
    if "papers" in t.get_text(): t.set_text(t.get_text().replace("papers", "events"))
ax_b = fig.add_subplot(gs[0, 1]); F.plot_domain_stacked_bar(df, ax=ax_b)
ax_c = fig.add_subplot(gs[1, 0])
m = df.groupby("month").size().sort_index(); x = pd.to_datetime(m.index, format="%Y-%m")
ax_c.axvspan(pd.Timestamp("2026-03-16"), pd.Timestamp("2026-08-16"), color="#E7298A", alpha=0.10, lw=0)
ax_c.fill_between(x, m.values, alpha=0.18, color="#1F78B4")
ax_c.plot(x, m.values, marker="o", markersize=5, linewidth=2.2, color="#1F78B4", markeredgecolor="white", markeredgewidth=0.8)
ax_c.set_xlim(pd.Timestamp("2023-12-01"), pd.Timestamp("2026-09-15")); ax_c.set_ylim(0, 290)
ticks = pd.date_range("2024-01-01", "2026-07-01", freq="6MS"); ax_c.set_xticks(ticks); ax_c.set_xticklabels([t.strftime("%b %Y") for t in ticks], rotation=35, ha="right")
ax_c.grid(axis="y", linestyle="--", alpha=0.25); ax_c.grid(axis="x", visible=False)
ax_c.set_ylabel("Number of events per month"); ax_c.set_xlabel("First publicly observable month")
ax_c.text(pd.Timestamp("2025-02-01"), 278, "Original corpus (Jan 2024–Mar 2026)", ha="center", va="top", fontsize=12, color="#333")
ax_c.text(pd.Timestamp("2026-06-01"), 278, "Extension\n(Apr–Aug 2026)", ha="center", va="top", fontsize=12, color="#A0185E")
img = plt.imread(sb); ax_d = fig.add_axes([0.50, 0.02, 0.50, 0.47]); ax_d.imshow(img); ax_d.axis("off")
for ax, lab in ((ax_a, "a"), (ax_b, "b"), (ax_c, "c")): ax.text(-0.08, 1.06, lab, transform=ax.transAxes, fontsize=26, fontweight="bold", va="bottom")
ax_d.text(0.02, 0.98, "d", transform=ax_d.transAxes, fontsize=26, fontweight="bold", va="bottom")
fig.savefig(OUT / "CUSP_Overview_rev.png", bbox_inches="tight", dpi=200)
m = df.groupby("month").size(); print("months", len(m), "mean %.1f sd %.1f" % (m.mean(), m.std()), "sources", df["source_clean"].value_counts().to_dict())
