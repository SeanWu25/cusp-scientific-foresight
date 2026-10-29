"""
detect.py — Study 2. Pairwise "which one is LLM-modified?"

Each sampled pair is shown to each judge TWICE: once with the original claim
first and once with the perturbed claim first. Dates are stripped from both
claims beforehand. The judge is asked only which statement a language model
modified -- never which is scientifically achievable, and never anything about
dates or ground-truth labels.

This pipeline reads nothing produced by verify.py and writes nothing that
verify.py reads.

Usage
  python detect.py --judge opus48 [--limit N] [--workers K]
  python detect.py --judge gpt54  [--limit N] [--workers K]
"""
from __future__ import annotations
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

from dotenv import load_dotenv
load_dotenv(C.ROOT / ".env")

JUDGES = {
    "opus48": dict(provider="anthropic", model="claude-opus-4-8", label="Claude Opus 4.8",
                   in_panel=False),
    "gpt54":  dict(provider="openai", model="gpt-5.4", label="GPT-5.4", in_panel=True),
}

SYSTEM = (
    "You compare two short statements and identify which one a language model rewrote. "
    "Answer with the JSON object only."
)

PROMPT = """\
Below are two statements about the same scientific result. One is the original \
statement. The other was produced by a language model that modified the original.

Statement A: {a}

Statement B: {b}

Which of these two statements was modified by a language model?

Reply with ONLY a JSON object, no prose around it:
{{"answer": "A" | "B", "confidence": <0.0-1.0>, "reason": "one short sentence"}}"""

_lock = threading.Lock()


def extract_json(text: str) -> dict | None:
    t = (text or "").strip()
    if t.startswith("```"):
        parts = t.split("```")
        if len(parts) > 1:
            t = parts[1]
        t = t[4:] if t.lower().startswith("json") else t
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(t[i:j + 1])
    except Exception:
        return None


def ask_anthropic(client, model, prompt):
    r = client.messages.create(
        model=model, max_tokens=2000, system=SYSTEM,
        thinking={"type": "adaptive"}, output_config={"effort": "high"},
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    return text, dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens), r.model, r.stop_reason


def ask_openai(client, model, prompt):
    r = client.chat.completions.create(
        model=model, max_completion_tokens=2000, reasoning_effort="medium",
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
    text = r.choices[0].message.content or ""
    u = r.usage
    return text, dict(input_tokens=u.prompt_tokens, output_tokens=u.completion_tokens), r.model, r.choices[0].finish_reason


def run_one(client, judge: str, pair: dict, order: str) -> dict:
    cfg = JUDGES[judge]
    orig, pert = pair["claim_original"], pair["claim_perturbed"]
    a, b = (orig, pert) if order == "original_first" else (pert, orig)
    perturbed_slot = "B" if order == "original_first" else "A"
    prompt = PROMPT.format(a=a, b=b)
    t0, err, text, usage, served, stop = time.time(), None, None, None, None, None
    parsed, attempts = {}, 0
    for attempt in range(4):
        attempts = attempt + 1
        try:
            fn = ask_anthropic if cfg["provider"] == "anthropic" else ask_openai
            text, usage, served, stop = fn(client, cfg["model"], prompt)
            parsed = extract_json(text or "") or {}
            a0 = str(parsed.get("answer", "")).strip().upper()[:1]
            if a0 in ("A", "B"):
                err = None
                break
            if stop == "refusal":
                err = "refusal"
                break
            err = f"empty_or_unparsed(stop={stop},out_tok={(usage or {}).get('output_tokens')})"
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        time.sleep(2 * (attempt + 1))
    ans = str(parsed.get("answer", "")).strip().upper()[:1]
    ans = ans if ans in ("A", "B") else None
    return dict(
        pair_id=pair["id"], judge=judge, judge_model=cfg["model"], served_model=served,
        order=order, perturbed_slot=perturbed_slot, answer=ans,
        correct=(None if ans is None else ans == perturbed_slot),
        chose_first=(None if ans is None else ans == "A"),
        confidence=parsed.get("confidence"), reason=(parsed.get("reason") or "")[:400],
        main_area=pair.get("main_area"), ptype=pair.get("ptype"), corpus=pair.get("corpus"),
        weight=pair.get("weight"), stratum=pair.get("stratum"),
        len_original=pair["len_original"], len_perturbed=pair["len_perturbed"],
        usage=usage, error=err, parse_ok=bool(parsed), stop_reason=stop, attempts=attempts,
        refused=(stop == "refusal"),
        prompt_sha=C.sha(SYSTEM + "\n" + PROMPT), raw_text=(text or "")[:1500],
        ts=C.now_utc(), elapsed_s=round(time.time() - t0, 1),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", required=True, choices=list(JUDGES))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    pairs = json.loads((C.S2 / "pairs.json").read_text(encoding="utf-8"))["pairs"]
    out = Path(a.out) if a.out else (C.S2 / "judgments.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["pair_id"], r["judge"], r["order"]) for r in C.read_jsonl(out) if r.get("answer")}

    jobs = [(p, o) for p in pairs for o in ("original_first", "perturbed_first")
            if (p["id"], a.judge, o) not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f"judge={a.judge} ({JUDGES[a.judge]['model']}): {len(pairs)} pairs x 2 orders, "
          f"{len(jobs)} calls to run -> {out}")
    if not jobs:
        return

    if JUDGES[a.judge]["provider"] == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=300.0, max_retries=3)
    else:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=300.0, max_retries=3)

    n_ok = n_bad = n_corr = 0
    tot = dict(input_tokens=0, output_tokens=0)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_one, client, a.judge, p, o) for p, o in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with _lock:
                C.append_jsonl(out, rec)
            for k in tot:
                tot[k] += (rec.get("usage") or {}).get(k, 0)
            if rec["answer"]:
                n_ok += 1
                n_corr += bool(rec["correct"])
            else:
                n_bad += 1
            if i % 50 == 0 or i == len(jobs):
                acc = n_corr / n_ok if n_ok else 0
                print(f"  [{i}/{len(jobs)}] parsed={n_ok} failed={n_bad} running_acc={acc:.3f} "
                      f"in={tot['input_tokens']:,} out={tot['output_tokens']:,} "
                      f"{(time.time()-t0)/60:.1f}min", flush=True)
    print(f"done {a.judge}: {n_ok} judgments, {n_bad} failures, acc={n_corr/max(n_ok,1):.4f}, usage={tot}")


if __name__ == "__main__":
    main()
