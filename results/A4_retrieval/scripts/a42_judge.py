"""
A4.2 — does the retrieved evidence contain the ground truth?

For every sampled case: reconstruct the evidence the model saw, then ask a judge
(Claude Sonnet 5, outside the retrieval loop) whether any retrieved source is the
source paper itself or states the realized outcome. Checkpointed per case in
verdicts.jsonl; resumable.

Evidence reconstruction
  youcom runs : re-issue the STORED query to You.com with the run's freshness bound
                (cutoff for WS+Cutoff; run date for WS), then apply the unmodified
                filter/format code from scripts/web_search.py. Live-vs-stored URL
                overlap is recorded per case.
  native runs : the evidence is the set of URLs the provider tool cited; each URL is
                fetched (title + first 1,500 chars of text). This is a lower bound
                on what the tool read.
"""
from __future__ import annotations
import argparse, json, os, sys, time, re, html
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
sys.path.insert(0, str(ROOT / "scripts"))
from dotenv import load_dotenv; load_dotenv(str(ROOT / ".env"))
import web_search as W          # unmodified filter / formatting functions
from youdotcom import You
import requests, anthropic

JUDGE_MODEL = "claude-sonnet-5"
JUDGE_PROMPT = """You are checking whether a set of web-search results contains the ground truth for a scientific forecasting item.

The item is derived from a source paper. Ground truth for the item:
- source paper link: {link}
- first observable month: {pub}
- problem: {problem}
- technical approach (what the paper did): {approach}
- realized outcome (the result the paper reports): {result}
- abstract (start): {abstract}

Retrieved results (as shown to the forecasting model):
{evidence}

Decide whether ANY retrieved result
 (a) IS the source paper itself (same paper: same title/abstract, the same arXiv id or DOI, an earlier preprint version, or a page reproducing its abstract), or
 (b) STATES THE REALIZED OUTCOME (reports, by the same or other authors, that the specific result described under "realized outcome" has been achieved), even if it is not the source paper.
Retrieved results that merely cover the same topic, earlier related work, or the problem without the outcome do NOT count.

Answer with JSON only:
{{"verdict": "INCLUDED" or "NOT_INCLUDED", "match_type": "source_paper" | "outcome_stated" | null, "matched_source": <1-based index of the matching result or null>, "matched_url": "<url or null>", "passage": "<verbatim quote from the matching result, at most 300 characters, or null>", "confidence": <0.0-1.0>, "reason": "<one sentence>"}}"""

_you = None
def youcom_evidence(query, freshness_to):
    global _you
    if _you is None: _you = You(os.environ["YOU_API_KEY"])
    cutoff_dt = datetime.strptime(freshness_to, "%Y-%m-%d")
    res = _you.search.unified(query=query, freshness=f"1900-01-01to{freshness_to}")
    docs = W._extract_and_filter(res, query, cutoff_dt)
    return W._build_context(docs), [d["url"] for d in docs][:8]

_page_cache = {}
def fetch_page(url, timeout=12):
    if url in _page_cache: return _page_cache[url]
    out = {"url": url, "title": "", "text": "", "status": None}
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (research; CUSP A4.2 check)"})
        out["status"] = r.status_code
        if r.ok and "text" in r.headers.get("content-type", ""):
            t = r.text; m = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
            out["title"] = html.unescape(m.group(1)).strip()[:200] if m else ""
            body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I); body = re.sub(r"<[^>]+>", " ", body); body = html.unescape(re.sub(r"\s+", " ", body)).strip()
            out["text"] = body[:1500]
    except Exception as e:
        out["error"] = str(e)[:120]
    _page_cache[url] = out; return out

def native_evidence(urls):
    blocks = []
    for i, u in enumerate(urls[:12]):
        p = fetch_page(u); blocks.append(f"[Source {i+1}]\nTitle: {p['title']}\nURL: {u}\n{p['text'] or '(page text unavailable)'}")
    return "\n\n".join(blocks), urls[:12]

