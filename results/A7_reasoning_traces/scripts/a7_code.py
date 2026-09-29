"""
a7_code.py — Step 2: code the sample with one coder model. Resumable per trace.

  python scripts/a7_code.py --coder haiku45 [--limit 200] [--concurrency 8]
  python scripts/a7_code.py --coder haiku45 --faithfulness      # analysis D judge

Blinding: every call goes through a7_prompts.code_prompt / faith_prompt, which rebuild the
user message from a fixed template and compare it byte for byte, and reject any forbidden
field. A failure raises and the item is written with an error rather than silently coded.
Output: raw/<coder>[_faith].jsonl, one record per trace, appended, resumable.
"""
from __future__ import annotations
import argparse, json, os, random, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P

CODERS = {
    "haiku45":   dict(name="Claude Haiku 4.5", model="claude-haiku-4-5", provider="anthropic",
                      price=(1.00, 5.00), conc=12),
    "gpt54mini": dict(name="GPT-5.4-mini", model="gpt-5.4-mini", provider="openai",
                      price=(0.25, 2.00), conc=12, reasoning_effort="none"),
    "gpt54mini_low": dict(name="GPT-5.4-mini (low effort)", model="gpt-5.4-mini", provider="openai",
                          price=(0.25, 2.00), conc=12, reasoning_effort="low"),
}
MAXTOK = {"code": 900, "faith": 300}


def client(provider):
    from dotenv import load_dotenv; load_dotenv(str(C.ROOT / ".env"))
    if provider == "anthropic":
        import anthropic
        return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], max_retries=0, timeout=180)
    from openai import OpenAI
    return OpenAI(base_url="https://api.openai.com/v1", api_key=os.environ["OPENAI_API_KEY"], max_retries=0, timeout=180)


def call(cl, m, system, user, kind, retries=3):
    """Returns (text, meta). System prompt is cached (explicit for Anthropic, automatic for OpenAI)."""
    meta, last = {}, None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            if m["provider"] == "anthropic":
                # The codebook travels as the FIRST user content block with a cache breakpoint.
                # cache_control on a `system` block is accepted but not honoured on this account
                # (verified: cache_creation stays 0), so the shared prefix is sent this way instead.
                blocks = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}},
                          {"type": "text", "text": user}]
                assert [b["text"] for b in blocks] == [system, user], "transport altered the prompt"
                r = cl.messages.create(model=m["model"], max_tokens=MAXTOK[kind],
                                       messages=[{"role": "user", "content": blocks}])
                txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
                u = r.usage
                meta.update(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                            cache_read=getattr(u, "cache_read_input_tokens", 0) or 0,
                            cache_write=getattr(u, "cache_creation_input_tokens", 0) or 0,
                            snapshot=r.model, stop_reason=r.stop_reason)
            else:
                kw = {}
                if m.get("reasoning_effort"): kw["reasoning_effort"] = m["reasoning_effort"]
                r = cl.chat.completions.create(
                    model=m["model"], messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    max_completion_tokens=MAXTOK[kind], response_format={"type": "json_object"}, **kw)
                txt = (r.choices[0].message.content or "").strip()
                u = r.usage
                det = getattr(u, "prompt_tokens_details", None)
                meta.update(input_tokens=u.prompt_tokens, output_tokens=u.completion_tokens,
                            cache_read=getattr(det, "cached_tokens", 0) or 0, cache_write=0,
                            snapshot=r.model, stop_reason=r.choices[0].finish_reason)
            meta["retries"] = attempt; meta["latency_s"] = round(time.time() - t0, 3)
            return txt, meta
        except Exception as e:
            last = e
            if attempt < retries: time.sleep(2 ** attempt)
    return "", dict(error=str(last)[:300], retries=retries + 1, input_tokens=0, output_tokens=0, cache_read=0, cache_write=0)


def _json(txt):
    try:
        return json.loads(txt)
    except Exception:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", txt, re.DOTALL) or re.search(r"(\{.*\})", txt, re.DOTALL)
        if m:
            try: return json.loads(m.group(1))
            except Exception: return None
    return None


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def _verbatim(span, hay):
    """True when the span is a contiguous quote of the passage. A span the coder joined with an
    ellipsis counts only if its longest fragment (>= 4 words) is itself verbatim; that case is
    counted separately in agreement.md as a partial quote."""
    n = _norm(span)
    if not n:
        return None
    if n in hay:
        return True
    parts = [p for p in re.split(r"\.{2,}|\u2026", n) if len(p.split()) >= 4]
    return bool(parts) and max(parts, key=len) in hay


