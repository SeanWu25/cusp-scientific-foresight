#!/usr/bin/env python3
"""
a5_common.py -- shared loaders and statistics for study A5 (selection bias).

Reads finalized reports and benchmark metadata only. No inference, no writes
outside results/A5_selection_bias/.

Stratification metadata available per event (see metadata_audit.md):
  source     -- 6 strata, 100% coverage, pooled corpora (5,575 events)
  citations  -- 481 events (8.6%), original corpus only, pinned-500 subset
  latency    -- 708 events (12.7%), extension only, 0-3 months, right-censored
"""
from __future__ import annotations
import json, math, os, sys
from collections import defaultdict

import numpy as np

REPO = "/home/seanwu/FutureScience"
sys.path.insert(0, os.path.join(REPO, "run_evaluation"))
from full_corpus_tables import PANEL, mo  # noqa: E402

ORIG = f"{REPO}/archive/data/canonical/merged_validated_cusp_fixed.jsonl"
EXT  = f"{REPO}/benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"
CITE = ("/home/seanwu/FutureScience_backup_20260508_013823/benchmark_data/"
        "CUSP/sample_500_stratified_with_citations.jsonl")
CITE_RETRIEVED = "2026-05-12"          # mtime of CITE; Semantic Scholar batch API

TASKS = ["binary", "mcq", "date", "frq"]
TASK_LABEL = {"binary": "Binary (bal. acc)", "mcq": "MCQ (acc)",
              "date": "Date (score)", "frq": "FRQ (0-10)"}

SOURCE_LABEL = {
    "nature": "Nature", "science": "Science", "cell": "Cell",
    "hugging_face_top_ai_papers": "HF Daily Papers (arXiv)",
    "top_ai_papers": "Top-10 AI Paper of Week (arXiv)",
    "leaderboard_questions": "Leaderboards",
}
SOURCE_ORDER = ["nature", "science", "cell", "hugging_face_top_ai_papers",
                "top_ai_papers", "leaderboard_questions"]


# --------------------------------------------------------------------------
# metadata
# --------------------------------------------------------------------------
def load_meta():
    """event id -> dict(pub, source, area, corpus, citations, latency)."""
    meta = {}
    for corpus, path in (("original", ORIG), ("extension", EXT)):
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            d = json.loads(line)
            lat = None
            f, o = d.get("first_date_found"), d.get("original_publication_date")
            if f and o:
                a, b = mo(f), mo(o)
                if a is not None and b is not None:
                    lat = b - a
            meta[d["id"]] = dict(
                pub=str(d.get("publication_date", ""))[:7],
                source=d.get("source"), area=d.get("main_area"),
                corpus=corpus, citations=None, latency=lat,
            )
    n_cite = 0
    if os.path.exists(CITE):
        for line in open(CITE, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            c = r.get("citation_count")
            if c is not None and r["id"] in meta:
                meta[r["id"]]["citations"] = int(c)
                n_cite += 1
    else:
        print(f"  WARN citation file missing: {CITE}", file=sys.stderr)
    return meta, n_cite


def citation_quartiles(meta):
    """Quartile edges over every event carrying a citation count."""
    vals = sorted(m["citations"] for m in meta.values() if m["citations"] is not None)
    if not vals:
        return None
    q = [float(np.quantile(vals, p)) for p in (0.25, 0.50, 0.75)]
    return q


def cite_bin(c, edges):
    if c is None:
        return None
    if c <= edges[0]:
        return "Q1"
    if c <= edges[1]:
        return "Q2"
    if c <= edges[2]:
        return "Q3"
    return "Q4"


def latency_bin(l):
    """Bins chosen from the observed distribution (0:442, 1:156, 2:101, 3:9).
    3 months carries n=9, so 2 and 3 are pooled into '2-3 mo'."""
    if l is None:
        return None
    if l <= 0:
        return "0 mo"
    if l == 1:
        return "1 mo"
    return "2-3 mo"


LATENCY_ORDER = ["0 mo", "1 mo", "2-3 mo"]
CITE_ORDER = ["Q1", "Q2", "Q3", "Q4"]


# --------------------------------------------------------------------------
# per-event records
# --------------------------------------------------------------------------
def load_model_events(name, cutoff, paths, meta, rule="main"):
    """Return list of per-event dicts for one model, deduplicated by id.

    Each record: id, part ('pre'/'post'), and per-task outcomes:
      b / bp : 1/0 on the real and perturbed binary question (None if absent)
      mcq    : 1/0     date: float score     frq: float score
    """
    cm = mo(cutoff)
    out, seen = [], set()
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        for x in json.load(open(path, encoding="utf-8")).get("results", []):
            rid = x.get("id")
            if rid in seen or rid not in meta:
                continue
            seen.add(rid)
            pm = mo(meta[rid]["pub"])
            if pm is None or cm is None:
                continue
            part = ("pre" if pm < cm else "post") if rule == "main" else \
                   ("pre" if pm <= cm else "post")
            t = x.get("tasks") or {}

            def ok(key):
                v = t.get(key)
                if not v or v.get("skipped"):
                    return None
                return v

            b, bp, m = ok("binary"), ok("binary_perturbed"), ok("mcq")
            d, f = ok("date"), ok("frq")
            out.append(dict(
                id=rid, part=part,
                b=(1.0 if b["correct"] else 0.0) if b and "correct" in b else None,
                bp=(1.0 if bp["correct"] else 0.0) if bp and "correct" in bp else None,
                mcq=(1.0 if m["correct"] else 0.0) if m and "correct" in m else None,
                date=float(d["score"]) if d and d.get("score") is not None else None,
                frq=float(f["score"]) if f and f.get("score") is not None else None,
            ))
    return out


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------
def _arrays(recs, task):
    """Per-event arrays for a task. Binary returns two columns (real, pert)."""
    if task == "binary":
        a = np.array([[r["b"] if r["b"] is not None else np.nan,
                       r["bp"] if r["bp"] is not None else np.nan] for r in recs],
                     dtype=float)
        return a if len(a) else np.empty((0, 2))
    key = {"mcq": "mcq", "date": "date", "frq": "frq"}[task]
    return np.array([r[key] if r[key] is not None else np.nan for r in recs],
                    dtype=float).reshape(-1, 1)


def _stat(a, task):
    """Point statistic from a per-event array. NaN when undefined."""
    if a.size == 0:
        return np.nan
    if task == "binary":
        real, pert = a[:, 0], a[:, 1]
        nr, np_ = np.count_nonzero(~np.isnan(real)), np.count_nonzero(~np.isnan(pert))
        if nr == 0 or np_ == 0:
            return np.nan
        return 0.5 * (np.nanmean(real) + np.nanmean(pert))
    col = a[:, 0]
    return np.nanmean(col) if np.count_nonzero(~np.isnan(col)) else np.nan


def _n(a, task):
    """Observation count backing the statistic (binary counts both questions)."""
    if a.size == 0:
        return 0
    return int(np.count_nonzero(~np.isnan(a)))


def n_events(a):
    """Events contributing at least one observation -- the bootstrap unit."""
    if a.size == 0:
        return 0
    return int(np.count_nonzero(np.any(~np.isnan(a), axis=1)))


def cell(recs, task, n_boot=2000, seed=0, min_n=20):
    """Point estimate, event-clustered bootstrap percentile CI, N.

    Returns None when the cell is empty, and a dict with suppressed=True when
    it falls below min_n -- the caller prints a suppression marker, never a
    bare point estimate.
    """
    a = _arrays(recs, task)
    n = _n(a, task)
    ne = n_events(a)
    if n == 0:
        return None
    pt = _stat(a, task)
    if np.isnan(pt):
        return None
    if n < min_n:
        return dict(stat=pt, lo=None, hi=None, n=n, n_events=ne, suppressed=True)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, a.shape[0], size=(n_boot, a.shape[0]))
    draws = np.empty(n_boot)
    for i in range(n_boot):
        draws[i] = _stat(a[idx[i]], task)
    draws = draws[~np.isnan(draws)]
    if draws.size < n_boot // 10:
        return dict(stat=pt, lo=None, hi=None, n=n, n_events=ne, suppressed=True)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return dict(stat=float(pt), lo=float(lo), hi=float(hi), n=n,
                n_events=ne, suppressed=False)


