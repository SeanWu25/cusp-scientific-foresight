"""
metrics.py — calibration / discrimination metrics, vectorised over bootstrap
resample weights so 10k paired resamples are cheap.

Conventions (stated in every table):
  * ECE / MCE / Murphy: 10 equal-width bins on [0,1]: [0,.1),[.1,.2),...,[.9,1.0]
    (last bin closed). MCE is the max |obs - pred| over bins with >= 10 items.
    ECE_q is a robustness check with 10 equal-mass (quantile) bins whose edges
    are fixed from the point estimate.
  * log loss: probabilities clipped to [0.01, 0.99] ("raw-with-clipping"); arm D
    additionally reports the Laplace-smoothed version, which needs no clipping.
  * Murphy: Brier = REL - RES + UNC + within-bin residual, where the residual
    (within-bin variance minus twice the within-bin covariance) is reported so the
    identity holds exactly.
  * AUROC: Mann-Whitney with ties counted 1/2 (rank-based), weighted.
  * Bootstrap: cluster (event-level) resampling — an event's binary and perturbed
    items are drawn together — 10,000 resamples, percentile CIs, paired across arms
    by reusing the same event-count matrix for every cell.
"""
from __future__ import annotations
import numpy as np

EPS = 0.01
NBINS = 10
MCE_MIN = 10


def _w(w, n):
    return np.ones((1, n)) if w is None else w


def wmean(x, w=None):
    x = np.asarray(x, float); w = _w(w, len(x))
    return (w * x).sum(1) / w.sum(1)


def accuracy(correct, w=None):
    return wmean(np.asarray(correct, float), w)


def brier(p, y, w=None):
    p = np.asarray(p, float); y = np.asarray(y, float)
    return wmean((p - y) ** 2, w)


def logloss(p, y, w=None, eps=EPS):
    p = np.clip(np.asarray(p, float), eps, 1 - eps); y = np.asarray(y, float)
    return wmean(-(y * np.log(p) + (1 - y) * np.log(1 - p)), w)


def bin_index(p, edges=None):
    p = np.asarray(p, float)
    if edges is None:
        return np.minimum((p * NBINS).astype(int), NBINS - 1)
    return np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)


def quantile_edges(p):
    p = np.asarray(p, float)
    e = np.quantile(p, np.linspace(0, 1, NBINS + 1))
    e[0], e[-1] = 0.0, 1.0 + 1e-9
    return e


def _binsums(p, y, w, edges=None):
    p = np.asarray(p, float); y = np.asarray(y, float); w = _w(w, len(p))
    b = bin_index(p, edges); nb = NBINS if edges is None else len(edges) - 1
    onehot = np.zeros((len(p), nb)); onehot[np.arange(len(p)), b] = 1.0
    nk = w @ onehot; pk = (w * p) @ onehot; ok = (w * y) @ onehot; p2k = (w * p * p) @ onehot
    return nk, pk, ok, p2k, w.sum(1)


def ece(p, y, w=None, edges=None):
    nk, pk, ok, _, N = _binsums(p, y, w, edges)
    return np.abs(ok - pk).sum(1) / N


def mce(p, y, w=None, edges=None):
    nk, pk, ok, _, N = _binsums(p, y, w, edges)
    with np.errstate(divide="ignore", invalid="ignore"):
        gap = np.abs(ok / nk - pk / nk)
    gap[nk < MCE_MIN] = np.nan
    return np.nanmax(np.where(np.isnan(gap), -np.inf, gap), axis=1).astype(float)


def murphy(p, y, w=None):
    """Return dict of arrays: rel, res, unc, resid, brier."""
    nk, pk, ok, p2k, N = _binsums(p, y, w)
    obar = ok.sum(1) / N
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.nansum(np.where(nk > 0, (pk - ok) ** 2 / nk, 0.0), axis=1) / N
        res = np.nansum(np.where(nk > 0, nk * (ok / nk - obar[:, None]) ** 2, 0.0), axis=1) / N
    unc = obar * (1 - obar)
    b = brier(p, y, w)
    return dict(rel=rel, res=res, unc=unc, resid=b - (rel - res + unc), brier=b)


def auroc(s, y, w=None):
    """Weighted Mann-Whitney AUROC (ties = 1/2)."""
    s = np.asarray(s, float); y = np.asarray(y, float); w = _w(w, len(s))
    u, g = np.unique(s, return_inverse=True)
    onehot = np.zeros((len(s), len(u))); onehot[np.arange(len(s)), g] = 1.0
    pos = (w * y) @ onehot; neg = (w * (1 - y)) @ onehot
    cneg_below = np.cumsum(neg, axis=1) - neg
    Wp, Wn = pos.sum(1), neg.sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (pos * (cneg_below + 0.5 * neg)).sum(1) / (Wp * Wn)


def boot_counts(n_events: int, B: int, seed: int = 0):
    rng = np.random.default_rng(seed)
    return rng.multinomial(n_events, np.full(n_events, 1.0 / n_events), size=B)


def ci(v, lo=2.5, hi=97.5):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if v.size == 0:
        return (float("nan"), float("nan"))
    return (float(np.percentile(v, lo)), float(np.percentile(v, hi)))


def boot_p(d):
    """Two-sided percentile-bootstrap p-value for H0: delta = 0."""
    d = np.asarray(d, float); d = d[np.isfinite(d)]
    if d.size == 0:
        return float("nan")
    B = d.size
    lo = ((d <= 0).sum() + 1) / (B + 1); hi = ((d >= 0).sum() + 1) / (B + 1)
    return float(min(1.0, 2 * min(lo, hi)))


def holm(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni step-down adjustment; NaNs are passed through."""
    idx = [i for i, p in enumerate(pvals) if p == p]
    m = len(idx); out = [float("nan")] * len(pvals)
    order = sorted(idx, key=lambda i: pvals[i]); running = 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, (m - rank) * pvals[i]); running = max(running, adj); out[i] = running
    return out
