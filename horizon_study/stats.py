"""stats.py — bootstrap, binned summaries, trend tests, pooled models, continuous fits, anchoring null."""
from __future__ import annotations
import math, sys, warnings
import numpy as np
import pandas as pd
from data import PRIMARY_BINS, assign_bin, bin_label

warnings.filterwarnings("ignore")
B_DEFAULT = 10000


# ----------------------------------------------------------------------------- bootstrap machinery
def event_weights(ids: np.ndarray, B: int, seed: int = 0):
    """Cluster (event-level) multinomial resample weights, shape (B, n_items)."""
    u, inv = np.unique(ids, return_inverse=True)
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(len(u), np.full(len(u), 1 / len(u)), size=B)
    return counts[:, inv].astype(float)


def wmean(x, w):
    return (w * x).sum(1) / w.sum(1)


def ci(v, lo=2.5, hi=97.5):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return (float(np.percentile(v, lo)), float(np.percentile(v, hi))) if v.size else (float("nan"), float("nan"))


def boot_p(d):
    d = np.asarray(d, float); d = d[np.isfinite(d)]
    if d.size == 0:
        return float("nan")
    return float(min(1.0, 2 * min(((d <= 0).sum() + 1) / (d.size + 1), ((d >= 0).sum() + 1) / (d.size + 1))))


def holm(p: list[float]) -> list[float]:
    idx = [i for i, v in enumerate(p) if v == v]; m = len(idx); out = [float("nan")] * len(p)
    run = 0.0
    for rank, i in enumerate(sorted(idx, key=lambda i: p[i])):
        run = max(run, min(1.0, (m - rank) * p[i])); out[i] = run
    return out


def wslope(x, y, w):
    """Weighted OLS slope of y on x, vectorised over weight rows."""
    xm = wmean(x, w); ym = wmean(y, w)
    cov = (w * (x - xm[:, None]) * (y - ym[:, None])).sum(1); var = (w * (x - xm[:, None]) ** 2).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return cov / var


def auroc(s, y):
    s = np.asarray(s, float); y = np.asarray(y, float)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    return float((np.sum(pos[:, None] > neg[None, :]) + 0.5 * np.sum(pos[:, None] == neg[None, :])) / (len(pos) * len(neg)))


# ----------------------------------------------------------------------------- metric extraction
def outcome_columns(task_group: str) -> list[str]:
    return {"binary_merged": ["accuracy"], "mcq": ["accuracy"], "date": ["signed_err", "abs_err", "date_score"]}[task_group]


def metric_series(df: pd.DataFrame, task_group: str, metric: str) -> pd.Series:
    if metric == "accuracy":
        return df.y.astype(float)
    return df[metric].astype(float)


# ----------------------------------------------------------------------------- binned tables
def binned_table(df: pd.DataFrame, bins, B=B_DEFAULT, min_n=20, seed=0) -> list[dict]:
    """Per model x task_group x bin: n_items, n_events, mean, std, CI; plus bias index / AUROC for binary."""
    rows = []
    for (model, tg), g in df.groupby(["model", "task_group"]):
        g = g.assign(bin=g.h.map(lambda h: assign_bin(int(h), bins)))
        for metric in outcome_columns(tg):
            for lo, hi in bins:
                lab = bin_label(lo, hi); s = g[g.bin == lab]
                row = dict(model=model, task_group=tg, metric=metric, bin=lab, bin_lo=lo, bin_hi=hi,
                           n_items=len(s), n_events=s.id.nunique(), h_mean=(float(s.h.mean()) if len(s) else float("nan")))
                if len(s) < min_n:
                    row.update(suppressed=True, mean=float("nan"), std=float("nan"), ci_lo=float("nan"), ci_hi=float("nan"))
                else:
                    v = metric_series(s, tg, metric).to_numpy(); w = event_weights(s.id.to_numpy(), B, seed)
                    bm = wmean(v[None, :], w)
                    row.update(suppressed=False, mean=float(v.mean()), std=float(v.std(ddof=1)), ci_lo=ci(bm)[0], ci_hi=ci(bm)[1])
                    if tg == "binary_merged":
                        b, p = s[s.task == "binary"], s[s.task == "binary_perturbed"]
                        if len(b) >= min_n and len(p) >= min_n:
                            wb, wp = event_weights(b.id.to_numpy(), B, seed), event_weights(p.id.to_numpy(), B, seed)
                            bi = wmean(b.y.to_numpy(float)[None, :], wb) - wmean(p.y.to_numpy(float)[None, :], wp)
                            row.update(bias_index=float(b.y.mean() - p.y.mean()), bias_ci_lo=ci(bi)[0], bias_ci_hi=ci(bi)[1],
                                       n_binary=len(b), n_perturbed=len(p))
                        pp = s[s.p_yes.notna()]
                        if len(pp) >= min_n and pp.task.nunique() == 2:
                            row["auroc"] = auroc(pp.p_yes.to_numpy(), (pp.task == "binary").to_numpy(float))
                            row["n_auroc"] = len(pp)
                rows.append(row)
    return rows


