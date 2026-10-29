"""curvature_continuous.py - event-stratified curvature test for the CONTINUOUS horizon outcomes (FRQ score, date score),
the analogue of the conditional-logit curvature test that SI Table S30 reports for Binary and MCQ (stats.event_fe_conditional).

Model (per task and corpus, base condition, post-cutoff items h >= 1, nine Table-1 models as in run_no_v4pro.py):
    y_jim = alpha_i + gamma_m + beta2 * hc_im^2 + e_jim,   hc = (h - mean h) / 12  (horizon in centred years)
alpha_i = event fixed effect, gamma_m = model fixed effect. A linear horizon term is collinear with the two fixed effects
(h = calendar month of the event - cutoff month of the model), so only the curvature term beta2 is identified, as in the
conditional logit. Estimation: within-event demeaning (Frisch-Waugh-Lovell) then OLS with standard errors clustered by event.

Also extracts the 95% CI of the quadratic GLMM term (h+h2 fit) for FRQ and date from tables_no_v4pro/pooled.json.
Writes tables_no_v4pro/curvature_continuous.{json,md}. Does not modify any other file.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H))
import data as D, stats as S
D.MODELS.pop("dsv4pro", None); D.MODEL_ORDER[:] = [m for m in D.MODEL_ORDER if m != "dsv4pro"]
OUT = H / "tables_no_v4pro"
ev = D.load_events()
pooled = json.load(open(OUT / "pooled.json"))
res = {}
for ds in ("orig", "merged"):
    df = D.load_items(ds, ev); df = df[df.condition == "base"]
    for tg, metric in (("frq", "frq_score"), ("date", "date_score")):
        d = df[df.task_group == tg].copy()
        d["y"] = S.metric_series(d, tg, metric).astype(float)
        d = d[d.y.notna() & (d.h >= 1)]
        hc = (d.h - d.h.mean()) / 12.0
        X = pd.concat([pd.Series(hc ** 2, index=d.index, name="h_years_sq"),
                       pd.get_dummies(d.model, prefix="m", drop_first=True).astype(float)], axis=1)
        Z = pd.concat([d[["y"]], X], axis=1)
        Zd = Z - Z.groupby(d.id).transform("mean")                    # absorb event fixed effects
        Zd = Zd.loc[:, Zd.std() > 0]
        r = sm.OLS(Zd["y"].to_numpy(), Zd.drop(columns="y").to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.id)[0]})
        k = list(Zd.drop(columns="y").columns).index("h_years_sq")
        glmm = pooled[ds][tg][metric]["h+h2"]["coef"]["hy2"]
        res.setdefault(ds, {})[tg] = dict(
            n_items=int(len(d)), n_events=int(d.id.nunique()), n_models=int(d.model.nunique()),
            curvature=dict(coef=float(r.params[k]), se=float(r.bse[k]), ci_lo=float(r.conf_int()[k][0]), ci_hi=float(r.conf_int()[k][1]), p=float(r.pvalues[k]),
                           method="OLS with event and model fixed effects (within-event demeaning), event-clustered SE"),
            glmm_quadratic=dict(coef=glmm["mean"], ci_lo=glmm["ci_lo"], ci_hi=glmm["ci_hi"], z=glmm["z"]))
        print(ds, tg, res[ds][tg], file=sys.stderr)
json.dump(res, open(OUT / "curvature_continuous.json", "w"), indent=1)
L = ["# Curvature for continuous horizon outcomes (FRQ score, date score)", "",
     "Event-stratified curvature: OLS of the outcome on squared centred horizon (years) with event and model fixed effects, "
     "event-clustered SE (analogue of the conditional-logit curvature for Binary/MCQ). GLMM quadratic: the h+h2 crossed random-intercept fit (pooled.json).", "",
     "| corpus | task | items / events | GLMM quadratic [95% CI] | event-stratified curvature [95% CI] (p) |", "|---|---|---|---|---|"]
for ds, lab in (("orig", "Original"), ("merged", "Merged")):
    for tg in ("frq", "date"):
        x = res[ds][tg]; g = x["glmm_quadratic"]; c = x["curvature"]
        L.append(f"| {lab} | {tg} | {x['n_items']:,} / {x['n_events']:,} | {g['coef']:+.3f} [{g['ci_lo']:+.3f}, {g['ci_hi']:+.3f}] | {c['coef']:+.3f} [{c['ci_lo']:+.3f}, {c['ci_hi']:+.3f}] ({c['p']:.2g}) |")
(OUT / "curvature_continuous.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
