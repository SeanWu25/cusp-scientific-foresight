"""
binned_coef.py — the reviewer-4 model with horizon entered as BIN DUMMIES.

    g(E[Y_imc]) = b0 + sum_b beta_b 1[H_im in b] + beta2 R_c + sum_b beta3_b 1[H_im in b] R_c + u_i + v_m

Two bin schemes (1-month, 3-month), reference bin = the shortest. Two settings:

  base  : R absent (base condition only), datasets orig and merged, four tasks.
          Estimator 1: crossed random intercepts (event, model), Laplace GLMM —
          the equation as written.
          Estimator 2: conditional logit stratified by event with model fixed
          effects (binary/MCQ) or event-demeaned OLS with model FE and
          event-clustered SE (date/FRQ) — the bin contrasts are identified
          there without the random-effects assumption; a LINEAR horizon term
          would not be (h = calendar − cutoff), which is why bins are the
          right way to ask this question.
  ws    : base vs WS+Cutoff on the pinned 500 subset, same items under both
          conditions. Estimator 1: the full equation with R and bin × R via the
          crossed GLMM. Estimator 2: stratified by (event, model, question) so
          only the condition varies within a stratum — conditional logit for
          binary/MCQ, paired-difference OLS for date/FRQ.

Every fit reports per-bin coefficients with 95% CI, the bin n, and an
approximate likelihood-ratio (GLMM, Laplace) or Wald (stratified) omnibus test
that the bin block is zero. Post-cutoff only (asserted in data.load_items).

  python horizon_study/binned_coef.py            # ~10 min
"""
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats as sps
sys.path.insert(0, str(Path(__file__).resolve().parent))
import data as D, glmm as G  # noqa: E402
warnings.filterwarnings("ignore")

T = D.STUDY / "tables"; F = D.STUDY / "figures"; F.mkdir(exist_ok=True)
SCHEMES = {"3m": [(k, k + 2) for k in range(1, 37, 3)], "1m": [(k, k) for k in range(1, 37)]}
MIN_BIN = 30                 # a bin with fewer items than this is pooled into its neighbour above
OUTCOMES = {"binary_merged": [("y", "binomial")], "mcq": [("y", "binomial")],
            "date": [("signed_err", "gaussian"), ("abs_err", "gaussian"), ("date_score", "gaussian")],
            "frq": [("frq_score", "gaussian")]}


def label(lo, hi):
    return f"{lo}" if lo == hi else f"{lo}–{hi}"


def make_bins(d, scheme):
    """Assign bins, pooling sparse ones upward so every bin has >= MIN_BIN items."""
    bins = [b for b in SCHEMES[scheme] if b[0] <= d.h.max()]
    counts = [int(((d.h >= lo) & (d.h <= hi)).sum()) for lo, hi in bins]
    merged = []
    for (lo, hi), c in zip(bins, counts):
        if merged and merged[-1][2] < MIN_BIN:
            plo, _, pc = merged[-1]; merged[-1] = (plo, hi, pc + c)
        else:
            merged.append((lo, hi, c))
    if len(merged) > 1 and merged[-1][2] < MIN_BIN:
        (lo1, _, c1), (lo2, hi2, c2) = merged[-2], merged[-1]; merged[-2:] = [(lo1, hi2, c1 + c2)]
    edges = [(lo, hi) for lo, hi, _ in merged]
    lab = pd.Series(pd.NA, index=d.index, dtype="object")
    for lo, hi in edges:
        lab[(d.h >= lo) & (d.h <= hi)] = label(lo, hi)
    return lab, [label(lo, hi) for lo, hi in edges]


def dummies(lab, labs):
    X = pd.get_dummies(pd.Categorical(lab, categories=labs), drop_first=True).astype(float)
    X.columns = [f"bin_{c}" for c in X.columns]
    return X


def lr_p(l1, l0, df):
    """Laplace-likelihood LR. A negative LR means the larger model's optimiser stopped at a
    worse point than the smaller model's; the p is then reported as NaN, not 1."""
    lr = 2 * (l1 - l0)
    if lr < -1e-6 or df <= 0:
        return float(lr), float("nan")
    return float(lr), float(sps.chi2.sf(lr, df))


