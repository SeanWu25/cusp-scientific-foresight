"""make_ed_horizon_nature.py — Extended Data figure (Nature format, 183 mm): post-cutoff performance by forecasting horizon,
nine Table 1 models (DeepSeek-V4-Pro excluded), merged original + extension corpus, base condition.
a Feasibility: balanced accuracy | b Feasibility: yes/no bias | c Feasibility: stated confidence
d MCQ accuracy | e MCQ stated confidence | f FRQ rubric score | g absolute date error | h signed date error; legend in the ninth cell.
Bins 1–3, 4–6, 7–12, 13–24, 25+ months, plotted at their mean horizon; ribbons = 95% event-level bootstrap CI (10,000 resamples);
marker area ∝ items in the bin; bins with < 20 items hidden. b–f from tables_no_v4pro/binned_merged_primary.json; a computed in
make_ed_horizon.py (same bins, minimum n and bootstrap). Writes manuscript_updates/ed_horizon.{pdf,png}."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib as mpl; mpl.use("Agg"); import matplotlib.pyplot as plt
import sys as _s; _s.path.insert(0, "run_evaluation"); import display_names; display_names.install()
from matplotlib.lines import Line2D
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H))
import make_ed_horizon as E, data as D
OUT = H.parent / "manuscript_updates"; T = H / "tables_no_v4pro"
MM = 1 / 25.4
mpl.rcParams.update({"font.family": "FreeSans", "font.size": 6.5, "axes.linewidth": 0.5, "axes.labelsize": 6.5, "axes.titlesize": 7,
    "xtick.labelsize": 6, "ytick.labelsize": 6, "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2.2,
    "ytick.major.size": 2.2, "xtick.direction": "out", "ytick.direction": "out", "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "ps.fonttype": 42, "legend.frameon": False, "lines.solid_capstyle": "round"})
# Table 1 / Figure 3 colours; legend in order of knowledge cutoff
MODELS = [("gpt4o", "GPT-4o", "Oct 2023", "#E07B22", "s"), ("llama33", "LLaMA 3.3", "Dec 2023", "#6EC0EA", "P"),
          ("gptoss20b", "GPT-OSS", "Jun 2024", "#E8AE25", "v"), ("deepseek_r1", "DeepSeek R1", "Jul 2024", "#D58BB4", "D"),
          ("claude45", "Claude S4.5", "Jan 2025", "#1F7BB8", "o"), ("gpt54", "GPT-5.4", "Aug 2025", "#22A884", "^"),
          ("opus48", "Claude Opus 4.8", "Jan 2026", "#7B4FA0", "p"), ("sonnet5", "Claude Sonnet 5", "Jan 2026", "#C0392B", "X"),
          ("sol", "GPT-5.6 Sol", "Feb 2026", "#7F7F7F", "*")]
BINS = [(1, 3), (4, 6), (7, 12), (13, 24), (25, 34)]
def conf_binned(items, tg, B=10000, min_n=20, seed=0):
    import stats as S
    rows = []
    d = items[items.task_group == tg].copy(); d["c"] = pd.to_numeric(d.conf, errors="coerce"); d = d[d.c.notna()]
    for key, *_ in MODELS:
        g = d[d.model == key]
        for lo, hi in D.PRIMARY_BINS:
            s_ = g[(g.h >= lo) & (g.h <= hi)]
            if len(s_) < min_n: continue
            w = S.event_weights(s_.id.to_numpy(), B, seed); bm = S.wmean(s_.c.to_numpy(float)[None, :], w)
            rows.append(dict(model=key, bin_lo=lo, h_mean=float(s_.h.mean()), n_items=len(s_), v=float(s_.c.mean()), lo=S.ci(bm)[0], hi=S.ci(bm)[1]))
    return pd.DataFrame(rows)
def size(n): return 2.2 + 4.6 * np.sqrt(np.clip(n, 20, 3500) / 3500)      # marker diameter in pt
def main():
    ev = D.load_events(); items = D.load_items("merged", ev); items = items[items.condition == "base"]
    bal = E.balanced(items); bal = bal[~bal.suppressed].rename(columns={"mean": "v", "ci_lo": "lo", "ci_hi": "hi"})
    B = pd.DataFrame(json.load(open(T / "binned_merged_primary.json"))); B = B[B.condition == "base"]
    def pick(tg, metric):
        d = B[(B.task_group == tg) & (B.metric == metric) & (~B.suppressed)]
        return d.rename(columns={"mean": "v", "ci_lo": "lo", "ci_hi": "hi"})
    bias = B[(B.task_group == "binary_merged") & (B.metric == "accuracy") & B.bias_index.notna() & (~B.suppressed)]
    bias = bias.assign(v=bias.bias_index, lo=bias.bias_ci_lo, hi=bias.bias_ci_hi)
    cb, cm = conf_binned(items, "binary_merged"), conf_binned(items, "mcq")
    json.dump({"binary": cb.to_dict("records"), "mcq": cm.to_dict("records")}, open(T / "ed_horizon_confidence.json", "w"), indent=1)
    P = [("a", "Feasibility Assessment", "Balanced accuracy", bal, (0.36, 0.66), [(0.5, "chance")], None),
         ("b", "Feasibility Assessment", "Yes/no bias (original − perturbed)", bias, (-1.18, 1.2), [(0, "no bias")], ("answers ‘yes’", "answers ‘no’")),
         ("c", "Feasibility Assessment", "Stated confidence", cb, (0.5, 0.95), [], ("more certain", "less certain")),
         ("d", "Mechanistic Forecasting", "MCQ accuracy", pick("mcq", "accuracy"), (0.2, 1.0), [(0.25, "chance")], None),
         ("e", "Mechanistic Forecasting", "Stated confidence", cm, (0.45, 1.0), [], ("more certain", "less certain")),
         ("f", "Solution Design", "FRQ rubric score (0–10)", pick("frq", "frq_score"), (2.8, 5.6), [(5.0, "pass threshold")], None),
         ("g", "Temporal Prediction", "Absolute date error (months)", pick("date", "abs_err"), (0, 52), [], None),
         ("h", "Temporal Prediction", "Signed date error (months)", pick("date", "signed_err"), (-48, 58), [(0, "")], ("later than truth", "earlier than truth"))]
    fig = plt.figure(figsize=(183 * MM, 178 * MM))
    gs = fig.add_gridspec(3, 3, left=0.065, right=0.99, top=0.965, bottom=0.06, wspace=0.34, hspace=0.46)
    for k, (lab, fam, ylab, d, ylim, refs, arrows) in enumerate(P):
        ax = fig.add_subplot(gs[k // 3, k % 3])
        for i, (lo, hi) in enumerate(BINS):
            if i % 2 == 0: ax.axvspan(lo - 0.5, hi + 0.5, color="#F3F3F3", lw=0, zorder=0)
        for y, txt in refs:
            ax.axhline(y, color="#9A9A9A", lw=0.6, ls=(0, (3, 2)), zorder=1)
            if txt: ax.text(33.6, y, txt, fontsize=5.2, color="#7A7A7A", ha="right", va="bottom")
        for key, name, cut, col, mk in MODELS:
            r = d[d.model == key].sort_values("bin_lo")
            if r.empty: continue
            x = r.h_mean.to_numpy(float); y = r.v.to_numpy(float)
            ax.fill_between(x, r.lo.to_numpy(float), r.hi.to_numpy(float), color=col, alpha=0.14, lw=0, zorder=2)
            ax.plot(x, y, color=col, lw=0.9, zorder=3)
            for xi, yi, n in zip(x, y, r.n_items.to_numpy(int)):
                ax.plot(xi, yi, marker=mk, ms=size(n) * (1.25 if mk == "*" else 1.0), color=col, mec="white", mew=0.45, zorder=4, ls="none")
        ax.set_xlim(0.3, 34); ax.set_ylim(*ylim); ax.set_xticks([1, 6, 12, 18, 24, 30])
        ax.set_ylabel(ylab, labelpad=2)
        if k >= 5: ax.set_xlabel("Months after knowledge cutoff", labelpad=2)
        ax.text(-0.215, 1.045, lab, transform=ax.transAxes, fontsize=8.5, fontweight="bold", va="bottom")
        ax.text(0.0, 1.045, fam, transform=ax.transAxes, fontsize=7, fontweight="bold", va="bottom")
        if arrows:
            ax.text(0.02, 0.985, "↑ " + arrows[0], transform=ax.transAxes, ha="left", va="top", fontsize=5.2, color="#7A7A7A")
            ax.text(0.02, 0.015, "↓ " + arrows[1], transform=ax.transAxes, ha="left", va="bottom", fontsize=5.2, color="#7A7A7A")
    lax = fig.add_subplot(gs[2, 2]); lax.axis("off")
    hs = [Line2D([0], [0], color=c, lw=0.9, marker=m, ms=4.6 * (1.25 if m == "*" else 1), mec="white", mew=0.45) for _, _, _, c, m in MODELS]
    labs = [f"{n}  ({c})" for _, n, c, _, _ in MODELS]
    leg = lax.legend(hs, labs, loc="upper left", bbox_to_anchor=(-0.02, 1.08), ncol=1, fontsize=6.2, handlelength=2.0, handletextpad=0.6, labelspacing=0.5,
                     title="Model (knowledge cutoff)", title_fontsize=6.4, alignment="left")
    lax.add_artist(leg)
    ks = [Line2D([0], [0], marker="o", ls="none", ms=size(n), color="#8C8C8C", mec="white", mew=0.45) for n in (50, 500, 2000)]
    lax.legend(ks, ["50", "500", "2,000"], loc="lower left", bbox_to_anchor=(-0.02, -0.06), ncol=3, fontsize=6, handletextpad=0.25, columnspacing=1.2,
               title="Items per bin", title_fontsize=6.4, alignment="left")
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "ed_horizon.pdf"); fig.savefig(OUT / "ed_horizon.png", dpi=600); plt.close(fig); print("written")
if __name__ == "__main__": main()
