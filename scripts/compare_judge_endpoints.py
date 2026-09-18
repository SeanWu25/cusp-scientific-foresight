#!/usr/bin/env python3
"""
compare_judge_endpoints.py — is the OpenAI-direct judge interchangeable with the
Azure deployment that produced the six published models?

Compares paired judgements of the SAME FRQ responses by the SAME judge model id
on the two serving stacks. The question is whether swapping the endpoint is a
judge-configuration change or a no-op.
"""
from __future__ import annotations
import argparse, collections, json, math, statistics


def load(p):
    out = {}
    for l in open(p, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            out[r["id"]] = r
    return out


def paired(a, b, get):
    xs, ys = [], []
    for k in set(a) & set(b):
        va, vb = get(a[k]), get(b[k])
        if va is not None and vb is not None:
            xs.append(va); ys.append(vb)
    return xs, ys


def report(name, xs, ys):
    n = len(xs)
    if n < 2:
        print(f"  {name:16s} n={n} (too few)"); return
    d = [y - x for x, y in zip(xs, ys)]
    md = statistics.fmean(d)
    sd = statistics.stdev(d)
    se = sd / math.sqrt(n)
    t = md / se if se else float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    # Pearson r
    sx, sy = statistics.pstdev(xs), statistics.pstdev(ys)
    r = (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n / (sx * sy)) if sx and sy else float("nan")
    flag = "" if abs(t) < 1.96 else "   <-- DIFFERS (|t|>1.96)"
    print(f"  {name:16s} n={n:4d}  azure={mx:6.3f}  openai={my:6.3f}  "
          f"delta={md:+6.3f} +/-{1.96*se:.3f}  t={t:+5.2f}  r={r:.3f}{flag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--azure", required=True)
    ap.add_argument("--openai", required=True)
    a = ap.parse_args()
    A, O = load(a.azure), load(a.openai)
    shared = set(A) & set(O)
    print(f"azure judgements={len(A)}  openai judgements={len(O)}  paired={len(shared)}\n")

    print("FRQ rubric (paired, per-dimension):")
    for d in ("frq_score", "alignment", "specificity", "novelty", "feasibility"):
        xs, ys = paired(A, O, lambda r, d=d: (r.get("frq") or {}).get(d))
        report(d, xs, ys)

    print("\nLeakage verdicts:")
    ca = collections.Counter((A[k].get("leakage") or {}).get("verdict") for k in shared)
    co = collections.Counter((O[k].get("leakage") or {}).get("verdict") for k in shared)
    print(f"  azure : {dict(ca)}")
    print(f"  openai: {dict(co)}")
    agree = sum(1 for k in shared
                if (A[k].get("leakage") or {}).get("verdict")
                == (O[k].get("leakage") or {}).get("verdict"))
    print(f"  verdict agreement: {agree}/{len(shared)} ({100*agree/max(len(shared),1):.1f}%)")
    xs, ys = paired(A, O, lambda r: (r.get("leakage") or {}).get("score"))
    report("leakage_score", xs, ys)

    print("\nWeb search actually used:")
    for lbl, D in (("azure", A), ("openai", O)):
        f = sum(1 for k in shared if (D[k].get("frq") or {}).get("web_search_used"))
        g = sum(1 for k in shared if (D[k].get("leakage") or {}).get("web_search_used"))
        ns = [(D[k].get("frq") or {}).get("n_web_searches", 0) for k in shared]
        print(f"  {lbl:7s} frq={f}/{len(shared)}  leakage={g}/{len(shared)}  "
              f"mean searches/frq={statistics.fmean(ns) if ns else 0:.2f}")

    print("\nLatency (s per FRQ response, both judge calls):")
    for lbl, D in (("azure", A), ("openai", O)):
        t = [D[k].get("frq_judge_s", 0) + D[k].get("leakage_judge_s", 0) for k in shared]
        if t:
            print(f"  {lbl:7s} mean={statistics.fmean(t):6.1f}  median={statistics.median(t):6.1f}")


if __name__ == "__main__":
    main()
