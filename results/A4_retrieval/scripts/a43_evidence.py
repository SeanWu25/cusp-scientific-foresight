"""
A4.3 step 2 — fixed-query evidence. For each event and each freshness bound (one per
evaluated model's cutoff, plus unrestricted), one You.com call with the FIXED query,
filtered and formatted by the unmodified scripts/web_search.py code. Stored per
(event, bound) in evidence/<bound>.jsonl with context text, URLs and titles.
"""
import json, sys, os, time, argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
sys.path.insert(0, str(ROOT / "scripts"))
from dotenv import load_dotenv; load_dotenv(str(ROOT / ".env"))
import web_search as W
from youdotcom import You
BOUNDS = {"2023-10-01": "GPT-4o", "2023-12-01": "LLaMA 3.3 70B", "2025-01-01": "Claude S4.5", "2025-08-01": "GPT-5.4", "2026-01-01": "Claude Sonnet 5", "2026-02-01": "GPT-5.6 Sol", "unrestricted": "all (WS)"}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bounds", default=",".join(BOUNDS)); ap.add_argument("--max", type=int, default=None); ap.add_argument("--concurrency", type=int, default=4); a = ap.parse_args()
    qs = {}
    for l in open(OUT / "A4_3_fixed_queries/queries.jsonl"):
        r = json.loads(l)
        if r.get("query"): qs[r["id"]] = r["query"]
    you = You(os.environ["YOU_API_KEY"]); ev_dir = OUT / "A4_3_fixed_queries/evidence"; ev_dir.mkdir(exist_ok=True)
    for bound in a.bounds.split(","):
        outp = ev_dir / f"{bound}.jsonl"; done = set()
        if outp.exists():
            for l in open(outp):
                if l.strip(): done.add(json.loads(l)["id"])
        todo = [i for i in qs if i not in done][: a.max]
        to = "2100-01-01" if bound == "unrestricted" else bound; cutoff_dt = datetime.strptime(to, "%Y-%m-%d")
        def one(i):
            q = qs[i]; res = you.search.unified(query=q, freshness=f"1900-01-01to{to}"); docs = W._extract_and_filter(res, q, cutoff_dt)
            return dict(id=i, bound=bound, query=q, context=W._build_context(docs), urls=[d["url"] for d in docs[:8]], titles=[d["title"] for d in docs[:8]], n_docs=len(docs), retrieved_utc=datetime.utcnow().isoformat())
        with open(outp, "a") as f, ThreadPoolExecutor(a.concurrency) as ex:
            futs = {ex.submit(one, i): i for i in todo}
            for n, fut in enumerate(as_completed(futs), 1):
                try: rec = fut.result()
                except Exception as e: rec = dict(id=futs[fut], bound=bound, error=str(e)[:200])
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
        print(f"evidence {bound}: {len(done)} existing + {len(todo)} new", file=sys.stderr)
if __name__ == "__main__": main()
