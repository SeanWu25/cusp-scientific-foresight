"""
run_split.py — the A4 horizon analyses with (a) binary split into the ORIGINAL and the PERTURBED
question instead of the merged binary task, and (b) FRQ split into its four rubric dimensions
(alignment, specificity, novelty, feasibility; each 0-10, the stored score is their mean), in
addition to the total. Same loaders, same statistics, same estimators as run_all.py /
binned_coef.py: this module only rebinds the task list, the outcome columns and the output
directory, and supplies split-aware versions of the two stages whose loops hard-code task names.

  python horizon_study/run_split.py                  # all stages (~45 min)
  python horizon_study/run_split.py --stage binned   # one of: counts, binned, trends, pooled,
                                                     #         continuous, ws, bincoef, figures
Outputs: horizon_study/tables/split/*.{json,md}, horizon_study/figures/split/*.png
Not re-run here: the date task and the anchoring null (unchanged by the split), the MCC stage
(already uses both binary variants), and the sensitivity stage (about the horizon definition,
not the outcome; its conclusions carry over).
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data as D, stats as S, glmm as G, run_all as R, binned_coef as BC

# ----------------------------------------------------------------------------- rebinding
SPLIT_TASKS = ["binary", "binary_perturbed", "frq"]
FRQ_DIMS = ["frq_score", "frq_alignment", "frq_specificity", "frq_novelty", "frq_feasibility"]
OUTCOMES = {"binary": ["accuracy"], "binary_perturbed": ["accuracy"], "mcq": ["accuracy"],
            "date": ["signed_err", "abs_err", "date_score"], "frq": FRQ_DIMS}
T = D.STUDY / "tables" / "split"; F = D.STUDY / "figures" / "split"; T.mkdir(parents=True, exist_ok=True); F.mkdir(parents=True, exist_ok=True)
R.T = T; BC.T = T; BC.F = F
D.TASKS = SPLIT_TASKS
S.outcome_columns = lambda tg: OUTCOMES[tg]
BC.OUTCOMES = {"binary": [("y", "binomial")], "binary_perturbed": [("y", "binomial")], "frq": [(m, "gaussian") for m in FRQ_DIMS]}
BC.UNIT.update({m: "points (0–10)" for m in FRQ_DIMS})
_load_items = D.load_items


def load_items_split(*a, **k):
    df = _load_items(*a, **k)
    df["task_group"] = df.task            # binary and binary_perturbed become their own groups
    return df.reset_index(drop=True)


D.load_items = load_items_split
DATASETS, DS_LABEL, dump, f3 = R.DATASETS, R.DS_LABEL, R.dump, R.f3
DIM_LABEL = {"frq_score": "FRQ total (mean of 4)", "frq_alignment": "FRQ alignment", "frq_specificity": "FRQ specificity",
             "frq_novelty": "FRQ novelty", "frq_feasibility": "FRQ feasibility", "accuracy": "accuracy"}


# ----------------------------------------------------------------------------- stages
def stage_counts(ev):
    out = {}; L = ["# Split analysis — post-cutoff N per dataset × model × task (h ≥ 1)", "",
                   "N = events with a scored item. `binary` = the original question, `binary_perturbed` = the perturbed twin; FRQ counts items with all four rubric dimensions.", ""]
    for ds in DATASETS:
        df = D.load_items(ds, ev)
        for cond in sorted(df.condition.unique()):
            d = df[df.condition == cond]
            d = d[(d.task != "frq") | d[FRQ_DIMS].notna().all(axis=1)]
            tab = d.groupby(["model", "task_group"]).id.nunique().unstack(fill_value=0).reindex(D.MODEL_ORDER).fillna(0).astype(int)
            out[f"{ds}:{cond}"] = {m: {t: int(tab.loc[m, t]) for t in tab.columns} for m in D.MODEL_ORDER}
            L += [f"\n## {DS_LABEL[ds]} — condition `{cond}`\n", "| model | binary (original) | binary (perturbed) | FRQ (4 dims) |", "|---|---|---|---|"]
            for m in D.MODEL_ORDER:
                L.append(f"| {D.MODELS[m]['name']} | {tab.loc[m].get('binary', 0)} | {tab.loc[m].get('binary_perturbed', 0)} | {tab.loc[m].get('frq', 0)} |")
    dump("n_post_cutoff", out); (T / "n_post_cutoff.md").write_text("\n".join(L) + "\n")


def _prep(d):
    return R._prep(d)


def stage_pooled(ev):
    res = {}
    for ds in DATASETS:
        df = D.load_items(ds, ev); df = df[df.condition == "base"]; res[ds] = {}
        for tg in ("binary", "binary_perturbed"):
            d = _prep(df[df.task_group == tg])
            if d.model.nunique() < 3 or len(d) < 500:
                res[ds][tg] = dict(skipped=True, n=len(d), n_models=int(d.model.nunique())); continue
            r = {}
            for label, cols, slope in (("h", ["hy"], None), ("h+cal", ["hy", "caly"], None), ("h+h2", ["hy", "hy2"], None), ("h+random_slope", ["hy"], "hy")):
                try: r[label] = G.fit_crossed(d, "y", cols, "binomial", random_slope_col=slope)
                except Exception as e: r[label] = dict(error=str(e)[:200])
            r["event_fe_h2"] = S.event_fe_conditional(d, tg, ["h2"]); r["event_fe_bins"] = S.event_fe_bins(d, tg)
            r["n"] = len(d); r["n_events"] = int(d.id.nunique()); r["n_models"] = int(d.model.nunique()); r["h_range"] = [int(d.h.min()), int(d.h.max())]
            res[ds][tg] = r; print(f"  pooled {ds} {tg}", file=sys.stderr)
        d = _prep(df[(df.task_group == "frq") & df[FRQ_DIMS].notna().all(axis=1)])
        if d.model.nunique() < 3 or len(d) < 300:
            res[ds]["frq"] = dict(skipped=True, n=len(d), n_models=int(d.model.nunique()))
        else:
            r = {}
            for metric in FRQ_DIMS:
                r[metric] = {}
                for label, cols in (("h", ["hy"]), ("h+cal", ["hy", "caly"]), ("h+h2", ["hy", "hy2"])):
                    try: r[metric][label] = G.fit_crossed(d, metric, cols, "gaussian")
                    except Exception as e: r[metric][label] = dict(error=str(e)[:200])
            r["n"] = len(d); r["n_events"] = int(d.id.nunique()); r["n_models"] = int(d.model.nunique()); r["h_range"] = [int(d.h.min()), int(d.h.max())]
            res[ds]["frq"] = r; print(f"  pooled {ds} frq", file=sys.stderr)
    fam = []
    for ds in res:
        for tg, r in res[ds].items():
            if r.get("skipped"): continue
            if tg == "frq":
                for metric in FRQ_DIMS:
                    c = r.get(metric, {}).get("h", {}).get("coef", {}).get("hy")
                    if c: fam.append((ds, tg, metric, c))
            else:
                c = r.get("h", {}).get("coef", {}).get("hy")
                if c: fam.append((ds, tg, "accuracy", c))
    from scipy.stats import norm
    ps = [2 * (1 - norm.cdf(abs(c["z"]))) for *_, c in fam]
    for (ds, tg, metric, c), p, ph in zip(fam, ps, S.holm(ps)): c["p"] = p; c["p_holm"] = ph
    dump("pooled", res)
    L = ["# Split analysis — pooled mixed-effects results (post-cutoff, base condition)", "",
         "Same estimator as `tables/pooled.md`: crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace GLMM (logistic for the two binary variants, Gaussian for the FRQ total and each rubric dimension). "
         "Holm across the family of pooled linear-horizon coefficients in this file; `*` = Holm p < 0.05. The identification note of the main table applies unchanged.", ""]
    for ds in DATASETS:
        L.append(f"\n## {DS_LABEL[ds]}\n")
        for tg, r in res.get(ds, {}).items():
            if r.get("skipped"): L.append(f"- {tg}: skipped (n={r['n']}, models={r['n_models']})"); continue
            if tg == "frq":
                L += [f"### FRQ by rubric dimension — n={r['n']} items, {r['n_events']} events, {r['n_models']} models, horizon {r['h_range'][0]}–{r['h_range'][1]} months\n",
                      "| dimension | model | horizon coef (points per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |", "|---|---|---|---|---|---|---|---|---|"]
                for metric in FRQ_DIMS:
                    for label in ("h", "h+cal", "h+h2"):
                        f = r[metric].get(label, {})
                        if "coef" not in f: L.append(f"| {DIM_LABEL[metric]} | {label} | error: {f.get('error')} | | | | | | |"); continue
                        c = f["coef"]; hy = c["hy"]; pp = f"{hy.get('p', float('nan')):.3g} / {hy.get('p_holm', float('nan')):.3g}{'*' if hy.get('p_holm', 1) < 0.05 else ''}" if label == "h" else "—"
                        L.append(f"| {DIM_LABEL[metric]} | {label} | {hy['mean']:+.3f} [{hy['ci_lo']:+.3f}, {hy['ci_hi']:+.3f}] | {pp} | {f3(c.get('caly', {}).get('mean'))} | {f3(c.get('hy2', {}).get('mean'))} | {f3(f['vc_sd'].get('event'))} | {f3(f['vc_sd'].get('model'))} | {f3(f.get('resid_sd'))} |")
            else:
                L += [f"### {tg} — n={r['n']} items, {r['n_events']} events, {r['n_models']} models, horizon {r['h_range'][0]}–{r['h_range'][1]} months\n",
                      "| model | horizon coef (log-odds per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | model slope SD |", "|---|---|---|---|---|---|---|---|"]
                for label in ("h", "h+cal", "h+h2", "h+random_slope"):
                    f = r.get(label, {})
                    if "coef" not in f: L.append(f"| {label} | error: {f.get('error')} | | | | | | |"); continue
                    c = f["coef"]; hy = c["hy"]; pp = f"{hy.get('p', float('nan')):.3g} / {hy.get('p_holm', float('nan')):.3g}{'*' if hy.get('p_holm', 1) < 0.05 else ''}" if label == "h" else "—"
                    L.append(f"| {label} | {hy['mean']:+.3f} [{hy['ci_lo']:+.3f}, {hy['ci_hi']:+.3f}] | {pp} | {f3(c.get('caly', {}).get('mean'))} | {f3(c.get('hy2', {}).get('mean'))} [{f3(c.get('hy2', {}).get('ci_lo'))}, {f3(c.get('hy2', {}).get('ci_hi'))}] | {f3(f['vc_sd'].get('event'))} | {f3(f['vc_sd'].get('model'))} | {f3(f['vc_sd'].get('model:hy'))} |")
                e = r.get("event_fe_h2", {})
                if "coef" in e:
                    c = e["coef"].get("h_years_sq", {}); L.append(f"| event-FE conditional logit, curvature only | quadratic {c.get('mean', float('nan')):+.3f} [{c.get('ci_lo', float('nan')):+.3f}, {c.get('ci_hi', float('nan')):+.3f}] p={c.get('p', float('nan')):.3g} (n informative strata = {e['n_events']}) | | | | | | |")
                eb = r.get("event_fe_bins", {})
                if "coef" in eb:
                    L.append("\nEvent-FE bin contrasts (log-odds vs the 1–3 month bin, same event, model FE): " + "; ".join(f"{b}: {v['log_odds_vs_ref']:+.2f} (p={v['p']:.2g}, n={v['n']})" for b, v in eb["coef"].items()) + "\n")
    (T / "pooled.md").write_text("\n".join(L) + "\n")


def stage_ws(ev):
    from statsmodels.discrete.conditional_models import ConditionalLogit
    import statsmodels.api as sm
    df = D.load_items("ws", ev)
    out = {"per_model": [], "pooled": {}}
    L = ["# Split analysis — WS+Cutoff vs base on the pinned 500 subset, post-cutoff", "",
         "Same estimators as `tables/ws_vs_base.md`. Per model: slope of outcome on horizon (per 12 months) under each condition on the SAME items, paired difference by event bootstrap (10k). "
         "Pooled: conditional logit stratified by (event, model) for the binary variants; paired-difference OLS with model FE and event-clustered SE for each FRQ dimension.", "",
         "| model | task | metric | n paired items | horizon | base slope /12mo [CI] | WS+cut slope /12mo [CI] | difference (WS − base) [CI] | p |", "|---|---|---|---|---|---|---|---|---|"]
    for m in D.MODEL_ORDER:
        for tg in SPLIT_TASKS:
            b = df[(df.model == m) & (df.task_group == tg) & (df.condition == "base")]; w = df[(df.model == m) & (df.task_group == tg) & (df.condition == "ws_cutoff")]
            if b.empty or w.empty: continue
            pair = b.merge(w, on=["id", "task"], suffixes=("_b", "_w"))
            if len(pair) < 60 or (pair.h_b.max() - pair.h_b.min()) < 3:
                out["per_model"].append(dict(model=m, task_group=tg, n=len(pair), skipped=True)); L.append(f"| {D.MODELS[m]['name']} | {tg} | — | {len(pair)} | | too thin (n<60 or range<3) | | | |"); continue
            for metric in OUTCOMES[tg]:
                pp = pair if metric == "accuracy" else pair[pair[f"{metric}_b"].notna() & pair[f"{metric}_w"].notna()]
                vb = (pp.y_b if metric == "accuracy" else pp[f"{metric}_b"]).to_numpy(float); vw = (pp.y_w if metric == "accuracy" else pp[f"{metric}_w"]).to_numpy(float)
                h = pp.h_b.to_numpy(float); W = S.event_weights(pp.id.to_numpy(), 10000)
                sb, sw = S.wslope(h[None, :], vb[None, :], W), S.wslope(h[None, :], vw[None, :], W); dd = sw - sb
                r = dict(model=m, task_group=tg, metric=metric, n=len(pp), h_min=int(h.min()), h_max=int(h.max()), base_slope_12m=float(12 * np.polyfit(h, vb, 1)[0]), base_ci=[12 * x for x in S.ci(sb)],
                         ws_slope_12m=float(12 * np.polyfit(h, vw, 1)[0]), ws_ci=[12 * x for x in S.ci(sw)], diff_12m=float(12 * (np.polyfit(h, vw, 1)[0] - np.polyfit(h, vb, 1)[0])), diff_ci=[12 * x for x in S.ci(dd)], p=S.boot_p(dd),
                         base_mean=float(vb.mean()), ws_mean=float(vw.mean()))
                out["per_model"].append(r)
                L.append(f"| {D.MODELS[m]['name']} | {tg} | {DIM_LABEL[metric]} | {len(pp)} | {r['h_min']}–{r['h_max']} | {r['base_slope_12m']:+.3f} [{r['base_ci'][0]:+.3f}, {r['base_ci'][1]:+.3f}] | {r['ws_slope_12m']:+.3f} [{r['ws_ci'][0]:+.3f}, {r['ws_ci'][1]:+.3f}] | {r['diff_12m']:+.3f} [{r['diff_ci'][0]:+.3f}, {r['diff_ci'][1]:+.3f}] | {r['p']:.3g} |")
    L += ["\n## Pooled condition × horizon interaction\n", "| task | n strata / pairs | ws main effect | ws × horizon (per year) [CI] | p |", "|---|---|---|---|---|"]
    for tg in ("binary", "binary_perturbed"):
        d = df[df.task_group == tg].copy(); d["stratum"] = pd.factorize(d.id + "|" + d.model)[0]
        d["ws"] = (d.condition == "ws_cutoff").astype(float); d["hy"] = (d.h - d.h.mean()) / 12.0; d["ws_h"] = d.ws * d.hy
        keep = d.groupby("stratum").y.transform(lambda s: 0 < s.sum() < len(s)); d2 = d[keep]
        try:
            X = d2[["ws", "ws_h"]].to_numpy(); r = ConditionalLogit(d2.y.to_numpy(), X, groups=d2.stratum.to_numpy()).fit(disp=0)
            out["pooled"][tg] = dict(n_strata=int(d2.stratum.nunique()), ws=float(r.params[0]), ws_se=float(r.bse[0]), ws_h=float(r.params[1]), ws_h_se=float(r.bse[1]), ws_h_p=float(r.pvalues[1]))
            L.append(f"| {tg} (conditional logit, event × model strata) | {d2.stratum.nunique()} | {r.params[0]:+.3f} log-odds (se {r.bse[0]:.3f}) | {r.params[1]:+.3f} [{r.params[1] - 1.96 * r.bse[1]:+.3f}, {r.params[1] + 1.96 * r.bse[1]:+.3f}] | {r.pvalues[1]:.3g} |")
        except Exception as e:
            out["pooled"][tg] = dict(error=str(e)[:200]); L.append(f"| {tg} | error {str(e)[:60]} | | | |")
    d = df[df.task_group == "frq"]; b = d[d.condition == "base"]; w = d[d.condition == "ws_cutoff"]; pair = b.merge(w, on=["id", "model"], suffixes=("_b", "_w"))
    for metric in FRQ_DIMS:
        pp = pair[pair[f"{metric}_b"].notna() & pair[f"{metric}_w"].notna()]
        if len(pp) < 60: continue
        dif = (pp[f"{metric}_w"] - pp[f"{metric}_b"]).to_numpy(float); h = pp.h_b.to_numpy(float) / 12
        X = sm.add_constant(np.column_stack([h, pd.get_dummies(pp.model, drop_first=True).astype(float).to_numpy()]))
        r = sm.OLS(dif, X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(pp.id)[0]})
        out["pooled"][metric] = dict(n=len(pp), ws_h=float(r.params[1]), se=float(r.bse[1]), p=float(r.pvalues[1]), ws_mean_diff=float(dif.mean()))
        L.append(f"| {DIM_LABEL[metric]} (WS − base difference on horizon, model FE, event-clustered) | {len(pp)} | mean diff {dif.mean():+.3f} points | {r.params[1]:+.3f} [{r.params[1] - 1.96 * r.bse[1]:+.3f}, {r.params[1] + 1.96 * r.bse[1]:+.3f}] | {r.pvalues[1]:.3g} |")
    dump("ws_vs_base", out); (T / "ws_vs_base.md").write_text("\n".join(L) + "\n")


def stage_bincoef(ev):
    BC.run()


def stage_figures(ev):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    panels = [("binary", "accuracy", "Binary (original) accuracy", 0.5), ("binary_perturbed", "accuracy", "Binary (perturbed) accuracy", 0.5),
              ("frq", "frq_score", "FRQ total (0–10)", None), ("frq", "frq_alignment", "FRQ alignment", None), ("frq", "frq_specificity", "FRQ specificity", None),
              ("frq", "frq_novelty", "FRQ novelty", None), ("frq", "frq_feasibility", "FRQ feasibility", None)]
    cols = plt.cm.tab10.colors
    for ds in ("orig", "ext", "merged", "ws"):
        p = T / f"binned_{ds}_primary.json"
        if not p.exists(): continue
        rows = pd.DataFrame(json.load(open(p))); rows = rows[rows.condition == ("ws_cutoff" if ds == "ws" else "base")]
        fig, axes = plt.subplots(1, len(panels), figsize=(3.1 * len(panels), 3.3), sharex=True)
        for ax, (tg, metric, title, ref) in zip(axes, panels):
            sub = rows[(rows.task_group == tg) & (rows.metric == metric) & (~rows.suppressed)]
            for i, m in enumerate(D.MODEL_ORDER):
                r = sub[sub.model == m].sort_values("bin_lo")
                if r.empty: continue
                ax.errorbar(r.h_mean, r["mean"], yerr=[r["mean"] - r.ci_lo, r.ci_hi - r["mean"]], fmt="o-", ms=3, lw=1, capsize=2, color=cols[i % 10], label=D.MODELS[m]["name"])
            if ref is not None: ax.axhline(ref, color="#888888", lw=0.8, ls="--")
            ax.set_title(title, fontsize=8); ax.set_xlabel("horizon (months after cutoff)", fontsize=7); ax.tick_params(labelsize=7); ax.grid(color="#EEEEEE", lw=0.5)
        axes[0].legend(fontsize=5, frameon=False); fig.suptitle(f"{DS_LABEL[ds]} — binned means by horizon (bins 1–3, 4–6, 7–12, 13–24, 25+), 95% event-bootstrap CI", fontsize=8)
        fig.tight_layout(); fig.savefig(F / f"horizon_split_{ds}.png", dpi=170); plt.close(fig)
        print(f"  figure {ds}", file=sys.stderr)


STAGES = dict(counts=stage_counts, binned=R.stage_binned, trends=R.stage_trends, pooled=stage_pooled, continuous=R.stage_continuous,
              ws=stage_ws, bincoef=stage_bincoef, figures=stage_figures)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="all"); a = ap.parse_args()
    ev = D.load_events()
    for name, fn in STAGES.items():
        if a.stage in ("all", name):
            t = time.time(); print(f"== split {name}", file=sys.stderr); fn(ev); print(f"== split {name} done in {time.time() - t:.0f}s", file=sys.stderr)
