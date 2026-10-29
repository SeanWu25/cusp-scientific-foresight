#!/usr/bin/env python3
"""
a5_common.py -- shared loaders and statistics for study A5 (selection bias).

Reads finalized reports and benchmark metadata only. No inference, no writes
outside this study directory.

Stratification metadata available per event (see metadata_audit.md):
  source        -- 6 strata, 100% coverage, pooled corpora (5,575 events)
  visibility    -- OpenAlex cited_by_count, single snapshot (metadata/SNAPSHOT.json),
                   every linked event that resolves (whole corpus)
  vis_rate      -- the same counts per month since first observable date
  latency       -- Crossref online-publication month minus CUSP first-observable
                   month, every journal event (Nature/Science/Cell, both halves)
  lat_review    -- Crossref online month minus manuscript-received month
                   (Nature and Science deposit the received date; Cell does not)
  legacy        -- the first-pass 481-event Semantic Scholar citations and the
                   708-event extension latency, kept only so the earlier tables
                   and the S19-S23 fold-in remain reproducible
"""
from __future__ import annotations
import json, math, os, sys
from collections import defaultdict

import numpy as np

REPO = "."
sys.path.insert(0, os.path.join(REPO, "run_evaluation"))
from full_corpus_tables import PANEL, mo  # noqa: E402
# A5 without DeepSeek-V4-Pro (Reviewer 1 c5 request, 2026-10-18): no provider-reported cutoff, so it is removed from the panel.
PANEL = [p for p in PANEL if p[0] != "DeepSeek-V4-Pro"]

# Partition rule (2026-10-25). "cmpre" (default): an event published in the
# cutoff month counts as PRE (post iff pub_month > cutoff_month), the rule of
# the information-access analysis and Table 1. "main": the earlier rule, cutoff
# month counts as POST (pre iff pub_month < cutoff_month). Set A5_RULE=main to
# reproduce results/A5_selection_bias_no_v4pro/.
PARTITION_RULE = os.environ.get("A5_RULE", "cmpre")
assert PARTITION_RULE in ("cmpre", "main"), PARTITION_RULE
PARTITION_RULE_TEXT = {"cmpre": "cmpre (cutoff month counts as PRE; post iff pub_month > cutoff_month)",
                       "main": "main (cutoff month counts as POST)"}[PARTITION_RULE]


def is_post(pm, cm, rule=None):
    rule = rule or PARTITION_RULE
    return pm > cm if rule == "cmpre" else pm >= cm


def before_cutoff(xm, cm, rule=None):
    """True if a date in month xm was observable at the cutoff under the rule."""
    rule = rule or PARTITION_RULE
    return xm <= cm if rule == "cmpre" else xm < cm

ORIG = f"{REPO}/archive/data/canonical/merged_validated_cusp_fixed.jsonl"
EXT  = f"{REPO}/benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"
CITE = ("archive/backup_20260508/benchmark_data/"
        "CUSP/sample_500_stratified_with_citations.jsonl")
CITE_RETRIEVED = "2026-05-12"          # mtime of CITE; Semantic Scholar batch API
META_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "metadata")
SNAPSHOT = (json.load(open(os.path.join(META_DIR, "SNAPSHOT.json")))["snapshot_date"]
            if os.path.exists(os.path.join(META_DIR, "SNAPSHOT.json")) else None)

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
    _attach_whole_corpus(meta)
    return meta, n_cite


def _jsonl_by_doi(path):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                out[r["doi"]] = r
    return out