# ----------------------------------------------------------------------------- per-model trend tests
def trend_tests(df: pd.DataFrame, B=B_DEFAULT, seed=0, min_n=100, min_range=3) -> list[dict]:
    """Within-model OLS slope of each outcome on horizon (per month), event-bootstrap CI + p; logistic check."""
    import statsmodels.api as sm
    rows = []
    for (model, tg), g in df.groupby(["model", "task_group"]):
        if len(g) < min_n or (g.h.max() - g.h.min()) < min_range:
            rows.append(dict(model=model, task_group=tg, n_items=len(g), n_events=g.id.nunique(), h_min=int(g.h.min()), h_max=int(g.h.max()),
                             skipped=True, reason="n<100 or horizon range<3 months"))
            continue
        for metric in outcome_columns(tg):
            v = metric_series(g, tg, metric).to_numpy(); h = g.h.to_numpy(float)
            w = event_weights(g.id.to_numpy(), B, seed); sl = wslope(h[None, :], v[None, :], w)
            row = dict(model=model, task_group=tg, metric=metric, n_items=len(g), n_events=g.id.nunique(), h_min=int(h.min()), h_max=int(h.max()),
                       skipped=False, slope_per_month=float(np.polyfit(h, v, 1)[0]), ci_lo=ci(sl)[0], ci_hi=ci(sl)[1], p_boot=boot_p(sl),
                       slope_per_12m=float(12 * np.polyfit(h, v, 1)[0]), ci_lo_12m=12 * ci(sl)[0], ci_hi_12m=12 * ci(sl)[1])
            if metric == "accuracy":
                try:
                    X = sm.add_constant(h); fit = sm.Logit(v, X).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(g.id)[0]})
                    row.update(logit_slope=float(fit.params[1]), logit_se=float(fit.bse[1]), logit_p=float(fit.pvalues[1]))
                except Exception as e:
                    row.update(logit_slope=float("nan"), logit_error=str(e)[:80])
            rows.append(row)
    return rows


# ----------------------------------------------------------------------------- pooled models
def _design(df: pd.DataFrame, terms: list[str], model_fe: bool):
    X = pd.DataFrame(index=df.index)
    hc = (df.h - df.h.mean()) / 12.0                     # horizon in YEARS, centred
    cc = (df.cal_m - df.cal_m.mean()) / 12.0             # calendar in years, centred
    if "h" in terms: X["h_years"] = hc
    if "h2" in terms: X["h_years_sq"] = hc ** 2
    if "cal" in terms: X["cal_years"] = cc
    if model_fe:
        d = pd.get_dummies(df.model, prefix="m", drop_first=True).astype(float); X = pd.concat([X, d], axis=1)
    return X


