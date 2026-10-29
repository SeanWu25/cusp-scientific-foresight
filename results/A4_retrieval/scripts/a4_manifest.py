"""Build results/A4_retrieval/MANIFEST.json: models and snapshot ids, dates, seeds, prompt hashes, token usage and list-price cost, git SHA."""
import json, hashlib, subprocess, inspect, collections, sys, os
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
sys.path.insert(0, str(ROOT / "scripts")); import web_search as W, a42_judge as J
PRICES = {"claude-sonnet-5": (2, 10), "claude-opus-4-8": (15, 75), "gpt-5.4-mini": (0.25, 2), "gpt-4o": (2.5, 10), "gpt-4o-2024-11-20": (2.5, 10), "gpt-5.4": (2.5, 15), "Llama-3.3-70B-Instruct": (0.71, 0.71),
          "claude-sonnet-4-5-20250929": (3, 15), "gpt-5.6-sol": (4, 20)}
def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
def usage_of(path, key_model=None):
    tin = tout = n = 0; snaps = collections.Counter()
    for l in open(path):
        r = json.loads(l)
        if r.get("fatal_error"): continue
        n += 1
        if "judge" in r and r["judge"] and r["judge"].get("usage"): tin += r["judge"]["usage"]["input"]; tout += r["judge"]["usage"]["output"]
        for t in ("binary", "binary_perturbed", "mcq", "frq", "date"):
            tin += r.get(f"{t}_input_tokens") or 0; tout += r.get(f"{t}_output_tokens") or 0
            if r.get(f"{t}_model_snapshot"): snaps[r[f"{t}_model_snapshot"]] += 1
    return dict(records=n, input_tokens=tin, output_tokens=tout, snapshots=dict(snaps))
git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
m = dict(created_utc=__import__("datetime").datetime.utcnow().isoformat(), git_sha=git, repo=str(ROOT),
         a4_1=dict(verified_files={"scripts/web_search.py": sha(open(ROOT / "scripts/web_search.py").read()), "scripts/test_LLM.py": sha(open(ROOT / "scripts/test_LLM.py").read()), "scripts/run_cusp.py": sha(open(ROOT / "scripts/run_cusp.py").read())}),
         a4_2=dict(seed=json.load(open(OUT / "A4_2_groundtruth_inclusion/sample.json"))["seed"], judge_model=J.JUDGE_MODEL, judge_prompt_sha=sha(J.JUDGE_PROMPT), retrieval_api="you.com search.unified", runs={k: dict(model=v[0], condition=v[1], dataset=v[2], predictions=str(v[3]), mechanism=v[4], freshness_to=v[5] or v[6]) for k, v in RUNS.items()},
                   usage=usage_of(OUT / "A4_2_groundtruth_inclusion/verdicts.jsonl")),
         a4_3=dict(query_prompt_sha=sha(inspect.getsource(W._generate_combined_query)), evidence_bounds=[p.stem for p in sorted((OUT / "A4_3_fixed_queries/evidence").glob("*.jsonl"))], mcq_permutation_seed=42, harness="scripts/run_cusp.py process_row (unmodified)", scoring="scripts/build_report.py (scoring_v1)"))
q = collections.Counter(json.loads(l).get("query_model") for l in open(OUT / "A4_3_fixed_queries/queries.jsonl") if '"query"' in l); m["a4_3"]["query_models"] = dict(q)
mo = OUT / "A4_3_fixed_queries/model_outputs.jsonl"
if mo.exists():
    per = collections.defaultdict(lambda: dict(records=0, input_tokens=0, output_tokens=0, snapshots=collections.Counter()))
    for l in open(mo):
        r = json.loads(l)
        if r.get("fatal_error"): continue
        k = f"{r['model_key']}|{r['condition']}"; per[k]["records"] += 1; per[k]["model"] = r.get("model")
        for t in ("binary", "binary_perturbed", "mcq", "frq", "date"):
            per[k]["input_tokens"] += r.get(f"{t}_input_tokens") or 0; per[k]["output_tokens"] += r.get(f"{t}_output_tokens") or 0
            if r.get(f"{t}_model_snapshot"): per[k]["snapshots"][r[f"{t}_model_snapshot"]] += 1
    tot = 0
    for k, v in per.items():
        v["snapshots"] = dict(v["snapshots"]); pr = PRICES.get(v.get("model"), (0, 0)); v["usd_list_price"] = round((v["input_tokens"] * pr[0] + v["output_tokens"] * pr[1]) / 1e6, 2); tot += v["usd_list_price"]
    m["a4_3"]["model_runs"] = per; m["a4_3"]["usd_list_price_total_model_runs"] = round(tot, 2)
if (OUT / "A4_3_fixed_queries/inclusion_verdicts.jsonl").exists(): m["a4_3"]["inclusion_usage"] = usage_of(OUT / "A4_3_fixed_queries/inclusion_verdicts.jsonl")
u = m["a4_2"]["usage"]; m["a4_2"]["usd_list_price_judge"] = round((u["input_tokens"] * 2 + u["output_tokens"] * 10) / 1e6, 2)
m["notes"] = ["Prices are list prices, not invoice figures.", "You.com calls: A4.2 = one per You.com-run case; A4.3 = 500 events x 7 bounds; $5 per 1,000 calls list price."]
json.dump(m, open(OUT / "MANIFEST.json", "w"), indent=1, default=str); print(json.dumps({k: m[k] for k in ("git_sha",)}, indent=0)); print("manifest written")
