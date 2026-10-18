"""
A4.3 step 1 — fixed search queries from a model outside the panel (Claude Opus 4.8).
Same combined-query prompt as scripts/web_search.py (imported, unmodified), one query
per event over the pinned 500 subset. Checkpointed in queries.jsonl.
"""
import json, sys, time, hashlib, argparse, inspect, os
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
sys.path.insert(0, str(ROOT / "scripts"))
from dotenv import load_dotenv; load_dotenv(str(ROOT / ".env"))
import web_search as W, anthropic
QUERY_MODEL = "claude-opus-4-8"   # outside the evaluated panel; override with --query-model
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max", type=int, default=None); ap.add_argument("--concurrency", type=int, default=4); ap.add_argument("--query-model", default=QUERY_MODEL); ap.add_argument("--set", default="main", choices=list(A43_SETS)); a = ap.parse_args()
    ids_file, d3 = A43_SETS[a.set]
    qmodel = a.query_model
    ev = load_events(); sub = [l.strip() for l in open(ids_file) if l.strip()]
    outp = d3 / "queries.jsonl"; done = set()
    if outp.exists():
        for l in open(outp):
            if l.strip():
                r = json.loads(l)
                if r.get("query"): done.add(r["id"])      # errored records (refusals) are retried
    todo = [i for i in sub if i not in done][: a.max]
    if qmodel.startswith("claude"):
        client = anthropic.Anthropic()
    else:   # fallback model (for events the Claude model refuses) on the Azure AI Foundry OpenAI-compatible endpoint
        from openai import OpenAI
        client = OpenAI(base_url="https://bascolm.services.ai.azure.com/openai/v1", api_key=os.environ["AZURE_OPENAI_KEY"])
    def one(i):
        r = ev[i]; qs = [r[f] for f in ("binary_question", "binary_question_perturbed", "mcq_question", "frq_prompt", "date_prediction_prompt") if r.get(f)]
        t0 = time.time(); q = W._generate_combined_query(client, qs, qmodel)   # _chat handles the Anthropic client path
        return dict(id=i, query=q, query_model=qmodel, n_questions=len(qs), prompt_sha=hashlib.sha256(inspect.getsource(W._generate_combined_query).encode()).hexdigest()[:16], latency_s=round(time.time() - t0, 2))
    with open(outp, "a") as f, ThreadPoolExecutor(a.concurrency) as ex:
        futs = {ex.submit(one, i): i for i in todo}
        for n, fut in enumerate(as_completed(futs), 1):
            try: rec = fut.result()
            except Exception as e: rec = dict(id=futs[fut], error=str(e)[:200], query_model=qmodel)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if n % 50 == 0: print(f"  {n}/{len(todo)}", file=sys.stderr)
    print(f"queries: {len(done)} existing + {len(todo)} new", file=sys.stderr)
if __name__ == "__main__": main()
