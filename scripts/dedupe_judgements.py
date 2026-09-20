#!/usr/bin/env python3
"""
dedupe_judgements.py — collapse duplicate leakage judgements to one per event.

Two judge drivers briefly wrote to the same output file concurrently. Writes
were line-atomic, so nothing is corrupt, but some events were judged twice.
Because the two judgements were independent calls on the same item, the
duplicates also measure the judge's self-consistency -- reported here rather
than discarded.

Keeps the FIRST judgement per event id (deterministic given file order) and
writes the agreement rate alongside.
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
    for k, v in dupes.items():
        verdicts = {x.get("leakage", {}).get("verdict") for x in v}
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
            print(f"  events judged twice: {n}")
            print(f"  judge self-consistency: {agree}/{n} = {100*agree/n:.1f}% "
                  f"identical verdict on an independent re-judgement")
            for d in disagreements[:5]:
                print(f"    disagreed: {d['id']} -> {d['verdicts']}")

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            for r in kept:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if report:
            print(f"  wrote {out_path}")

    return {"path": path, "lines": len(rows), "corrupt": bad,
            "unique": len(kept), "judged_twice": agree + disagree,
            "agree": agree, "disagree": disagree,
            "disagreements": disagreements}


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
