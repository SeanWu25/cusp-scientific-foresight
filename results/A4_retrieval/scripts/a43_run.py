"""
A4.3 step 3 — run each evaluated model on the FIXED-QUERY evidence, with the same
harness code path as its original retrieval run (scripts/run_cusp.py process_row,
imported unmodified). The only difference from the original condition is that the
retrieval context is injected from evidence/<bound>.jsonl instead of being fetched
with a model-written query.

  python a43_run.py --model gpt4o --condition fixed_ws_cutoff [--max-rows N]

Output: model_outputs.jsonl (one record per model x condition x event; resumable).
"""
import argparse, json, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
sys.path.insert(0, str(ROOT / "scripts"))
from dotenv import load_dotenv; load_dotenv(str(ROOT / ".env"))
import run_cusp as RC
# per-model decoding = the model's ORIGINAL retrieval run; provider/env as the base runs
MODELS = {
    # gpt-4o / gpt-5.4: the Azure OpenAI resource deployments used by the base runs now return 404; the same models are served
    # by the Azure AI Foundry OpenAI-compatible endpoint (gpt-4o -> gpt-4o-2024-11-20, gpt-5.4 -> gpt-5.4-2026-03-05).
    "gpt4o":    dict(name="GPT-4o",          provider="OPENAI",    model="gpt-4o",                      bound="2023-10-01", extra=["--temperature", "0", "--frq-max-tokens", "250"],
                     env={"OPENAI_API_BASE": "https://bascolm.services.ai.azure.com/openai/v1", "OPENAI_API_KEY": os.environ.get("AZURE_OPENAI_KEY", "")}),
    "gpt54":    dict(name="GPT-5.4",         provider="OPENAI",    model="gpt-5.4",                     bound="2025-08-01", extra=["--temperature", "0", "--frq-max-tokens", "250"],
                     env={"OPENAI_API_BASE": "https://bascolm.services.ai.azure.com/openai/v1", "OPENAI_API_KEY": os.environ.get("AZURE_OPENAI_KEY", "")}),
    "llama33":  dict(name="LLaMA 3.3 70B",   provider="OPENAI",    model="Llama-3.3-70B-Instruct",      bound="2023-12-01", extra=["--temperature", "0", "--frq-max-tokens", "2048"],
                     env={"OPENAI_API_BASE": "https://bascolm.services.ai.azure.com/openai/v1", "OPENAI_API_KEY": os.environ.get("AZURE_OPENAI_KEY", "")}),
    "claude45": dict(name="Claude S4.5",     provider="ANTHROPIC", model="claude-sonnet-4-5-20250929",  bound="2025-01-01", extra=["--temperature", "0", "--frq-max-tokens", "250"]),
    "sonnet5":  dict(name="Claude Sonnet 5", provider="ANTHROPIC", model="claude-sonnet-5",             bound="2026-01-01", extra=["--effort", "medium", "--frq-max-tokens", "384"]),
    "sol":      dict(name="GPT-5.6 Sol",     provider="OPENAI",    model="gpt-5.6-sol",                 bound="2026-02-01", extra=["--effort", "medium", "--frq-max-tokens", "2048"]),
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=list(MODELS)); ap.add_argument("--condition", required=True, choices=["fixed_ws_cutoff", "fixed_ws"])
    ap.add_argument("--max-rows", type=int, default=None); ap.add_argument("--concurrency", type=int, default=6); a = ap.parse_args()
    M = MODELS[a.model]
    for k, v in (M.get("env") or {}).items(): os.environ[k] = v
    bound = M["bound"] if a.condition == "fixed_ws_cutoff" else "unrestricted"
    evidence = {}
    for l in open(OUT / f"A4_3_fixed_queries/evidence/{bound}.jsonl"):
        r = json.loads(l)
        if r.get("context") is not None: evidence[r["id"]] = r
    args = RC.build_parser().parse_args(["--input", str(ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl"), "--output", "unused", "--provider", M["provider"], "--model", M["model"],
                                          "--condition", "ws_cutoff", "--run-index", "1", "--max-tokens", "2048", "--ids-file", str(SUBSET), "--seed", "42"] + M["extra"])
    client, model_name = RC.setup_client(args.provider, args.model); args.model = model_name; args.condition = a.condition
    RC.load_citations(args.citations)
    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]; keep = {l.strip() for l in open(SUBSET) if l.strip()}; rows = [r for r in rows if r["id"] in keep]
    import random; rng = random.Random(args.seed); shuffles = {}
    for r in rows:
        if not RC.detect_tasks(r)["mcq"]: continue
        oc = list(r["mcq_choices"]); correct = oc[r["mcq_answer_key"]]; idx = list(range(len(oc))); rng.shuffle(idx); sc = [oc[i] for i in idx]; shuffles[r["id"]] = (sc, RC.LABELS[sc.index(correct)])
    outp = OUT / "A4_3_fixed_queries/model_outputs.jsonl"; done = set()
    if outp.exists():
        for l in open(outp):
            try: r = json.loads(l); done.add((r.get("model_key"), r.get("condition"), r.get("id")))
            except Exception: pass
    todo = [r for r in rows if (a.model, a.condition, r["id"]) not in done and r["id"] in evidence][: a.max_rows]
    print(f"{M['name']} {a.condition} bound={bound}: {len(todo)} rows to run ({len(done)} records already in file)", file=sys.stderr)
    lock = threading.Lock(); t0 = time.time(); n = 0
    def one(row):
        e = evidence[row["id"]]
        ws_fn = lambda questions: {"context": e["context"], "urls": e["urls"], "query": e["query"]}
        pred = RC.process_row(row, shuffles.get(row["id"]), args, client, ws_fn)
        pred.update(model_key=a.model, model_name=M["name"], condition=a.condition, evidence_bound=bound, query_source="fixed:" + e.get("query_model", "external"), fixed_query=e["query"])
        return pred
    with open(outp, "a", encoding="utf-8") as f, ThreadPoolExecutor(a.concurrency) as ex:
        futs = {ex.submit(one, r): r for r in todo}
        for fut in as_completed(futs):
            try: pred = fut.result()
            except Exception as ex_: pred = dict(id=futs[fut]["id"], model_key=a.model, model_name=M["name"], condition=a.condition, fatal_error=str(ex_)[:200])
            with lock:
                f.write(json.dumps(pred, ensure_ascii=False) + "\n"); f.flush(); n += 1
                if n % 50 == 0: print(f"  {n}/{len(todo)} {time.time()-t0:.0f}s", file=sys.stderr)
    print(f"DONE {M['name']} {a.condition}: {n} rows in {time.time()-t0:.0f}s", file=sys.stderr)
if __name__ == "__main__": main()
