#!/usr/bin/env python3
"""
judge_frq.py — run the unmodified two-stage FRQ judge concurrently over a
run_cusp.py predictions file.

Stage 1 judge_leakage (web search forced), stage 2 judge_frq_combined
(4-dimension rubric). Both imported verbatim from eval.py; nothing here
re-implements or alters a rubric. Writes one JSONL record per event.
"""

from __future__ import annotations

import argparse, json, os, random, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval import LLMClient, judge_frq_combined, judge_leakage  # noqa: E402

_lock = threading.Lock()


# The six published runs judged 100% of FRQ responses WITH web search
# (web_search_used is True on every stored record). When the Responses API is
# rate-limited, eval.LLMClient._call_responses_api silently degrades to a plain
# chat call, which would produce a judgement drawn from a different protocol.
# We therefore retry until the web-search path succeeds rather than accept a
# degraded verdict; eval.py itself is left untouched.
MAX_ATTEMPTS = 6


def _with_web_search(fn, *, used, attempts=MAX_ATTEMPTS):
    """Call fn() until its result actually used web search. Returns (result, tries)."""
    last = None
    for i in range(1, attempts + 1):
        try:
            r = fn()
            if used(r):
                return r, i
            last = RuntimeError("judge ran without web search (rate-limited fallback)")
        except Exception as e:
            last = e
        if i < attempts:
            time.sleep(min(2 ** i, 30) + random.random() * 2)
    raise last if last else RuntimeError("judge failed")


def judge_one(row, frq_text, jc, stage="both"):
    out = {"id": row["id"], "publication_date": row.get("publication_date", ""),
           "stage": stage}
    t0 = time.time()
    if stage == "leakage":
        out["frq"] = None
        out["frq_skipped_reason"] = "stage-2 rubric deferred pending rubric revision"
    else:
      try:
        r, tries = _with_web_search(
            lambda: judge_frq_combined(row, frq_text, llm_client=jc),
            used=lambda r: bool(r.get("web_search_used")))
        out["frq"] = {k: r[k] for k in ("frq_score", "alignment", "specificity",
                                        "novelty", "feasibility", "frq_rationale",
                                        "urls", "web_search_used")}
        out["frq"]["n_web_searches"] = len(r.get("web_searches") or [])
        out["frq_attempts"] = tries
      except Exception as e:
        out["frq_error"] = f"{type(e).__name__}: {e}"
    out["frq_judge_s"] = round(time.time() - t0, 2)
    t0 = time.time()
    if stage == "rubric":
        out["leakage"] = None
    else:
      try:
        lv, tries = _with_web_search(
            lambda: judge_leakage(row, frq_text, "", llm_client=jc),
            used=lambda v: bool((v.details or {}).get("web_search_used")))
        det = lv.details or {}
        out["leakage"] = {"verdict": lv.verdict, "score": lv.score,
                          "reason": lv.reason[:500],
                          "indicators": det.get("leakage_indicators", []),
                          "web_search_used": det.get("web_search_used"),
                          # stage 1 depends on live search, so archive the
                          # evidence it actually saw — it will not reproduce later
                          "web_searches": det.get("web_searches", []),
                          "judged_utc": datetime.now(timezone.utc).isoformat()}
        out["leakage_attempts"] = tries
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
    ap.add_argument("--concurrency", type=int, default=3,
                    help="Keep low: the judge deployment rate-limits, and a "
                         "rate-limited call degrades to a non-web-search judgement.")
    ap.add_argument("--max-rows", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--stage", choices=["leakage", "rubric", "both"], default="both",
                    help="leakage = stage 1 only (contamination audit; depends on "
                         "live web search, so it must be run NOW and cannot be "
                         "reproduced later). rubric = stage 2 only (the "
                         "4-dimension quality rubric, currently under revision). "
                         "both = the published protocol.")
    ap.add_argument("--endpoint", choices=["azure", "openai"], default="azure",
                    help="Which serving stack judges. 'azure' is the configuration "
                         "that produced the six published models. 'openai' must be "
                         "validated against it before use.")
    ap.add_argument("--judge-model", default=None,
                    help="Override the judge model id (default: AZURE_OPENAI_DEPLOYMENT).")
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

    judge_model = a.judge_model or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")
    if a.endpoint == "openai":
        # eval.LLMClient routes to Azure whenever AZURE_OPENAI_ENDPOINT is set and
        # reads the deployment name from AZURE_OPENAI_DEPLOYMENT. Clear both inside
        # this process so the client resolves to api.openai.com. eval.py is untouched.
        os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        os.environ.pop("AZURE_OPENAI_DEPLOYMENT", None)
        os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
        jc = LLMClient(model=judge_model,
                       api_key=os.environ["OPENAI_API_KEY"],
                       api_base="https://api.openai.com/v1")
    else:
        jc = LLMClient(model=judge_model, api_key=None, api_base=None)
    print(f"judging {len(work)} FRQ responses with {judge_model} + web search "
          f"via {a.endpoint}, concurrency={a.concurrency}", file=sys.stderr)

    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    out = open(a.output, "a", encoding="utf-8")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = {ex.submit(judge_one, row, txt, jc, a.stage): row["id"]
                for row, txt in work}
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