def pooled_re_glmm(df: pd.DataFrame, tg: str, terms: list[str], random_slope=False) -> dict:
    """Crossed random intercepts for event and model (variational Bayes, statsmodels)."""
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    d = df[df.task_group == tg].copy()
    if tg == "date":
        raise ValueError("use pooled_re_linear for date metrics")
    d["hy"] = (d.h - d.h.mean()) / 12.0; d["hy2"] = d.hy ** 2; d["caly"] = (d.cal_m - d.cal_m.mean()) / 12.0
    fixed = "y ~ " + " + ".join({"h": "hy", "h2": "hy2", "cal": "caly"}[t] for t in terms)
    vc = {"event": "0 + C(id)", "model": "0 + C(model)"}
    if random_slope:
        vc["model_slope"] = "0 + C(model):hy"
    m = BinomialBayesMixedGLM.from_formula(fixed, vc, d)
    r = m.fit_vb()
    out = dict(task_group=tg, terms=terms, random_slope=random_slope, n_items=len(d), n_events=d.id.nunique(), n_models=d.model.nunique(),
               method="BinomialBayesMixedGLM.fit_vb (crossed random intercepts: event, model)", coef={}, vc_sd={})
    names = list(r.model.exog_names)
    for i, nm in enumerate(names):
        mean, sd = float(r.fe_mean[i]), float(r.fe_sd[i])
        out["coef"][nm] = dict(mean=mean, sd=sd, ci_lo=mean - 1.96 * sd, ci_hi=mean + 1.96 * sd, z=mean / sd if sd > 0 else float("nan"))
    for i, nm in enumerate(r.model.vcp_names):
        out["vc_sd"][nm] = float(np.exp(r.vcp_mean[i]))
    return out


def pooled_re_linear(df: pd.DataFrame, metric: str, terms: list[str]) -> dict:
    """Event random intercept (MixedLM grouped by event) + model fixed effects, for date metrics."""
    import statsmodels.formula.api as smf
    d = df[df.task_group == "date"].copy()
    d["hy"] = (d.h - d.h.mean()) / 12.0; d["hy2"] = d.hy ** 2; d["caly"] = (d.cal_m - d.cal_m.mean()) / 12.0
    fixed = f"{metric} ~ " + " + ".join({"h": "hy", "h2": "hy2", "cal": "caly"}[t] for t in terms) + " + C(model)"
    try:
        r = smf.mixedlm(fixed, d, groups=d["id"]).fit(reml=True, method="lbfgs", maxiter=200)
        out = dict(task_group="date", metric=metric, terms=terms, n_items=len(d), n_events=d.id.nunique(), method="MixedLM: event random intercept + model fixed effects", coef={})
        for nm in r.params.index:
            if nm.startswith("C(model)") or nm == "Group Var":
                continue
            out["coef"][nm] = dict(mean=float(r.params[nm]), sd=float(r.bse[nm]), ci_lo=float(r.conf_int().loc[nm, 0]), ci_hi=float(r.conf_int().loc[nm, 1]), p=float(r.pvalues[nm]))
        out["event_var"] = float(r.cov_re.iloc[0, 0]); out["resid_var"] = float(r.scale)
        return out
    except Exception as e:
        return dict(task_group="date", metric=metric, terms=terms, error=str(e)[:200])


