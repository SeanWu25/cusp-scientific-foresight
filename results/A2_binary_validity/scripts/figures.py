"""
figures.py — manuscript figures for A2.

Colour: the first three slots of the validated categorical palette
(blue #2a78d6, orange #eb6834, aqua #1baf7a), which clear the all-pairs CVD and
normal-vision separation floors in light mode. Single value axis throughout,
recessive grid and spines, legend whenever more than one series is drawn.
"""
from __future__ import annotations
import csv, json, sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"

plt.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "axes.titlesize": 9, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "legend.frameon": False, "legend.fontsize": 7.5,
})


def tidy(ax, xgrid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_axisbelow(True)
    if xgrid:
        ax.xaxis.grid(True, color=GRID, lw=0.6)
        ax.yaxis.grid(False)
    else:
        ax.yaxis.grid(True, color=GRID, lw=0.6)
        ax.xaxis.grid(False)


def read_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(s):
    try:
        return float(s)
    except Exception:
        return None


def fig1_mislabel():
    rows = read_csv(C.TABLES / "t2_breakdowns.csv")
    dom = [r for r in rows if r["split"] == "negatives/domain"]
    if not dom:
        return
    dom.sort(key=lambda r: -fnum(r["rate"]))
    labs = [r["group"] for r in dom]
    vals = [fnum(r["rate"]) * 100 for r in dom]
    lo = [(fnum(r["rate"]) - fnum(r["wilson_lo"])) * 100 for r in dom]
    hi = [(fnum(r["wilson_hi"]) - fnum(r["rate"])) * 100 for r in dom]
    ns = [r["n"] for r in dom]

    pt = [r for r in rows if r["split"] == "negatives/ptype"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.4), gridspec_kw={"width_ratios": [2.4, 1.25], "wspace": 0.38})
    y = range(len(labs))
    ax.barh(list(y), vals, height=0.62, color=BLUE, zorder=3)
    ax.errorbar(vals, list(y), xerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=0.9,
                capsize=2.5, capthick=0.9, zorder=4)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{l}  (n={n})" for l, n in zip(labs, ns)])
    ax.invert_yaxis()
    ax.set_xlabel("synthetic negatives found achieved elsewhere (%)")
    ax.set_xlim(0, max(v + h for v, h in zip(vals, hi)) * 1.22 + 2)
    ax.set_title("a  By domain")
    tidy(ax)
    for i, v in enumerate(vals):
        ax.text(v + hi[i] + 0.6, i, f"{v:.1f}%", va="center", ha="left", fontsize=7, color=INK2)

    snd = [r for r in rows if r["split"] == "soundness/ptype"]
    if pt:
        order = ["constraint", "numeric"]
        lab = {"constraint": "added\nconstraint", "numeric": "numeric\nmodification"}
        x = range(len(order))
        w = 0.36
        for si, (src, col, name) in enumerate(((pt, BLUE, "achieved elsewhere"),
                                               (snd, ORANGE, "perturbation did not bind"))):
            if not src:
                continue
            v, el, eh, xs = [], [], [], []
            for gi, g in enumerate(order):
                r = next((q for q in src if q["group"] == g), None)
                if not r:
                    continue
                xs.append(gi + (si - 0.5) * w)
                v.append(fnum(r["rate"]) * 100)
                el.append((fnum(r["rate"]) - fnum(r["wilson_lo"])) * 100)
                eh.append((fnum(r["wilson_hi"]) - fnum(r["rate"])) * 100)
            ax2.bar(xs, v, width=w - 0.03, color=col, label=name, zorder=3)
            ax2.errorbar(xs, v, yerr=[el, eh], fmt="none", ecolor=INK2, elinewidth=0.9,
                         capsize=2.5, capthick=0.9, zorder=4)
            for xi, vi, hi_ in zip(xs, v, eh):
                ax2.text(xi, vi + hi_ + 1.2, f"{vi:.1f}", ha="center", fontsize=6.8, color=INK2)
        ax2.set_xticks(list(x))
        ax2.set_xticklabels([lab[g] for g in order])
        ax2.set_ylabel("% of synthetic negatives")
        ax2.set_ylim(0, max(50, ax2.get_ylim()[1] * 1.1))
        ax2.set_title("b  Which perturbations fail")
        ax2.legend(loc="upper right", fontsize=6.8)
        tidy(ax2, xgrid=False)
    fig.suptitle("Study 1 — how often a synthetic negative was actually achieved by the target date",
                 fontsize=9.5, fontweight="bold", y=1.04, color=INK)
    fig.savefig(C.FIGS / "fig1_mislabelling_rate.png")
    fig.savefig(C.FIGS / "fig1_mislabelling_rate.pdf")
    plt.close(fig)