def omnibus(groups, task, n_perm=10000, seed=0, min_n=20):
    """Permutation test: does the statistic differ across strata?

    groups: {stratum -> [recs]}. Strata below min_n are dropped first; the test
    runs on the retained strata only. Statistic is the N-weighted between-
    stratum variance of the cell statistic; the null shuffles stratum labels
    across EVENTS, so event clustering is preserved.
    """
    kept = {}
    for k, recs in groups.items():
        a = _arrays(recs, task)
        if _n(a, task) >= min_n and not np.isnan(_stat(a, task)):
            kept[k] = a
    if len(kept) < 2:
        return None
    keys = list(kept)
    allrows = np.vstack([kept[k] for k in keys])
    sizes = [kept[k].shape[0] for k in keys]
    bounds = np.cumsum([0] + sizes)

    def T(rows):
        stats, ns = [], []
        for i in range(len(keys)):
            seg = rows[bounds[i]:bounds[i + 1]]
            s = _stat(seg, task)
            if np.isnan(s):
                return np.nan
            stats.append(s)
            ns.append(_n(seg, task))
        stats, ns = np.array(stats), np.array(ns, dtype=float)
        gm = np.sum(stats * ns) / np.sum(ns)
        return float(np.sum(ns * (stats - gm) ** 2) / np.sum(ns))

    t_obs = T(allrows)
    if np.isnan(t_obs):
        return None
    rng = np.random.default_rng(seed)
    ge = 0
    valid = 0
    for _ in range(n_perm):
        perm = rng.permutation(allrows.shape[0])
        t = T(allrows[perm])
        if np.isnan(t):
            continue
        valid += 1
        if t >= t_obs:
            ge += 1
    if valid == 0:
        return None
    p = (ge + 1) / (valid + 1)
    spread = {}
    for i, k in enumerate(keys):
        spread[k] = _stat(kept[k][:, :], task)
    lo_k = min(spread, key=lambda k: spread[k])
    hi_k = max(spread, key=lambda k: spread[k])
    return dict(p=p, n_strata=len(keys), n_perm=valid,
                range=float(spread[hi_k] - spread[lo_k]),
                min_stratum=lo_k, max_stratum=hi_k, strata=keys)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values, order preserved."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(order):
        v = (m - rank) * pvals[i]
        run = max(run, v)
        adj[i] = min(1.0, run)
    return adj


def fmt(c, dec=3):
    """Render a cell: value [lo, hi] (n), or a suppression marker."""
    if c is None:
        return "--"
    if c.get("suppressed"):
        return f"n<20 ({c['n']})"
    return f"{c['stat']:.{dec}f} [{c['lo']:.{dec}f}, {c['hi']:.{dec}f}] ({c['n']:,})"
