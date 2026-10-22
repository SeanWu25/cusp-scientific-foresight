"""make_ed_anchor.py — Extended Data figure: anchor-point effect in temporal prediction for the nine Table 1 models
(original corpus, Jan 2024–Mar 2026, all date questions, as main Fig. 4e; DeepSeek R1 has no extension run).
Each panel: predicted vs ground-truth month (hexbin, model colour), y = x (dashed), knowledge cutoff (dotted), and a
marginal histogram of predicted months; text = share of predictions on the three most frequent months.
Writes manuscript_updates/ed_anchor.{pdf,png} and manuscript_updates/ed_anchor_numbers.json."""
import json, sys, collections
from pathlib import Path
import numpy as np
import matplotlib as mpl; mpl.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation"))
import make_table1_overleaf as T, display_names; display_names.install()
MM = 1 / 25.4
mpl.rcParams.update({"font.family": "FreeSans", "font.size": 6.5, "axes.linewidth": 0.5, "xtick.labelsize": 5.8, "ytick.labelsize": 5.8,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2, "axes.spines.top": False,
    "axes.spines.right": False, "pdf.fonttype": 42})
# Figure 3 / Extended Data Fig. 1 colours, ordered by knowledge cutoff
ORDER = [("GPT-4o", "#E07B22"), ("LLaMA 3.3", "#6EC0EA"), ("GPT-OSS", "#E8AE25"), ("DeepSeek R1", "#D58BB4"), ("Claude S4.5", "#1F7BB8"),
         ("GPT-5.4", "#22A884"), ("Claude Opus 4.8", "#7B4FA0"), ("Claude Sonnet 5", "#C0392B"), ("GPT-5.6 Sol", "#7F7F7F")]
LO, HI = T.mo("2022-01"), T.mo("2031-12")
def main():
    M = {name: (cut, op) for name, cut, icon, op, ep, new in T.MODELS}
    fig = plt.figure(figsize=(183 * MM, 190 * MM)); outer = fig.add_gridspec(3, 3, left=0.075, right=0.985, top=0.965, bottom=0.075, wspace=0.42, hspace=0.42)
    nums = {}
    for k, (name, col) in enumerate(ORDER):
        cut, op = M[name]; g, p = [], []
        for r in json.load(open(ROOT / op))["results"]:
            v = (r.get("tasks") or {}).get("date")
            if v and v.get("parsed_date") and v.get("ground_truth"):
                pm, gm = T.mo(v["parsed_date"]), T.mo(v["ground_truth"])
                if pm and gm: g.append(gm); p.append(pm)
        g, p = np.array(g), np.array(p); n = len(p); cnt = collections.Counter(p.tolist()); top = cnt.most_common(3)
        share3 = sum(c for _, c in top) / n; out = float(np.mean((p < LO) | (p > HI)))
        nums[name] = dict(n=n, top3=[(T.ym(m), c / n) for m, c in top], top3_share=share3, distinct_pred=len(cnt), distinct_truth=int(len(set(g.tolist()))), outside_range=out)
        inner = outer[k // 3, k % 3].subgridspec(1, 2, width_ratios=[4.2, 1], wspace=0.06)
        ax = fig.add_subplot(inner[0]); mx = fig.add_subplot(inner[1], sharey=ax)
        keep = (p >= LO) & (p <= HI)
        cmap = LinearSegmentedColormap.from_list("c", ["#F4F4F4", col])
        ax.hexbin(g[keep], p[keep], gridsize=(14, 22), extent=(T.mo("2023-12"), T.mo("2026-04"), LO, HI), mincnt=1, cmap=cmap, bins="log", linewidths=0.1)
        ax.plot([T.mo("2023-12"), T.mo("2026-04")], [T.mo("2023-12"), T.mo("2026-04")], ls=(0, (3, 2)), color="#333", lw=0.7)
        cm = T.mo(cut); ax.axhline(cm, color=col, ls=":", lw=0.9); ax.text(T.mo("2026-03"), cm + 1.2, "cutoff", color=col, fontsize=5.4, ha="right", bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))
        ax.set_xlim(T.mo("2023-12"), T.mo("2026-04")); ax.set_ylim(LO, HI)
        ax.set_xticks([T.mo(x) for x in ("2024-01", "2025-01", "2026-01")]); ax.set_xticklabels(["2024", "2025", "2026"])
        ax.set_yticks([T.mo(f"{y}-01") for y in range(2022, 2032, 2)]); ax.set_yticklabels([str(y) for y in range(2022, 2032, 2)])
        ax.set_title(name, loc="left", fontsize=7, fontweight="bold", color="#222", pad=3)
        ax.text(0.03, 0.97, f"top 3 months: {100*share3:.0f}%", transform=ax.transAxes, fontsize=5.6, va="top", color="#333",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
        # marginal histogram of predicted months (one bar per month), anchors highlighted
        months = np.arange(LO, HI + 1); h = np.array([cnt.get(m, 0) for m in months]) / n
        tops = {m for m, _ in top}
        mx.barh(months, h, height=1.0, color=[col if m in tops else "#BDBDBD" for m in months], lw=0)
        top_x = max(0.2, np.ceil(h.max() * 10) / 10); mx.set_xlim(0, top_x * 1.02)
        mx.tick_params(axis="y", left=False, labelleft=False); mx.set_xticks([top_x]); mx.set_xticklabels([f"{100*top_x:.0f}%"]); mx.spines["left"].set_visible(False)
        if k // 3 == 2: ax.set_xlabel("True month", labelpad=1.5)
        if k % 3 == 0: ax.set_ylabel("Predicted month", labelpad=1.5)
        ax.text(-0.3 if k % 3 == 0 else -0.2, 1.08, "abcdefghi"[k], transform=ax.transAxes, fontsize=8.5, fontweight="bold", va="bottom")
    out = ROOT / "manuscript_updates"; fig.savefig(out / "ed_anchor.pdf"); fig.savefig(out / "ed_anchor.png", dpi=600); plt.close(fig)
    json.dump(nums, open(out / "ed_anchor_numbers.json", "w"), indent=1)
    for m, v in nums.items(): print(f"{m:16s} n={v['n']} top3={100*v['top3_share']:.0f}% {v['top3'][0][0]} distinct={v['distinct_pred']} out={100*v['outside_range']:.1f}%")
if __name__ == "__main__": main()
