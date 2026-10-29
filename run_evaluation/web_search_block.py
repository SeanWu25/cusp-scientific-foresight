#!/usr/bin/env python3
"""
web_search_block.py — Tables S2 / S3: base vs WS+Cutoff vs WS, with deltas, SEs
and p-values, using the same tests the published tables use.

Test selection mirrors compare_web_search.py exactly:
  binary / binary_perturbed / mcq / date_exact  -> McNemar, continuity-corrected,
                                                   exact binomial when discordant n < 25
  frq / date score / overall                    -> paired t-test (scipy.stats.ttest_rel)
SE is the normal-approximation SE of the mean, as in the published generator.
Pairing is by event id over the ids shared by all three conditions.

Unlike the published table this one prints n for every row, and suppresses a
comparison below --min-n instead of reporting a point estimate.
"""

from __future__ import annotations

import argparse, json, math, os, statistics, sys

try:
    from scipy import stats
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False

ROWS = [
    ("Binary (original)",  "binary",           "score",          "mcnemar"),
    ("Binary (perturbed)", "binary_perturbed", "score",          "mcnemar"),
    ("MCQ",                "mcq",              "score",          "mcnemar"),
    ("FRQ score (0-10)",   "frq",              "score",          "ttest"),
    ("Date score (0-1)",   "date",             "score",          "ttest"),
    ("Date exact match",   "date",             "exact_match",    "mcnemar"),
    ("Date month error",   "date",             "month_distance", "ttest"),
]


def load(path, drop_failed=True):
    rep = json.load(open(path, encoding="utf-8"))
    out = {}
    for r in rep.get("results", []):
        if drop_failed and r.get("retrieval_failed"):
            continue
        out[r["id"]] = r
    return out


def val(rec, task, field):
    t = (rec.get("tasks") or {}).get(task)
    if not t or t.get("skipped"):
        return None
    v = t.get(field)
    if v is None:
        return None
    return float(v) if not isinstance(v, bool) else float(int(v))


def mcnemar(a, b):
    """Continuity-corrected McNemar; exact binomial when discordant n < 25."""
    n01 = sum(1 for x, y in zip(a, b) if x == 0 and y == 1)
    n10 = sum(1 for x, y in zip(a, b) if x == 1 and y == 0)
    nd = n01 + n10
    if nd == 0:
        return float("nan"), float("nan")
    if not HAVE_SCIPY:
        return float("nan"), float("nan")
    if nd < 25:
        p = 2 * min(stats.binom.cdf(min(n01, n10), nd, 0.5),
                    1 - stats.binom.cdf(max(n01, n10) - 1, nd, 0.5))
        return (n01 - n10) ** 2 / nd, float(min(p, 1.0))
    chi2 = (abs(n01 - n10) - 1.0) ** 2 / nd
    return chi2, float(stats.chi2.sf(chi2, df=1))


def ttest(a, b):
    if not HAVE_SCIPY or len(a) < 3:
        return float("nan"), float("nan")
    t, p = stats.ttest_rel(a, b)
    return float(t), float(p)


def stars(p):
    if p != p:
        return ""
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--wscut", required=True)
    ap.add_argument("--ws", required=True)
    ap.add_argument("--label", default="Claude Sonnet 5")
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--cutoff", default="2026-01")
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--post-only", action="store_true",
                    help="restrict to post-cutoff instances (the Delta-decomposition view)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if not HAVE_SCIPY:
        print("WARNING: scipy unavailable — p-values will be NaN", file=sys.stderr)

    pub = {}
    for l in open(a.benchmark, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            pub[r["id"]] = r.get("publication_date", "")

    B = load(a.base, drop_failed=False)
    C = load(a.wscut)
    W = load(a.ws)
    ids = sorted(set(B) & set(C) & set(W))
    if a.post_only:
        ids = [i for i in ids if pub.get(i, "") > a.cutoff]
    print(f"{a.label}: shared ids={len(ids)}"
          f"{'  (post-cutoff only)' if a.post_only else ''}\n")

    out = {"label": a.label, "post_only": a.post_only, "n_shared_ids": len(ids),
           "min_n": a.min_n, "rows": {}}
    hdr = (f"{'Metric':22s}{'n':>6s}{'base (mean+/-SE)':>22s}"
           f"{'WS+Cutoff  delta (p)':>30s}{'WS  delta (p)':>30s}")
    print(hdr)
    print("-" * len(hdr))
    for label, task, field, test in ROWS:
        b, c, w = [], [], []
        for i in ids:
            vb, vc, vw = val(B[i], task, field), val(C[i], task, field), val(W[i], task, field)
            if vb is None or vc is None or vw is None:
                continue
            b.append(vb); c.append(vc); w.append(vw)
        n = len(b)
        cell = {"n": n}
        if n < a.min_n:
            cell["suppressed"] = True
            out["rows"][label] = cell
            print(f"{label:22s}{n:6d}{'  [suppressed, n<'+str(a.min_n)+']':>22s}"
                  f"{'--':>30s}{'--':>30s}")
            continue
        mb = statistics.fmean(b)
        se = statistics.stdev(b) / math.sqrt(n) if n > 1 else float("nan")
        parts = []
        for name, arr in (("wscut", c), ("ws", w)):
            d = statistics.fmean(arr) - mb
            if test == "mcnemar":
                _, p = mcnemar([int(round(x)) for x in b], [int(round(x)) for x in arr])
            else:
                _, p = ttest(b, arr)
            diffs = [x - y for x, y in zip(arr, b)]
            dse = statistics.stdev(diffs) / math.sqrt(n) if n > 1 else float("nan")
            cell[name] = {"mean": statistics.fmean(arr), "delta": d,
                          "delta_se": dse, "p": p,
                          "ci": (d - 1.96 * dse, d + 1.96 * dse)}
            ptxt = "  n/a " if p != p else (f"p<0.001" if p < 0.001 else f"p={p:.3f}")
            parts.append(f"{d:+.3f}+/-{dse:.3f} ({ptxt} {stars(p)})")
        cell["base_mean"] = mb
        cell["base_se"] = se
        cell["test"] = test
        out["rows"][label] = cell
        print(f"{label:22s}{n:6d}{f'{mb:.3f}+/-{se:.3f}':>22s}"
              f"{parts[0]:>30s}{parts[1]:>30s}")

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