# ----------------------------------------------------------------------------- base condition
def base_glmm(d, ycol, family, lab, labs):
    X = dummies(lab, labs); dd = pd.concat([d, X], axis=1)
    r1 = G.fit_crossed(dd, ycol, list(X.columns), family)
    r0 = G.fit_crossed(dd, ycol, [], family)
    lr, p = lr_p(r1["laplace_loglik"], r0["laplace_loglik"], X.shape[1])
    coef = {labs[0]: dict(mean=0.0, ci_lo=0.0, ci_hi=0.0, n=int((lab == labs[0]).sum()), ref=True)}
    for c in X.columns:
        b = c[4:]; coef[b] = dict(**{k: r1["coef"][c][k] for k in ("mean", "sd", "ci_lo", "ci_hi")}, n=int((lab == b).sum()))
    return dict(method="crossed RE GLMM (event, model)", coef=coef, lr=lr, lr_df=X.shape[1], lr_p=p,
                vc_sd=r1["vc_sd"], converged=r1["converged"], n=len(d))


def base_stratified(d, ycol, family, lab, labs):
    """Event FE + model FE. Logistic: conditional logit by event. Gaussian: within-event
    demeaned OLS, model FE, event-clustered SE."""
    X = dummies(lab, labs)
    M = pd.get_dummies(d.model, prefix="m", drop_first=True).astype(float)
    if family == "binomial":
        from statsmodels.discrete.conditional_models import ConditionalLogit
        keep = d.groupby("id")[ycol].transform(lambda s: 0 < s.sum() < len(s))
        XX = pd.concat([X, M], axis=1)[keep]; XX = XX.loc[:, XX.std() > 0]
        mod = ConditionalLogit(d[ycol][keep].to_numpy(), XX.to_numpy(), groups=pd.factorize(d.id[keep])[0]); r = mod.fit(method="newton", maxiter=300, disp=0)
        names = list(XX.columns); params, bse, cov = r.params, r.bse, r.cov_params()
        n_used = int(keep.sum()); method = "conditional logit by event + model FE"
        conv = bool(np.abs(mod.score(r.params)).max() < 1e-3); rank_ok = bool(np.all(np.isfinite(np.asarray(bse))))
    else:
        import statsmodels.api as sm
        XX = pd.concat([X, M], axis=1)
        y = d[ycol].to_numpy(float); g = pd.factorize(d.id)[0]
        # within-event demeaning of y and X (event fixed effects), then OLS with cluster-robust SE by event
        def dm(a):
            a = np.asarray(a, float); out = a.copy()
            for col in range(a.shape[1] if a.ndim == 2 else 1):
                v = a[:, col] if a.ndim == 2 else a
                m = pd.Series(v).groupby(g).transform("mean").to_numpy()
                if a.ndim == 2: out[:, col] = v - m
                else: out = v - m
            return out
        Xd = dm(XX.to_numpy()); yd = dm(y)
        keepc = Xd.std(axis=0) > 1e-9; names = [c for c, k in zip(XX.columns, keepc) if k]
        r = sm.OLS(yd, Xd[:, keepc]).fit(cov_type="cluster", cov_kwds={"groups": g})
        params, bse, cov = r.params, r.bse, r.cov_params(); n_used = len(d); method = "event-demeaned OLS + model FE, event-clustered SE"
        conv = True; rank_ok = int(np.linalg.matrix_rank(Xd[:, keepc])) == int(keepc.sum())
    coef = {labs[0]: dict(mean=0.0, ci_lo=0.0, ci_hi=0.0, n=int((lab == labs[0]).sum()), ref=True)}
    idx = [i for i, nm in enumerate(names) if nm.startswith("bin_")]
    for i in idx:
        b = names[i][4:]
        coef[b] = dict(mean=float(params[i]), sd=float(bse[i]), ci_lo=float(params[i] - 1.96 * bse[i]), ci_hi=float(params[i] + 1.96 * bse[i]), n=int((lab == b).sum()))
    # joint Wald on the bin block
    bidx = np.array(idx); cb = np.asarray(cov)[np.ix_(bidx, bidx)]; pb = np.asarray(params)[bidx]
    try:
        w = float(pb @ np.linalg.solve(cb, pb)); wp = float(sps.chi2.sf(w, len(bidx)))
    except Exception:
        w, wp = float("nan"), float("nan")
    if not (conv and rank_ok):
        w, wp = float("nan"), float("nan")
    return dict(method=method, coef=coef, wald=w, wald_df=len(idx), wald_p=wp, n=n_used, converged=conv, full_rank=rank_ok,
                note=None if (conv and rank_ok) else ("optimizer did not converge" if not conv else "design rank-deficient: with event FE, bin membership varies only through the model's cutoff, and 1-month bins are too fine for ten cutoffs"))