def _attach_whole_corpus(meta):
    """Whole-corpus fields from metadata/ (a5_fetch_metadata.py), one snapshot.

    cites      : Semantic Scholar citationCount, OpenAlex cited_by_count as the
                 fallback (cite_src records which); None if neither resolved.
                 S2 is primary because OpenAlex credits most arXiv citations to
                 the later journal version and returns ~0 for arXiv records.
    cite_rate  : cites per month between first-observable month and snapshot
    online     : Crossref published-online (else created) month of the journal
                 version, journal DOIs only
    first_obs  : the earlier of CUSP's publication_date and any Crossref-linked
                 preprint's posted month (the build pipeline missed some)
    lat_obs    : online - first_obs, months the finding was publicly observable
                 before formal publication (0 = no earlier public trace);
                 negatives are clipped to 0 and counted in the manifest
    lat_review : online - received (Nature, Science)
    preprint   : earliest Crossref-linked preprint month, when a link exists
    """
    ids = os.path.join(META_DIR, "event_ids.json")
    for m in meta.values():
        m.update(doi=None, kind="none", cites=None, cite_rate=None, online=None,
                 lat_obs=None, lat_review=None, preprint=None)
    if not os.path.exists(ids) or SNAPSHOT is None:
        print("  WARN whole-corpus metadata missing; run a5_fetch_metadata.py",
              file=sys.stderr)
        return
    oa = _jsonl_by_doi(os.path.join(META_DIR, "openalex_citations.jsonl"))
    s2 = _jsonl_by_doi(os.path.join(META_DIR, "s2_citations.jsonl"))
    cr = _jsonl_by_doi(os.path.join(META_DIR, "crossref_dates.jsonl"))
    pp = _jsonl_by_doi(os.path.join(META_DIR, "crossref_preprints.jsonl"))
    snap_m = mo(SNAPSHOT)
    for e in json.load(open(ids)):
        m = meta.get(e["id"])
        if m is None:
            continue
        m["doi"], m["kind"] = e["doi"], e["kind"]
        m["cite_src"] = None
        w = s2.get(e["doi"]) if e["doi"] else None
        if w and w.get("found") and w.get("citation_count") is not None:
            m["cites"], m["cite_src"] = int(w["citation_count"]), "s2"
        else:
            w = oa.get(e["doi"]) if e["doi"] else None
            if w and w.get("found") and w.get("cited_by_count") is not None:
                m["cites"], m["cite_src"] = int(w["cited_by_count"]), "openalex"
        if m["cites"] is not None:
            age = max(1, snap_m - mo(m["pub"]))
            m["cite_rate"] = m["cites"] / age
        r = cr.get(e["doi"]) if e["kind"] == "doi" else None
        if r and r.get("found"):
            posted = []
            for pdoi in r.get("has_preprint") or []:
                q = pp.get(pdoi)
                if q and q.get("found"):
                    d = q.get("posted") or q.get("created")
                    if d and mo(d) is not None:
                        posted.append(d[:7])
            if posted:
                m["preprint"] = min(posted)
            # first observable = the earlier of CUSP's date and any Crossref-
            # linked preprint the build pipeline missed. The cutoff partition
            # stays on CUSP's publication_date (the benchmark's definition);
            # only the latency uses the corrected date.
            first = m["pub"]
            if m["preprint"] and mo(m["preprint"]) < mo(first):
                first = m["preprint"]
            m["first_obs"] = first
            m["preprint_gap"] = mo(m["pub"]) - mo(m["preprint"]) if m["preprint"] else None
            online = r.get("published_online") or r.get("created")
            if online and mo(online) is not None:
                m["online"] = online[:7]
                m["lat_obs_raw"] = mo(online) - mo(first)
                m["lat_obs"] = max(0, m["lat_obs_raw"])
                rec = (r.get("assertions") or {}).get("received")
                if rec and mo(rec) is not None and mo(online) >= mo(rec):
                    m["lat_review"] = mo(online) - mo(rec)


def quartile_edges(meta, field):
    vals = sorted(m[field] for m in meta.values() if m.get(field) is not None)
    if not vals:
        return None
    return [float(np.quantile(vals, p)) for p in (0.25, 0.50, 0.75)]


def qbin(v, edges):
    if v is None or edges is None:
        return None
    if v <= edges[0]:
        return "Q1"
    if v <= edges[1]:
        return "Q2"
    if v <= edges[2]:
        return "Q3"
    return "Q4"


# Whole-corpus latency bins. Edges are inclusive upper bounds in months; the
# labels are what the tables print. Chosen from the observed distributions
# (see metadata_audit.md, section 4) and fixed here so every script agrees.
LAT_OBS_BINS = [(0, "0 mo"), (6, "1-6 mo"), (10**6, ">6 mo")]
LAT_REVIEW_BINS = [(6, "<=6 mo"), (12, "7-12 mo"), (24, "13-24 mo"), (10**6, ">24 mo")]
LAT_OBS_ORDER = [lab for _, lab in LAT_OBS_BINS]
LAT_REVIEW_ORDER = [lab for _, lab in LAT_REVIEW_BINS]