def fig2_corrected():
    rows = read_csv(C.S1 / "corrected_accuracy.csv")
    if not rows:
        return
    names = [r["model"] for r in rows]
    series = [("as published", "acc_sample_published", "samp_lo", "samp_hi", BLUE, "o"),
              ("excluding flagged", "acc_excluding_flagged", "excl_lo", "excl_hi", ORANGE, "s"),
              ("re-labelled", "acc_relabelled", "relab_lo", "relab_hi", AQUA, "^")]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    off = {0: -0.24, 1: 0.0, 2: 0.24}
    for si, (lab, kc, kl, kh, col, mk) in enumerate(series):
        ys, xs, el, eh = [], [], [], []
        for i, r in enumerate(rows):
            v, l, h = fnum(r[kc]), fnum(r[kl]), fnum(r[kh])
            if v is None:
                continue
            ys.append(i + off[si])
            xs.append(v * 100)
            el.append((v - l) * 100)
            eh.append((h - v) * 100)
        ax.errorbar(xs, ys, xerr=[el, eh], fmt=mk, ms=4.2, color=col, ecolor=col,
                    elinewidth=1.1, capsize=0, label=lab, mec="white", mew=0.5, zorder=3)
    ax.axvline(50, color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=2)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_ylim(len(names) - 0.35, -0.75)
    ax.annotate("chance", xy=(50, len(names) - 0.45), xytext=(1.5, 0),
                textcoords="offset points", color=INK2, fontsize=7, ha="left", va="bottom")
    ax.set_xlabel("binary accuracy on the verified sample (%)")
    ax.set_title("Study 1 — binary accuracy before and after correcting the flagged labels",
                 pad=10)
    fig.legend(loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.06), columnspacing=2.2)
    tidy(ax)
    fig.savefig(C.FIGS / "fig2_corrected_accuracy.png")
    fig.savefig(C.FIGS / "fig2_corrected_accuracy.pdf")
    plt.close(fig)