def parse_codes(obj, passage):
    """-> (codes dict, problems list). codes[CODE] = {verdict, span, span_verbatim}."""
    out, prob = {}, []
    fired = (obj or {}).get("fired") or {}
    if not isinstance(fired, dict):
        prob.append("fired is not an object"); fired = {}
    hay = _norm(passage)
    for code in P.CODES:
        sp = fired.get(code)
        if sp is None:
            out[code] = dict(verdict="no", span="", span_verbatim=None)
        else:
            sp = sp if isinstance(sp, str) else json.dumps(sp)
            out[code] = dict(verdict="yes", span=sp[:400], span_verbatim=_verbatim(sp, hay))
    for k in fired:
        if k not in P.CODES: prob.append(f"unknown code {k}")
    # RESTATEMENT_ONLY is defined as "nothing else fires"; enforce it rather than trusting the coder
    if out["RESTATEMENT_ONLY"]["verdict"] == "yes" and any(
            out[c]["verdict"] == "yes" for c in P.CODES if c != "RESTATEMENT_ONLY"):
        out["RESTATEMENT_ONLY"] = dict(verdict="no", span="", span_verbatim=None)
        prob.append("RESTATEMENT_ONLY overridden: other codes fired")
    h = (obj or {}).get("HEDGING")
    if isinstance(h, dict) and str(h.get("level")) in ("0", "1", "2", "3"):
        sp = h.get("span") or ""
        out["HEDGING"] = dict(verdict=int(h["level"]), span=str(sp)[:400], span_verbatim=_verbatim(str(sp), hay))
    else:
        out["HEDGING"] = dict(verdict=None, span="", span_verbatim=None); prob.append("HEDGING missing or invalid")
    return out, prob


def do_one(cl, m, coder, r, faith):
    system, user = (P.faith_prompt(r) if faith else P.code_prompt(r))
    txt, meta = call(cl, m, system, user, "faith" if faith else "code")
    rec = dict(trace_id=r["trace_id"], coder=coder, coder_model=m["model"],
               kind=("faithfulness" if faith else "codes"),
               system_sha=C.sha(system)[:16], user_sha=C.sha(user)[:16],
               timestamp=datetime.now(timezone.utc).isoformat(), raw=txt, **meta)
    obj = _json(txt) if txt else None
    if faith:
        pa = str((obj or {}).get("predicted_answer") or "").strip()
        rec["predicted_answer"] = pa or None
        rec["judge_confidence"] = (obj or {}).get("confidence")
        b = str((obj or {}).get("basis") or "")
        rec["basis"] = b[:400]; rec["basis_verbatim"] = _verbatim(b, _norm(r["trace"]))
        if not pa: rec["parse_error"] = "no predicted_answer"
    else:
        codes, prob = parse_codes(obj, r["trace"])
        rec["codes"] = codes
        if prob: rec["problems"] = prob
        if obj is None: rec["parse_error"] = "unparseable JSON"
    pi, po = m["price"]
    cr, cw = rec.get("cache_read", 0), rec.get("cache_write", 0)
    fresh = max(0, (rec.get("input_tokens") or 0) - cr - cw)
    rec["cost_usd"] = round((fresh * pi + cr * pi * 0.1 + cw * pi * 1.25 + (rec.get("output_tokens") or 0) * po) / 1e6, 8)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coder", required=True, choices=list(CODERS))
    ap.add_argument("--faithfulness", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="pilot: cap items this invocation")
    ap.add_argument("--pilot-seed", type=int, default=None, help="with --limit, draw a random subset instead of a prefix")
    ap.add_argument("--concurrency", type=int, default=None)
    a = ap.parse_args()
    m = CODERS[a.coder]
    samp = json.load(open(C.STUDY / "coding_sample.json"))
    want = {r["trace_id"] for r in samp["traces"]}
    tr = {r["trace_id"]: r for r in C.iter_traces(lambda r: r["trace_id"] in want)}
    items = [tr[i] for i in sorted(want) if i in tr]
    if a.faithfulness:
        items = [r for r in items if r["task"] in ("binary", "binary_perturbed", "mcq")]
    out = C.STUDY / "raw" / f"{a.coder}{'_faith' if a.faithfulness else ''}.jsonl"
    done = set()
    if out.exists():
        for l in open(out, encoding="utf-8"):
            if l.strip():
                d = json.loads(l)
                if not d.get("error"): done.add(d["trace_id"])
    todo = [r for r in items if r["trace_id"] not in done]
    if a.limit:
        todo = random.Random(a.pilot_seed).sample(todo, min(a.limit, len(todo))) if a.pilot_seed is not None else todo[:a.limit]
    cl = client(m["provider"])
    conc = a.concurrency or m["conc"]
    print(f"{a.coder} ({m['model']}) {'faithfulness' if a.faithfulness else 'coding'}: {len(done)} done, {len(todo)} to run, conc {conc}", file=sys.stderr)
    lock = threading.Lock(); t0 = time.time(); k = 0; cost = 0.0; nerr = 0; npar = 0
    with open(out, "a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=conc) as ex:
        futs = {ex.submit(do_one, cl, m, a.coder, r, a.faithfulness): r["trace_id"] for r in todo}
        for fut in as_completed(futs):
            try:
                rec = fut.result()
            except Exception as e:
                rec = dict(trace_id=futs[fut], coder=a.coder, error=f"worker: {e}"[:300],
                           timestamp=datetime.now(timezone.utc).isoformat())
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); k += 1
                cost += rec.get("cost_usd") or 0.0; nerr += bool(rec.get("error")); npar += bool(rec.get("parse_error"))
                if k % 200 == 0 or k == len(todo):
                    print(f"  {k}/{len(todo)}  {time.time()-t0:.0f}s  ${cost:.2f}  errors {nerr}  parse_errors {npar}", file=sys.stderr)
    print(f"finished {a.coder}: {k} records, ${cost:.2f}, {nerr} errors, {npar} parse errors -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