def event_fe_conditional(df: pd.DataFrame, tg: str, terms: list[str]) -> dict:
    """Conditional logit stratified by EVENT with model fixed effects. A linear horizon term is
    exactly collinear with event + model effects (h = calendar - cutoff), so only curvature
    terms (h^2) and bin contrasts are identified here."""
    from statsmodels.discrete.conditional_models import ConditionalLogit
    d = df[df.task_group == tg].copy()
    keep = d.groupby("id").y.transform(lambda s: 0 < s.sum() < len(s))   # informative strata only
    d = d[keep]
    X = _design(d, terms, model_fe=True)
    try:
        r = ConditionalLogit(d.y.to_numpy(), X.to_numpy(), groups=pd.factorize(d.id)[0]).fit(disp=0)
        out = dict(task_group=tg, terms=terms, n_items=len(d), n_events=d.id.nunique(), method="ConditionalLogit stratified by event + model FE", coef={})
        for i, nm in enumerate(X.columns):
            if nm.startswith("m_"):
                continue
            out["coef"][nm] = dict(mean=float(r.params[i]), sd=float(r.bse[i]), ci_lo=float(r.params[i] - 1.96 * r.bse[i]), ci_hi=float(r.params[i] + 1.96 * r.bse[i]), p=float(r.pvalues[i]))
        return out
    except Exception as e:
        return dict(task_group=tg, terms=terms, error=str(e)[:200])


def event_fe_bins(df: pd.DataFrame, tg: str, bins=PRIMARY_BINS) -> dict:
    """Conditional logit by event + model FE with horizon BIN dummies (reference = first bin)."""
    from statsmodels.discrete.conditional_models import ConditionalLogit
    d = df[df.task_group == tg].copy()
    d["bin"] = d.h.map(lambda h: assign_bin(int(h), bins))
    keep = d.groupby("id").y.transform(lambda s: 0 < s.sum() < len(s)); d = d[keep]
    labs = [bin_label(lo, hi) for lo, hi in bins]
    X = pd.get_dummies(pd.Categorical(d.bin, categories=labs), prefix="bin", drop_first=True).astype(float)
    X = pd.concat([X, pd.get_dummies(d.model, prefix="m", drop_first=True).astype(float)], axis=1)
    X = X.loc[:, X.std() > 0]
    try:
        r = ConditionalLogit(d.y.to_numpy(), X.to_numpy(), groups=pd.factorize(d.id)[0]).fit(disp=0)
        out = dict(task_group=tg, reference_bin=labs[0], n_items=len(d), n_events=d.id.nunique(), coef={})
        for i, nm in enumerate(X.columns):
            if nm.startswith("bin_"):
                out["coef"][nm[4:]] = dict(log_odds_vs_ref=float(r.params[i]), sd=float(r.bse[i]), p=float(r.pvalues[i]), n=int(d.bin.eq(nm[4:]).sum()))
        return out
    except Exception as e:
        return dict(task_group=tg, error=str(e)[:200])


# ----------------------------------------------------------------------------- continuous fits
def natural_spline_basis(x, knots):
    """Natural cubic spline basis (truncated power, natural constraints), columns = len(knots)-2 + 1."""
    x = np.asarray(x, float); k = np.asarray(knots, float); K = len(k)
    def d(j):
        return (np.maximum(x - k[j], 0) ** 3 - np.maximum(x - k[K - 1], 0) ** 3) / (k[K - 1] - k[j])
    cols = [x] + [d(j) - d(K - 2) for j in range(K - 2)]
    return np.column_stack(cols)


def _fit_logit(X, y, w=None, iters=12):
    """Weighted logistic regression by Newton-IRLS (numpy); returns (beta, deviance)."""
    n, p = X.shape; w = np.ones(n) if w is None else w; beta = np.zeros(p)
    for _ in range(iters):
        eta = X @ beta; mu = 1 / (1 + np.exp(-eta)); ww = w * mu * (1 - mu) + 1e-12
        z = eta + (y - mu) / (mu * (1 - mu) + 1e-12)
        XtW = X.T * ww; beta_new = np.linalg.solve(XtW @ X + 1e-8 * np.eye(p), XtW @ z)
        if np.max(np.abs(beta_new - beta)) < 1e-7:
            beta = beta_new; break
        beta = beta_new
    mu = 1 / (1 + np.exp(-(X @ beta))); dev = -2 * np.sum(w * (y * np.log(mu + 1e-12) + (1 - y) * np.log(1 - mu + 1e-12)))
    return beta, dev


