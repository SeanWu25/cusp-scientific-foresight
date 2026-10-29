"""a7_inductive_sample.py — 300 base-condition traces stratified across model x task x correctness
(10 x 5 x 2 = 100 cells, 3 per cell, seed 7). Written to inductive_sample.jsonl for the inductive pass."""
import json, random, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C
SEED = 7
cells = collections.defaultdict(list)
for r in C.iter_traces(lambda r: r["condition"] == "base" and r["correct"] is not None and not r["trace_is_raw_json"] and 8 <= r["trace_words"] <= 400):
    cells[(r["model"], r["task"], r["correct"])].append(r)
rng = random.Random(SEED); out = []
for key in sorted(cells):
    pool = sorted(cells[key], key=lambda r: r["trace_id"])
    out += rng.sample(pool, min(3, len(pool)))
with open(C.STUDY / "inductive_sample.jsonl", "w", encoding="utf-8") as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out), "traces from", len(cells), "cells; seed", SEED)
