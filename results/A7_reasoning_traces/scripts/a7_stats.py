"""a7_stats.py — the statistical machinery shared by analyses A-G.

* consensus labels from the two coders (primary = both agree; sensitivity = either)
* event-clustered bootstrap CIs for differences in proportions and means
* a random-intercept GLMM/LMM for event (and optionally model), reusing the validated
  sparse PIRLS + Laplace implementation in horizon_study/glmm.py
* Holm-Bonferroni across codes within each analysis family
"""
from __future__ import annotations
import json, sys, collections, math
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path("/home/seanwu/FutureScience/horizon_study")))
import a7_common as C, a7_prompts as P
from glmm import CrossedGLMM, onehot

B_DEFAULT = 2000


def load_labels(primary="both"):
    """-> rows: one per (trace_id, code) with consensus label + trace metadata."""
    per = collections.defaultdict(dict)
    meta = {}
    for l in open(C.STUDY / "coded_traces.jsonl", encoding="utf-8"):
        d = json.loads(l)
        per[(d["trace_id"], d["code"])][d["coder"]] = d
        meta[d["trace_id"]] = d
    coders = sorted({c for v in per.values() for c in v})
    rows = []
    for (tid, code), v in per.items():
        if len(v) < len(coders):
            continue
        vals = [v[c] for c in coders]
        if code == "HEDGING":
            lv = [x["verdict"] for x in vals]
            lab = float(np.mean(lv)) if all(x is not None for x in lv) else None
            both = all(x is not None for x in lv)
        else:
            yes = [x["verdict"] == "yes" for x in vals]
            lab = int(all(yes)) if primary == "both" else int(any(yes))
            both = True
        m = vals[0]
        rows.append(dict(trace_id=tid, code=code, label=lab, agreed=(len(set(
            x["verdict"] for x in vals)) == 1), model=m["model"], condition=m["condition"], half=m["half"],
            task=m["task"], id=m["id"], partition=m["partition"], correct=m["correct"], score=m["score"],
            frq_score=m["frq_score"], month_distance=m["month_distance"],
            signed_error_months=m["signed_error_months"], trace_words=m["trace_words"]))
    return rows, coders


def reliable_codes():
    return json.load(open(C.STUDY / "agreement.json"))["reliable_codes"]


def boot_events(ids, B=B_DEFAULT, seed=0):
    """Event-cluster resample weights: (B, n) integer counts aligned to `ids`."""
    uniq, inv = np.unique(np.asarray(ids), return_inverse=True)
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(uniq), (B, len(uniq)))
    cnt = np.zeros((B, len(uniq)), dtype=np.int32)
    for b in range(B):
        cnt[b] = np.bincount(draw[b], minlength=len(uniq))
    return cnt[:, inv].astype(float)


def wmean(x, w):
    x = np.asarray(x, float)
    return (w * x).sum(1) / np.maximum(w.sum(1), 1e-12)


def diff_ci(y, g, ids, B=B_DEFAULT, seed=0):
    """Difference in mean(y) between g==1 and g==0, event-clustered bootstrap CI and p."""
    y = np.asarray(y, float); g = np.asarray(g).astype(bool)
    n1, n0 = int(g.sum()), int((~g).sum())
    if n1 == 0 or n0 == 0:
        return dict(diff=float("nan"), lo=float("nan"), hi=float("nan"), p=float("nan"), n1=n1, n0=n0,
                    m1=float("nan"), m0=float("nan"))
    w = boot_events(ids, B, seed)
    d = wmean(y[g], w[:, g]) - wmean(y[~g], w[:, ~g])
    d = d[np.isfinite(d)]
    lo, hi = (np.percentile(d, [2.5, 97.5]) if len(d) else (np.nan, np.nan))
    p = float(min(1.0, 2 * min(((d <= 0).sum() + 1) / (len(d) + 1), ((d >= 0).sum() + 1) / (len(d) + 1)))) if len(d) else float("nan")
    return dict(diff=float(y[g].mean() - y[~g].mean()), lo=float(lo), hi=float(hi), p=p,
                n1=n1, n0=n0, m1=float(y[g].mean()), m0=float(y[~g].mean()))


def glmm_effect(y, x, ids, models=None, family="binomial"):
    """y ~ 1 + x with a random intercept for event (and for model when `models` is given).
    Returns the coefficient on x with a Wald CI and p."""
    y = np.asarray(y, float); x = np.asarray(x, float)
    if len(np.unique(x)) < 2 or len(y) < 30:
        return dict(beta=float("nan"), se=float("nan"), lo=float("nan"), hi=float("nan"), p=float("nan"), n=len(y))
    X = np.column_stack([np.ones(len(y)), x])
    Zs, names = [], []
    Ze, _ = onehot(np.asarray(ids)); Zs.append(Ze); names.append("event")
    if models is not None and len(np.unique(models)) > 1:
        Zm, _ = onehot(np.asarray(models)); Zs.append(Zm); names.append("model")
    try:
        r = CrossedGLMM(family).fit(y, X, Zs, ["intercept", "code"], names)
    except Exception as e:
        return dict(beta=float("nan"), se=float("nan"), lo=float("nan"), hi=float("nan"), p=float("nan"),
                    n=len(y), error=str(e)[:120])
    c = r["coef"]["code"]
    b, se = float(c["mean"]), float(c["sd"])
    from math import erf, sqrt
    z = b / se if se > 0 else float("nan")
    p = float(2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))) if np.isfinite(z) else float("nan")
    return dict(beta=b, se=se, lo=float(c["ci_lo"]), hi=float(c["ci_hi"]), p=p, n=len(y),
                converged=bool(r.get("converged")), vc_sd=r.get("vc_sd", {}))


def holm(pvals):
    """Holm-Bonferroni adjusted p-values; NaNs pass through."""
    idx = [i for i, p in enumerate(pvals) if p is not None and np.isfinite(p)]
    out = [float("nan")] * len(pvals)
    order = sorted(idx, key=lambda i: pvals[i])
    m = len(order); run = 0.0
    for r, i in enumerate(order):
        adj = (m - r) * pvals[i]
        run = max(run, adj)
        out[i] = float(min(1.0, run))
    return out


def fmt(v, d=3):
    return "--" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{d}f}"


def fmtp(p):
    if p is None or not np.isfinite(p):
        return "--"
    return "<0.001" if p < 0.001 else f"{p:.3f}"