def fig3_detection():
    head = read_csv(C.TABLES / "t5_detection_headline.csv")
    base = read_csv(C.TABLES / "t6_detection_baselines.csv")
    cons = read_csv(C.TABLES / "t7_order_consistency.csv")
    if not head:
        return
    lenbase = next((fnum(r["accuracy"]) for r in base if r["baseline"].startswith("always")), None)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.34})

    labs = [r["model"] for r in head]
    vals = [fnum(r["accuracy"]) * 100 for r in head]
    lo = [(fnum(r["accuracy"]) - fnum(r["ci_lo"])) * 100 for r in head]
    hi = [(fnum(r["ci_hi"]) - fnum(r["accuracy"])) * 100 for r in head]
    ax.bar(range(len(labs)), vals, width=0.5, color=BLUE, zorder=3)
    ax.errorbar(range(len(labs)), vals, yerr=[lo, hi], fmt="none", ecolor=INK2,
                elinewidth=0.9, capsize=3, capthick=0.9, zorder=4)
    ax.axhline(50, color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=2)
    ax.text(-0.44, 51.5, "chance", fontsize=7, color=INK2, ha="left")
    if lenbase:
        ax.axhline(lenbase * 100, color=ORANGE, lw=1.2, ls=(0, (1, 2)), zorder=2)
        ax.text(-0.44, lenbase * 100 + 1.5, "always pick the shorter claim",
                fontsize=7, color=ORANGE, ha="left")
    for i, v in enumerate(vals):
        ax.text(i, v + hi[i] + 1.4, f"{v:.1f}%", ha="center", fontsize=7.5, color=INK)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels(labs)
    ax.set_ylabel("detection accuracy (%)")
    ax.set_ylim(0, 118)
    ax.set_xlim(-0.55, len(labs) - 0.45)
    ax.set_title("a  Can a judge spot the modified claim?")
    tidy(ax, xgrid=False)

    if cons:
        cl = [r["judge"] for r in cons]
        cv = [fnum(r["consistency_rate"]) * 100 for r in cons]
        sv = [fnum(r["rate_strict"]) * 100 for r in cons]
        x = range(len(cl))
        w = 0.34
        ax2.bar([i - w / 2 for i in x], cv, width=w, color=AQUA, label="order-swap consistent", zorder=3)
        ax2.bar([i + w / 2 for i in x], sv, width=w, color=BLUE, label="correct in both orders", zorder=3)
        for i, (a, b) in enumerate(zip(cv, sv)):
            ax2.text(i - w / 2, a + 1.4, f"{a:.0f}%", ha="center", fontsize=7, color=INK2)
            ax2.text(i + w / 2, b + 1.4, f"{b:.0f}%", ha="center", fontsize=7, color=INK2)
        ax2.set_xticks(list(x))
        ax2.set_xticklabels([next(r["model"] for r in head if r["judge"] == j) for j in cl])
        ax2.set_ylabel("% of pairs")
        ax2.set_ylim(0, 118)
        ax2.set_title("b  Separating detection from position bias")
        ax2.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.16), columnspacing=1.0)
        tidy(ax2, xgrid=False)
    fig.suptitle("Study 2 — pairwise detection of the LLM-modified claim",
                 fontsize=9.5, fontweight="bold", y=1.10, color=INK)
    fig.savefig(C.FIGS / "fig3_detection.png")
    fig.savefig(C.FIGS / "fig3_detection.pdf")
    plt.close(fig)


def fig4_join():
    rows = [r for r in read_csv(C.TABLES / "t9_detection_x_accuracy.csv") if r["task"] == "perturbed"]
    if not rows:
        return
    head = read_csv(C.TABLES / "t5_detection_headline.csv")
    judge_model = {r["judge"]: r["model"] for r in head}
    judges = sorted({r["judge"] for r in rows})
    fig, axes = plt.subplots(1, len(judges), figsize=(4.0 * len(judges), 3.6), squeeze=False,
                             gridspec_kw={"wspace": 0.12})
    for ji, j in enumerate(judges):
        ax = axes[0][ji]
        sub = [r for r in rows if r["judge"] == j]
        names = [r["model"] for r in sub]
        for i, r in enumerate(sub):
            d, u = fnum(r["acc_detected"]) * 100, fnum(r["acc_undetected"]) * 100
            ax.plot([u, d], [i, i], color=GRID, lw=1.6, zorder=2, solid_capstyle="round")
            ax.plot(u, i, "o", ms=5, color=ORANGE, mec="white", mew=0.6, zorder=3)
            ax.plot(d, i, "o", ms=5, color=BLUE, mec="white", mew=0.6, zorder=3)
        ax.axvline(50, color=INK2, lw=1.0, ls=(0, (4, 3)), zorder=1)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names if ji == 0 else [""] * len(names))
        ax.invert_yaxis()
        ax.set_xlabel("accuracy on the perturbed item (%)")
        ax.set_title(f"judge: {judge_model.get(j, j)}")
        ax.set_ylim(len(names) - 0.4, -0.9)
        tidy(ax)
    fig.legend(handles=[Line2D([], [], marker="o", ls="", ms=5, color=BLUE,
                               label="pairs the judge detected (correct under both orders)"),
                        Line2D([], [], marker="o", ls="", ms=5, color=ORANGE,
                               label="pairs it did not")],
               loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.09))
    fig.suptitle("Study 2 — is binary accuracy higher on the pairs a judge can tell apart?",
                 fontsize=9.5, fontweight="bold", y=1.02, color=INK)
    fig.savefig(C.FIGS / "fig4_detection_x_accuracy.png")
    fig.savefig(C.FIGS / "fig4_detection_x_accuracy.pdf")
    plt.close(fig)