def judge(client, ev_row, evidence):
    prompt = JUDGE_PROMPT.format(link=ev_row.get("paper_link"), pub=ev_row.get("publication_date"), problem=(ev_row.get("problem_statement") or "")[:700],
                                 approach=(ev_row.get("technical_approach") or "")[:700], result=(ev_row.get("results_and_metrics") or "")[:900],
                                 abstract=(ev_row.get("source_abstract") or "")[:900], evidence=evidence or "(no results)")
    for attempt in range(3):
        try:
            r = client.messages.create(model=JUDGE_MODEL, max_tokens=600, output_config={"effort": "low"}, messages=[{"role": "user", "content": prompt}])
            txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
            m = re.search(r"\{.*\}", txt, re.S); obj = json.loads(m.group(0)) if m else None
            if obj and obj.get("verdict") in ("INCLUDED", "NOT_INCLUDED"):
                obj["usage"] = dict(input=r.usage.input_tokens, output=r.usage.output_tokens); return obj
            last = f"unparsable: {txt[:200]}"
        except Exception as e:
            last = str(e)[:200]; time.sleep(2 ** attempt)
    return {"verdict": None, "error": last}

def process(case, events, client):
    run = RUNS[case["run"]]; model, cond, ds, path, mech, cutoff, run_date = run
    row = next(r for r in load_run.cache[case["run"]] if r["id"] == case["id"]); ev_row = events[case["id"]]
    kind, key = paper_key(ev_row)
    rec = dict(case=case["case"], run=case["run"], model=model, condition=cond, dataset=ds, id=case["id"], mechanism=mech, area=ev_row.get("main_area"),
               has_tasks=[t for t, f in (("binary", "binary_question"), ("binary_perturbed", "binary_question_perturbed"), ("mcq", "mcq_question"), ("frq", "frq_prompt"), ("date", "date_prediction_prompt")) if ev_row.get(f)],
               stored_urls=row["urls"], judged_utc=datetime.utcnow().isoformat())
    rec["url_match_stored"] = any(url_matches(kind, key, u) for u in row["urls"])
    if mech == "youcom":
        rec["query"] = row["query"]; to = cutoff or run_date
        try:
            evidence, live_urls = youcom_evidence(row["query"], to); rec["freshness_to"] = to; rec["live_urls"] = live_urls
            rec["stored_live_overlap"] = len(set(live_urls) & set(row["urls"])) / max(len(row["urls"]), 1)
        except Exception as e:
            rec["error"] = f"youcom: {e}"[:200]; return rec
    else:
        rec["per_task_queries"] = {t: v["queries"] for t, v in row["per_task"].items()}
        evidence, live_urls = native_evidence(row["urls"]); rec["fetched_urls"] = live_urls; rec["fetch_ok"] = sum(1 for u in live_urls if _page_cache.get(u, {}).get("text"))
    rec["url_match_evidence"] = any(url_matches(kind, key, u) for u in live_urls)
    rec["evidence_chars"] = len(evidence)
    rec["judge"] = judge(client, ev_row, evidence)
    return rec

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max-cases", type=int, default=None); ap.add_argument("--concurrency", type=int, default=4); ap.add_argument("--runs", default=None); a = ap.parse_args()
    sample = json.load(open(OUT / "A4_2_groundtruth_inclusion/sample.json")); events = load_events()
    outp = OUT / "A4_2_groundtruth_inclusion/verdicts.jsonl"; done = set()
    if outp.exists():
        for l in open(outp):
            if l.strip(): done.add(json.loads(l)["case"])
    cases = [c for c in sample["cases"] if c["case"] not in done and (a.runs is None or c["run"] in a.runs.split(","))]
    if a.max_cases: cases = cases[:a.max_cases]
    load_run.cache = {k: load_run(k) for k in {c["run"] for c in cases}}
    client = anthropic.Anthropic(); t0 = time.time(); n = 0
    print(f"{len(done)} done, {len(cases)} to judge", file=sys.stderr)
    with open(outp, "a") as f, ThreadPoolExecutor(a.concurrency) as ex:
        futs = {ex.submit(process, c, events, client): c for c in cases}
        for fut in as_completed(futs):
            try: rec = fut.result()
            except Exception as e: rec = dict(case=futs[fut]["case"], run=futs[fut]["run"], id=futs[fut]["id"], error=f"worker: {e}"[:200])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); n += 1
            if n % 25 == 0: print(f"  {n}/{len(cases)} {time.time()-t0:.0f}s", file=sys.stderr)
    print(f"done {n} in {time.time()-t0:.0f}s", file=sys.stderr)

if __name__ == "__main__": main()
