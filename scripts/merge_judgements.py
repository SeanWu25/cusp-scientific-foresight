#!/usr/bin/env python3
"""
merge_judgements.py — combine several judgement files into one row per event.

Field-level, not row-level. A run can end up with its stage-1 leakage verdict
in one file and its stage-2 rubric score in another (the rubric was deferred,
then filled in later from a todo subset), and a naive dedupe would keep one row
and silently lose the other stage. So for each event id:

    leakage  <- the first row carrying a leakage dict
    frq      <- the first row carrying a non-null frq_score
    everything else <- the first row seen

Input order is therefore a preference order: list the file you trust most
first. Rows with an frq dict but no score (a failed or refused grading) never
override a scored one regardless of order.
"""

from __future__ import annotations

import argparse, json, os, sys


def load(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def has_score(r):
    f = r.get("frq")
    return isinstance(f, dict) and f.get("frq_score") is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="judgement JSONL files, most trusted first")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    merged: dict[str, dict] = {}
    order: list[str] = []
    src_rows = 0
    for p in a.files:
        for r in load(p):
            src_rows += 1
            k = r.get("id")
            if not k:
                continue
            if k not in merged:
                merged[k] = dict(r)
                order.append(k)
                continue
            m = merged[k]
            if not isinstance(m.get("leakage"), dict) and isinstance(r.get("leakage"), dict):
                m["leakage"] = r["leakage"]
                for aux in ("leakage_attempts", "leakage_judge_s"):
                    if aux in r:
                        m[aux] = r[aux]
            if not has_score(m) and has_score(r):
                m["frq"] = r["frq"]
                for aux in ("frq_attempts", "frq_judge_s"):
                    if aux in r:
                        m[aux] = r[aux]
                m.pop("frq_error", None)
                m.pop("frq_skipped_reason", None)

    with open(a.out, "w", encoding="utf-8") as f:
        for k in order:
            f.write(json.dumps(merged[k], ensure_ascii=False) + "\n")

    n_leak = sum(1 for k in order if isinstance(merged[k].get("leakage"), dict))
    n_frq = sum(1 for k in order if has_score(merged[k]))
    print(f"{os.path.basename(a.out)}: {src_rows} source rows -> {len(order)} events; "
          f"leakage {n_leak}, rubric-scored {n_frq}")


if __name__ == "__main__":
    sys.exit(main())
