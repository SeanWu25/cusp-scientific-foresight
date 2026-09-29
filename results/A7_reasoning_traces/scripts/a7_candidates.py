"""a7_candidates.py — surface candidate codebook examples for ONE code, restricted to the
Artificial Intelligence / Materials Science areas (keeps the published codebook's examples in
neutral technical territory). Prints trace_id + a short excerpt. Usage: a7_candidates.py CODE [n]"""
import re, sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C
from a7_screen import PAT
from a7_inductive import FEAT
code, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8
task = sys.argv[3] if len(sys.argv) > 3 else None
AREAS = {"Artificial Intelligence", "Materials Science", "Physics"}
hits = []
for r in C.iter_traces(lambda r: r["condition"] == "base" and r["main_area"] in AREAS and not r["trace_is_raw_json"] and 15 <= r["trace_words"] <= 120):
    if task and r["task"] != task: continue
    ok = re.search(PAT[code], r["trace"], re.I) if code in PAT else FEAT[code](r)
    if ok: hits.append(r)
rng = random.Random(5)
print(f"{len(hits)} candidates for {code}" + (f" / {task}" if task else ""))
for r in rng.sample(hits, min(n, len(hits))):
    print(f"\n--- {r['trace_id']} [{r['task']}|{r['main_area']}|correct={r['correct']}|ans={r.get('parsed_answer')}|gt={r.get('ground_truth')}]\n{r['trace'][:340]}")