def edge_bin(v, bins):
    if v is None:
        return None
    for hi, lab in bins:
        if v <= hi:
            return lab
    return None


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
def load_model_events(name, cutoff, paths, meta, rule=None):
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
            part = "post" if is_post(pm, cm, rule) else "pre"
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


# --------------------------------------------------------------------------
# stratification registry -- the single place that says which dimensions
# exist, their stratum order and labels, and where their outputs live.
# a5_analysis / a5_tables / a5_summarize / a5_figures / a5_make_response all
# read this, so a dimension added here appears everywhere.
# --------------------------------------------------------------------------
def _qlabels(edges, fmt):
    return {"Q1": f"Q1 (<={fmt(edges[0])})", "Q2": f"Q2 (<={fmt(edges[1])})",
            "Q3": f"Q3 (<={fmt(edges[2])})", "Q4": f"Q4 (>{fmt(edges[2])})"}


def dim_registry(meta, out_root):
    """dim -> dict(title, short, order, labels, outdir, notes, key(meta_rec))."""
    e_c = quartile_edges(meta, "cites")
    e_r = quartile_edges(meta, "cite_rate")
    e_l = citation_quartiles(meta)
    n_c = sum(1 for m in meta.values() if m.get("cites") is not None)
    n_r = sum(1 for m in meta.values() if m.get("cite_rate") is not None)
    n_lo = sum(1 for m in meta.values() if m.get("lat_obs") is not None)
    n_lr = sum(1 for m in meta.values() if m.get("lat_review") is not None)
    n_leg_c = sum(1 for m in meta.values() if m.get("citations") is not None)
    n_leg_l = sum(1 for m in meta.values() if m.get("latency") is not None)
    N = len(meta)
    cellnote = ("Cells are `value [95% CI] (n observations)`; binary n counts the "
                "real and perturbed question separately. Cells below n=20 are printed "
                "as `n<20 (n)` with no point estimate. `p (perm)` is a 10,000-draw "
                "permutation test shuffling stratum labels across events; `p (Holm)` "
                "is Holm-Bonferroni corrected across every model x partition x task "
                "test in this stratification.")
    R = {}
    R["source"] = dict(
        title="A5.1 -- performance by source / repository", short="source / venue",
        order=SOURCE_ORDER, labels=SOURCE_LABEL, outdir=f"{out_root}/by_source",
        key=lambda m: m["source"],
        notes=["Entire dataset (5,575 events); `source` is one-to-one with the venue "
               "(Nature = 10.1038/s41586, Science = 10.1126/science, Cell = "
               "10.1016/j.cell, both AI feeds = arXiv), so this is simultaneously the "
               "per-journal stratification. No stratum is a singleton, so no 'other' "
               "bucket is needed.", "", cellnote])
    R["visibility"] = dict(
        title="A5.2 -- performance by event visibility (citation quartile, whole corpus)",
        short="citation quartile", order=CITE_ORDER,
        labels=_qlabels(e_c, lambda v: f"{int(v)}") if e_c else {},
        outdir=f"{out_root}/by_visibility",
        key=lambda m: qbin(m.get("cites"), e_c),
        notes=[f"Citation counts for {n_c:,} of {N:,} events ({100*n_c/N:.1f}%): every "
               "event with a paper link that resolved at Semantic Scholar (primary) or "
               f"OpenAlex (fallback), one snapshot taken {SNAPSHOT}. Quartile edges over "
               f"all {n_c:,} events: Q1 <= {int(e_c[0])}, Q2 <= {int(e_c[1])}, "
               f"Q3 <= {int(e_c[2])}, Q4 > {int(e_c[2])}." if e_c else "no counts",
               "", "Raw counts favour older events: an Apr-Aug 2026 extension event has "
               "had a few months to be cited, a Jan 2024 event has had two and a half "
               "years. Read this table together with the citation-rate version (A5.2b), "
               "which divides by months since the first-observable date.", "", cellnote])
    R["vis_rate"] = dict(
        title="A5.2b -- performance by citation rate (citations per month since first observable, whole corpus)",
        short="citation-rate quartile", order=CITE_ORDER,
        labels=_qlabels(e_r, lambda v: f"{v:.2f}/mo") if e_r else {},
        outdir=f"{out_root}/by_vis_rate",
        key=lambda m: qbin(m.get("cite_rate"), e_r),
        notes=[f"Citation rate = citations / max(1, months from first-observable month to "
               f"the {SNAPSHOT} snapshot), for the same {n_r:,} events as A5.2. Quartile "
               f"edges: Q1 <= {e_r[0]:.2f}, Q2 <= {e_r[1]:.2f}, Q3 <= {e_r[2]:.2f}, "
               f"Q4 > {e_r[2]:.2f} citations per month." if e_r else "no rates",
               "", "This is the age-adjusted visibility measure and the one we treat as "
               "primary: it puts a 2026 extension event and a 2024 event on the same "
               "footing.", "", cellnote])
    R["latency"] = dict(
        title="A5.3 -- performance by publication latency (months publicly observable before the journal version)",
        short="publication latency", order=LAT_OBS_ORDER,
        labels={s: s for s in LAT_OBS_ORDER}, outdir=f"{out_root}/by_latency",
        key=lambda m: edge_bin(m.get("lat_obs"), LAT_OBS_BINS),
        notes=[f"Latency = Crossref online-publication month of the journal version minus "
               f"CUSP's first-observable month (`publication_date`, which the build "
               f"pipeline set to the earliest date found across Crossref, bioRxiv, "
               f"medRxiv, Semantic Scholar and Europe PMC). Computable for {n_lo:,} "
               f"journal events (Nature, Science, Cell; both halves), i.e. every journal "
               f"event whose DOI resolved at Crossref on {SNAPSHOT}. arXiv events have no "
               "journal version and are excluded by construction; leaderboard items have "
               "no paper.",
               "", "0 mo means no earlier public trace was found: the first observable "
               "date is the journal's own online date. Larger values mean a preprint or "
               "other public record predated the journal version by that many months.",
               "", cellnote])
    R["lat_review"] = dict(
        title="A5.3b -- performance by editorial latency (received -> online, Nature and Science)",
        short="editorial latency", order=LAT_REVIEW_ORDER,
        labels={s: s for s in LAT_REVIEW_ORDER}, outdir=f"{out_root}/by_lat_review",
        key=lambda m: edge_bin(m.get("lat_review"), LAT_REVIEW_BINS),
        notes=[f"Editorial latency = Crossref online-publication month minus the "
               f"manuscript-received month deposited by the publisher. Nature and Science "
               f"deposit received dates; Cell (Elsevier) does not, so this covers "
               f"{n_lr:,} Nature and Science events. This measures how long the result "
               "sat in peer review, a different construct from A5.3.", "", cellnote])
    R["legacy_visibility"] = dict(
        title="LEGACY A5.2 (first pass) -- citation quartile over the 481 pinned-subset events",
        short="citation quartile (legacy 481)", order=CITE_ORDER,
        labels=_qlabels(e_l, lambda v: f"{int(v)}") if e_l else {},
        outdir=f"{out_root}/by_legacy/visibility_481",
        key=lambda m: cite_bin(m.get("citations"), e_l),
        notes=[f"Superseded by A5.2 / A5.2b. Kept so the first-pass tables and the "
               f"S19-S23 fold-in remain reproducible: {n_leg_c} events, Semantic Scholar, "
               f"retrieved {CITE_RETRIEVED}, original half only.", "", cellnote])
    R["legacy_latency"] = dict(
        title="LEGACY A5.3 (first pass) -- extension latency over 708 events",
        short="publication latency (legacy 708)", order=LATENCY_ORDER,
        labels={s: s for s in LATENCY_ORDER}, outdir=f"{out_root}/by_legacy/latency_708",
        key=lambda m: latency_bin(m.get("latency")),
        notes=[f"Superseded by A5.3. original_publication_date - first_date_found over "
               f"{n_leg_l} extension events; for 96% of them first_date_found is the "
               "Crossref record-creation date, so this mostly measured online-first "
               "versus print-issue scheduling.", "", cellnote])
    return R


DIMS_MAIN = ["source", "visibility", "vis_rate", "latency", "lat_review"]
DIMS_ALL = DIMS_MAIN + ["legacy_visibility", "legacy_latency"]
