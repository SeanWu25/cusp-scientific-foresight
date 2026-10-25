#!/usr/bin/env python3
"""
make_fig3_overleaf.py — revision Figure 3 (main.tex, fig:gaps), same layout and style as the submitted Figures/forecasting_gap.png.

a  knowledge gap (WS+Cutoff − Base) and forecasting gap (WS − WS+Cutoff) from the FIXED-EVIDENCE PACKET experiment (A4.3):
   values read from results/A4_retrieval/tables/A4_3_gaps_pre_post.json (= response Tables 20/21); Feasibility Assessment pools original + perturbed binary items;
   Solution Design (FRQ) on the 0–1 scale (score / 10) as in the submitted figure; cells with < 20 events omitted.
b  per-domain POST-cutoff performance (as in the submitted panel) of the nine Table-1 models on the full corpus to Aug 2026
   (DeepSeek R1 original corpus only); merged binary accuracy, MCQ accuracy, date score, FRQ score; error bars s.e.m.; cells with < 20 items omitted;
   diamonds + dashed line = cross-model mean; dashed grey = chance (0.5, 0.25) and the FRQ pass threshold (5).
   Feasibility Assessment uses BALANCED accuracy in both panels (a: mean of the original and perturbed gaps).
Output: manuscript_updates/forecasting_gap_rev.png (+ .pdf)
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sys as _s; _s.path.insert(0, "/home/seanwu/FutureScience/run_evaluation"); import display_names; display_names.install()
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "manuscript_updates"
sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
# Cutoff-month rule (2026-10-25): an event published in the model's knowledge-cutoff month counts as PRE-cutoff
# (post iff pub_month > cutoff_month), as in Table 1 and the information-access gaps. False = old rule (cutoff month = post).
CUTOFF_MONTH_PRE = True
sys.path.insert(0, str(ROOT / "results/A4_retrieval/scripts")); import a43_gaps as G

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
KC, FC = "#4F6FA8", "#A65A48"
COL = {"GPT-4o": "#E07B22", "GPT-OSS": "#E8AE25", "DeepSeek R1": "#D58BB4", "LLaMA 3.3": "#6EC0EA", "Claude S4.5": "#1F7BB8",
       "GPT-5.4": "#22A884", "Claude Opus 4.8": "#7B4FA0", "Claude Sonnet 5": "#C0392B", "GPT-5.6 Sol": "#7F7F7F"}
ORDER = ["GPT-4o", "GPT-OSS", "DeepSeek R1", "LLaMA 3.3", "Claude S4.5", "GPT-5.4", "Claude Opus 4.8", "Claude Sonnet 5", "GPT-5.6 Sol"]
SHORT = {"LLaMA 3.3 70B": "LLaMA 3.3", "Claude Sonnet 5": "Claude Sonnet 5", "GPT-5.6 Sol": "GPT-5.6 Sol"}
TASKS = [("Feasibility Assessment", ("binary", "binary_perturbed"), 1.0), ("Mechanistic Forecasting", ("mcq",), 1.0),
         ("Temporal Prediction", ("date",), 1.0), ("Solution Design", ("frq",), 10.0)]
AREAS = [("Chemistry", "Chemistry"), ("Materials Science", "Mat. Sci."), ("Artificial Intelligence", "AI"), ("Medicine", "Medicine"),
         ("Physics", "Physics"), ("Biology", "Biology"), ("Neuroscience", "Neurosci."), ("Environmental Science", "Env. Sci.")]

# ---------------------------------------------------------------- a: fixed-evidence gaps
# Read the published gap tables (response letter Tables 20/21 = results/A4_retrieval/tables/A4_3_gaps_pre_post.json, written by
# a43_pre_post_correlation.py) so that the figure and the tables are identical: same shared events, same partition rule
# (post = publication month AFTER the cutoff month), same >= 20-event suppression.
# `--packets 1000`: panel a from the 1,000-event matched table (= response Tables 20/21 on 1,000 events, A43_EVENTS=1000 a43_pre_post_correlation.py);
# output gets the suffix _1000 so the 500-event figure stays reproducible.
P1000 = "--packets" in sys.argv and sys.argv[sys.argv.index("--packets") + 1] == "1000"; SUF = "_1000" if P1000 else ""
GJ = json.load(open(ROOT / ("results/A4_retrieval/tables/A4_3_gaps_pre_post_1000.json" if P1000 else "results/A4_retrieval/tables/A4_3_gaps_pre_post.json")))
J = {(r["scope"], r["task"], r["model"]): r for r in GJ if not r.get("suppressed")}
JT = {"Feasibility Assessment": ("Binary", "Binary (pert.)"), "Mechanistic Forecasting": ("MCQ",), "Temporal Prediction": ("Date (0-1)",), "Solution Design": ("FRQ (0-10)",)}
gap = {}
for (scope, task, model) in {(k[0], None, k[2]) for k in J}:
    nm = SHORT.get(model, model)
    for lab, tasks, sc in TASKS:
        rs = [J.get((scope, t, model)) for t in JT[lab]]
        if any(r is None for r in rs): continue
        sc = 10.0 if lab == "Solution Design" else 1.0
        gap[(scope, lab, nm)] = (st.fmean([r["know_fixed"] for r in rs]) / sc, st.fmean([r["fore_fixed"] for r in rs]) / sc)

# ---------------------------------------------------------------- b: per-domain post-cutoff, nine models
rows = T.load("full", six_only=False)
meta = {}
for bfile in T.BENCH:
    for l in open(ROOT / bfile):
        if l.strip(): r = json.loads(l); meta[r["id"]] = r["main_area"]
dom = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))   # model -> area -> task -> values
for name, cut, icon, op, ep, new in T.MODELS:
    seen = set(); cm = T.mo(cut)
    pubd = {}
    for bfile in T.BENCH:
        for l in open(ROOT / bfile):
            if l.strip(): r = json.loads(l); pubd[r["id"]] = r["publication_date"]
    for p in [op] + ([ep] if ep else []):
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen or r["id"] not in pubd or (T.mo(pubd[r["id"]]) <= cm if CUTOFF_MONTH_PRE else T.mo(pubd[r["id"]]) < cm): continue
            seen.add(r["id"]); a = meta[r["id"]]; t = r.get("tasks", {})
            for task in ("binary", "binary_perturbed"):
                v = t.get(task)
                if v and not v.get("skipped") and "correct" in v: dom[name][a][task].append(1.0 if v["correct"] else 0.0)
            v = t.get("mcq")
            if v and not v.get("skipped") and "correct" in v: dom[name][a]["Mechanistic Forecasting"].append(1.0 if v["correct"] else 0.0)
            v = t.get("date")
            if v and not v.get("skipped") and v.get("score") is not None: dom[name][a]["Temporal Prediction"].append(float(v["score"]))
            v = t.get("frq")
            if v and not v.get("skipped") and v.get("score") is not None: dom[name][a]["Solution Design"].append(float(v["score"]))

# ---------------------------------------------------------------- draw
fig = plt.figure(figsize=(15.8, 16.2))
gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.05], hspace=0.30)
gsa = gs[0].subgridspec(2, 1, hspace=0.95)
for row, scope in enumerate(("pre", "post")):
    ax = fig.add_subplot(gsa[row]); xticks, xlabels, centers = [], [], []; x0 = 0
    models_here = [m for m in ["GPT-4o", "LLaMA 3.3", "GPT-5.4", "Claude S4.5", "Claude Sonnet 5", "GPT-5.6 Sol"]]
    for gi, (lab, _, _) in enumerate(TASKS):
        ms = [m for m in models_here if (scope, lab, m) in gap]; start = x0
        for m in ms:
            kv, fv = gap[(scope, lab, m)]
            for dx, v, c in ((-0.18, kv, KC), (0.18, fv, FC)):
                ax.bar(x0 + dx, v, 0.36, color=c)
                vv = 0.0 if abs(v) < 0.005 else v
                up = v >= 0 or vv == 0.0
                ax.text(x0 + dx, (max(v, 0) + 0.012) if up else v - 0.012, "0.00" if vv == 0.0 else f"{vv:+.2f}", rotation=90, ha="center", va="bottom" if up else "top", fontsize=10)
            xticks.append(x0); xlabels.append(m); x0 += 1
        centers.append(((start + x0 - 1) / 2, lab)); x0 += 0.8
        if gi < len(TASKS) - 1: ax.axvline(x0 - 0.9, color="#bbbbbb", lw=1)
    ax.axhline(0, color="#444", lw=1); ax.set_xticks(xticks); ax.set_xticklabels(xlabels, rotation=35, ha="right", fontsize=12)
    ax.set_ylabel("Gap value", fontsize=14); ax.tick_params(axis="y", labelsize=12); ax.set_ylim(-0.25, 0.62); ax.spines["bottom"].set_visible(False)
    import matplotlib.transforms as mt
    for cx, lab in centers: ax.text(cx, -0.50, lab, ha="center", va="top", fontsize=15, fontweight="bold", transform=mt.blended_transform_factory(ax.transData, ax.transAxes))
    ax.set_title(f"Knowledge and forecasting gaps on {scope}-cutoff events", loc="left", fontsize=17, fontweight="bold", pad=12)
    if row == 0:
        ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=KC), plt.Rectangle((0, 0), 1, 1, color=FC)], labels=["Knowledge gap", "Forecasting gap"],
                  loc="upper right", bbox_to_anchor=(1.0, 1.32), ncol=2, frameon=False, fontsize=13)
gsb = gs[1].subgridspec(2, 2, hspace=0.32, wspace=0.12)
panels = [("Feasibility Assessment", "Balanced accuracy", (0, 0.8), 0.5), ("Mechanistic Forecasting", "Accuracy", (0, 1.0), 0.25),
          ("Temporal Prediction", "Score (0–1)", (0, 0.7), None), ("Solution Design", "Score (0–10)", (0, 8), 5.0)]
for k, (task, ylab, ylim, ref) in enumerate(panels):
    ax = fig.add_subplot(gsb[k // 2, k % 2]); n = len(ORDER); w = 0.86 / n; means = []
    for j, m in enumerate(ORDER):
        vals, errs = [], []
        for a, _ in AREAS:
            if task == "Feasibility Assessment":   # balanced accuracy = mean of original and perturbed accuracy
                o, q = dom[m][a]["binary"], dom[m][a]["binary_perturbed"]
                if len(o) >= 10 and len(q) >= 10 and len(o) + len(q) >= 20:
                    po, pq = st.fmean(o), st.fmean(q); vals.append((po + pq) / 2)
                    errs.append(0.5 * math.sqrt(po * (1 - po) / len(o) + pq * (1 - pq) / len(q)))
                else: vals.append(np.nan); errs.append(0)
                continue
            v = dom[m][a][task]
            if len(v) >= 20: vals.append(st.fmean(v)); errs.append(st.stdev(v) / math.sqrt(len(v)))
            else: vals.append(np.nan); errs.append(0)
        ax.bar(np.arange(len(AREAS)) + (j - n / 2 + 0.5) * w, vals, w * 0.95, yerr=errs, color=COL[m], error_kw=dict(lw=0.8, capsize=1.5, ecolor="#555"))
    for i, (a, _) in enumerate(AREAS):
        if task == "Feasibility Assessment":
            v = [(st.fmean(dom[m][a]["binary"]) + st.fmean(dom[m][a]["binary_perturbed"])) / 2 for m in ORDER
                 if len(dom[m][a]["binary"]) >= 10 and len(dom[m][a]["binary_perturbed"]) >= 10 and len(dom[m][a]["binary"]) + len(dom[m][a]["binary_perturbed"]) >= 20]
        else:
            v = [st.fmean(dom[m][a][task]) for m in ORDER if len(dom[m][a][task]) >= 20]
        means.append(st.fmean(v) if v else np.nan)
    ax.plot(np.arange(len(AREAS)), means, "D--", color="#444", ms=5, lw=1.2, zorder=5)
    if ref is not None: ax.axhline(ref, color="#bbbbbb", ls="--", lw=1)
    ax.set_title(task, fontsize=15, fontweight="bold"); ax.set_ylabel(ylab, fontsize=11); ax.set_ylim(*ylim)
    ax.set_xticks(np.arange(len(AREAS))); ax.set_xticklabels([s for _, s in AREAS] if k >= 2 else [""] * len(AREAS), rotation=30, ha="right", fontsize=11)
    ax.tick_params(axis="y", labelsize=10)
handles = [plt.Line2D([], [], color="#444", marker="D", ls="--", ms=5), plt.Line2D([], [], color="#bbbbbb", ls="--")] + [plt.Rectangle((0, 0), 1, 1, color=COL[m]) for m in ORDER]
labels = ["Cross-model mean", "Chance / pass threshold"] + [m + ("$^\\dagger$" if m == "DeepSeek R1" else "") for m in ORDER]
fig.legend(handles, labels, loc="lower center", ncol=6, fontsize=11, frameon=True, edgecolor="#cccccc", bbox_to_anchor=(0.5, 0.005))
fig.text(0.01, 0.985, "a", fontsize=30, fontweight="bold", va="top"); fig.text(0.01, 0.475, "b", fontsize=30, fontweight="bold", va="top")
fig.subplots_adjust(left=0.06, right=0.99, top=0.95, bottom=0.08)
fig.savefig(OUT / f"forecasting_gap_rev{SUF}.png", dpi=300); fig.savefig(OUT / f"forecasting_gap_rev{SUF}.pdf")
print({k: tuple(round(x, 2) for x in v) for k, v in sorted(gap.items())})
