"""a7_screen_counts.py — keyword-screen PREVALENCE only (no trace text printed).
Gives an upper bound on how often each deductive code could fire, to size the codebook."""
import re, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C
from a7_screen import PAT
n = collections.Counter(); hit = collections.Counter(); bytask = collections.defaultdict(collections.Counter)
for r in C.iter_traces(lambda r: r["condition"] == "base" and not r["trace_is_raw_json"]):
    n["all"] += 1; n[r["task"]] += 1
    for k, p in PAT.items():
        if re.search(p, r["trace"], re.I):
            hit[k] += 1; bytask[k][r["task"]] += 1
print(f"base traces screened: {n['all']}")
print(f"{'code':26s} {'overall':>8s} " + " ".join(f"{t:>10s}" for t in C.TASKS))
for k in PAT:
    print(f"{k:26s} {100*hit[k]/n['all']:7.1f}% " + " ".join(f"{100*bytask[k][t]/max(1,n[t]):9.1f}%" for t in C.TASKS))
