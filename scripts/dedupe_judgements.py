#!/usr/bin/env python3
"""
dedupe_judgements.py — collapse duplicate judgements to one per event.

Handles both judge stages. Concurrent judges twice ended up writing to the same
output file -- once when an older driver was still alive during stage 1, once
when a throughput probe overlapped a running job during stage 2. Writes are
line-atomic so nothing is corrupt, but some events were judged twice.

Those duplicates are independent re-judgements of the same item, so they
measure the judge rather than waste the calls, and both stages are reported:

  stage 1 (leakage): agreement on a three-way verdict
  stage 2 (rubric):  agreement on frq_score, a continuous 0-10 mean of four
                     dimensions -- a far harder target, so it is reported as
                     exact / within +/-0.5 / within +/-1.0 plus correlation,
                     not as a single agreement percentage

Keeps the FIRST judgement per event id (deterministic given file order).
"""

from __future__ import annotations

import argparse, json, os, sys
from collections import Counter, defaultdict


def dedupe(path, out_path=None, report=True):
    rows, bad = [], 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1

    by_id = defaultdict(list)
    for r in rows:
        by_id[r["id"]].append(r)

    dupes = {k: v for k, v in by_id.items() if len(v) > 1}
    agree = disagree = 0
    disagreements = []
    score_pairs = []
    for k, v in dupes.items():
        # stage 2: collect paired frq_score for the reproducibility stats
        sc = [x["frq"]["frq_score"] for x in v
              if isinstance(x.get("frq"), dict) and x["frq"].get("frq_score") is not None]
        if len(sc) > 1:
            score_pairs.append((float(sc[0]), float(sc[1])))
        # stage 1: three-way verdict agreement
        verdicts = {x.get("leakage", {}).get("verdict") for x in v
                    if isinstance(x.get("leakage"), dict)}
        if not verdicts:
            continue
        if len(verdicts) == 1:
            agree += 1
        else:
            disagree += 1
            disagreements.append({"id": k, "verdicts": sorted(map(str, verdicts))})

    kept = []
    seen = set()
    for r in rows:                      # preserve original order, keep first
        if r["id"] not in seen:
            seen.add(r["id"])
            kept.append(r)

    if report:
        print(f"{os.path.basename(path)}")
        print(f"  lines {len(rows)}  corrupt {bad}  unique events {len(kept)}")
        if dupes:
            n = agree + disagree
            if n:
                print(f"  events judged twice: {n}")
                print(f"  leakage self-consistency: {agree}/{n} = {100*agree/n:.1f}% "
                      f"identical verdict on an independent re-judgement")
                for d in disagreements[:5]:
                    print(f"    disagreed: {d['id']} -> {d['verdicts']}")
            if score_pairs:
                import statistics as _st
                m = len(score_pairs)
                diffs = [abs(a - b) for a, b in score_pairs]
                ex = sum(1 for d in diffs if d == 0)
                w5 = sum(1 for d in diffs if d <= 0.5)
                w1 = sum(1 for d in diffs if d <= 1.0)
                print(f"  rubric re-grading: {m} items scored twice")
                print(f"    exact {100*ex/m:.0f}%   within +/-0.5 {100*w5/m:.0f}%   "
                      f"within +/-1.0 {100*w1/m:.0f}%   MAD {_st.mean(diffs):.3f}")
                print(f"    -> do not report FRQ differences below ~{_st.mean(diffs):.1f} "
                      f"as meaningful; that is the judge noise floor")

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            for r in kept:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if report:
            print(f"  wrote {out_path}")

    return {"path": path, "lines": len(rows), "corrupt": bad,
            "unique": len(kept), "judged_twice": agree + disagree,
            "agree": agree, "disagree": disagree,
            "disagreements": disagreements,
            "rubric_score_pairs": score_pairs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.out and len(a.files) > 1:
        sys.exit("--out takes a single input file")
    stats = []
    for p in a.files:
        out = a.out or (p if a.in_place else None)
        if a.in_place:
            tmp = p + ".dedup.tmp"
            s = dedupe(p, tmp)
            os.replace(tmp, p)
        else:
            s = dedupe(p, out)
        stats.append(s)
    tot = sum(s["judged_twice"] for s in stats)
    if tot:
        ag = sum(s["agree"] for s in stats)
        print(f"\nacross {len(stats)} file(s): {ag}/{tot} = {100*ag/tot:.1f}% "
              f"judge self-consistency")


if __name__ == "__main__":
    main()
