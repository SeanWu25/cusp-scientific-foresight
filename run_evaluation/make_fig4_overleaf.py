#!/usr/bin/env python3
"""
make_fig4_overleaf.py — revision version of the failure-modes figure (main.tex fig:radar_areas, Figures/Failure_Modes_final.png)
for the nine Table-1 models, post-cutoff events of the FULL corpus (Jan 2024–Aug 2026; DeepSeek R1: original corpus only).
(Until 2026-10-22 the figure used the full corpus; those numbers are kept in manuscript_updates/fig4_numbers_fullcorpus.json.) Panels as submitted:
 a  binary answer distribution by truth (all events)          b  FRQ sub-dimension violins (all events)
 c  reliability curves + ECE, Binary and MCQ (post-cutoff)     d  signed date error histograms (post-cutoff)
 e  predicted vs ground-truth date hexbins for three models (all events), cutoff marked
Output: manuscript_updates/Failure_Modes_rev.png (+ .pdf); manuscript_updates/fig4_numbers.json
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sys as _s; _s.path.insert(0, "/home/seanwu/FutureScience/run_evaluation"); import display_names; display_names.install()
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
# Cutoff-month rule (2026-10-25): an event published in the model's knowledge-cutoff month counts as PRE-cutoff
# (post iff pub_month > cutoff_month), as in Table 1 and the information-access gaps. False = old rule (cutoff month = post).
CUTOFF_MONTH_PRE = True
# 2026-10-26: every panel uses post-cutoff events only (POST_ONLY=1, default). 2026-10-27: FIG4_CORPUS=full (default) uses the
# original corpus + the Apr-Aug 2026 extension for models with an extension run (DeepSeek R1: original only);
# FIG4_CORPUS=orig keeps the original corpus for every model and writes *_orig files.
import os
POST_ONLY = os.environ.get("POST_ONLY", "1") != "0"
CORPUS = os.environ.get("FIG4_CORPUS", "full"); SUF = "" if CORPUS == "full" else "_orig"   # 2026-10-27: full corpus is the default (Sean)
COL = {"GPT-4o": "#D55E00", "GPT-OSS": "#E69F00", "DeepSeek R1": "#CC79A7", "LLaMA 3.3": "#56B4E9", "Claude S4.5": "#0072B2",
       "GPT-5.4": "#009E73", "Claude Opus 4.8": "#7B4FA0", "Claude Sonnet 5": "#B2182B", "GPT-5.6 Sol": "#6E6E6E"}
DIMC = {"alignment": "#D6604D", "specificity": "#F4A582", "novelty": "#92C5DE", "feasibility": "#4DAC26"}
def fece(cal, lo, n=10):
    tot = len(cal); e = 0; edges = np.linspace(lo, 1, n + 1)
    for a, b in zip(edges[:-1], edges[1:]):
        pts = [(c, v) for c, v in cal if a <= c < b]
        if pts: e += len(pts) / tot * abs(np.mean([v for _, v in pts]) - np.mean([c for c, _ in pts]))
    return e
def curve(cal, lo, n=6, min_n=20):
    edges = np.linspace(lo, 1, n + 1); xs, ys, lo_, hi_ = [], [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        pts = [(c, v) for c, v in cal if a <= c < b]
        if len(pts) < min_n: continue
        k = sum(v for _, v in pts); nn = len(pts); p = k / nn; z = 1.96
        d = 1 + z * z / nn; c0 = (p + z * z / (2 * nn)) / d; hw = z * math.sqrt(p * (1 - p) / nn + z * z / (4 * nn * nn)) / d
        xs.append(np.mean([c for c, _ in pts])); ys.append(p); lo_.append(c0 - hw); hi_.append(c0 + hw)
    return xs, ys, lo_, hi_
pub = {}
for b in T.BENCH:
    for l in open(ROOT / b):
        if l.strip(): r = json.loads(l); pub[r["id"]] = r["publication_date"][:7]
D = {}
for name, cut, icon, op, ep, new in T.MODELS:
    cm = T.mo(cut); seen = set(); d = defaultdict(list)
    for p in ([op] if CORPUS == "orig" or not ep else [op, ep]):   # ORIGINAL corpus only for every model by default (DeepSeek R1 has no extension run), 2026-10-22
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen or r["id"] not in pub: continue
            seen.add(r["id"]); post = (T.mo(pub[r["id"]]) > cm) if CUTOFF_MONTH_PRE else (T.mo(pub[r["id"]]) >= cm); t = r["tasks"]
            if POST_ONLY and not post: continue
            d["n_events"].append(1)
            for k, truth in (("binary", "yes"), ("binary_perturbed", "no")):
                v = t.get(k)
                if v and "correct" in v:
                    ans = str(v.get("parsed_answer", "")).lower()
                    if ans in ("yes", "no"): d[f"ans_{truth}"].append(ans == "yes")
                    if post and v.get("confidence") is not None: d["bcal"].append((float(v["confidence"]), 1.0 if v["correct"] else 0.0))
            v = t.get("mcq")
            if post and v and "correct" in v and v.get("confidence") is not None: d["mcal"].append((float(v["confidence"]), 1.0 if v["correct"] else 0.0))
            v = t.get("frq")
            if v and v.get("score") is not None:
                for k in DIMC:
                    if v.get(k) is not None: d[k].append(float(v[k]))
            v = t.get("date")
            if v and v.get("parsed_date") and v.get("ground_truth"):
                pd_, gt = T.mo(v["parsed_date"]), T.mo(v["ground_truth"])
                if pd_ is not None and gt is not None:
                    d["hex"].append((gt, pd_))
                    if post: d["err"].append(pd_ - gt)
    D[name] = dict(d, cut=cut)
order = sorted(D, key=lambda m: -np.mean(D[m]["ans_yes"] + D[m]["ans_no"]))
nums = {m: dict(ece_bin_post=fece(D[m]["bcal"], .5), ece_mcq_post=fece(D[m]["mcal"], .25), yes_truth_yes=np.mean(D[m]["ans_yes"]), yes_truth_no=np.mean(D[m]["ans_no"]),
                n_events=len(D[m]["n_events"]), n_bin=len(D[m]["ans_yes"]) + len(D[m]["ans_no"]), n_bcal=len(D[m]["bcal"]), n_mcal=len(D[m]["mcal"]), n_err=len(D[m]["err"]), frq_means={k: float(np.mean(D[m][k])) for k in DIMC}, err_median=float(np.median(D[m]["err"])), err_mean=float(np.mean(D[m]["err"])), within12=float(np.mean(np.abs(D[m]["err"]) <= 12))) for m in D}
json.dump(nums, open(ROOT / f"manuscript_updates/fig4_numbers{SUF}.json", "w"), indent=1)

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
fig = plt.figure(figsize=(18, 25))
gs = fig.add_gridspec(3, 2, height_ratios=[1.15, 1.2, 0.75], hspace=0.14, wspace=0.12, top=0.985, bottom=0.03, left=0.08, right=0.98)
FIRST = {}
# a
ax = fig.add_subplot(gs[0, 0]); FIRST["a"] = ax; y = 0; yt, yl = [], []
for m in order:
    for truth, lab in (("yes", "truth = Yes"), ("no", "truth = No")):
        p = np.mean(D[m][f"ans_{truth}"])
        ax.barh(y, p, color="#C0303F", height=0.8); ax.barh(y, 1 - p, left=p, color="#3A73B5", height=0.8)
        if p > 0.08: ax.text(p / 2, y, f"{100*p:.0f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        if 1 - p > 0.08: ax.text(p + (1 - p) / 2, y, f"{100*(1-p):.0f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(-0.01, y, lab, ha="right", va="center", fontsize=8, color="#555"); y -= 1
    ax.text(-0.22, y + 1.5, m, ha="right", va="center", fontsize=11, fontweight="bold"); y -= 0.6
ax.axvline(0.5, color="#888", ls=":", lw=1); ax.set_yticks([]); ax.set_xlim(0, 1); ax.spines["left"].set_visible(False)
ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"]); ax.set_xlabel("Share of answers", fontsize=11)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color="#C0303F"), plt.Rectangle((0, 0), 1, 1, color="#3A73B5")], labels=['Answered "Yes"', 'Answered "No"'], loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=2, frameon=False, fontsize=10)
# b
gb = gs[0, 1].subgridspec(3, 3, hspace=0.45, wspace=0.25)
for i, m in enumerate(order):
    ax = fig.add_subplot(gb[i // 3, i % 3]); FIRST.setdefault("b", ax); data = [D[m][k] for k in DIMC]
    parts = ax.violinplot(data, showmeans=False, showextrema=False, widths=0.8)
    for pc, c in zip(parts["bodies"], DIMC.values()): pc.set_facecolor(c); pc.set_alpha(0.6)
    for j, (k, c) in enumerate(DIMC.items()):
        mu = np.mean(D[m][k]); ax.plot(j + 1, mu, "D", color=c, ms=4, mec="#333", mew=0.4); ax.text(j + 1, 10.6, f"{mu:.2f}", ha="center", fontsize=7, color=c, fontweight="bold")
    ax.axhline(5, color="#bbb", ls=":", lw=0.8); ax.set_ylim(0, 11); ax.set_title(m, fontsize=10, fontweight="bold", pad=12)
    ax.set_xticks(range(1, 5)); ax.set_xticklabels([k.capitalize() for k in DIMC] if i >= 6 else [""] * 4, rotation=35, fontsize=8); ax.tick_params(axis="y", labelsize=7)
    if i % 3 == 0: ax.set_ylabel("FRQ score (0–10)", fontsize=8)
# c
gc = gs[1, 0].subgridspec(3, 3, hspace=0.45, wspace=0.25)
for i, m in enumerate(order):
    ax = fig.add_subplot(gc[i // 3, i % 3]); FIRST.setdefault("c", ax); ax.plot([0.2, 1.02], [0.2, 1.02], ls="--", color="#bbb", lw=0.8)
    for key, lo, c, mk, lab in (("bcal", .5, "#2166AC", "o", "Binary"), ("mcal", .25, "#C0392B", "s", "MCQ")):
        xs, ys, l_, h_ = curve(D[m][key], lo)
        if xs: ax.fill_between(xs, l_, h_, color=c, alpha=0.1, lw=0); ax.plot(xs, ys, marker=mk, color=c, lw=1.4, ms=4)
    ax.text(0.04, 0.97, f"Binary ECE = {nums[m]['ece_bin_post']:.3f}", transform=ax.transAxes, fontsize=7.5, color="#2166AC", fontweight="bold", va="top")
    ax.text(0.04, 0.88, f"MCQ ECE = {nums[m]['ece_mcq_post']:.3f}", transform=ax.transAxes, fontsize=7.5, color="#C0392B", fontweight="bold", va="top")
    ax.set_xlim(0.2, 1.02); ax.set_ylim(0, 1.12); ax.set_title(m, fontsize=10, fontweight="bold"); ax.tick_params(labelsize=7)
    if i % 3 == 0: ax.set_ylabel("Fraction correct", fontsize=8)
    if i >= 6: ax.set_xlabel("Stated confidence", fontsize=8)
# d
gd = gs[1, 1].subgridspec(3, 3, hspace=0.45, wspace=0.25)
for i, m in enumerate(order):
    ax = fig.add_subplot(gd[i // 3, i % 3]); FIRST.setdefault("d", ax); e = np.clip(D[m]["err"], -60, 60)
    ax.hist(e, bins=np.arange(-62, 63, 4), color=COL[m], weights=np.ones(len(e)) / len(e))
    ax.axvspan(-6, 6, color="#4DAC26", alpha=0.12); ax.axvline(0, color="#222", lw=1); ax.axvline(np.mean(D[m]["err"]), color="#222", ls="--", lw=1)
    ax.text(0.03, 0.95, f"median {nums[m]['err_median']:+.0f} mo\nmean {nums[m]['err_mean']:+.1f} mo\n≤12 mo: {100*nums[m]['within12']:.0f}%", transform=ax.transAxes, fontsize=7, va="top")
    ax.set_title(m, fontsize=10, fontweight="bold"); ax.set_xlim(-62, 62); ax.tick_params(labelsize=7)
    if i % 3 == 0: ax.set_ylabel("Fraction of predictions", fontsize=8)
    if i >= 6: ax.set_xlabel("Signed error (months)\n+ = predicted too late", fontsize=8)
# e
ge = gs[2, :].subgridspec(1, 3, wspace=0.3)
for i, m in enumerate(["DeepSeek R1", "Claude S4.5", "GPT-5.4"]):   # GPT-5.4 replaces Claude Opus 4.8 (2026-10-26): post-cutoff, original corpus leaves O4.8 only Feb-Mar 2026
    ax = fig.add_subplot(ge[i]); FIRST.setdefault("e", ax); g = np.array([h[0] for h in D[m]["hex"]]); p_ = np.array([h[1] for h in D[m]["hex"]])
    lo, hi = g.min() - 1, g.max() + 1; keep = (p_ >= lo - 12) & (p_ <= lo + 72)
    from matplotlib.colors import LinearSegmentedColormap
    hb = ax.hexbin(g[keep], p_[keep], gridsize=22, mincnt=1, cmap=LinearSegmentedColormap.from_list("c", ["#f2f2f2", COL[m]]))
    ax.plot([lo, hi], [lo, hi], "--", color="#444", lw=1.5); cm = T.mo(D[m]["cut"]); ax.axhline(cm, color=COL[m], ls=":", lw=1.2); ax.text(lo + 1, cm + 1, "cutoff", color=COL[m], fontsize=9)
    ticks = list(range(T.mo("2023-01"), T.mo("2032-01"), 12))
    ax.set_xticks([t for t in ticks if lo <= t <= hi + 1]); ax.set_xticklabels([T.ym(t) for t in ax.get_xticks()], rotation=35, fontsize=8)
    ax.set_yticks([t for t in ticks + [T.mo("2023-01")] if lo - 12 <= t <= lo + 72]); ax.set_yticklabels([T.ym(t) for t in ax.get_yticks()], fontsize=8)
    ax.set_title(f"{m}  [cutoff {D[m]['cut']}]", fontsize=13, fontweight="bold", color=COL[m]); ax.set_xlabel("Ground-truth date", fontsize=11)
    if i == 0: ax.set_ylabel("Predicted date", fontsize=12)
    fig.colorbar(hb, ax=ax, shrink=0.7, label="Count")
# centre the lower rows: panel a needs a wide left margin for its model labels, the rows below do not
_top_bottom = FIRST["a"].get_position().y0 - 0.01; _L0, _L1, _R = 0.08, 0.03, 0.98
for _ax in fig.axes:
    _b = _ax.get_position()
    if _b.y1 < _top_bottom:
        _ax.set_position([_L1 + (_b.x0 - _L0) * (_R - _L1) / (_R - _L0), _b.y0, _b.width * (_R - _L1) / (_R - _L0), _b.height])
for lab, ax_ in FIRST.items():
    bb = ax_.get_position(); fig.text(bb.x0 - (0.07 if lab == "a" else 0.035), bb.y1 + 0.012, lab, fontsize=30, fontweight="bold", va="bottom")
fig.savefig(ROOT / f"manuscript_updates/Failure_Modes_rev{SUF}.png", dpi=200, bbox_inches="tight"); fig.savefig(ROOT / f"manuscript_updates/Failure_Modes_rev{SUF}.pdf", bbox_inches="tight")
for m in order: print(f"{m:16s} yes|truth=yes {100*nums[m]['yes_truth_yes']:.0f}% yes|truth=no {100*nums[m]['yes_truth_no']:.0f}%  ECE bin {nums[m]['ece_bin_post']:.3f} mcq {nums[m]['ece_mcq_post']:.3f}  median {nums[m]['err_median']:+.0f}")
