"""
run_all.py — regenerate every table of the A4 horizon study from stored reports.

  python horizon_study/run_all.py                 # everything (~30-40 min)
  python horizon_study/run_all.py --stage binned  # one stage
Stages: counts, dates, binned, trends, pooled, continuous, ws, null, sensitivity
Figures: python horizon_study/figures.py
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data as D, stats as S, glmm as G

T = D.STUDY / "tables"; T.mkdir(exist_ok=True)
DATASETS = ["orig", "ext", "merged", "ws"]
DS_LABEL = {"orig": "1. original corpus (Jan 2024–Mar 2026), base", "ext": "2. extension (Apr–Aug 2026), base",
            "merged": "4. merged original + extension, base", "ws": "3. WS+Cutoff on the pinned 500 subset"}


def dump(name, obj):
    json.dump(obj, open(T / f"{name}.json", "w"), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating,)) else (int(o) if isinstance(o, np.integer) else str(o)))


def f3(v, d=3):
    return "—" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{d}f}"


def load(ds, ev, **kw):
    df = D.load_items(ds, ev, **kw)
    return df[df.condition == "base"] if ds != "ws" else df


# ----------------------------------------------------------------------------- stages
def stage_counts(ev):
    out = {}; L = ["# Post-cutoff N per dataset × model × task (h ≥ 1; base condition)", "",
                   "N = events with a scored item; binary counts events with either the original or the perturbed question.", ""]
    for ds in DATASETS:
        df = D.load_items(ds, ev)
        for cond in sorted(df.condition.unique()):
            d = df[df.condition == cond]
            tab = d.groupby(["model", "task_group"]).id.nunique().unstack(fill_value=0).reindex(D.MODEL_ORDER).fillna(0).astype(int)
            items = d.groupby(["model", "task_group"]).size().unstack(fill_value=0).reindex(D.MODEL_ORDER).fillna(0).astype(int)
            hr = d.groupby("model").h.agg(["min", "max", "median"]).reindex(D.MODEL_ORDER)
            out[f"{ds}:{cond}"] = {m: dict(events={t: int(tab.loc[m, t]) for t in tab.columns}, items={t: int(items.loc[m, t]) for t in items.columns},
                                          h_min=(None if pd.isna(hr.loc[m, "min"]) else int(hr.loc[m, "min"])), h_max=(None if pd.isna(hr.loc[m, "max"]) else int(hr.loc[m, "max"])))
                                  for m in D.MODEL_ORDER}
            L += [f"\n## {DS_LABEL[ds]} — condition `{cond}`\n", "| model | cutoff | binary events (items) | MCQ events | date events | horizon range (months) |", "|---|---|---|---|---|---|"]
            for m in D.MODEL_ORDER:
                b = tab.loc[m].get("binary_merged", 0); bi = items.loc[m].get("binary_merged", 0)
                rng = "—" if pd.isna(hr.loc[m, "min"]) else f"{int(hr.loc[m, 'min'])}–{int(hr.loc[m, 'max'])} (median {hr.loc[m, 'median']:.0f})"
                L.append(f"| {D.MODELS[m]['name']} | {D.MODELS[m]['cutoff']} | {b} ({bi}) | {tab.loc[m].get('mcq', 0)} | {tab.loc[m].get('date', 0)} | {rng} |")
    L += ["\n## Cutoff verification (2026-09-20)\n", "| model | cutoff used | source / status | sensitivity value |", "|---|---|---|---|"]
    for m, c in D.MODELS.items():
        L.append(f"| {c['name']} | {c['cutoff']} | {c['cutoff_source']} | {c['cutoff_alt'] or '—'} |")
    L += ["\nNotes: GPT-5.6 Sol's WS+Cutoff run was re-generated on 2026-09-20 after a fix to scripts/web_search.py (the original run had `web_search_error` on all 500 rows and no retrieval context). "
          "DeepSeek R1 has no extension run (deployment retired). DeepSeek-V4-Pro has no post-cutoff items on the original corpus."]
    dump("n_post_cutoff", out); (T / "n_post_cutoff.md").write_text("\n".join(L) + "\n")


def stage_dates(ev):
    g = ev.doi_m - ev.first_m
    out = {}
    L = ["# First-observable vs DOI/journal date", "",
         "Horizon uses the FIRST-OBSERVABLE month. For the original corpus the stored `publication_date` already is the earliest date the build pipeline found "
         "(Crossref creation, bioRxiv/medRxiv, Semantic Scholar, Europe PMC); the journal date was recovered from the build-stage CSVs for 3,150 of 3,642 DOI-linked events "
         "(the other 492 fall back to the first-observable date, so their gap is recorded as 0). arXiv-linked events use the earlier of the stored month and the month in the arXiv id; "
         "their 'DOI date' is the listing month. Extension events carry both fields natively (`original_publication_date` − `first_date_found`).", ""]
    for corpus in ("orig", "ext"):
        e = ev[ev.corpus == corpus]; gg = g[e.index]
        dist = gg.value_counts().sort_index()
        out[corpus] = dict(n=len(e), gap_distribution={int(k): int(v) for k, v in dist.items()}, share_zero=float((gg == 0).mean()), share_ge3=float((gg >= 3).mean()),
                           mean=float(gg.mean()), median=float(gg.median()), p90=float(gg.quantile(0.9)), max=int(gg.max()),
                           by_link_kind={k: dict(n=int(len(s)), mean=float(gg[s.index].mean()), share_zero=float((gg[s.index] == 0).mean()), max=int(gg[s.index].max())) for k, s in e.groupby("link_kind")},
                           by_source={k: dict(n=int(len(s)), mean=float(gg[s.index].mean()), share_zero=float((gg[s.index] == 0).mean()), p90=float(gg[s.index].quantile(.9))) for k, s in e.groupby("source")})
        L += [f"\n## {corpus} (n = {len(e)})\n", f"gap = DOI/journal month − first-observable month: mean {gg.mean():.2f}, median {gg.median():.0f}, 90th pct {gg.quantile(.9):.0f}, max {gg.max()}; "
              f"{(gg == 0).mean():.1%} zero, {(gg >= 3).mean():.1%} ≥ 3 months.", "", "| gap (months) | " + " | ".join(str(int(k)) for k in dist.index) + " |", "|---|" + "---|" * len(dist),
              "| events | " + " | ".join(str(int(v)) for v in dist.values) + " |", "", "| source | n | mean gap | share zero | p90 |", "|---|---|---|---|---|"]
        for k, s in e.groupby("source"):
            L.append(f"| {k} | {len(s)} | {gg[s.index].mean():.2f} | {(gg[s.index] == 0).mean():.1%} | {gg[s.index].quantile(.9):.0f} |")
    dump("dates_gap", out); (T / "dates_gap.md").write_text("\n".join(L) + "\n")


def render_binned(rows, ds, scheme):
    df = pd.DataFrame(rows)
    L = [f"# Binned horizon table — {DS_LABEL[ds]} — bins: {scheme}", "", "Cells with n < 20 items are suppressed. CI = 95% percentile bootstrap over events (10k resamples for the primary scheme, 2k for robustness schemes). "
         "Binary rows also give the bias index (acc_original − acc_perturbed) and the event-framed AUROC of P(Yes) where both question types are present.", ""]
    for cond in sorted(df.condition.unique()) if "condition" in df else [None]:
        for tg in D.TASKS:
            for metric in S.outcome_columns(tg):
                sub = df[(df.task_group == tg) & (df.metric == metric)]
                if cond is not None:
                    sub = sub[sub.condition == cond]
                if sub.empty:
                    continue
                bins = list(dict.fromkeys(sub.bin))
                L += [f"\n## {tg} — {metric}" + (f" — condition `{cond}`" if cond else "") + "\n", "| model | " + " | ".join(bins) + " |", "|---|" + "---|" * len(bins)]
                for m in D.MODEL_ORDER:
                    r = sub[sub.model == m]
                    if r.empty:
                        continue
                    cells = []
                    for b in bins:
                        c = r[r.bin == b]
                        if c.empty or c.iloc[0].suppressed:
                            cells.append(f"n={int(c.iloc[0].n_items) if not c.empty else 0}")
                        else:
                            c = c.iloc[0]; s = f"{c['mean']:.3f} [{c.ci_lo:.3f}, {c.ci_hi:.3f}] n={int(c.n_items)} sd={c['std']:.2f}"
                            if tg == "binary_merged" and metric == "accuracy" and "bias_index" in c and pd.notna(c.get("bias_index")):
                                s += f" bias={c.bias_index:+.2f}"
                                if pd.notna(c.get("auroc")): s += f" AUROC={c.auroc:.2f}"
                            cells.append(s)
                    L.append(f"| {D.MODELS[m]['name']} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


def stage_binned(ev):
    schemes = {"primary": (D.PRIMARY_BINS, 10000), "2m": (D.BINS_2M, 2000), "6m": (D.BINS_6M, 2000)}
    for ds in DATASETS:
        df = D.load_items(ds, ev)
        for name, (bins, B) in schemes.items():
            rows = []
            for cond in sorted(df.condition.unique()):
                r = S.binned_table(df[df.condition == cond], bins, B=B)
                for x in r: x["condition"] = cond
                rows += r
            dump(f"binned_{ds}_{name}", rows)
            if name == "primary":
                (T / f"binned_{ds}.md").write_text(render_binned(rows, ds, "1–3, 4–6, 7–12, 13–24, 25+"))
            print(f"  binned {ds} {name}: {len(rows)} cells", file=sys.stderr)


def stage_trends(ev):
    allrows = []
    for ds in DATASETS:
        df = D.load_items(ds, ev)
        for cond in sorted(df.condition.unique()):
            r = S.trend_tests(df[df.condition == cond]); 
            for x in r: x["dataset"] = ds; x["condition"] = cond
            allrows += r
        print(f"  trends {ds}", file=sys.stderr)
    tested = [i for i, r in enumerate(allrows) if not r.get("skipped")]
    ph = S.holm([allrows[i]["p_boot"] for i in tested])
    for i, p in zip(tested, ph): allrows[i]["p_holm"] = p
    dump("trends", allrows)
    L = ["# Within-model horizon trends (slope of outcome on horizon, per 12 months)", "",
         "Descriptive: within a single model horizon is collinear with calendar date, so these slopes mix horizon and corpus drift. "
         "Slope = OLS per month × 12, with 95% event-bootstrap CI (10k) and two-sided bootstrap p; logistic slope (log-odds/month, event-clustered SE) as a check. "
         f"Holm–Bonferroni across the whole family of {len(tested)} tests (datasets × conditions × models × tasks × metrics); `*` = Holm p < 0.05. "
         "Models with < 100 items or < 3 months of horizon range are skipped.", ""]
    df = pd.DataFrame(allrows)
    for ds in DATASETS:
        for cond in sorted(df[df.dataset == ds].condition.unique()):
            L += [f"\n## {DS_LABEL[ds]} — `{cond}`\n", "| model | task | metric | n items | horizon | slope /12 mo [CI] | p (boot) | p (Holm) | logit slope /mo (p) |", "|---|---|---|---|---|---|---|---|---|"]
            for m in D.MODEL_ORDER:
                for r in [x for x in allrows if x["dataset"] == ds and x["condition"] == cond and x["model"] == m]:
                    if r.get("skipped"):
                        L.append(f"| {D.MODELS[m]['name']} | {r['task_group']} | — | {r['n_items']} | {r.get('h_min')}–{r.get('h_max')} | skipped ({r['reason']}) | | | |"); continue
                    star = "*" if r.get("p_holm", 1) < 0.05 else ""
                    lg = f"{r['logit_slope']:+.4f} ({r['logit_p']:.3g})" if r.get("logit_slope") == r.get("logit_slope") and "logit_slope" in r else "—"
                    L.append(f"| {D.MODELS[m]['name']} | {r['task_group']} | {r['metric']} | {r['n_items']} | {r['h_min']}–{r['h_max']} | {r['slope_per_12m']:+.3f} [{r['ci_lo_12m']:+.3f}, {r['ci_hi_12m']:+.3f}] | {r['p_boot']:.3g} | {r['p_holm']:.3g}{star} | {lg} |")
    (T / "trends.md").write_text("\n".join(L) + "\n")


def _prep(df):
    d = df.copy(); d["hy"] = (d.h - d.h.mean()) / 12.0; d["hy2"] = d.hy ** 2; d["caly"] = (d.cal_m - d.cal_m.mean()) / 12.0
    return d


def stage_pooled(ev):
    res = {}
    for ds in DATASETS:
        df = D.load_items(ds, ev); df = df[df.condition == "base"]
        res[ds] = {}
        for tg in ("binary_merged", "mcq"):
            d = _prep(df[df.task_group == tg])
            if d.model.nunique() < 3 or len(d) < 500:
                res[ds][tg] = dict(skipped=True, n=len(d), n_models=int(d.model.nunique())); continue
            r = {}
            for label, cols, slope in (("h", ["hy"], None), ("h+cal", ["hy", "caly"], None), ("h+h2", ["hy", "hy2"], None), ("h+random_slope", ["hy"], "hy")):
                try:
                    r[label] = G.fit_crossed(d, "y", cols, "binomial", random_slope_col=slope)
                except Exception as e:
                    r[label] = dict(error=str(e)[:200])
            r["event_fe_h2"] = S.event_fe_conditional(d, tg, ["h2"])
            r["event_fe_bins"] = S.event_fe_bins(d, tg)
            r["n"] = len(d); r["n_events"] = int(d.id.nunique()); r["n_models"] = int(d.model.nunique()); r["h_range"] = [int(d.h.min()), int(d.h.max())]
            res[ds][tg] = r; print(f"  pooled {ds} {tg}", file=sys.stderr)
        d = _prep(df[df.task_group == "date"])
        if d.model.nunique() >= 3 and len(d) >= 300:
            r = {}
            for metric in ("signed_err", "abs_err", "date_score"):
                r[metric] = {}
                for label, cols in (("h", ["hy"]), ("h+cal", ["hy", "caly"]), ("h+h2", ["hy", "hy2"])):
                    try:
                        r[metric][label] = G.fit_crossed(d, metric, cols, "gaussian")
                    except Exception as e:
                        r[metric][label] = dict(error=str(e)[:200])
            r["n"] = len(d); r["n_events"] = int(d.id.nunique()); r["n_models"] = int(d.model.nunique())
            res[ds]["date"] = r; print(f"  pooled {ds} date", file=sys.stderr)
    # Holm across the family of pooled horizon coefficients (model 'h', per dataset x task/metric)
    fam = []
    for ds in res:
        for tg, r in res[ds].items():
            if r.get("skipped"): continue
            if tg == "date":
                for metric in ("signed_err", "abs_err", "date_score"):
                    c = r[metric].get("h", {}).get("coef", {}).get("hy")
                    if c: fam.append((ds, tg, metric, c))
            else:
                c = r.get("h", {}).get("coef", {}).get("hy")
                if c: fam.append((ds, tg, "accuracy", c))
    from scipy.stats import norm
    ps = [2 * (1 - norm.cdf(abs(c["z"]))) for *_, c in fam]
    for (ds, tg, metric, c), p, ph in zip(fam, ps, S.holm(ps)):
        c["p"] = p; c["p_holm"] = ph
    dump("pooled", res)
    L = ["# Pooled mixed-effects results (post-cutoff, base condition)", "",
         "Crossed random intercepts for EVENT and MODEL, horizon in years (centred), Laplace-approximated GLMM (logistic for binary/MCQ, Gaussian for date metrics), "
         "fixed-effect SE from the inverse augmented Hessian. `h+cal` adds calendar month of the event (years, centred). `h+h2` adds a quadratic. "
         "`event_fe_h2` is a conditional logit stratified by event with model fixed effects; there a LINEAR horizon term is exactly collinear "
         "(h = calendar − cutoff, both absorbed), so only curvature is reported. Holm across the family of pooled linear-horizon coefficients (`h` model); `*` = Holm p < 0.05.", "",
         "**Identification note.** With one cutoff per model, horizon = calendar − cutoff. Adding calendar as a covariate leaves the linear horizon coefficient identified only "
         "through the between-model relation between cutoff date and model random intercept (nine models). Where `h+cal` moves the horizon coefficient far from the `h` fit, that is the "
         "collinearity speaking, not new information. The `h` fit answers 'does performance fall with horizon, allowing each event its own difficulty and each model its own level'; "
         "it cannot separate horizon from calendar drift. The quadratic term and the event-FE curvature ARE identified and answer the reviewer's shape question.", ""]
    for ds in DATASETS:
        L.append(f"\n## {DS_LABEL[ds]}\n")
        for tg, r in res.get(ds, {}).items():
            if r.get("skipped"):
                L.append(f"- {tg}: skipped (n={r['n']}, models={r['n_models']})"); continue
            if tg == "date":
                L += [f"### date — n={r['n']} items, {r['n_events']} events, {r['n_models']} models\n", "| metric | model | horizon coef (per year) [CI] | p / Holm | calendar coef | quadratic | event SD | model SD | resid SD |", "|---|---|---|---|---|---|---|---|---|"]
                for metric in ("signed_err", "abs_err", "date_score"):
                    for label in ("h", "h+cal", "h+h2"):
                        f = r[metric].get(label, {})
                        if "coef" not in f: L.append(f"| {metric} | {label} | error: {f.get('error')} | | | | | | |"); continue
                        c = f["coef"]; hy = c["hy"]; pp = f"{hy.get('p', float('nan')):.3g} / {hy.get('p_holm', float('nan')):.3g}{'*' if hy.get('p_holm', 1) < 0.05 else ''}" if label == "h" else "—"
                        L.append(f"| {metric} | {label} | {hy['mean']:+.3f} [{hy['ci_lo']:+.3f}, {hy['ci_hi']:+.3f}] | {pp} | {f3(c.get('caly', {}).get('mean'))} | {f3(c.get('hy2', {}).get('mean'))} | {f3(f['vc_sd'].get('event'))} | {f3(f['vc_sd'].get('model'))} | {f3(f.get('resid_sd'))} |")
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


def stage_continuous(ev):
    res = {}
    for ds in ("orig", "ext", "merged"):
        df = D.load_items(ds, ev); df = df[df.condition == "base"]; res[ds] = {}
        for tg in D.TASKS:
            for metric in S.outcome_columns(tg):
                res[ds][f"{tg}:{metric}"] = S.continuous_fit(df, tg, metric, B=500)
                print(f"  continuous {ds} {tg} {metric}", file=sys.stderr)
    dump("continuous", res)
    L = ["# Continuous horizon fits (pooled, model fixed effects, natural cubic spline with 4 df; broken-stick breakpoint search)", "",
         "Curves are for the model-average intercept; 95% band from 500 event-bootstrap refits. The broken-stick model fits `h + max(h − b, 0)` with model FE and picks b by deviance/SSE; "
         "its breakpoint CI is a 200-resample event bootstrap over a coarse grid. `bend (curvature)` is the grid month where the spline's second difference is largest. "
         "No event effects here: these fits describe the pooled shape, they do not identify horizon from calendar drift.", ""]
    for ds, r in res.items():
        L += [f"\n## {DS_LABEL[ds]}\n", "| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |", "|---|---|---|---|---|---|---|---|"]
        for k, f in r.items():
            if f.get("skipped"): L.append(f"| {k} | {f['n_items']} | skipped | | | | | |"); continue
            ls = f.get("linear_slope_logodds_per_month", f.get("linear_slope_per_month"))
            bp = f.get("stick_breakpoint"); bci = f.get("stick_breakpoint_ci")
            L.append(f"| {k} | {f['n_items']} | {f3(ls, 4)} | {bp if bp is not None else '—'} [{f3(bci[0], 0) if bci else '—'}, {f3(bci[1], 0) if bci else '—'}] | {f3(f.get('stick_slope_before'), 4)} | {f3(f.get('stick_slope_after'), 4)} | {f3(f.get('stick_vs_linear_crit_gain'), 1)} ({'deviance' if f['scale'] == 'probability' else 'SSE'}) | {f.get('bend_spline_max_curvature')} |")
    (T / "continuous.md").write_text("\n".join(L) + "\n")


def stage_ws(ev):
    from statsmodels.discrete.conditional_models import ConditionalLogit
    df = D.load_items("ws", ev)
    out = {"per_model": [], "pooled": {}}
    L = ["# Retrieval-constrained (WS+Cutoff) vs base on the pinned 500 subset, post-cutoff", "",
         "Per model: slope of outcome on horizon (per 12 months) under each condition on the SAME items, and the paired difference (event bootstrap, 10k). "
         "Pooled: conditional logit stratified by (event, model) — within a stratum only the condition varies, so `ws × horizon` is identified without any calendar confound.", "",
         "| model | task | metric | n paired items | horizon | base slope /12mo [CI] | WS+cut slope /12mo [CI] | difference (WS − base) [CI] | p |", "|---|---|---|---|---|---|---|---|---|"]
    for m in D.MODEL_ORDER:
        for tg in D.TASKS:
            b = df[(df.model == m) & (df.task_group == tg) & (df.condition == "base")]; w = df[(df.model == m) & (df.task_group == tg) & (df.condition == "ws_cutoff")]
            if b.empty or w.empty: continue
            key = ["id", "task"]; pair = b.merge(w, on=key, suffixes=("_b", "_w"))
            if len(pair) < 60 or (pair.h_b.max() - pair.h_b.min()) < 3:
                out["per_model"].append(dict(model=m, task_group=tg, n=len(pair), skipped=True)); L.append(f"| {D.MODELS[m]['name']} | {tg} | — | {len(pair)} | | too thin (n<60 or range<3) | | | |"); continue
            for metric in S.outcome_columns(tg):
                vb = (pair.y_b if metric == "accuracy" else pair[f"{metric}_b"]).to_numpy(float); vw = (pair.y_w if metric == "accuracy" else pair[f"{metric}_w"]).to_numpy(float)
                h = pair.h_b.to_numpy(float); W = S.event_weights(pair.id.to_numpy(), 10000)
                sb, sw = S.wslope(h[None, :], vb[None, :], W), S.wslope(h[None, :], vw[None, :], W); dd = sw - sb
                r = dict(model=m, task_group=tg, metric=metric, n=len(pair), h_min=int(h.min()), h_max=int(h.max()), base_slope_12m=float(12 * np.polyfit(h, vb, 1)[0]), base_ci=[12 * x for x in S.ci(sb)],
                         ws_slope_12m=float(12 * np.polyfit(h, vw, 1)[0]), ws_ci=[12 * x for x in S.ci(sw)], diff_12m=float(12 * (np.polyfit(h, vw, 1)[0] - np.polyfit(h, vb, 1)[0])), diff_ci=[12 * x for x in S.ci(dd)], p=S.boot_p(dd),
                         base_mean=float(vb.mean()), ws_mean=float(vw.mean()))
                out["per_model"].append(r)
                L.append(f"| {D.MODELS[m]['name']} | {tg} | {metric} | {len(pair)} | {r['h_min']}–{r['h_max']} | {r['base_slope_12m']:+.3f} [{r['base_ci'][0]:+.3f}, {r['base_ci'][1]:+.3f}] | {r['ws_slope_12m']:+.3f} [{r['ws_ci'][0]:+.3f}, {r['ws_ci'][1]:+.3f}] | {r['diff_12m']:+.3f} [{r['diff_ci'][0]:+.3f}, {r['diff_ci'][1]:+.3f}] | {r['p']:.3g} |")
    L += ["\n## Pooled condition × horizon interaction (stratified by event × model)\n", "| task | n strata | ws main effect (log-odds) | ws × horizon (per year) [CI] | p |", "|---|---|---|---|---|"]
    for tg in ("binary_merged", "mcq"):
        d = df[df.task_group == tg].copy(); d["stratum"] = pd.factorize(d.id + "|" + d.model + "|" + d.task)[0]
        d["ws"] = (d.condition == "ws_cutoff").astype(float); d["hy"] = (d.h - d.h.mean()) / 12.0; d["ws_h"] = d.ws * d.hy
        keep = d.groupby("stratum").y.transform(lambda s: 0 < s.sum() < len(s)); d2 = d[keep]
        try:
            X = d2[["ws", "ws_h"]].to_numpy(); r = ConditionalLogit(d2.y.to_numpy(), X, groups=d2.stratum.to_numpy()).fit(disp=0)
            out["pooled"][tg] = dict(n_strata=int(d2.stratum.nunique()), ws=float(r.params[0]), ws_se=float(r.bse[0]), ws_h=float(r.params[1]), ws_h_se=float(r.bse[1]), ws_h_p=float(r.pvalues[1]))
            L.append(f"| {tg} | {d2.stratum.nunique()} | {r.params[0]:+.3f} (se {r.bse[0]:.3f}) | {r.params[1]:+.3f} [{r.params[1] - 1.96 * r.bse[1]:+.3f}, {r.params[1] + 1.96 * r.bse[1]:+.3f}] | {r.pvalues[1]:.3g} |")
        except Exception as e:
            out["pooled"][tg] = dict(error=str(e)[:200]); L.append(f"| {tg} | error {str(e)[:60]} | | | |")
    # date: within-(event,model) difference regressed on horizon
    d = df[df.task_group == "date"]; b = d[d.condition == "base"]; w = d[d.condition == "ws_cutoff"]; pair = b.merge(w, on=["id", "model"], suffixes=("_b", "_w"))
    if len(pair) >= 60:
        import statsmodels.api as sm
        for metric in ("abs_err", "date_score", "signed_err"):
            dif = (pair[f"{metric}_w"] - pair[f"{metric}_b"]).to_numpy(float); h = pair.h_b.to_numpy(float) / 12
            X = sm.add_constant(np.column_stack([h, pd.get_dummies(pair.model, drop_first=True).astype(float).to_numpy()]))
            r = sm.OLS(dif, X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(pair.id)[0]})
            out["pooled"][f"date:{metric}"] = dict(n=len(pair), ws_h=float(r.params[1]), se=float(r.bse[1]), p=float(r.pvalues[1]), ws_mean_diff=float(dif.mean()))
            L.append(f"| date:{metric} (WS − base difference on horizon, model FE, event-clustered) | {len(pair)} | mean diff {dif.mean():+.3f} | {r.params[1]:+.3f} [{r.params[1] - 1.96 * r.bse[1]:+.3f}, {r.params[1] + 1.96 * r.bse[1]:+.3f}] | {r.pvalues[1]:.3g} |")
    dump("ws_vs_base", out); (T / "ws_vs_base.md").write_text("\n".join(L) + "\n")


def stage_null(ev):
    out = {}
    L = ["# Date task — anchoring null", "",
         "Null predictor: always predict cutoff + k months, k fitted per model on its own post-cutoff items, (a) to maximise mean exp(−0.1|Δ|), (b) to minimise mean |Δ|. "
         "Because ground truth = cutoff + horizon, the null's signed error is k − h exactly: slope −1 month per month of horizon with zero forecasting content. "
         "A third null uses k = the model's own median (prediction − cutoff): a constant predictor placed where the model typically predicts. Slopes are per month of horizon. "
         "'Share reproduced' = null(median) abs-error slope / model abs-error slope on the same items.", ""]
    for ds in ("orig", "ext", "merged"):
        df = D.load_items(ds, ev); df = df[df.condition == "base"]; out[ds] = {}
        L += [f"\n## {DS_LABEL[ds]}\n", "| model | n | model: mean (median) pred − cutoff, months | k*: max score / min abs / model median | signed-error slope: model / null(k*) / null(median) | abs-error slope: model / null(k*) / null(median) | score slope: model / null(k*) / null(median) | share of model abs-error slope reproduced by null(median) |", "|---|---|---|---|---|---|---|---|"]
        for m in D.MODEL_ORDER:
            r = S.anchoring_null(df, m); out[ds][m] = r
            if r.get("skipped"): continue
            ms = r["model_slopes"]; a = r["choices"]["max_score"]; b = r["choices"]["min_abs"]; c = r["choices"]["model_median_offset"]
            share = (c["slope_abs"] / ms["slope_abs"]) if abs(ms["slope_abs"]) > 1e-9 else float("nan")
            L.append(f"| {D.MODELS[m]['name']} | {r['n']} | {r['mean_prediction_minus_cutoff_months']:+.1f} ({r['median_prediction_minus_cutoff_months']:+.0f}) | {a['k']} / {b['k']} / {c['k']} | {ms['slope_signed']:+.2f} / {a['slope_signed']:+.2f} / {c['slope_signed']:+.2f} | {ms['slope_abs']:+.2f} / {a['slope_abs']:+.2f} / {c['slope_abs']:+.2f} | {ms['slope_score']:+.4f} / {a['slope_score']:+.4f} / {c['slope_score']:+.4f} | {share:.0%} |")
    dump("anchoring_null", out); (T / "anchoring_null.md").write_text("\n".join(L) + "\n")


def stage_sensitivity(ev):
    """DOI dates; alternative cutoffs; include h=0; bin-width dependence."""
    out = {}; L = ["# Sensitivity checks", ""]
    def slopes(df):
        r = S.trend_tests(df[df.condition == "base"], B=2000); return {(x["model"], x["task_group"], x["metric"]): x for x in r if not x.get("skipped")}
    base = {ds: slopes(D.load_items(ds, ev)) for ds in ("orig", "ext", "merged")}
    # 1. DOI dates
    L += ["## 1. DOI / journal dates instead of first-observable dates\n", "Horizon and the date-task errors recomputed against the DOI date. Sign/CI agreement of within-model slopes:", "",
          "| dataset | model | task:metric | slope first-obs /12mo [CI] | slope DOI /12mo [CI] | same sign | CI-excludes-0 agreement |", "|---|---|---|---|---|---|---|"]
    out["doi"] = []
    for ds in ("orig", "merged"):
        alt = slopes(D.load_items(ds, ev, date_field="doi_m"))
        for k, r in base[ds].items():
            a = alt.get(k)
            if not a: continue
            same = np.sign(r["slope_per_12m"]) == np.sign(a["slope_per_12m"]); sig_r = (r["ci_lo"] > 0) or (r["ci_hi"] < 0); sig_a = (a["ci_lo"] > 0) or (a["ci_hi"] < 0)
            out["doi"].append(dict(dataset=ds, model=k[0], task=k[1], metric=k[2], first=r["slope_per_12m"], doi=a["slope_per_12m"], same_sign=bool(same), sig_first=bool(sig_r), sig_doi=bool(sig_a)))
            L.append(f"| {ds} | {D.MODELS[k[0]]['name']} | {k[1]}:{k[2]} | {r['slope_per_12m']:+.3f} [{r['ci_lo_12m']:+.3f}, {r['ci_hi_12m']:+.3f}] | {a['slope_per_12m']:+.3f} [{a['ci_lo_12m']:+.3f}, {a['ci_hi_12m']:+.3f}] | {'yes' if same else 'NO'} | {'yes' if sig_r == sig_a else 'NO'} |")
    doi_rows = out["doi"]
    L.append(f"\nSummary: {sum(x['same_sign'] for x in doi_rows)}/{len(doi_rows)} slopes keep their sign; {sum(x['sig_first'] == x['sig_doi'] for x in doi_rows)}/{len(doi_rows)} keep their CI-excludes-zero status.\n")
    # pooled GLMM under DOI dates
    out["doi_pooled"] = {}
    for ds in ("orig", "merged"):
        df = D.load_items(ds, ev, date_field="doi_m"); df = df[df.condition == "base"]; out["doi_pooled"][ds] = {}
        for tg in ("binary_merged", "mcq"):
            d = _prep(df[df.task_group == tg]); r = G.fit_crossed(d, "y", ["hy"], "binomial"); out["doi_pooled"][ds][tg] = r["coef"]["hy"]
        d = _prep(df[df.task_group == "date"]); r = G.fit_crossed(d, "abs_err", ["hy"], "gaussian"); out["doi_pooled"][ds]["date:abs_err"] = r["coef"]["hy"]
    L += ["Pooled GLMM horizon coefficient (per year) under DOI dates: " + "; ".join(f"{ds} {k}: {v['mean']:+.3f} [{v['ci_lo']:+.3f}, {v['ci_hi']:+.3f}]" for ds in out["doi_pooled"] for k, v in out["doi_pooled"][ds].items()), ""]
    # 2. alternative cutoffs
    L += ["## 2. Alternative cutoffs (Claude S4.5 → 2025-07 training-data cutoff; DeepSeek R1 → 2023-12 self-reported)\n", "| dataset | model | task:metric | n (primary → alt) | slope primary /12mo [CI] | slope alt /12mo [CI] |", "|---|---|---|---|---|---|"]
    out["alt_cutoff"] = []
    altc = {m: c["cutoff_alt"] for m, c in D.MODELS.items() if c["cutoff_alt"]}
    for ds in ("orig", "merged"):
        alt = slopes(D.load_items(ds, ev, cutoffs=altc))
        for k, r in base[ds].items():
            if k[0] not in altc: continue
            a = alt.get(k)
            out["alt_cutoff"].append(dict(dataset=ds, model=k[0], task=k[1], metric=k[2], primary=r["slope_per_12m"], alt=(a["slope_per_12m"] if a else None), n_primary=r["n_items"], n_alt=(a["n_items"] if a else None)))
            L.append(f"| {ds} | {D.MODELS[k[0]]['name']} | {k[1]}:{k[2]} | {r['n_items']} → {a['n_items'] if a else '—'} | {r['slope_per_12m']:+.3f} [{r['ci_lo_12m']:+.3f}, {r['ci_hi_12m']:+.3f}] | " + (f"{a['slope_per_12m']:+.3f} [{a['ci_lo_12m']:+.3f}, {a['ci_hi_12m']:+.3f}]" if a else "skipped") + " |")
    # 3. include h = 0
    L += ["\n## 3. Including the cutoff month (h = 0) as post-cutoff\n", "| dataset | model | task:metric | n (h≥1 → h≥0) | slope h≥1 /12mo [CI] | slope h≥0 /12mo [CI] |", "|---|---|---|---|---|---|"]
    out["h0"] = []
    for ds in ("orig", "merged"):
        alt = slopes(D.load_items(ds, ev, include_h0=True))
        for k, r in base[ds].items():
            a = alt.get(k)
            if not a or a["n_items"] == r["n_items"]: continue
            out["h0"].append(dict(dataset=ds, model=k[0], task=k[1], metric=k[2], primary=r["slope_per_12m"], alt=a["slope_per_12m"], n_primary=r["n_items"], n_alt=a["n_items"]))
            L.append(f"| {ds} | {D.MODELS[k[0]]['name']} | {k[1]}:{k[2]} | {r['n_items']} → {a['n_items']} | {r['slope_per_12m']:+.3f} [{r['ci_lo_12m']:+.3f}, {r['ci_hi_12m']:+.3f}] | {a['slope_per_12m']:+.3f} [{a['ci_lo_12m']:+.3f}, {a['ci_hi_12m']:+.3f}] |")
    # 4. bin-width dependence: for each model x task, is the direction (first vs last populated bin) the same under 2m / 6m / primary?
    L += ["\n## 4. Bin-width dependence\n", "Direction = sign(last populated bin − first populated bin) among bins with n ≥ 20, per scheme (P = primary, 2 = 2-month, 6 = 6-month); "
          "`monotone` = fraction of adjacent populated-bin steps that move in the direction of the overall slope.", "", "| dataset | model | task:metric | P: first→last (dir) | 2m | 6m | agree |", "|---|---|---|---|---|---|---|"]
    out["bins"] = []
    for ds in ("orig", "ext", "merged"):
        tabs = {s: pd.DataFrame(json.load(open(T / f"binned_{ds}_{s}.json"))) for s in ("primary", "2m", "6m")}
        for (m, tg, metric) in sorted({(r.model, r.task_group, r.metric) for r in tabs["primary"].itertuples()}):
            res = {}
            for s, t in tabs.items():
                x = t[(t.model == m) & (t.task_group == tg) & (t.metric == metric) & (t.condition == "base") & (~t.suppressed)].sort_values("bin_lo")
                if len(x) < 2: res[s] = None; continue
                d = float(x["mean"].iloc[-1] - x["mean"].iloc[0]); steps = np.diff(x["mean"].to_numpy()); mono = float((np.sign(steps) == np.sign(d)).mean()) if d != 0 else float("nan")
                res[s] = dict(delta=d, dir=int(np.sign(d)), n_bins=len(x), monotone=mono)
            if res["primary"] is None: continue
            dirs = [v["dir"] for v in res.values() if v]
            agree = len(set(dirs)) == 1
            out["bins"].append(dict(dataset=ds, model=m, task=tg, metric=metric, schemes=res, agree=agree))
            fmt = lambda v: "—" if v is None else f"{v['delta']:+.3f} ({'+' if v['dir'] > 0 else '−'}, {v['n_bins']} bins, mono {v['monotone']:.2f})"
            L.append(f"| {ds} | {D.MODELS[m]['name']} | {tg}:{metric} | {fmt(res['primary'])} | {fmt(res['2m'])} | {fmt(res['6m'])} | {'yes' if agree else 'NO'} |")
    L.append(f"\nSummary: direction agrees across all three bin schemes in {sum(x['agree'] for x in out['bins'])}/{len(out['bins'])} model × task × metric × dataset cells.\n")
    dump("sensitivity", out); (T / "sensitivity.md").write_text("\n".join(L) + "\n")


STAGES = dict(counts=stage_counts, dates=stage_dates, binned=stage_binned, trends=stage_trends, pooled=stage_pooled, continuous=stage_continuous, ws=stage_ws, null=stage_null, sensitivity=stage_sensitivity)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="all"); a = ap.parse_args()
    ev = D.load_events()
    for name, fn in STAGES.items():
        if a.stage in ("all", name):
            t = time.time(); print(f"== {name}", file=sys.stderr); fn(ev); print(f"== {name} done in {time.time() - t:.0f}s", file=sys.stderr)
