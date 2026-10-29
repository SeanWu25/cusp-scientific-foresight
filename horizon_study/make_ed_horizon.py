"""make_ed_horizon.py — Extended Data figure: post-cutoff performance by forecasting horizon, one panel per task family
(a Feasibility Assessment, b Mechanistic Forecasting, c Temporal Prediction, d Solution Design), nine Table 1 models
(DeepSeek-V4-Pro excluded, as in tables_no_v4pro/), merged original + extension corpus, base condition.

Horizon h = months(first-observable date) − months(model cutoff), post-cutoff only (h ≥ 1). Primary bins 1–3, 4–6, 7–12,
13–24, 25+ plotted at their mean horizon; bands = 95% event-level bootstrap CIs (10,000 resamples); bins with < 20 items hidden.
b–d read tables_no_v4pro/binned_merged_primary.json (run_no_v4pro.py main). a (balanced accuracy = mean of the accuracy on
original and perturbed binary questions, the Feasibility metric of the paper) is computed here from the same items with the
same bins, minimum n (20 per question type) and bootstrap.
Writes manuscript_updates/ed_horizon.{png,pdf} and horizon_study/tables_no_v4pro/ed_horizon_values.{json,md}."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H))
import data as D, stats as S
D.MODELS.pop("dsv4pro", None); D.MODEL_ORDER[:] = [m for m in D.MODEL_ORDER if m != "dsv4pro"]
T = H / "tables_no_v4pro"; OUT = H.parent / "manuscript_updates"
NAME = {"gpt4o": "GPT-4o", "gptoss20b": "GPT-OSS", "deepseek_r1": "DeepSeek R1", "llama33": "LLaMA 3.3", "claude45": "Claude S4.5",
        "gpt54": "GPT-5.4", "opus48": "Claude Opus 4.8", "sonnet5": "Claude Sonnet 5", "sol": "GPT-5.6 Sol"}
ORDER = ["gpt4o", "gptoss20b", "deepseek_r1", "llama33", "claude45", "gpt54", "opus48", "sonnet5", "sol"]   # = Figure 3 legend order
COL = {"GPT-4o": "#E07B22", "GPT-OSS": "#E8AE25", "DeepSeek R1": "#D58BB4", "LLaMA 3.3": "#6EC0EA", "Claude S4.5": "#1F7BB8",
       "GPT-5.4": "#22A884", "Claude Opus 4.8": "#7B4FA0", "Claude Sonnet 5": "#C0392B", "GPT-5.6 Sol": "#7F7F7F"}   # = make_fig3_overleaf.py
MARK = {"gpt4o": "s", "gptoss20b": "v", "deepseek_r1": "D", "llama33": "P", "claude45": "o", "gpt54": "^", "opus48": "p", "sonnet5": "X", "sol": "*"}

def balanced(df, B=S.B_DEFAULT, min_n=20, seed=0):
    rows = []
    for m in ORDER:
        g = df[(df.model == m) & (df.task_group == "binary_merged")]
        for lo, hi in D.PRIMARY_BINS:
            s = g[(g.h >= lo) & (g.h <= hi)]; b, p = s[s.task == "binary"], s[s.task == "binary_perturbed"]
            row = dict(model=m, bin=D.bin_label(lo, hi), bin_lo=lo, h_mean=float(s.h.mean()) if len(s) else np.nan, n_items=len(s), n_binary=len(b), n_perturbed=len(p))
            if len(b) >= min_n and len(p) >= min_n:
                wb, wp = S.event_weights(b.id.to_numpy(), B, seed), S.event_weights(p.id.to_numpy(), B, seed)
                bm = 0.5 * (S.wmean(b.y.to_numpy(float)[None, :], wb) + S.wmean(p.y.to_numpy(float)[None, :], wp))
                row.update(suppressed=False, mean=float(0.5 * (b.y.mean() + p.y.mean())), ci_lo=S.ci(bm)[0], ci_hi=S.ci(bm)[1])
            else: row.update(suppressed=True)
            rows.append(row)
    return pd.DataFrame(rows)

def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    ev = D.load_events(); items = D.load_items("merged", ev); items = items[items.condition == "base"]
    bal = balanced(items)
    binned = pd.DataFrame(json.load(open(T / "binned_merged_primary.json"))); binned = binned[(binned.condition == "base") & (~binned.suppressed)]
    def pick(tg, metric): return binned[(binned.task_group == tg) & (binned.metric == metric)][["model", "bin", "bin_lo", "h_mean", "n_items", "mean", "ci_lo", "ci_hi"]]
    panels = [("a", "Feasibility Assessment", "Balanced accuracy", bal[~bal.suppressed], (0.3, 0.8), 0.5),
              ("b", "Mechanistic Forecasting", "MCQ accuracy", pick("mcq", "accuracy"), (0.2, 1.0), 0.25),
              ("c", "Temporal Prediction", "Absolute date error (months)", pick("date", "abs_err"), (0, 60), None),
              ("d", "Solution Design", "FRQ rubric score (0–10)", pick("frq", "frq_score"), (2.5, 6.0), 5.0)]
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.6)); vals = {}
    for ax, (lab, title, ylab, d, ylim, ref) in zip(axes.ravel(), panels):
        for m in ORDER:
            r = d[d.model == m].sort_values("bin_lo")
            if r.empty: continue
            x, y = r.h_mean.to_numpy(float), r["mean"].to_numpy(float)
            ax.fill_between(x, r.ci_lo.to_numpy(float), r.ci_hi.to_numpy(float), color=COL[NAME[m]], alpha=0.13, lw=0)
            ax.plot(x, y, marker=MARK[m], color=COL[NAME[m]], lw=1.8, ms=6.5, mec="white", mew=0.7, label=NAME[m])
            vals.setdefault(title, {})[NAME[m]] = [dict(bin=b, h_mean=round(h, 2), n=int(n), mean=round(v, 4), ci=[round(lo, 4), round(hi, 4)])
                                                   for b, h, n, v, lo, hi in zip(r["bin"], x, r.n_items, y, r.ci_lo, r.ci_hi)]
        if ref is not None: ax.axhline(ref, color="#999999", lw=1, ls="--", zorder=0)
        for b in (3.5, 6.5, 12.5, 24.5): ax.axvline(b, color="#EEEEEE", lw=0.8, zorder=0)
        ax.set_ylim(*ylim); ax.set_xlim(0, 31); ax.set_title(title, fontsize=14, fontweight="bold"); ax.set_ylabel(ylab, fontsize=12)
        ax.set_xlabel("Months after knowledge cutoff", fontsize=12); ax.tick_params(labelsize=11)
        ax.text(-0.11, 1.06, lab, transform=ax.transAxes, fontsize=20, fontweight="bold", va="bottom")
    h, l = axes[0, 0].get_legend_handles_labels()
    for ax in axes.ravel():
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l: h.append(hh); l.append(ll)
    order = [NAME[m] for m in ORDER if NAME[m] in l]; h = [h[l.index(n)] for n in order]
    fig.legend(h, order, loc="lower center", ncol=5, fontsize=11.5, frameon=False, bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0, 0.075, 1, 1), h_pad=2.8, w_pad=2.5)
    OUT.mkdir(exist_ok=True); fig.savefig(OUT / "ed_horizon.png", dpi=300); fig.savefig(OUT / "ed_horizon.pdf"); plt.close(fig)
    json.dump(vals, open(T / "ed_horizon_values.json", "w"), indent=1)
    L = ["# Extended Data: post-cutoff performance by horizon (values plotted)", "", "Merged corpus, base condition, nine Table 1 models; mean [95% event-bootstrap CI] (n items) per horizon bin.", ""]
    for title, mods in vals.items():
        L += [f"## {title}", "", "| Model | " + " | ".join(lab for lab in ["1-3", "4-6", "7-12", "13-24", "25+"]) + " |", "|---|---|---|---|---|---|"]
        for mname, pts in mods.items():
            byb = {p["bin"]: p for p in pts}
            L.append(f"| {mname} | " + " | ".join((f"{byb[b]['mean']:.3f} [{byb[b]['ci'][0]:.3f}, {byb[b]['ci'][1]:.3f}] ({byb[b]['n']})" if b in byb else "—") for b in ["1-3", "4-6", "7-12", "13-24", "25+"]) + " |")
        L.append("")
    (T / "ed_horizon_values.md").write_text("\n".join(L)); print("written", OUT / "ed_horizon.png")
if __name__ == "__main__": main()
