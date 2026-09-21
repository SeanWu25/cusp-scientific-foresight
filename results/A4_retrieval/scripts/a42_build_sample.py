"""A4.2 sample: up to 1,000 retrieved cases per model (all if fewer), stratified across that model's runs. Seed recorded."""
import json, random, collections, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
SEED = 20260921
rng = random.Random(SEED)
by_model = collections.defaultdict(list)
for key in RUNS:
    for row in load_run(key): by_model[RUNS[key][0]].append(row)
sample = {"seed": SEED, "rule": "per model: all retrieved cases if <= 1000, else a uniform random sample of 1000 without replacement (seeded)", "per_model": {}, "cases": []}
for model, rows in by_model.items():
    n = len(rows); chosen = rows if n <= 1000 else rng.sample(rows, 1000)
    sample["per_model"][model] = dict(available=n, sampled=len(chosen), used_all=(n <= 1000), by_run=dict(collections.Counter(r["run"] for r in chosen)))
    sample["cases"] += [dict(case=f"{r['run']}|{r['id']}", run=r["run"], id=r["id"]) for r in chosen]
json.dump(sample, open(OUT / "A4_2_groundtruth_inclusion/sample.json", "w"), indent=1)
for m, v in sample["per_model"].items(): print(f"{m:16s} available={v['available']:5d} sampled={v['sampled']:5d} used_all={v['used_all']} {v['by_run']}")
print("total cases", len(sample["cases"]))