def _fit_wls(X, y, w=None):
    n, p = X.shape; w = np.ones(n) if w is None else w
    XtW = X.T * w; beta = np.linalg.solve(XtW @ X + 1e-10 * np.eye(p), XtW @ y); r = y - X @ beta
    return beta, float(np.sum(w * r * r))


def continuous_fit(df: pd.DataFrame, tg: str, metric: str, B=500, seed=0, grid=None, n_stick_boot=200) -> dict:
    """Pooled fit with model FE + natural cubic spline in h (4 df); curve for the model-average intercept;
    event-bootstrap band; broken-stick fit with breakpoint search and bootstrap CI."""
    d = df[df.task_group == tg].copy(); v = metric_series(d, tg, metric).to_numpy(float); h = d.h.to_numpy(float)
    if len(d) < 200 or h.max() - h.min() < 6:
        return dict(task_group=tg, metric=metric, skipped=True, n_items=len(d))
    knots = np.unique(np.quantile(h, [0.05, 0.35, 0.65, 0.95]))
    if len(knots) < 3:
        return dict(task_group=tg, metric=metric, skipped=True, n_items=len(d), reason="too few distinct horizons")
    M = pd.get_dummies(d.model).astype(float).to_numpy()
    S_ = natural_spline_basis(h, knots); X = np.column_stack([M, S_])
    grid = np.arange(int(h.min()), int(h.max()) + 1) if grid is None else grid
    Sg = natural_spline_basis(grid, knots); Xg = np.column_stack([np.full((len(grid), M.shape[1]), 1 / M.shape[1]), Sg])
    is_logit = metric == "accuracy"
    fit = (lambda w=None: _fit_logit(X, v, w)) if is_logit else (lambda w=None: _fit_wls(X, v, w))
    link = (lambda e: 1 / (1 + np.exp(-e))) if is_logit else (lambda e: e)
    beta, _ = fit(); curve = link(Xg @ beta)
    W = event_weights(d.id.to_numpy(), B, seed); curves = np.empty((B, len(grid)))
    for b in range(B):
        try:
            bb, _ = fit(W[b]); curves[b] = link(Xg @ bb)
        except Exception:
            curves[b] = np.nan
    lo, hi = np.nanpercentile(curves, 2.5, axis=0), np.nanpercentile(curves, 97.5, axis=0)
    d2 = np.abs(np.diff(curve, 2)); bend_spline = int(grid[1 + int(np.argmax(d2))]) if len(d2) else None
    cands = list(range(int(h.min()) + 3, int(h.max()) - 2))
    def stick(w, cand):
        best = None
        for bp in cand:
            Xb = np.column_stack([M, h, np.maximum(h - bp, 0)])
            bb, crit = _fit_logit(Xb, v, w) if is_logit else _fit_wls(Xb, v, w)
            if best is None or crit < best[0]:
                best = (crit, bp, float(bb[-2]), float(bb[-2] + bb[-1]))
        return best
    out = dict(task_group=tg, metric=metric, skipped=False, n_items=len(d), n_events=int(d.id.nunique()), knots=knots.tolist(),
               grid=grid.tolist(), curve=curve.tolist(), band_lo=lo.tolist(), band_hi=hi.tolist(), bend_spline_max_curvature=bend_spline,
               scale=("probability" if is_logit else metric))
    if len(cands) >= 3:
        crit, bp, s1, s2 = stick(None, cands)
        bps = []
        coarse = cands[::max(1, len(cands) // 12)]
        for b in range(min(B, n_stick_boot)):
            try:
                bps.append(stick(W[b], coarse)[1])
            except Exception:
                pass
        Xl = np.column_stack([M, h]); bl, critl = _fit_logit(Xl, v) if is_logit else _fit_wls(Xl, v)
        out.update(stick_breakpoint=bp, stick_slope_before=s1, stick_slope_after=s2, stick_slope_units=("log-odds/month" if is_logit else f"{metric}/month"),
                   stick_breakpoint_ci=list(ci(bps)) if bps else None, stick_bootstrap_n=len(bps), stick_vs_linear_crit_gain=float(critl - crit))
        out["linear_slope_logodds_per_month" if is_logit else "linear_slope_per_month"] = float(bl[-1])
    return out


# ----------------------------------------------------------------------------- anchoring null for the date task
def anchoring_null(df: pd.DataFrame, model: str, k_grid=range(0, 37)) -> dict:
    """Synthetic predictor = cutoff + k. k* chosen (a) to maximise mean exp(-0.1|err|), (b) to minimise mean |err|,
    on the model's own post-cutoff date items. Returns null curves by horizon and slopes for both choices."""
    d = df[(df.task_group == "date") & (df.model == model)]
    if len(d) < 20:
        return dict(model=model, skipped=True, n=len(d))
    gt = d.cal_m.to_numpy(float); cut = d.cutoff_m.to_numpy(float); h = d.h.to_numpy(float)
    res = dict(model=model, skipped=False, n=len(d), choices={})
    kmed = int(round(float((d.pred_m - d.cutoff_m).median())))
    for label, objective in (("max_score", lambda err: np.exp(-0.1 * np.abs(err)).mean()), ("min_abs", lambda err: -np.abs(err).mean()), ("model_median_offset", None)):
        best = kmed if objective is None else max(k_grid, key=lambda k: objective(cut + k - gt)); err = cut + best - gt
        res["choices"][label] = dict(k=int(best), mean_signed=float(err.mean()), mean_abs=float(np.abs(err).mean()), mean_score=float(np.exp(-0.1 * np.abs(err)).mean()),
                                     slope_signed=float(np.polyfit(h, err, 1)[0]), slope_abs=float(np.polyfit(h, np.abs(err), 1)[0]),
                                     slope_score=float(np.polyfit(h, np.exp(-0.1 * np.abs(err)), 1)[0]))
    # the model's own slopes on the same items
    res["model_slopes"] = dict(slope_signed=float(np.polyfit(h, d.signed_err, 1)[0]), slope_abs=float(np.polyfit(h, d.abs_err, 1)[0]),
                               slope_score=float(np.polyfit(h, d.date_score, 1)[0]), mean_signed=float(d.signed_err.mean()), mean_abs=float(d.abs_err.mean()), mean_score=float(d.date_score.mean()))
    res["mean_prediction_minus_cutoff_months"] = float((d.pred_m - d.cutoff_m).mean())
    res["median_prediction_minus_cutoff_months"] = float((d.pred_m - d.cutoff_m).median())
    return res


def null_binned(df: pd.DataFrame, model: str, k: int, bins, metric: str) -> list[dict]:
    d = df[(df.task_group == "date") & (df.model == model)].copy()
    err = d.cutoff_m + k - d.cal_m
    val = {"signed_err": err, "abs_err": err.abs(), "date_score": np.exp(-0.1 * err.abs())}[metric]
    d["bin"] = d.h.map(lambda h: assign_bin(int(h), bins)); d["val"] = val
    return [dict(bin=b, n=len(g), mean=float(g.val.mean())) for b, g in d.groupby("bin")]


# ----------------------------------------------------------------------------- MCC / balanced accuracy by horizon
def _confusion_arrays(items: pd.DataFrame):
    """Binary + perturbed items -> (gt_yes, pred_yes) 0/1 arrays. Original question: ground truth Yes;
    perturbed: ground truth No. pred_yes = correct on an original item, or wrong on a perturbed item."""
    gt = (items.task == "binary").to_numpy(float); c = items.y.to_numpy(float)
    pred = np.where(gt == 1, c, 1 - c)
    return gt, pred


def mcc_w(gt, pred, w):
    """Weighted MCC and balanced accuracy, vectorised over weight rows (B, n)."""
    tp = (w * (gt * pred)).sum(1); tn = (w * ((1 - gt) * (1 - pred))).sum(1)
    fp = (w * ((1 - gt) * pred)).sum(1); fn = (w * (gt * (1 - pred))).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = np.where(den > 0, (tp * tn - fp * fn) / den, np.nan)
        bal = 0.5 * (tp / (tp + fn) + tn / (tn + fp))
    return mcc, bal


def mcc_by_horizon(df: pd.DataFrame, bins, B=B_DEFAULT, min_n=20, seed=0, min_each=5) -> list[dict]:
    """Per model x bin: n items, n original / perturbed, MCC and balanced accuracy with event-bootstrap CIs."""
    rows = []
    d = df[df.task_group == "binary_merged"]
    for model, g in d.groupby("model"):
        g = g.assign(bin=g.h.map(lambda h: assign_bin(int(h), bins)))
        for lo, hi in bins:
            lab = bin_label(lo, hi); s = g[g.bin == lab]
            nb, npt = int((s.task == "binary").sum()), int((s.task == "binary_perturbed").sum())
            row = dict(model=model, bin=lab, bin_lo=lo, bin_hi=hi, n_items=len(s), n_events=int(s.id.nunique()), n_binary=nb, n_perturbed=npt,
                       h_mean=(float(s.h.mean()) if len(s) else float("nan")))
            if len(s) < min_n or nb < min_each or npt < min_each:
                row.update(suppressed=True); rows.append(row); continue
            gt, pred = _confusion_arrays(s); w = event_weights(s.id.to_numpy(), B, seed)
            m0, b0 = mcc_w(gt, pred, np.ones((1, len(s)))); mb, bb = mcc_w(gt, pred, w)
            row.update(suppressed=False, mcc=float(m0[0]), mcc_ci_lo=ci(mb)[0], mcc_ci_hi=ci(mb)[1], mcc_p=boot_p(mb),
                       bal_acc=float(b0[0]), bal_ci_lo=ci(bb)[0], bal_ci_hi=ci(bb)[1])
            rows.append(row)
    return rows


def mcc_short_vs_long(df: pd.DataFrame, split=6, B=B_DEFAULT, seed=0, min_n=40) -> list[dict]:
    """Per model: MCC on horizons 1..split vs > split, and the paired difference (shared event resamples)."""
    rows = []
    d = df[df.task_group == "binary_merged"]
    for model, g in d.groupby("model"):
        a, b = g[g.h <= split], g[g.h > split]
        row = dict(model=model, split=split, n_short=len(a), n_long=len(b), h_short=[int(a.h.min()), int(a.h.max())] if len(a) else None, h_long=[int(b.h.min()), int(b.h.max())] if len(b) else None)
        if len(a) < min_n or len(b) < min_n:
            row["skipped"] = True; rows.append(row); continue
        gt_a, pr_a = _confusion_arrays(a); gt_b, pr_b = _confusion_arrays(b)
        # shared resample over the union of events so the difference is paired
        ev = np.concatenate([a.id.to_numpy(), b.id.to_numpy()]); W = event_weights(ev, B, seed); Wa, Wb = W[:, :len(a)], W[:, len(a):]
        ma, _ = mcc_w(gt_a, pr_a, Wa); mb, _ = mcc_w(gt_b, pr_b, Wb); m0a, _ = mcc_w(gt_a, pr_a, np.ones((1, len(a)))); m0b, _ = mcc_w(gt_b, pr_b, np.ones((1, len(b))))
        dd = ma - mb
        row.update(skipped=False, mcc_short=float(m0a[0]), short_ci=list(ci(ma)), short_p=boot_p(ma), mcc_long=float(m0b[0]), long_ci=list(ci(mb)), long_p=boot_p(mb),
                   diff=float(m0a[0] - m0b[0]), diff_ci=list(ci(dd)), diff_p=boot_p(dd))
        rows.append(row)
    return rows