def fig5_strict():
    cmp = read_csv(C.TABLES / "t14_permissive_vs_strict.csv")
    tiers = read_csv(C.TABLES / "t13_strict_tiers.csv")
    if not cmp or not tiers:
        return
    routes = ["Achieved elsewhere", "Perturbation did not bind", "Union"]
    lab = {"Achieved elsewhere": "achieved\nelsewhere",
           "Perturbation did not bind": "perturbation\ndid not bind", "Union": "either route"}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.4),
                                  gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.34})
    x = range(len(routes))
    w = 0.36
    for si, (crit, col, name) in enumerate((("permissive", ORANGE, "is the claim true?"),
                                            ("strict", BLUE, "strict: every element quoted"))):
        v, el, eh, xs = [], [], [], []
        for gi, r0 in enumerate(routes):
            r = next((q for q in cmp if q["criterion"] == crit and q["route"] == r0), None)
            if not r:
                continue
            xs.append(gi + (si - 0.5) * w)
            v.append(fnum(r["rate"]) * 100)
            el.append((fnum(r["rate"]) - fnum(r["ci_lo"])) * 100)
            eh.append((fnum(r["ci_hi"]) - fnum(r["rate"])) * 100)
        ax.bar(xs, v, width=w - 0.03, color=col, label=name, zorder=3)
        ax.errorbar(xs, v, yerr=[el, eh], fmt="none", ecolor=INK2, elinewidth=0.9,
                    capsize=2.5, capthick=0.9, zorder=4)
        for xi, vi, hh in zip(xs, v, eh):
            ax.text(xi, vi + hh + 0.8, f"{vi:.1f}", ha="center", fontsize=6.8, color=INK2)
    ax.set_xticks(list(x))
    ax.set_xticklabels([lab[r] for r in routes])
    ax.set_ylabel("% of synthetic negatives")
    ax.set_ylim(0, max(34, ax.get_ylim()[1] * 1.12))
    ax.set_title("a  What the strict criterion removes")
    ax.legend(loc="upper left", fontsize=6.8)
    tidy(ax, xgrid=False)

    want = [("Demonstrably mislabelled", BLUE, "demonstrably\nmislabelled"),
            ("Probable", AQUA, "probable\n(one referee)"),
            ("Undecidable claim", ORANGE, "undecidable\nclaim"),
            ("Sound", GRID, "sound")]
    vals, cols, labs = [], [], []
    for pref, col, nm in want:
        r = next((q for q in tiers if q["category"].strip().startswith(pref)), None)
        if r:
            vals.append(fnum(r["rate"]) * 100)
            cols.append(col)
            labs.append(nm)
    left = 0.0
    for v, c, nm in zip(vals, cols, labs):
        ax2.barh([0], [v], left=left, color=c, height=0.5, zorder=3,
                 edgecolor="white", linewidth=1.4)
        if v >= 6:
            ax2.text(left + v / 2, 0, f"{v:.0f}%", ha="center", va="center", fontsize=7.5,
                     color=("#0b0b0b" if c == GRID else "white"), fontweight="bold")
        left += v
    ax2.set_xlim(0, 100)
    ax2.set_ylim(-0.6, 0.9)
    ax2.set_yticks([])
    ax2.set_xlabel("% of synthetic negatives")
    ax2.set_title("b  Where the 200 sampled negatives land")
    ax2.legend(handles=[Line2D([], [], marker="s", ls="", ms=6, color=c, label=nm.replace(chr(10), " "))
                        for c, nm in zip(cols, labs)],
               loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=2, fontsize=6.6)
    tidy(ax2, xgrid=True)
    fig.suptitle("Study 1 — the strict criterion, and the third bucket it exposes",
                 fontsize=9.5, fontweight="bold", y=1.04, color=INK)
    fig.savefig(C.FIGS / "fig5_strict_criterion.png")
    fig.savefig(C.FIGS / "fig5_strict_criterion.pdf")
    plt.close(fig)


def main():
    C.FIGS.mkdir(parents=True, exist_ok=True)
    for fn in (fig1_mislabel, fig2_corrected, fig3_detection, fig4_join, fig5_strict):
        try:
            fn()
            print("ok", fn.__name__)
        except Exception as e:
            print("FAIL", fn.__name__, type(e).__name__, e)


if __name__ == "__main__":
    main()