# ----------------------------------------------------------------------------- ws condition
def ws_glmm(d, ycol, family, lab, labs):
    X = dummies(lab, labs); ws = (d.condition == "ws_cutoff").astype(float).rename("ws")
    XI = X.mul(ws, axis=0); XI.columns = [f"wsx_{c[4:]}" for c in X.columns]
    dd = pd.concat([d, X, ws, XI], axis=1)
    full = G.fit_crossed(dd, ycol, list(X.columns) + ["ws"] + list(XI.columns), family)
    noint = G.fit_crossed(dd, ycol, list(X.columns) + ["ws"], family)
    lr, p = lr_p(full["laplace_loglik"], noint["laplace_loglik"], XI.shape[1])
    out = dict(method="crossed RE GLMM (event, model), full equation", ws_main=full["coef"]["ws"],
               ws_main_no_interaction=noint["coef"]["ws"], lr_interaction=lr, lr_df=XI.shape[1], lr_p=p, n=len(d), coef={})
    out["coef"][labs[0]] = dict(bin=full["coef"]["intercept"], ws_x_bin=dict(mean=0.0, ci_lo=0.0, ci_hi=0.0), ws_effect=full["coef"]["ws"],
                                n=int((lab == labs[0]).sum()) // 2, ref=True)
    for c in X.columns:
        b = c[4:]; wi = full["coef"][f"wsx_{b}"]; wm = full["coef"]["ws"]
        out["coef"][b] = dict(bin=full["coef"][c], ws_x_bin=wi, n=int((lab == b).sum()) // 2,
                              ws_effect=dict(mean=wm["mean"] + wi["mean"]))
    return out


def ws_stratified(d, ycol, family, lab, labs):
    X = dummies(lab, labs); ws = (d.condition == "ws_cutoff").astype(float)
    if family == "binomial":
        from statsmodels.discrete.conditional_models import ConditionalLogit
        strat = pd.factorize(d.id + "|" + d.model + "|" + d.task.astype(str))[0]
        keep = pd.Series(d[ycol].to_numpy()).groupby(strat).transform(lambda s: 0 < s.sum() < len(s)).to_numpy().astype(bool)
        XI = X.mul(ws, axis=0); XI.columns = [f"wsx_{c[4:]}" for c in X.columns]
        XX = pd.concat([ws.rename("ws"), XI], axis=1)[keep]; XX = XX.loc[:, XX.std() > 0]
        mod = ConditionalLogit(d[ycol][keep].to_numpy(), XX.to_numpy(), groups=strat[keep]); r = mod.fit(method="newton", maxiter=300, disp=0)
        names = list(XX.columns); params, bse, cov = np.asarray(r.params), np.asarray(r.bse), np.asarray(r.cov_params())
        method = "conditional logit stratified by (event, model, question)"; n_used = int(keep.sum()); conv = bool(np.abs(mod.score(r.params)).max() < 1e-3)
    else:
        import statsmodels.api as sm
        b = d[d.condition == "base"]; w = d[d.condition == "ws_cutoff"]
        pair = b.merge(w, on=["id", "model", "task"], suffixes=("_b", "_w"))
        lab_p = lab.loc[b.index].to_numpy(); labp = pd.Series(lab_p, index=b.index).loc[pair.index] if False else None
        pair = b.reset_index().merge(w, on=["id", "model", "task"], suffixes=("_b", "_w"))
        labp = lab.loc[pair["index"]].reset_index(drop=True)
        Xp = dummies(labp, labs); Xp.columns = [f"wsx_{c[4:]}" for c in Xp.columns]
        M = pd.get_dummies(pair.model, prefix="m", drop_first=True).astype(float)
        XX = pd.concat([pd.Series(1.0, index=Xp.index, name="ws"), Xp, M], axis=1); XX = XX.loc[:, (XX.std() > 0) | (XX.columns == "ws")]
        dif = (pair[f"{ycol}_w"] - pair[f"{ycol}_b"]).to_numpy(float)
        r = sm.OLS(dif, XX.to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(pair.id)[0]})
        names = list(XX.columns); params, bse, cov = np.asarray(r.params), np.asarray(r.bse), np.asarray(r.cov_params())
        method = "paired difference (WS − base) OLS, model FE, event-clustered SE"; n_used = len(pair); conv = True
    out = dict(method=method, n=n_used, coef={}, converged=conv, note=None if conv else "optimizer did not converge")
    i0 = names.index("ws"); out["ws_main"] = dict(mean=float(params[i0]), sd=float(bse[i0]), ci_lo=float(params[i0] - 1.96 * bse[i0]), ci_hi=float(params[i0] + 1.96 * bse[i0]))
    out["coef"][labs[0]] = dict(ws_x_bin=dict(mean=0.0, ci_lo=0.0, ci_hi=0.0), ws_effect=out["ws_main"], n=int((lab == labs[0]).sum()) // 2, ref=True)
    idx = [i for i, nm in enumerate(names) if nm.startswith("wsx_")]
    for i in idx:
        bname = names[i][4:]; m_, s_ = float(params[i]), float(bse[i])
        v = cov[i0, i0] + cov[i, i] + 2 * cov[i0, i]
        out["coef"][bname] = dict(ws_x_bin=dict(mean=m_, sd=s_, ci_lo=m_ - 1.96 * s_, ci_hi=m_ + 1.96 * s_), n=int((lab == bname).sum()) // 2,
                                  ws_effect=dict(mean=float(params[i0] + m_), ci_lo=float(params[i0] + m_ - 1.96 * np.sqrt(v)), ci_hi=float(params[i0] + m_ + 1.96 * np.sqrt(v))))
    if idx:
        bidx = np.array(idx); cb = cov[np.ix_(bidx, bidx)]; pb = params[bidx]
        try:
            wv = float(pb @ np.linalg.solve(cb, pb)); out["wald_interaction"] = wv; out["wald_df"] = len(idx); out["wald_p"] = float(sps.chi2.sf(wv, len(idx)))
        except Exception:
            out["wald_interaction"] = float("nan"); out["wald_p"] = float("nan")
    return out


# ----------------------------------------------------------------------------- driver
def run():
    ev = D.load_events(); out = {"base": {}, "ws": {}, "schemes": SCHEMES, "min_bin": MIN_BIN}
    for ds in ("orig", "merged"):
        df = D.load_items(ds, ev); df = df[df.condition == "base"]; out["base"][ds] = {}
        for tg, outs in OUTCOMES.items():
            d0 = df[df.task_group == tg].reset_index(drop=True)
            for ycol, fam in outs:
                d = d0[d0[ycol].notna()].reset_index(drop=True)
                for scheme in SCHEMES:
                    lab, labs = make_bins(d, scheme)
                    key = f"{tg}:{ycol}:{scheme}"
                    try:
                        g = base_glmm(d, ycol, fam, lab, labs)
                    except Exception as e:
                        g = dict(error=str(e)[:200])
                    try:
                        s = base_stratified(d, ycol, fam, lab, labs)
                    except Exception as e:
                        s = dict(error=str(e)[:200])
                    out["base"][ds][key] = dict(task=tg, outcome=ycol, scheme=scheme, bins=labs, n=len(d), n_events=int(d.id.nunique()),
                                                n_models=int(d.model.nunique()), glmm=g, stratified=s)
                    print(f"base {ds} {key} n={len(d)} bins={len(labs)} glmm_p={g.get('lr_p', float('nan')):.3g} strat_p={s.get('wald_p', float('nan')):.3g}", file=sys.stderr, flush=True)
    df = D.load_items("ws", ev)
    # keep only items present under BOTH conditions for the same model
    both = df.groupby(["id", "model", "task"]).condition.transform("nunique") == 2; df = df[both]
    for tg, outs in OUTCOMES.items():
        d0 = df[df.task_group == tg].reset_index(drop=True)
        for ycol, fam in outs:
            d = d0[d0[ycol].notna()].reset_index(drop=True)
            for scheme in SCHEMES:
                lab, labs = make_bins(d, scheme)
                key = f"{tg}:{ycol}:{scheme}"
                try:
                    g = ws_glmm(d, ycol, fam, lab, labs)
                except Exception as e:
                    g = dict(error=str(e)[:200])
                try:
                    s = ws_stratified(d, ycol, fam, lab, labs)
                except Exception as e:
                    s = dict(error=str(e)[:200])
                out["ws"][key] = dict(task=tg, outcome=ycol, scheme=scheme, bins=labs, n=len(d), n_pairs=len(d) // 2, n_events=int(d.id.nunique()),
                                      n_models=int(d.model.nunique()), glmm=g, stratified=s)
                print(f"ws {key} n_pairs={len(d)//2} bins={len(labs)} glmm_int_p={g.get('lr_p', float('nan')):.3g} strat_int_p={s.get('wald_p', float('nan')):.3g}", file=sys.stderr, flush=True)
    (T / "binned_coef.json").write_text(json.dumps(out, indent=1, default=float))
    write_md(out); figures(out)


def fmt(c, dec=3):
    if c is None: return "—"
    if c.get("ref"): return "0 (ref)"
    return f"{c['mean']:+.{dec}f} [{c['ci_lo']:+.{dec}f}, {c['ci_hi']:+.{dec}f}]"


UNIT = {"y": "log-odds", "signed_err": "months", "abs_err": "months", "date_score": "score", "frq_score": "points (0–10)"}


def write_md(out):
    L = ["# Horizon entered as bin dummies — coefficients of the reviewer-4 model", "",
         "`g(E[Y_imc]) = β0 + Σ_b β_b·1[H_im ∈ b] + β2·R_c + Σ_b β3_b·1[H_im ∈ b]·R_c + u_i + v_m`, reference bin = the shortest horizon. "
         "Bins with fewer than %d items are pooled upward, so the last bin can be wider than the scheme. Post-cutoff only." % MIN_BIN, "",
         "Two estimators per fit. **GLMM** = the equation as written (crossed random intercepts for event and model, Laplace). "
         "**Stratified** = event fixed effects + model fixed effects (conditional logit for binary/MCQ; event-demeaned OLS with event-clustered SE for date/FRQ), "
         "which identifies the bin contrasts without the random-effects assumption. Omnibus: GLMM likelihood-ratio (Laplace, approximate) or stratified Wald that the bin block is zero.", "",
         "Reading rule: the *pattern* across bins is the identified quantity. Because h = calendar − cutoff, a smooth linear drift across bins cannot be separated from calendar drift by either estimator; "
         "departures from linearity (a knee, a plateau, a collapse) can.", ""]
    for ds, lab_ in (("orig", "Original corpus (Jan 2024–Mar 2026)"), ("merged", "Original + extension (to Aug 2026)")):
        L += [f"\n## Base performance — {lab_}\n"]
        for key, r in out["base"][ds].items():
            g, s = r["glmm"], r["stratified"]
            L += [f"### {r['task']} · {r['outcome']} · {r['scheme']} bins — n={r['n']:,} items, {r['n_events']:,} events, {r['n_models']} models",
                  "", f"Omnibus: GLMM LR χ²({g.get('lr_df','')}) = {g.get('lr', float('nan')):.1f}, p = {g.get('lr_p', float('nan')):.3g}; "
                  f"stratified Wald χ²({s.get('wald_df','')}) = {s.get('wald', float('nan')):.1f}, p = {s.get('wald_p', float('nan')):.3g}. Units: {UNIT[r['outcome']]} vs reference bin."
                  + (f" **Stratified estimator: {s['note']}; its cells below are not interpretable.**" if s.get("note") else "")
                  + (" *(GLMM LR negative: optimizer artefact, p not reported.)*" if g.get("lr", 0) < -1e-6 else ""), "",
                  "| horizon (months) | n | GLMM β_b [95% CI] | stratified β_b [95% CI] |", "|---|---|---|---|"]
            for b in r["bins"]:
                gc, sc = (g.get("coef") or {}).get(b), (s.get("coef") or {}).get(b)
                L.append(f"| {b} | {(gc or sc or {}).get('n', '')} | {fmt(gc)} | {fmt(sc)} |")
            L.append("")
    L += ["\n## Base vs WS+Cutoff — pinned 500 subset, same items under both conditions\n",
          "`ws effect in bin b` = β2 + β3_b: the retrieval effect at that horizon. `β3_b` is its change relative to the reference bin. Omnibus tests the interaction block (all β3_b = 0).", ""]
    for key, r in out["ws"].items():
        g, s = r["glmm"], r["stratified"]
        L += [f"### {r['task']} · {r['outcome']} · {r['scheme']} bins — {r['n_pairs']:,} paired items, {r['n_events']:,} events, {r['n_models']} models", "",
              f"WS main effect (reference bin): GLMM {fmt(g.get('ws_main'))}; stratified {fmt(s.get('ws_main'))}. "
              f"Interaction omnibus: GLMM LR p = {g.get('lr_p', float('nan')):.3g}; stratified Wald p = {s.get('wald_p', float('nan')):.3g}. Units: {UNIT[r['outcome']]}."
              + (f" **Stratified estimator: {s['note']}.**" if s.get("note") else "")
              + (" *(GLMM LR negative: optimizer artefact, p not reported.)*" if g.get("lr_interaction", 0) < -1e-6 else ""), "",
              "| horizon (months) | n pairs | GLMM β3_b [CI] | GLMM ws effect | stratified β3_b [CI] | stratified ws effect [CI] |", "|---|---|---|---|---|---|"]
        for b in r["bins"]:
            gc, sc = (g.get("coef") or {}).get(b), (s.get("coef") or {}).get(b)
            L.append(f"| {b} | {(gc or sc or {}).get('n', '')} | {fmt((gc or {}).get('ws_x_bin'))} | {(gc or {}).get('ws_effect', {}).get('mean', float('nan')):+.3f} | {fmt((sc or {}).get('ws_x_bin'))} | {fmt((sc or {}).get('ws_effect'))} |")
        L.append("")
    (T / "binned_coef.md").write_text("\n".join(L) + "\n")


def _mid(b):
    p = b.split("–"); return (int(p[0]) + int(p[-1])) / 2


def figures(out):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    for ds in ("orig", "merged"):
        for scheme in SCHEMES:
            keys = [k for k in out["base"][ds] if k.endswith(f":{scheme}")]
            fig, axes = plt.subplots(1, len(keys), figsize=(3.6 * len(keys), 3.6))
            for ax, k in zip(np.atleast_1d(axes), keys):
                r = out["base"][ds][k]
                for est, col, off in (("glmm", "#1f77b4", -0.15), ("stratified", "#d62728", 0.15)):
                    c = r[est].get("coef")
                    if not c: continue
                    xs = [_mid(b) + off for b in r["bins"]]; ys = [c[b]["mean"] for b in r["bins"]]
                    lo = [c[b]["mean"] - c[b]["ci_lo"] for b in r["bins"]]; hi = [c[b]["ci_hi"] - c[b]["mean"] for b in r["bins"]]
                    ax.errorbar(xs, ys, yerr=[lo, hi], fmt="o-", ms=3, lw=1, capsize=2, color=col, label=est)
                ax.axhline(0, color="grey", lw=0.8, ls=":"); ax.set_title(f"{r['task']} · {r['outcome']}", fontsize=9); ax.set_xlabel("horizon (months)", fontsize=8)
                ax.tick_params(labelsize=7)
            np.atleast_1d(axes)[0].set_ylabel("β_b vs shortest bin", fontsize=8); np.atleast_1d(axes)[0].legend(fontsize=7, frameon=False)
            fig.suptitle(f"Base, {ds}, {scheme} bins", fontsize=10); fig.tight_layout(); fig.savefig(F / f"binned_coef_base_{ds}_{scheme}.png", dpi=150); plt.close(fig)
    for scheme in SCHEMES:
        keys = [k for k in out["ws"] if k.endswith(f":{scheme}")]
        fig, axes = plt.subplots(1, len(keys), figsize=(3.6 * len(keys), 3.6))
        for ax, k in zip(np.atleast_1d(axes), keys):
            r = out["ws"][k]
            for est, col, off in (("glmm", "#1f77b4", -0.15), ("stratified", "#d62728", 0.15)):
                c = r[est].get("coef")
                if not c: continue
                xs = [_mid(b) + off for b in r["bins"]]; ys = [c[b]["ws_effect"]["mean"] for b in r["bins"]]
                if est == "stratified":
                    lo = [c[b]["ws_effect"]["mean"] - c[b]["ws_effect"]["ci_lo"] for b in r["bins"]]; hi = [c[b]["ws_effect"]["ci_hi"] - c[b]["ws_effect"]["mean"] for b in r["bins"]]
                    ax.errorbar(xs, ys, yerr=[lo, hi], fmt="o-", ms=3, lw=1, capsize=2, color=col, label=est)
                else:
                    ax.plot(xs, ys, "s--", ms=3, lw=1, color=col, label=est)
            ax.axhline(0, color="grey", lw=0.8, ls=":"); ax.set_title(f"{r['task']} · {r['outcome']}", fontsize=9); ax.set_xlabel("horizon (months)", fontsize=8); ax.tick_params(labelsize=7)
        np.atleast_1d(axes)[0].set_ylabel("WS+Cutoff − base effect (β2 + β3_b)", fontsize=8); np.atleast_1d(axes)[0].legend(fontsize=7, frameon=False)
        fig.suptitle(f"Retrieval effect by horizon bin, pinned 500, {scheme} bins", fontsize=10); fig.tight_layout(); fig.savefig(F / f"binned_coef_ws_{scheme}.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    run()
