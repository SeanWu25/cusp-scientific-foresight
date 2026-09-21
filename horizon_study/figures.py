"""figures.py — regenerate every figure of the A4 horizon study from tables/*.json (+ items for the null overlay)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data as D, stats as S

T, F = D.STUDY / "tables", D.STUDY / "figures"; F.mkdir(exist_ok=True)
COLORS = {"gpt4o": "#D55E00", "llama33": "#56B4E9", "gptoss20b": "#E69F00", "deepseek_r1": "#CC79A7", "claude45": "#0072B2",
          "gpt54": "#009E73", "sonnet5": "#000000", "sol": "#F0E442", "dsv4pro": "#999999"}
MARK = {"gpt4o": "s", "llama33": "P", "gptoss20b": "v", "deepseek_r1": "D", "claude45": "o", "gpt54": "^", "sonnet5": "X", "sol": "*", "dsv4pro": "h"}
DS_TITLE = {"orig": "Original corpus (Jan 2024–Mar 2026), base", "ext": "Extension (Apr–Aug 2026), base", "merged": "Merged original + extension, base", "ws": "Pinned 500 subset"}
PANELS = [("binary_merged", "accuracy", "Binary (merged) accuracy", (0.3, 0.8)), ("binary_merged", "bias_index", "Binary bias index (acc_orig − acc_pert)", (-1, 1)),
          ("binary_merged", "auroc", "Binary AUROC of P(Yes)", (0.3, 0.8)), ("mcq", "accuracy", "MCQ accuracy", (0.2, 1.0)),
          ("date", "abs_err", "Date |error| (months)", None), ("date", "signed_err", "Date signed error (months, + = late)", None)]


def _load_binned(ds, scheme="primary"):
    p = T / f"binned_{ds}_{scheme}.json"
    return pd.DataFrame(json.load(open(p))) if p.exists() else None


def _plot_lines(ax, df, tg, metric, cond="base", annotate_n=True):
    sub = df[(df.task_group == tg) & (df.condition == cond)]
    if metric in ("bias_index", "auroc"):
        sub = sub[(sub.metric == "accuracy") & sub.get(metric, pd.Series(dtype=float)).notna()] if metric in sub else sub.iloc[0:0]
        val, lo, hi = metric, ("bias_ci_lo" if metric == "bias_index" else None), ("bias_ci_hi" if metric == "bias_index" else None)
    else:
        sub = sub[(sub.metric == metric) & (~sub.suppressed)]; val, lo, hi = "mean", "ci_lo", "ci_hi"
    for m in D.MODEL_ORDER:
        r = sub[sub.model == m].sort_values("bin_lo")
        if r.empty: continue
        x = r.h_mean.to_numpy(); y = r[val].to_numpy(float)
        if lo and lo in r:
            ax.fill_between(x, r[lo].to_numpy(float), r[hi].to_numpy(float), color=COLORS[m], alpha=0.12, lw=0)
        ax.plot(x, y, marker=MARK[m], color=COLORS[m], lw=1.6, ms=5, label=D.MODELS[m]["name"], mec="white", mew=0.6)
        if annotate_n:
            for xi, yi, n in zip(x, y, r.n_items):
                ax.annotate(str(int(n)), (xi, yi), textcoords="offset points", xytext=(0, 5), ha="center", fontsize=5, color=COLORS[m])


def fig_horizon(ds):
    df = _load_binned(ds)
    if df is None: return
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.2))
    for ax, (tg, metric, title, ylim) in zip(axes.ravel(), PANELS):
        _plot_lines(ax, df, tg, metric)
        ax.set_title(title, fontsize=9); ax.set_xlabel("horizon (months after cutoff, first-observable date)", fontsize=7); ax.tick_params(labelsize=7); ax.grid(color="#EEEEEE", lw=0.5)
        if ylim: ax.set_ylim(*ylim)
        if metric == "accuracy" and tg == "binary_merged": ax.axhline(0.5, color="#888888", lw=0.8, ls="--")
        if metric == "accuracy" and tg == "mcq": ax.axhline(0.25, color="#888888", lw=0.8, ls="--")
        if metric in ("bias_index", "signed_err"): ax.axhline(0, color="#888888", lw=0.8, ls="--")
        if metric == "auroc": ax.axhline(0.5, color="#888888", lw=0.8, ls="--")
        for b in (3.5, 6.5, 12.5, 24.5): ax.axvline(b, color="#DDDDDD", lw=0.6)
    h, l = axes[0][0].get_legend_handles_labels()
    if not h: h, l = axes[1][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=min(9, len(l)), fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(f"{DS_TITLE[ds]} — post-cutoff only (h ≥ 1); bins 1–3, 4–6, 7–12, 13–24, 25+ at their mean horizon; bands/bars = 95% event-bootstrap CI; labels = n items; cells n<20 hidden", fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96)); fig.savefig(F / f"horizon_{ds}.png", dpi=200); fig.savefig(F / f"horizon_{ds}.pdf"); plt.close(fig)


def fig_ws():
    df = _load_binned("ws")
    if df is None: return
    panels = [("binary_merged", "accuracy", "Binary (merged) accuracy", (0.3, 0.8)), ("mcq", "accuracy", "MCQ accuracy", (0.2, 1.0)), ("date", "abs_err", "Date |error| (months)", None)]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for row, cond in enumerate(("base", "ws_cutoff")):
        for ax, (tg, metric, title, ylim) in zip(axes[row], panels):
            _plot_lines(ax, df, tg, metric, cond=cond)
            ax.set_title(f"{title} — {'base' if cond == 'base' else 'WS+Cutoff (retrieval restricted to pre-cutoff)'}", fontsize=8.5); ax.tick_params(labelsize=7); ax.grid(color="#EEEEEE", lw=0.5)
            ax.set_xlabel("horizon (months after cutoff)", fontsize=7)
            if ylim: ax.set_ylim(*ylim)
            if metric == "accuracy": ax.axhline(0.5 if tg == "binary_merged" else 0.25, color="#888888", lw=0.8, ls="--")
    h, l = axes[0][0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=6, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Pinned 500-event subset, post-cutoff only: base vs retrieval-constrained condition on the same items", fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96)); fig.savefig(F / "horizon_ws.png", dpi=200); fig.savefig(F / "horizon_ws.pdf"); plt.close(fig)


def fig_date_null(ds, ev):
    df = D.load_items(ds, ev); df = df[df.condition == "base"]; nullj = json.load(open(T / "anchoring_null.json"))[ds]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, (metric, title) in zip(axes, (("signed_err", "signed error (months, + = late)"), ("abs_err", "|error| (months)"), ("date_score", "score exp(−0.1|Δ|)"))):
        for m in D.MODEL_ORDER:
            r = nullj.get(m, {})
            if r.get("skipped", True): continue
            d = df[(df.model == m) & (df.task_group == "date")].copy(); d["bin"] = d.h.map(lambda h: D.assign_bin(int(h), D.PRIMARY_BINS))
            g = d.groupby("bin").agg(h=("h", "mean"), v=(metric, "mean"), n=("id", "size")); g = g[g.n >= 20].sort_values("h")
            if g.empty: continue
            ax.plot(g.h, g.v, marker=MARK[m], color=COLORS[m], lw=1.6, ms=5, label=D.MODELS[m]["name"], mec="white", mew=0.6)
            k = r["choices"]["model_median_offset"]["k"]; nb = pd.DataFrame(S.null_binned(df, m, k, D.PRIMARY_BINS, metric)); nb = nb[nb.n >= 20]
            nb["h"] = nb.bin.map(dict(zip(g.index, g.h))); nb = nb.dropna().sort_values("h")
            ax.plot(nb.h, nb["mean"], color=COLORS[m], lw=1.2, ls="--", alpha=0.8)
        ax.set_title(f"Date task: {title}", fontsize=9); ax.set_xlabel("horizon (months after cutoff)", fontsize=7); ax.tick_params(labelsize=7); ax.grid(color="#EEEEEE", lw=0.5)
        if metric == "signed_err": ax.axhline(0, color="#888888", lw=0.8, ls="--")
    h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=min(9, len(l)), fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"{DS_TITLE[ds]} — solid: model; dashed (same colour): anchoring null 'always predict cutoff + model's median offset' (zero forecasting content)", fontsize=8)
    fig.tight_layout(rect=(0, 0.07, 1, 0.94)); fig.savefig(F / f"date_null_{ds}.png", dpi=200); fig.savefig(F / f"date_null_{ds}.pdf"); plt.close(fig)


def fig_continuous(ds):
    p = T / "continuous.json"
    if not p.exists(): return
    res = json.load(open(p)).get(ds, {}); keys = [k for k, v in res.items() if not v.get("skipped")]
    if not keys: return
    binned = _load_binned(ds)
    fig, axes = plt.subplots(1, len(keys), figsize=(3.6 * len(keys), 3.8), squeeze=False)
    for ax, k in zip(axes[0], keys):
        f = res[k]; g = np.array(f["grid"]); ax.fill_between(g, f["band_lo"], f["band_hi"], color="#BBBBBB", alpha=0.4, lw=0); ax.plot(g, f["curve"], color="black", lw=2, label="pooled spline (model FE, model-average)")
        if f.get("stick_breakpoint") is not None:
            bp = f["stick_breakpoint"]; ax.axvline(bp, color="#D55E00", lw=1.2, ls="--", label=f"broken-stick breakpoint {bp} mo" + (f" [CI {f['stick_breakpoint_ci'][0]:.0f}, {f['stick_breakpoint_ci'][1]:.0f}]" if f.get("stick_breakpoint_ci") else ""))
        if f.get("bend_spline_max_curvature") is not None:
            ax.axvline(f["bend_spline_max_curvature"], color="#0072B2", lw=1.0, ls=":", label=f"max curvature {f['bend_spline_max_curvature']} mo")
        tg, metric = k.split(":")
        if binned is not None:
            sub = binned[(binned.task_group == tg) & (binned.metric == metric) & (binned.condition == "base") & (~binned.suppressed)]
            for m in D.MODEL_ORDER:
                r = sub[sub.model == m].sort_values("bin_lo")
                if not r.empty: ax.plot(r.h_mean, r["mean"], marker=MARK[m], color=COLORS[m], lw=0.8, ms=3.5, alpha=0.7)
        ax.set_title(k, fontsize=9); ax.set_xlabel("horizon (months)", fontsize=7); ax.tick_params(labelsize=7); ax.grid(color="#EEEEEE", lw=0.5); ax.legend(fontsize=5.5, loc="best", frameon=False)
    fig.suptitle(f"{DS_TITLE[ds]} — continuous horizon fits (natural cubic spline, 4 df, model fixed effects; band = 95% event bootstrap); thin lines = per-model binned means", fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(F / f"continuous_{ds}.png", dpi=200); fig.savefig(F / f"continuous_{ds}.pdf"); plt.close(fig)


if __name__ == "__main__":
    ev = D.load_events()
    for ds in ("orig", "ext", "merged"):
        fig_horizon(ds); fig_date_null(ds, ev); fig_continuous(ds); print("figs", ds, file=sys.stderr)
    fig_ws(); print("done", file=sys.stderr)
