#!/usr/bin/env python3
"""
a5_summarize.py -- headline numbers from the A5 CSVs.

Pooled means across models are computed ONLY over models that have every
stratum unsuppressed. Averaging whatever cells survive suppression compares
different model sets in different columns and manufactures trends that are not
there -- on the citation quartiles the naive version produced a clean monotone
decline in MCQ and FRQ that disappears once the panel is balanced.
"""
import csv, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
sys.path.insert(0, HERE); import a5_common as C

META, _ = C.load_meta()
REG = C.dim_registry(META, OUT)
DIMS = [(d, [REG[d]["labels"].get(x, x) for x in REG[d]["order"]]) for d in C.DIMS_ALL]


def load(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def balanced(rows, part, task, order):
    """(models, {stratum: mean}) over models carrying every stratum; else None."""
    sub = [r for r in rows if r["partition"] == part and r["task"] == task
           and r["suppressed"] == "0"]
    bym = defaultdict(dict)
    for r in sub:
        bym[r["model"]][r["stratum"]] = float(r["statistic"])
    full = [m for m, d in bym.items() if all(s in d for s in order)]
    if not full:
        return None
    return full, {s: sum(bym[m][s] for m in full) / len(full) for s in order}


def main():
    for dim, order in DIMS:
        tests = load(f"{REG[dim]['outdir']}/{dim}_tests.csv")
        cells = load(f"{REG[dim]['outdir']}/{dim}_cells.csv")
        if not tests:
            print(f"\n##### {dim}: no tests"); continue
        print(f"\n##### {dim.upper()}  ({len(cells)} cells, {len(tests)} tests)")
        for part in ("pre", "post", "overall"):
            tp = [t for t in tests if t["partition"] == part]
            if not tp:
                continue
            bt = defaultdict(lambda: [0, 0])
            for t in tp:
                bt[t["task"]][0] += 1
                if float(t["p_holm"]) < 0.05:
                    bt[t["task"]][1] += 1
            n_sig = sum(v[1] for v in bt.values())
            print(f"  {part:8s}: {len(tp):3d} tests, {n_sig:3d} Holm-significant   "
                  + "  ".join(f"{k}:{v[1]}/{v[0]}" for k, v in sorted(bt.items())))
        for part in ("post", "overall"):
            print(f"  --- {part}-cutoff, mean across models carrying EVERY stratum ---")
            for task in ("binary", "mcq", "date", "frq"):
                b = balanced(cells, part, task, order)
                if not b:
                    print(f"    {task:7s} (no model carries every stratum)")
                    continue
                models, means = b
                print(f"    {task:7s} [{len(models)} models] "
                      + "  ".join(f"{s}={v:.3f}" for s, v in means.items()))
        tp = sorted([t for t in tests if t["partition"] == "post"],
                    key=lambda t: -float(t["range"]))[:5]
        print("  largest post-cutoff ranges:")
        for t in tp:
            print(f"    {t['model']:17s} {t['task']:7s} range={float(t['range']):+.3f}  "
                  f"{t['min_stratum']} -> {t['max_stratum']}  p_holm={float(t['p_holm']):.4f}")


if __name__ == "__main__":
    main()
