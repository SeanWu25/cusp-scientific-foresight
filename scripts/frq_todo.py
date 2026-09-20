#!/usr/bin/env python3
"""
frq_todo.py — emit the subset of a predictions file still needing a rubric score.

judge_frq.py --resume treats an event as done if its id appears in the output
file at all. That is right for a fresh run, but wrong for filling gaps in a
file that already holds rows for every event -- rows whose stage-2 call failed
or returned no score carry the id and so get skipped forever.

This writes a filtered predictions JSONL containing only events that

    * have a judgeable FRQ answer (non-empty, not a refusal, not an error), and
    * have no frq_score in ANY of the existing judgement files given,

so it can be graded into a fresh output file with no resume conflict. The
existing and new files are then combined field-by-field by merge_judgements.py.
"""

from __future__ import annotations

import argparse, json, os, sys


def judgeable(row) -> bool:
    a = row.get("frq_answer")
    if a in (None, "", "None"):
        return False
    if row.get("frq_refusal"):
        return False
    if str(a).startswith("Error:"):
        return False
    return True


def scored_ids(paths) -> set:
    done = set()
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            f = r.get("frq")
            if isinstance(f, dict) and f.get("frq_score") is not None:
                done.add(r["id"])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--existing", action="append", default=[],
                    help="judgement file(s) whose frq_score rows count as done")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    done = scored_ids(a.existing)
    total = judg = todo = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for line in open(a.predictions, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            total += 1
            if not judgeable(r):
                continue
            judg += 1
            if r["id"] in done:
                continue
            todo += 1
            f.write(line if line.endswith("\n") else line + "\n")
    print(f"{os.path.basename(a.predictions)}: {total} rows, {judg} judgeable, "
          f"{len(done)} already scored, {todo} to do -> {a.out}")
    return 0 if todo else 3          # 3 = nothing to do; drivers can skip


if __name__ == "__main__":
    sys.exit(main())
