"""a8_manifest.py — MANIFEST.json: models, snapshot ids, dates, seed, prompt hashes, costs, git SHA."""
import json, subprocess, collections, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a8_common as C

git = lambda *a: subprocess.run(["git", *a], cwd=C.ROOT, capture_output=True, text=True).stdout.strip()
sample = C.load_sample()
models = {}
for k in C.ORDER:
    m = C.MODELS[k]; p = C.RAW / f"{k}.jsonl"
    entry = dict(display_name=m["name"], model_id=m["model"], provider=m["provider"], endpoint=(C.ENDPOINTS.get(m["provider"]) if m["provider"] else None),
                 decoding=dict(m["decoding"], max_tokens=2048, retries=2, json_mode=(m["provider"] not in ("anthropic", None))),
                 knowledge_cutoff=m["cutoff"], price_usd_per_mtok=dict(input=m["price"][0], output=m["price"][1], source=m["price_src"]),
                 runnable=bool(m["provider"]), note=m.get("note"))
    if p.exists():
        snaps = collections.Counter(); n = 0; cost = 0.0; tin = tout = 0; first = last = None; st = collections.Counter()
        for l in open(p, encoding="utf-8"):
            if not l.strip(): continue
            r = json.loads(l); n += 1; snaps[r.get("model_snapshot")] += 1; cost += r.get("cost_usd") or 0
            tin += r.get("input_tokens") or 0; tout += r.get("output_tokens") or 0
            ts = r.get("timestamp"); first = min(first, ts) if first else ts; last = max(last, ts) if last else ts
            st["refusal" if r.get("refusal") else "error" if r.get("error") else "ok" if r.get("answer") else "empty"] += 1
        entry.update(n_records=n, api_reported_snapshots=dict(snaps), run_started_utc=first, run_finished_utc=last,
                     input_tokens=tin, output_tokens=tout, cost_usd_at_assumed_prices=round(cost, 2), record_statuses=dict(st),
                     raw_sha256=C.sha(open(p, encoding="utf-8").read()))
    models[k] = entry
man = dict(study="A8 base-rate injection sweep (Reviewer 2, C5)", created_utc=datetime.now(timezone.utc).isoformat(),
           git_sha=git("rev-parse", "HEAD"), git_branch=git("rev-parse", "--abbrev-ref", "HEAD"), git_dirty=git("status", "--porcelain", "--", "results/A8_base_rate"),
           sample=dict(seed=sample["seed"], n=500, n_candidates=sample["n_candidates"], n_from_extension=sample["n_from_extension"],
                       ids_sha256=C.sha("\n".join(sample["ids"])), candidate_pool=sample["candidate_pool"]),
           xs=C.XS, injected_sentence_template=C.injected_sentence(0).replace("0%", "X%"),
           base_prompt_sha256=C.BASE_PROMPT_SHA, injected_prompt_sha256={str(x): C.sha(C.injected_system(x)) for x in C.XS},
           baseline="stored base-condition reports listed in run_evaluation/full_corpus_tables.PANEL, read only",
           grader="scripts/eval.py grade_binary (frozen); parser scripts/test_LLM.py parse_structured_response (frozen)",
           frozen_code_sha256={f: C.sha(open(C.ROOT / f, encoding="utf-8").read()) for f in ("scripts/eval.py", "scripts/test_LLM.py")},
           total_cost_usd_at_assumed_prices=round(sum(m.get("cost_usd_at_assumed_prices", 0) for m in models.values()), 2),
           probe_cost_note="ten one-line endpoint probes before the run, < $0.05, not itemised",
           models=models)
json.dump(man, open(C.STUDY / "MANIFEST.json", "w"), indent=1)
print("MANIFEST.json written; total", man["total_cost_usd_at_assumed_prices"])
