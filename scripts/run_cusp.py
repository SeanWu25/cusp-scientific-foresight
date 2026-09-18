#!/usr/bin/env python3
"""
run_cusp.py — concurrent CUSP inference runner with per-instance run logging.

Why this exists
---------------
`test_LLM.py` is the harness that produced the six published models. It is
strictly serial (~2.75 s/call => ~40 h for one full-corpus pass) and its
prediction records keep only the parsed answer, which is not enough for the
frozen release: reviewers asked for raw verbatim responses, parse outcomes,
retries and refusals.

This runner adds concurrency and complete logging **without touching any
prompt, any parser, or any scoring code**. Every prompt constant and the
response parser are imported directly from `test_LLM`, so they are provably
byte-identical to what the published runs used (the freeze manifest hashes
them to prove it).

Determinism
-----------
MCQ choice permutations are drawn up-front, in benchmark file order, from
`random.Random(seed)` — the identical stream `test_LLM.py` produces with
`random.seed(seed)` + `random.shuffle`. Concurrency therefore cannot perturb
them, and a rerun with the same seed reproduces the same permutations.

Conditions
----------
  base       no tools
  ws_cutoff  You.com retrieval restricted to documents published <= cutoff
  ws         You.com retrieval with no date restriction

Output
------
JSONL, one record per EVENT, appended never overwritten, keyed by event id.
Legacy field names (`binary_answer`, `mcq_shuffled_answer_key`, ...) are kept
exactly as `eval.py` expects, so the existing evaluator reads these files
unchanged. Everything new is additive.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_LLM import (  # noqa: E402  — reused verbatim, never redefined
    BINARY_SYSTEM,
    MCQ_SYSTEM,
    FRQ_SYSTEM,
    DATE_SYSTEM,
    TASK_FIELDS,
    detect_tasks,
    parse_structured_response,
    setup_client,
    get_claude_response,
    get_model_response,
    claude_supports_effort,
    claude_supports_sampling_params,
)

LABELS = ["A", "B", "C", "D", "E", "F", "G", "H"]
_write_lock = threading.Lock()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, help="Benchmark JSONL")
    p.add_argument("--output", required=True, help="Predictions JSONL (appended)")
    p.add_argument("--provider", default="ANTHROPIC",
                   choices=["ANTHROPIC", "OPENAI", "AZURE", "AZURE_DEEPSEEK"])
    p.add_argument("--model", default="claude-sonnet-5")
    p.add_argument("--condition", default="base",
                   choices=["base", "ws_cutoff", "ws"])
    p.add_argument("--run-index", type=int, default=1)
    p.add_argument("--effort", default=None,
                   choices=["low", "medium", "high", "xhigh", "max"])
    p.add_argument("--temperature", type=float, default=0.0,
                   help="Sent only to models that still accept it.")
    p.add_argument("--max-tokens", type=int, default=2048)
    p.add_argument("--frq-max-tokens", type=int, default=250,
                   help="250 matches how Claude Sonnet 4.5 was run.")
    p.add_argument("--ws-cutoff", default=None,
                   help="YYYY-MM date ceiling for retrieval (condition ws_cutoff)")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-rows", type=int, default=None)
    p.add_argument("--ids-file", default=None,
                   help="Optional file of event ids (one per line) to restrict to")
    p.add_argument("--resume", action="store_true",
                   help="Skip ids already present in --output")
    return p


# ---------------------------------------------------------------------------
# Model call with full metadata capture
# ---------------------------------------------------------------------------

def call_model(client, model, provider, system, user, max_tokens, effort,
               temperature, retries) -> tuple[str, dict]:
    """Return (raw_text, meta). meta carries retries/refusal/usage/latency."""
    meta: dict = {"retries": 0, "refusal": False, "stop_reason": None,
                  "input_tokens": None, "output_tokens": None,
                  "model_snapshot": model, "error": None}
    t0 = time.time()
    if provider == "ANTHROPIC":
        raw = get_claude_response(client, model, system, user,
                                  temperature=temperature, max_tokens=max_tokens,
                                  retries=retries, effort=effort, meta_out=meta)
    else:
        raw = get_model_response(client, model, system, user,
                                 temperature=temperature, max_tokens=max_tokens,
                                 retries=retries, json_mode=False)
    meta["latency_s"] = round(time.time() - t0, 3)
    if raw.startswith("Error:"):
        meta["error"] = raw
    return raw, meta


def record_task(pred: dict, task: str, raw: str, meta: dict, parsed: dict | None):
    """Attach legacy + additive fields for one task to the prediction record."""
    pred[f"{task}_raw"] = raw
    pred[f"{task}_retries"] = meta.get("retries")
    pred[f"{task}_refusal"] = meta.get("refusal")
    pred[f"{task}_stop_reason"] = meta.get("stop_reason")
    pred[f"{task}_latency_s"] = meta.get("latency_s")
    pred[f"{task}_input_tokens"] = meta.get("input_tokens")
    pred[f"{task}_output_tokens"] = meta.get("output_tokens")
    if meta.get("error"):
        pred[f"{task}_error"] = meta["error"]
    if parsed is not None:
        pred[f"{task}_answer"] = parsed["answer"]
        pred[f"{task}_reasoning"] = parsed["reasoning"]
        pred[f"{task}_parse_method"] = parsed["parse_method"]
        if parsed["confidence"] is not None:
            pred[f"{task}_confidence"] = parsed["confidence"]


# ---------------------------------------------------------------------------
# Per-row worker
# ---------------------------------------------------------------------------

def process_row(row, shuffle, args, client, ws_fn) -> dict:
    tasks = detect_tasks(row)
    pred = {
        "id": row.get("id"),
        "publication_date": row.get("publication_date", ""),
        "main_area": row.get("main_area", ""),
        "model": args.model,
        "condition": args.condition,
        "run_index": args.run_index,
        "effort": args.effort,
        "frq_max_tokens": args.frq_max_tokens,
        "timestamp_start": datetime.now(timezone.utc).isoformat(),
    }

    # --- optional retrieval context, shared across this row's tasks ---
    row_context = ""
    if ws_fn is not None:
        qs = [row[f] for f in ("binary_question", "binary_question_perturbed",
                               "mcq_question", "frq_prompt", "date_prediction_prompt")
              if row.get(f)]
        if qs:
            try:
                res = ws_fn(qs)
                row_context = res["context"]
                pred["web_search_query"] = res["query"]
                pred["web_search_urls"] = res["urls"]
                pred["web_search_n_sources"] = len(res["urls"])
                pred["web_search_context_chars"] = len(row_context)
            except Exception as e:
                pred["web_search_error"] = f"{type(e).__name__}: {e}"

    def wrap(prompt: str) -> str:
        return (f"[Web Search Context]\n{row_context}\n\n---\n\n{prompt}"
                if row_context else prompt)

    def run(system, prompt, max_tokens):
        return call_model(client, args.model, args.provider, system, wrap(prompt),
                          max_tokens, args.effort, args.temperature, args.retries)

    if tasks["binary"]:
        raw, meta = run(BINARY_SYSTEM, row["binary_question"], args.max_tokens)
        record_task(pred, "binary", raw, meta, parse_structured_response(raw, "binary"))

    if tasks["binary_perturbed"]:
        raw, meta = run(BINARY_SYSTEM, row["binary_question_perturbed"], args.max_tokens)
        record_task(pred, "binary_perturbed", raw, meta,
                    parse_structured_response(raw, "binary_perturbed"))

    if tasks["mcq"]:
        sc, key = shuffle
        cs = "\n".join(f"({LABELS[i]}) {sc[i]}" for i in range(len(sc)))
        prompt = (f"{row['mcq_question']}\n\n{cs}\n\n"
                  f"Select exactly one answer: {', '.join(LABELS[:len(sc)])}.")
        raw, meta = run(MCQ_SYSTEM, prompt, args.max_tokens)
        record_task(pred, "mcq", raw, meta, parse_structured_response(raw, "mcq"))
        pred["mcq_shuffled_choices"] = {LABELS[i]: sc[i] for i in range(len(sc))}
        pred["mcq_shuffled_answer_key"] = key

    if tasks["frq"]:
        raw, meta = run(FRQ_SYSTEM, row["frq_prompt"], args.frq_max_tokens)
        record_task(pred, "frq", raw, meta, None)
        pred["frq_answer"] = raw
        pred["frq_truncated"] = meta.get("stop_reason") == "max_tokens"

    if tasks["date"]:
        raw, meta = run(DATE_SYSTEM, row["date_prediction_prompt"], args.max_tokens)
        record_task(pred, "date", raw, meta, parse_structured_response(raw, "date"))

    pred["model_reasoning"] = "\n---\n".join(
        v for v in (pred.get("binary_reasoning"), pred.get("binary_perturbed_reasoning"),
                    pred.get("mcq_reasoning"), pred.get("frq_answer"),
                    pred.get("date_reasoning")) if v)
    pred["timestamp_end"] = datetime.now(timezone.utc).isoformat()
    return pred


# ---------------------------------------------------------------------------

def main():
    args = build_parser().parse_args()
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), ".env"))
    except ImportError:
        pass

    client, model_name = setup_client(args.provider, args.model)
    args.model = model_name

    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]

    if args.ids_file:
        keep = {l.strip() for l in open(args.ids_file) if l.strip()}
        rows = [r for r in rows if r.get("id") in keep]

    # MCQ permutations: drawn in file order, before any concurrency.
    rng = random.Random(args.seed)
    shuffles: dict = {}
    for r in rows:
        if not detect_tasks(r)["mcq"]:
            continue
        oc = list(r["mcq_choices"])
        correct = oc[r["mcq_answer_key"]]
        idx = list(range(len(oc)))
        rng.shuffle(idx)
        sc = [oc[i] for i in idx]
        shuffles[r["id"]] = (sc, LABELS[sc.index(correct)])

    done: set = set()
    if args.resume and os.path.exists(args.output):
        for l in open(args.output, encoding="utf-8"):
            try:
                done.add(json.loads(l)["id"])
            except Exception:
                pass
    todo = [r for r in rows if r.get("id") not in done]
    if args.max_rows:
        todo = todo[: args.max_rows]

    ws_fn = None
    if args.condition in ("ws_cutoff", "ws"):
        from web_search import web_search_get_context
        you_key = os.environ.get("YOU_API_KEY")
        if not you_key:
            sys.exit("ERROR: YOU_API_KEY required for web-search conditions")
        cutoff_dt = (datetime.strptime(args.ws_cutoff + "-01", "%Y-%m-%d")
                     if args.condition == "ws_cutoff" else datetime(2100, 1, 1))

        def ws_fn(questions):  # noqa: F811
            return web_search_get_context(questions=questions, client=client,
                                          you_api_key=you_key, cutoff_date=cutoff_dt,
                                          model=model_name)

    print(f"model={model_name}  condition={args.condition}  run={args.run_index}  "
          f"effort={args.effort}  frq_max_tokens={args.frq_max_tokens}", file=sys.stderr)
    print(f"sampling_params_sent={claude_supports_sampling_params(model_name) if args.provider=='ANTHROPIC' else 'n/a'}  "
          f"effort_supported={claude_supports_effort(model_name) if args.provider=='ANTHROPIC' else 'n/a'}", file=sys.stderr)
    print(f"rows={len(todo)} (skipped {len(rows)-len(todo)} already done)  "
          f"concurrency={args.concurrency}  -> {args.output}", file=sys.stderr)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    out = open(args.output, "a", encoding="utf-8")
    t0 = time.time()
    n_ok = n_err = 0

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(process_row, r, shuffles.get(r["id"]), args, client, ws_fn): r
                for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            rid = futs[fut].get("id")
            try:
                pred = fut.result()
                n_ok += 1
            except Exception as e:
                pred = {"id": rid, "fatal_error": f"{type(e).__name__}: {e}",
                        "condition": args.condition, "run_index": args.run_index,
                        "timestamp_end": datetime.now(timezone.utc).isoformat()}
                n_err += 1
            with _write_lock:
                out.write(json.dumps(pred, ensure_ascii=False) + "\n")
                out.flush()
            if i % 25 == 0 or i == len(futs):
                el = time.time() - t0
                print(f"  {i}/{len(futs)}  ok={n_ok} err={n_err}  "
                      f"{el:.0f}s  {i/max(el,1e-9):.2f} rows/s  "
                      f"eta={(len(futs)-i)/max(i/max(el,1e-9),1e-9)/60:.1f} min",
                      file=sys.stderr)
    out.close()
    print(f"DONE rows={n_ok} errors={n_err} wall={time.time()-t0:.0f}s -> {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
