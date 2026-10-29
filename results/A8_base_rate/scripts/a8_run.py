"""
a8_run.py — inference runner for the base-rate injection sweep.

  python scripts/a8_run.py --model sonnet5 --dry-run          # print prompts, no calls
  python scripts/a8_run.py --model sonnet5 [--x 10,30] [--max-items N] [--concurrency K]

Holds everything fixed except the injected sentence:
  * system prompt = BINARY_SYSTEM (scripts/test_LLM.py, imported, never edited) with ONE
    sentence inserted between the instruction and the JSON/confidence block
    (a8_common.injected_system); asserted byte-identical elsewhere at start-up
  * user prompt = the stored question text, unchanged
  * call path = the frozen test_LLM.get_model_response / get_claude_response, with the
    same decoding the model's stored base run used (registry `decoding`), JSON mode for
    OpenAI-family providers, max_tokens 2048, retries 2 — as scripts/run_cusp.py
  * parser = test_LLM.parse_structured_response (the base run's parser)
Output: raw/<model>.jsonl, one record per (x, id, task), appended, resumable per item.
Job order is (id, task, x) so an interrupted run leaves complete curves on a prefix.
"""
from __future__ import annotations
import argparse, json, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a8_common as C
from test_LLM import get_model_response, get_claude_response, parse_structured_response


def make_client(provider: str):
    from dotenv import load_dotenv; load_dotenv(str(C.ROOT / ".env"))
    if provider == "anthropic":
        import anthropic
        return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], max_retries=0, timeout=180)
    from openai import OpenAI
    if provider == "azure":
        return OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_KEY"], max_retries=0, timeout=180)
    if provider == "openai":
        return OpenAI(base_url="https://api.openai.com/v1", api_key=os.environ["OPENAI_API_KEY"], max_retries=0, timeout=180)
    if provider == "local":
        return OpenAI(base_url="http://127.0.0.1:8077/v1", api_key="local-vllm", max_retries=0, timeout=600)
    raise ValueError(provider)


def call(client, m: dict, system: str, user: str) -> tuple[str, dict]:
    """Same call path as run_cusp.call_model: frozen test_LLM functions, meta captured."""
    meta = {"retries": 0, "refusal": False, "stop_reason": None, "input_tokens": None, "output_tokens": None,
            "model_snapshot": m["model"], "error": None, "reasoning_tokens": None}
    dec = m["decoding"]; t0 = time.time()
    if m["provider"] == "anthropic":
        raw = get_claude_response(client, m["model"], system, user, temperature=dec.get("temperature", 0.0),
                                  max_tokens=2048, retries=2, effort=dec.get("effort"), meta_out=meta)
    else:
        raw = get_model_response(client, m["model"], system, user, temperature=dec.get("temperature", 0.0),
                                 max_tokens=2048, retries=2, json_mode=True, reasoning_effort=dec.get("effort"), meta_out=meta)
    meta["latency_s"] = round(time.time() - t0, 3)
    if raw.startswith("Error:"):
        meta["error"] = raw[:400]
    meta.pop("thinking", None)
    return raw, meta


def do_item(client, key: str, m: dict, x: int, task: str, row: dict) -> dict:
    system = C.injected_system(x); user = C.user_prompt(task, row)
    rec = dict(id=row["id"], task=task, x=x, model=key, model_id=m["model"], provider=m["provider"], decoding=m["decoding"],
               y=(1 if task == "binary" else 0), system_sha=C.sha(system), user_sha=C.sha(user),
               timestamp=datetime.now(timezone.utc).isoformat())
    raw, meta = call(client, m, system, user)
    rec.update(raw=raw, **meta)
    p = parse_structured_response(raw, task_label=task) if raw and not raw.startswith("Error:") else None
    if p is None:
        rec.update(answer=None, reasoning=None, confidence=None, parse_method="error")
        rec.setdefault("error", "empty response")
    else:
        rec.update(answer=p["answer"], reasoning=p["reasoning"], confidence=p["confidence"], parse_method=p["parse_method"])
    pi, po = m["price"]
    if meta.get("input_tokens") is not None:
        rec["cost_usd"] = round((meta["input_tokens"] or 0) * pi / 1e6 + (meta["output_tokens"] or 0) * po / 1e6, 8)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=C.RUNNABLE)
    ap.add_argument("--x", default=",".join(map(str, C.XS)))
    ap.add_argument("--concurrency", type=int, default=None)
    ap.add_argument("--max-items", type=int, default=None, help="cap on (id, task, x) jobs this invocation")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry-errors", action="store_true", help="re-run items whose stored record carries a transport error (not refusals/truncations); the analysis keeps the LAST record per (x, id, task)")
    a = ap.parse_args()
    m = C.MODELS[a.model]; xs = [int(v) for v in a.x.split(",")]
    assert all(x in C.XS for x in xs), xs
    bench, sample = C.load_bench(), C.load_sample()
    out = C.RAW / f"{a.model}.jsonl"
    jobs = [(i, task, x) for i in sample["ids"] for task in ("binary", "binary_perturbed") for x in xs]
    if a.dry_run:
        for x in xs:
            print(f"\n===== SYSTEM PROMPT, X={x} (sha256 {C.sha(C.injected_system(x))[:16]})\n{C.injected_system(x)}")
        i = sample["ids"][0]
        print(f"\n===== USER PROMPT example, {i}\n[binary] {bench[i]['binary_question']}\n[binary_perturbed] {bench[i]['binary_question_perturbed']}")
        print(f"\n{len(jobs)} (id, task, x) jobs for {a.model} ({m['model']} via {m['provider']}, decoding {m['decoding']})")
        return
    done = set()
    if out.exists():
        for l in open(out, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                if a.retry_errors and r.get("error") and not r.get("refusal"):
                    continue
                done.add((r["id"], r["task"], r["x"]))
    jobs = [j for j in jobs if j not in done]
    if a.max_items:
        jobs = jobs[:a.max_items]
    conc = a.concurrency or m["conc"]
    client = make_client(m["provider"])
    print(f"{a.model} ({m['model']} via {m['provider']}, {m['decoding']}): {len(done)} done, {len(jobs)} to run, concurrency {conc}", file=sys.stderr)
    lock = threading.Lock(); t0 = time.time(); k = 0; tin = tout = nerr = 0; cost = 0.0
    with open(out, "a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=conc) as ex:
        futs = {ex.submit(do_item, client, a.model, m, x, task, bench[i]): (i, task, x) for i, task, x in jobs}
        for fut in as_completed(futs):
            try:
                rec = fut.result()
            except Exception as e:
                i, task, x = futs[fut]
                rec = dict(id=i, task=task, x=x, model=a.model, model_id=m["model"], provider=m["provider"], answer=None,
                           confidence=None, parse_method="error", error=f"worker: {e}"[:400], timestamp=datetime.now(timezone.utc).isoformat())
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); k += 1
                tin += rec.get("input_tokens") or 0; tout += rec.get("output_tokens") or 0
                nerr += bool(rec.get("error")); cost += rec.get("cost_usd") or 0.0
                if k % 100 == 0 or k == len(jobs):
                    print(f"  {k}/{len(jobs)}  {time.time() - t0:.0f}s  tokens in/out {tin:,}/{tout:,}  errors {nerr}  ${cost:.2f}", file=sys.stderr)
    print(f"finished {a.model}: wrote {k} records to {out}; ${cost:.2f} at assumed list prices", file=sys.stderr)


if __name__ == "__main__":
    main()
