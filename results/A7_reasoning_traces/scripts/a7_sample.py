"""a7_sample.py — the coding sample. Stratified, frozen, seed 13. Writes coding_sample.jsonl
(trace ids + stratum labels only; the text is joined from traces.jsonl at coding time).

Three strata, chosen so every analysis in the plan has power where it needs it:
  MAIN   base condition, both halves, capped per (model, task, partition) — analyses A, B, E, G
  DATE   extra base date traces per model                                 — analysis C (priority)
  PAIRED pinned-500 events present under base AND ws_cutoff AND ws for the
         same (model, task), all three conditions kept together           — analysis F
"""
import json, random, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C

SEED = 13
CAP_MAIN = 80           # per (model, task, partition)
CAP_DATE = 300          # per model, base date traces in total (MAIN included)
PAIRED_EVENTS = 30      # per (model, task): events kept as complete base/ws_cutoff/ws triples
MIN_WORDS = 5

rng = random.Random(SEED)
traces = {}
for r in C.iter_traces():
    if r["trace_words"] < MIN_WORDS or r["trace_is_raw_json"]:
        continue
    traces[r["trace_id"]] = r

pick, strata = {}, collections.defaultdict(list)


def add(r, stratum):
    pick.setdefault(r["trace_id"], set()).add(stratum)


# ---- MAIN
cells = collections.defaultdict(list)
for r in traces.values():
    if r["condition"] == "base" and r["graded"]:
        cells[(r["model"], r["task"], r["partition"])].append(r)
for k in sorted(cells, key=lambda k: tuple(map(str, k))):
    pool = sorted(cells[k], key=lambda r: r["trace_id"])
    for r in rng.sample(pool, min(CAP_MAIN, len(pool))):
        add(r, "MAIN")

# ---- DATE boost
dcells = collections.defaultdict(list)
for r in traces.values():
    if r["condition"] == "base" and r["task"] == "date" and r["graded"]:
        dcells[r["model"]].append(r)
for m in sorted(dcells):
    have = [r for r in dcells[m] if r["trace_id"] in pick]
    rest = sorted((r for r in dcells[m] if r["trace_id"] not in pick), key=lambda r: r["trace_id"])
    for r in rng.sample(rest, min(max(0, CAP_DATE - len(have)), len(rest))):
        add(r, "DATE")

# ---- PAIRED
by = collections.defaultdict(dict)
for r in traces.values():
    if r["in_subset500"] and r["half"] == "orig":
        by[(r["model"], r["task"], r["id"])][r["condition"]] = r
trip = collections.defaultdict(list)
for k, d in by.items():
    if {"base", "ws_cutoff", "ws"} <= set(d):
        trip[(k[0], k[1])].append(k[2])
for k in sorted(trip, key=lambda k: (k[0], k[1])):
    ev = sorted(trip[k])
    for e in rng.sample(ev, min(PAIRED_EVENTS, len(ev))):
        for cond in ("base", "ws_cutoff", "ws"):
            add(by[(k[0], k[1], e)][cond], "PAIRED")

out = []
for tid, st in pick.items():
    r = traces[tid]
    out.append(dict(trace_id=tid, strata=sorted(st), model=r["model"], task=r["task"], condition=r["condition"],
                    half=r["half"], partition=r["partition"], id=r["id"], trace_words=r["trace_words"]))
out.sort(key=lambda r: r["trace_id"])
with open(C.STUDY / "coding_sample.json", "w", encoding="utf-8") as f:
    json.dump(dict(seed=SEED, cap_main=CAP_MAIN, cap_date=CAP_DATE, paired_events=PAIRED_EVENTS,
                   min_words=MIN_WORDS, n=len(out), traces=out), f, indent=1)
c = collections.Counter(s for r in out for s in r["strata"])
print(f"coding sample: {len(out)} unique traces  (stratum membership: {dict(c)})")
print("by task:", dict(collections.Counter(r["task"] for r in out)))
print("by condition:", dict(collections.Counter(r["condition"] for r in out)))
print("by model:", dict(collections.Counter(r["model"] for r in out)))
print("paired complete triples:", sum(len(v[:PAIRED_EVENTS]) for v in trip.values()))
