"""a7_manifest.py — MANIFEST.json: coders, snapshots, dates, seeds, costs, prompt hashes, git SHA."""
import json, subprocess, collections, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P
from a7_code import CODERS

git = lambda *a: subprocess.run(["git", *a], cwd=C.ROOT, capture_output=True, text=True).stdout.strip()
runs = {}
for f in sorted((C.STUDY / "raw").glob("*.jsonl")):
    key = f.stem
    n = 0; cost = 0.0; snaps = collections.Counter(); st = collections.Counter(); first = last = None
    tin = tout = cr = cw = 0
    for l in open(f, encoding="utf-8"):
        if not l.strip(): continue
        d = json.loads(l); n += 1; cost += d.get("cost_usd") or 0.0
        snaps[d.get("snapshot")] += 1
        st["error" if d.get("error") else "parse_error" if d.get("parse_error") else "ok"] += 1
        tin += d.get("input_tokens") or 0; tout += d.get("output_tokens") or 0
        cr += d.get("cache_read") or 0; cw += d.get("cache_write") or 0
        ts = d.get("timestamp"); first = min(first, ts) if first else ts; last = max(last, ts) if last else ts
    runs[key] = dict(n_records=n, api_reported_snapshots=dict(snaps), statuses=dict(st),
                     input_tokens=tin, output_tokens=tout, cache_read_tokens=cr, cache_write_tokens=cw,
                     started_utc=first, finished_utc=last, cost_usd_at_assumed_prices=round(cost, 2),
                     sha256=C.sha(open(f, encoding="utf-8").read()))
samp = json.load(open(C.STUDY / "coding_sample.json"))
ag = json.load(open(C.STUDY / "agreement.json"))
man = dict(
    study="A7 analysis of stated reasoning (Reviewer 2, C5)",
    created_utc=datetime.now(timezone.utc).isoformat(),
    git_sha=git("rev-parse", "HEAD"), git_branch=git("rev-parse", "--abbrev-ref", "HEAD"),
    git_dirty=git("status", "--porcelain", "--", "results/A7_reasoning_traces"),
    nature_of_traces=("in-answer 1-2 sentence justifications emitted in the same call as the answer; "
                      "no provider-native thinking text exists for any model in this panel (see inventory.md)"),
    n_traces_total=sum(1 for _ in open(C.STUDY / "traces.jsonl", encoding="utf-8")),
    coding_sample=dict(n=samp["n"], seed=samp["seed"], cap_main=samp["cap_main"], cap_date=samp["cap_date"],
                       paired_events=samp["paired_events"], min_words=samp["min_words"],
                       ids_sha256=C.sha("\n".join(sorted(r["trace_id"] for r in samp["traces"])))),
    coders={k: dict(display=v["name"], model=v["model"], provider=v["provider"],
                    reasoning_effort=v.get("reasoning_effort"),
                    price_usd_per_mtok=dict(input=v["price"][0], output=v["price"][1],
                                            source="assumed list prices, not verified against invoices"))
            for k, v in CODERS.items()},
    blinding=dict(enforced_by="a7_prompts.blind_view + assert_blind (template reconstruction + identity scan)",
                  tests="scripts/a7_test_blinding.py", forbidden_fields=sorted(C.FORBIDDEN_FOR_CODER)),
    prompts=dict(codebook_prompt_sha256=C.sha(P.SYSTEM), codebook_prompt_chars=len(P.SYSTEM),
                 faithfulness_prompt_sha256=C.sha(P.FAITH_SYSTEM), codes=P.ALL_CODES),
    reliability=dict(kappa_min=ag["kappa_min"], min_positive=ag["min_positive"],
                     reliable_codes=ag["reliable_codes"],
                     excluded=[r["code"] for r in ag["rows"] if not r["reliable"]]),
    inductive_sample=dict(n=300, seed=7, file="inductive_sample.jsonl"),
    examples=dict(n=14, seed=31, selection="programmatic rule per box, see scripts/a7_examples.py"),
    human_validation=dict(file="human_validation.csv", rows=sum(1 for _ in open(C.STUDY / "human_validation.csv", encoding="utf-8")) - 7,
                          traces=300, seed=23, annotators=3, shared_block_fraction=0.20, status="built, not run"),
    runs=runs,
    total_cost_usd_at_assumed_prices=round(sum(r["cost_usd_at_assumed_prices"] for r in runs.values()), 2),
    inputs_read_only=[str(p) for _, _, _, p, _ in C.RUNS],
    frozen_code_sha256={f: C.sha(open(C.ROOT / f, encoding="utf-8").read())
                        for f in ("scripts/eval.py", "scripts/test_LLM.py")},
    note="No benchmark inference was run. The only API calls are coding and the faithfulness judge.")
json.dump(man, open(C.STUDY / "MANIFEST.json", "w"), indent=1)
print("MANIFEST.json written; total cost", man["total_cost_usd_at_assumed_prices"])
