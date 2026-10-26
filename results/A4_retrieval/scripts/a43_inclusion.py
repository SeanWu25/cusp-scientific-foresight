"""A4.3 step 5 — ground-truth inclusion check on the FIXED-QUERY evidence (same judge and prompt as A4.2; evidence text is stored, so no re-retrieval)."""
import json, sys, time, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
import a42_judge as J, anthropic
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--concurrency", type=int, default=4); ap.add_argument("--max", type=int, default=None)
    ap.add_argument("--set", choices=list(A43_SETS), default="main", help="main = first 500 events (original files); ext500 = the 500 added events (writes ext500/inclusion_verdicts.jsonl)")
    a = ap.parse_args(); SET_DIR = A43_SETS[a.set][1]
    ev = load_events(); outp = SET_DIR / "inclusion_verdicts.jsonl"; done = set()
    if outp.exists():
        for l in open(outp):
            if l.strip(): done.add(json.loads(l)["case"])
    cases = []
    for p in sorted((SET_DIR / "evidence").glob("*.jsonl")):
        for l in open(p):
            r = json.loads(l)
            if r.get("context") is None: continue
            c = f"fixed|{r['bound']}|{r['id']}"
            if c not in done: cases.append((c, r))
    cases = cases[: a.max]; client = anthropic.Anthropic(); t0 = time.time(); n = 0
    def one(c, r):
        row = ev[r["id"]]; kind, key = paper_key(row)
        rec = dict(case=c, bound=r["bound"], id=r["id"], area=row.get("main_area"), query=r["query"], urls=r["urls"], url_match=any(url_matches(kind, key, u) for u in r["urls"]), evidence_chars=len(r["context"]),
                   has_tasks=[t for t, f in (("binary", "binary_question"), ("binary_perturbed", "binary_question_perturbed"), ("mcq", "mcq_question"), ("frq", "frq_prompt"), ("date", "date_prediction_prompt")) if row.get(f)])
        rec["judge"] = J.judge(client, row, r["context"]); return rec
    print(f"{len(done)} done, {len(cases)} to judge", file=sys.stderr)
    with open(outp, "a") as f, ThreadPoolExecutor(a.concurrency) as ex:
        futs = {ex.submit(one, c, r): c for c, r in cases}
        for fut in as_completed(futs):
            try: rec = fut.result()
            except Exception as e: rec = dict(case=futs[fut], error=str(e)[:200])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); n += 1
            if n % 100 == 0: print(f"  {n}/{len(cases)} {time.time()-t0:.0f}s", file=sys.stderr)
    print(f"done {n}", file=sys.stderr)
if __name__ == "__main__": main()
