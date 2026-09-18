#!/usr/bin/env python3
"""
judge_frq.py — run the unmodified two-stage FRQ judge concurrently over a
run_cusp.py predictions file.

Stage 1 judge_leakage (web search forced), stage 2 judge_frq_combined
(4-dimension rubric). Both imported verbatim from eval.py; nothing here
re-implements or alters a rubric. Writes one JSONL record per event.
"""

from __future__ import annotations

import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval import LLMClient, judge_frq_combined, judge_leakage  # noqa: E402

_lock = threading.Lock()


def judge_one(row, frq_text, jc):
    out = {"id": row["id"], "publication_date": row.get("publication_date", "")}
    t0 = time.time()
    try:
        r = judge_frq_combined(row, frq_text, llm_client=jc)
        out["frq"] = {k: r[k] for k in ("frq_score", "alignment", "specificity",
                                        "novelty", "feasibility", "frq_rationale",
                                        "urls", "web_search_used")}
        out["frq"]["n_web_searches"] = len(r.get("web_searches") or [])
    except Exception as e:
        out["frq_error"] = f"{type(e).__name__}: {e}"
    out["frq_judge_s"] = round(time.time() - t0, 2)
    t0 = time.time()
    try:
        lv = judge_leakage(row, frq_text, "", llm_client=jc)
        out["leakage"] = {"verdict": lv.verdict, "score": lv.score,
                          "reason": lv.reason[:500],
                          "indicators": (lv.details or {}).get("leakage_indicators", []),
                          "web_search_used": (lv.details or {}).get("web_search_used")}
    except Exception as e:
        out["leakage_error"] = f"{type(e).__name__}: {e}"
    out["leakage_judge_s"] = round(time.time() - t0, 2)
    out["judged_utc"] = datetime.now(timezone.utc).isoformat()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--output", required=True)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--max-rows", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), ".env"))
    except ImportError:
        pass

    bench = {}
    for l in open(a.benchmark, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            bench[r["id"]] = r
    preds = [json.loads(l) for l in open(a.predictions, encoding="utf-8") if l.strip()]
    work = [(bench[p["id"]], p["frq_answer"]) for p in preds
            if p.get("frq_answer") and p["id"] in bench]

    done = set()
    if a.resume and os.path.exists(a.output):
        for l in open(a.output, encoding="utf-8"):
            try:
                done.add(json.loads(l)["id"])
            except Exception:
                pass
    work = [w for w in work if w[0]["id"] not in done]
    if a.max_rows:
        work = work[: a.max_rows]

    jc = LLMClient(model=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini"),
                   api_key=None, api_base=None)
    print(f"judging {len(work)} FRQ responses with "
          f"{os.environ.get('AZURE_OPENAI_DEPLOYMENT')} + web search, "
          f"concurrency={a.concurrency}", file=sys.stderr)

    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    out = open(a.output, "a", encoding="utf-8")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = {ex.submit(judge_one, row, txt, jc): row["id"] for row, txt in work}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                rec = f.result()
            except Exception as e:
                rec = {"id": futs[f], "fatal_error": f"{type(e).__name__}: {e}"}
            with _lock:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
            if i % 25 == 0 or i == len(futs):
                el = time.time() - t0
                print(f"  {i}/{len(futs)}  {el:.0f}s  "
                      f"eta={(len(futs)-i)/max(i/max(el,1e-9),1e-9)/60:.1f} min",
                      file=sys.stderr)
    out.close()
    print(f"DONE {len(work)} judged in {time.time()-t0:.0f}s -> {a.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
