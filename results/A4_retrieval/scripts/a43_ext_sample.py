"""
A4.3 extension — 500 additional events for the fixed-evidence-packet experiment (total 1,000).

Why: in the first 500-event subset (pinned in results_sonnet5_run1/subset500_ids.txt, publication
months Jan 2024 - Mar 2026) only 31 events are post-cutoff for Claude Sonnet 5 (cutoff 2026-01) and
4 for GPT-5.6 Sol (cutoff 2026-02), so their post-cutoff cells are suppressed (n < 20).

Rule (seeded, no inference): pool = every CUSP event (original corpus + Apr-Aug 2026 extension) that
  (1) is not in the first subset,
  (2) has publication month > 2026-02 (so it is post-cutoff for EVERY evaluated model, including Sol),
  (3) has a stored base-condition record for all six evaluated models.
Draw 500 without replacement, stratified by publication month (proportional allocation, largest
remainder), uniform within month. Writes ext500/subset_ext500_ids.txt and ext500/sample.json.
"""
import json, sys, random, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a42_common import ROOT, OUT, SUBSET, load_events
sys.path.insert(0, str(ROOT / "run_evaluation")); import gap_decomposition as GD
SEED, N, MIN_MONTH = 20261018, 500, "2026-02"
EXT = ROOT / "results_extension_run2/reports"
BASES = {  # model_key: base reports (original corpus, extension corpus) — the Table 1 base runs
    "gpt4o": ["run_evaluation/frq_results/gpt_4o_reeval.json", EXT / "gpt4o_base.json"],
    "gpt54": ["run_evaluation/frq_results/gpt_5_4_eval.json", EXT / "gpt54_base.json"],
    "llama33": ["run_evaluation/frq_results/llama_3_3_full.json", EXT / "llama33_base.json"],
    "claude45": ["run_evaluation/frq_results/claude_sonnet.json", EXT / "sonnet45_base.json"],
    "sonnet5": ["results_sonnet5_run1/reports/base_medium_run1.json", EXT / "sonnet5_base_run1.json"],
    "sol": ["results_sol_run1/reports/base_medium_run1.json", EXT / "sol_base.json"],
}
D = OUT / "A4_3_fixed_queries/ext500"
def main():
    ev = load_events(); first = {l.strip() for l in open(SUBSET) if l.strip()}
    have = {m: set().union(*(GD.load(str(ROOT / p), drop_retrieval_failures=False) for p in ps)) for m, ps in BASES.items()}
    pool = sorted(i for i, r in ev.items() if i not in first and r["publication_date"][:7] > MIN_MONTH and all(i in have[m] for m in have))
    by_m = collections.defaultdict(list)
    for i in pool: by_m[ev[i]["publication_date"][:7]].append(i)
    quota = {m: N * len(v) / len(pool) for m, v in by_m.items()}; alloc = {m: int(q) for m, q in quota.items()}
    for m in sorted(quota, key=lambda m: -(quota[m] - alloc[m]))[: N - sum(alloc.values())]: alloc[m] += 1
    rng = random.Random(SEED); chosen = []
    for m in sorted(by_m): chosen += rng.sample(by_m[m], alloc[m])
    D.mkdir(parents=True, exist_ok=True)
    (D / "subset_ext500_ids.txt").write_text("\n".join(sorted(chosen)) + "\n")
    json.dump(dict(seed=SEED, n=len(chosen), rule=__doc__.split("Rule")[1].strip(), pool=len(pool), pool_by_month={m: len(v) for m, v in sorted(by_m.items())},
                   sample_by_month=dict(sorted(alloc.items())), sample_by_area=dict(collections.Counter(ev[i]["main_area"] for i in chosen).most_common()),
                   pool_by_area=dict(collections.Counter(ev[i]["main_area"] for i in pool).most_common())), open(D / "sample.json", "w"), indent=1)
    print(f"pool {len(pool)}  sampled {len(chosen)}  by month {dict(sorted(alloc.items()))}")
if __name__ == "__main__": main()
