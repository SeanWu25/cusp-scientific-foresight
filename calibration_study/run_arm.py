"""
run_arm.py — inference runner for arms B1 / B2 / D / E of the A6 calibration study.

  python calibration_study/run_arm.py --model llama33 --arm B1 --temperature 0 --dry-run
  python calibration_study/run_arm.py --model llama33 --arm D  --temperature 1.0 --concurrency 6

Holds everything fixed except the named intervention:
  * system prompts are derived from scripts/test_LLM.py BINARY_SYSTEM / MCQ_SYSTEM
    (imported, never edited); the derivation is asserted at start-up and the full
    text + sha256 is written to raw/<model>_<arm>.manifest.json
  * user prompts are byte-identical to the base run (same question text; MCQ uses
    the SAME per-item option permutation the base run drew, read from the stored
    base predictions)
  * decoding: max_completion_tokens=2048, JSON mode, retries=2 — as get_model_response
  * items: the pinned 500-event subset; binary, binary_perturbed, mcq
Output: raw/<model>_<arm>.jsonl, one record per (id, task), appended, resumable.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, hashlib, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
from test_LLM import BINARY_SYSTEM, MCQ_SYSTEM, parse_structured_response  # frozen base prompts

FOUNDRY = "https://<your-azure-resource>.services.ai.azure.com/openai/v1"
INSTR = {"B1": "Before answering, consider what evidence would refute this realization.",
         "B2": "Before answering, consider the evidence for and the evidence against this realization."}
BASE_JSON_BIN = 'You MUST respond with valid JSON in exactly this format:\n{"reasoning": "<1-2 sentence justification>", "answer": "Yes or No", "confidence": <float 0.0-1.0>}'
BASE_JSON_MCQ = 'You MUST respond with valid JSON in exactly this format:\n{"reasoning": "<1-2 sentence justification>", "answer": "<single letter A, B, C, or D>", "confidence": <float 0.0-1.0>}'
assert BINARY_SYSTEM.endswith(BASE_JSON_BIN) and MCQ_SYSTEM.endswith(BASE_JSON_MCQ), "base prompts changed — stop"


def system_prompts(arm: str) -> dict:
    if arm in ("B1", "B2"):
        b = BINARY_SYSTEM.replace("give your final answer and confidence.\n\n", "give your final answer and confidence. " + INSTR[arm] + "\n\n")
        m = MCQ_SYSTEM.replace("about a technical development.\n\n", "about a technical development. " + INSTR[arm] + "\n\n")
        assert b != BINARY_SYSTEM and m != MCQ_SYSTEM
        assert b.endswith(BASE_JSON_BIN) and m.endswith(BASE_JSON_MCQ)  # confidence elicitation byte-identical
    elif arm == "D":
        b = BINARY_SYSTEM.replace("give your final answer and confidence.", "give your final answer.").replace(
            ', "answer": "Yes or No", "confidence": <float 0.0-1.0>}', ', "answer": "Yes or No"}')
        m = MCQ_SYSTEM.replace(', "answer": "<single letter A, B, C, or D>", "confidence": <float 0.0-1.0>}', ', "answer": "<single letter A, B, C, or D>"}')
        assert "confidence" not in b and "confidence" not in m
    elif arm == "E":
        b = BINARY_SYSTEM.replace("reason briefly then give your final answer and confidence.",
                                  "reason briefly then give the probability that the event occurs by the stated date. Do not give a yes/no answer.").replace(
            ', "answer": "Yes or No", "confidence": <float 0.0-1.0>}',
            ', "probability": <float 0.0-1.0, the probability that the answer is Yes>}')
        m = MCQ_SYSTEM.replace("You will be presented with a multiple-choice question about a technical development.",
                               "You will be presented with a multiple-choice question about a technical development. Do not pick a single answer; "
                               "give a probability for each option. The four probabilities must sum to 1.0.").replace(
            ', "answer": "<single letter A, B, C, or D>", "confidence": <float 0.0-1.0>}',
            ', "probabilities": {"A": <float>, "B": <float>, "C": <float>, "D": <float>}}')
        assert '"probability"' in b and '"probabilities"' in m
    else:
        raise ValueError(arm)
    return {"binary": b, "binary_perturbed": b, "mcq": m}


def user_prompt(task: str, bench_row: dict, base_raw_row: dict | None):
    if task == "binary":
        return bench_row["binary_question"], None, None
    if task == "binary_perturbed":
        return bench_row["binary_question_perturbed"], None, None
    labels = ["A", "B", "C", "D"]
    if base_raw_row and base_raw_row.get("mcq_shuffled_choices"):
        sc = base_raw_row["mcq_shuffled_choices"]; key = base_raw_row["mcq_shuffled_answer_key"]; src = "base_run"
        choices = [sc[L] for L in labels[:len(sc)]]
    else:  # deterministic fallback, flagged in the record
        import random
        orig = list(bench_row["mcq_choices"]); idx = list(range(len(orig)))
        random.Random(int(hashlib.sha256(bench_row["id"].encode()).hexdigest(), 16) % (2**32)).shuffle(idx)
        choices = [orig[i] for i in idx]; key = labels[choices.index(orig[bench_row["mcq_answer_key"]])]; src = "fallback_seeded"
    choices_str = "\n".join(f"({labels[i]}) {choices[i]}" for i in range(len(choices)))
    up = f"{bench_row['mcq_question']}\n\n{choices_str}\n\nSelect exactly one answer: {', '.join(labels[:len(choices)])}."
    return up, {labels[i]: choices[i] for i in range(len(choices))}, (key, src)


def _json_obj(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL) or re.search(r"(\{.*\})", raw, re.DOTALL)
        if m:
            try: return json.loads(m.group(1))
            except Exception: return None
    return None


def call(client, deploy, system, user, temperature, retries=2, max_tokens=2048):
    meta = {}
    last = None
    for attempt in range(1, retries + 2):
        t0 = time.time()
        try:
            r = client.chat.completions.create(model=deploy, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                                               max_completion_tokens=max_tokens, temperature=temperature, response_format={"type": "json_object"})
            ch = r.choices[0]; content = (ch.message.content or "").strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            u = r.usage
            meta.update(retries=attempt - 1, finish_reason=ch.finish_reason, model_snapshot=getattr(r, "model", deploy),
                        input_tokens=getattr(u, "prompt_tokens", None), output_tokens=getattr(u, "completion_tokens", None),
                        reasoning_tokens=getattr(getattr(u, "completion_tokens_details", None), "reasoning_tokens", None),
                        latency_s=round(time.time() - t0, 3), refusal=(ch.finish_reason == "content_filter"))
            return content, meta
        except Exception as e:
            last = e
            if "content_filter" in str(e) or "ResponsibleAIPolicyViolation" in str(e):
                meta.update(retries=attempt - 1, refusal=True, error=str(e)[:300], input_tokens=None, output_tokens=0, latency_s=round(time.time() - t0, 3))
                return "", meta
            if attempt <= retries:
                time.sleep(2 ** attempt)
    meta.update(retries=retries + 1, error=str(last)[:300], refusal=False, latency_s=None)
    return "", meta


def do_item(client, deploy, arm, temperature, n, sysp, task, bench_row, base_row):
    up, shuffled, keysrc = user_prompt(task, bench_row, base_row)
    rec = dict(id=bench_row["id"], task=task, arm=arm, deploy=deploy, temperature=temperature,
               system_sha=C.sha(sysp[task]), user_sha=C.sha(up), timestamp=datetime.now(timezone.utc).isoformat())
    if task == "mcq":
        rec.update(mcq_shuffled_choices=shuffled, mcq_answer_key=keysrc[0], mcq_permutation_source=keysrc[1])
    if arm == "D":
        samples, votes, tin, tout, lat, err = [], {}, 0, 0, 0.0, 0
        for k in range(n):
            raw, meta = call(client, deploy, sysp[task], up, temperature)
            obj = _json_obj(raw) if raw else None
            ans = None
            if obj and obj.get("answer") is not None:
                a = str(obj["answer"]).strip()
                ans = a.capitalize() if task != "mcq" else a.upper()[:1]
                if (task != "mcq" and ans not in ("Yes", "No")) or (task == "mcq" and ans not in "ABCD"):
                    ans = None
            samples.append(dict(raw=raw, answer=ans, reasoning=(obj or {}).get("reasoning"), **meta))
            if ans: votes[ans] = votes.get(ans, 0) + 1
            tin += meta.get("input_tokens") or 0; tout += meta.get("output_tokens") or 0; lat += meta.get("latency_s") or 0; err += bool(meta.get("error"))
        rec.update(n=n, n_valid=sum(votes.values()), votes=votes, samples=samples, n_calls=n, input_tokens=tin, output_tokens=tout,
                   latency_s=round(lat, 3), n_errors=err, error=(None if sum(votes.values()) else "no valid samples"))
        return rec
    raw, meta = call(client, deploy, sysp[task], up, temperature)
    rec.update(raw=raw, n_calls=1, **meta)
    if not raw:
        rec.setdefault("error", "empty response"); return rec
    if arm in ("B1", "B2"):
        p = parse_structured_response(raw, task_label=task)  # same parser as the base run
        rec.update(answer=p["answer"], reasoning=p["reasoning"], confidence=p["confidence"], parse_method=p["parse_method"])
    else:  # E
        obj = _json_obj(raw)
        rec["reasoning"] = (obj or {}).get("reasoning")
        if task != "mcq":
            try:
                v = float(obj["probability"]); rec["probability_raw"] = v; rec["probability"] = min(1.0, max(0.0, v))
                rec["parse_method"] = "json"
            except Exception:
                rec["probability"] = None; rec["parse_method"] = "error"; rec["error"] = "no probability parsed"
        else:
            pr = (obj or {}).get("probabilities")
            try:
                probs = {L: float(pr[L]) for L in "ABCD"}
                s = sum(probs.values()); rec["probs_raw"] = probs; rec["raw_sum"] = s
                if s > 0:
                    rec["probs_renorm"] = {L: v / s for L, v in probs.items()}
                else:
                    rec["probs_renorm"] = None; rec["error"] = "zero-sum probabilities"
                rec["parse_method"] = "json"
            except Exception:
                rec["probs_renorm"] = None; rec["parse_method"] = "error"; rec["error"] = "no probabilities parsed"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(C.MODELS))
    ap.add_argument("--arm", required=True, choices=["B1", "B2", "D", "E"])
    ap.add_argument("--temperature", type=float, required=True, help="set explicitly; recorded per record")
    ap.add_argument("--n", type=int, default=None, help="arm D samples per item (default: model registry n_sc)")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--deploy", default=None)
    a = ap.parse_args()
    m = C.MODELS[a.model]; deploy = a.deploy or m["deploy"]
    if not deploy:
        sys.exit(f"{a.model} has no live deployment configured")
    n = a.n or m["n_sc"]
    if a.arm == "D" and a.temperature <= 0:
        sys.exit("arm D at temperature 0 is meaningless — refuse to run")
    sysp = system_prompts(a.arm)
    bench, subset, base_raw = C.load_bench(), C.load_subset(), C.load_base_raw(a.model)
    out = C.RAW / f"{a.model}_{a.arm}.jsonl"
    manifest = dict(model=a.model, deploy=deploy, arm=a.arm, temperature=a.temperature, n=(n if a.arm == "D" else 1),
                    endpoint=FOUNDRY, max_completion_tokens=2048, json_mode=True, retries=2,
                    system_prompts={k: v for k, v in sysp.items()}, system_sha={k: C.sha(v) for k, v in sysp.items()},
                    base_prompt_sha={"binary": C.sha(BINARY_SYSTEM), "mcq": C.sha(MCQ_SYSTEM)},
                    subset_sha=C.sha("\n".join(subset)), created=datetime.now(timezone.utc).isoformat())
    jobs = []
    for i in subset:
        b = bench[i]
        for task, field in (("binary", "binary_question"), ("binary_perturbed", "binary_question_perturbed"), ("mcq", "mcq_question")):
            if b.get(field):
                jobs.append((task, b, base_raw.get(i)))
    if a.dry_run:
        print(json.dumps(manifest, indent=1)[:4000])
        for task, b, br in jobs[:3]:
            up, sc, ks = user_prompt(task, b, br)
            print(f"\n--- {task} {b['id']}\n[SYSTEM]\n{sysp[task]}\n[USER]\n{up}\n[key/src] {ks}")
        print(f"\n{len(jobs)} (id, task) jobs; arm D would make {len(jobs) * n} calls at n={n}")
        return
    done = set()
    if out.exists():
        for l in open(out):
            if l.strip():
                r = json.loads(l); done.add((r["id"], r["task"]))
    jobs = [j for j in jobs if (j[1]["id"], j[0]) not in done]
    if a.max_items:
        jobs = jobs[:a.max_items]
    (C.RAW / f"{a.model}_{a.arm}.manifest.json").write_text(json.dumps(manifest, indent=1))
    from dotenv import load_dotenv; load_dotenv(str(C.ROOT / ".env"))
    from openai import OpenAI
    client = OpenAI(base_url=FOUNDRY, api_key=os.environ["AZURE_OPENAI_KEY"], max_retries=2, timeout=180)
    print(f"{a.model}/{a.arm} deploy={deploy} T={a.temperature} n={n if a.arm == 'D' else 1}: {len(done)} done, {len(jobs)} to run", file=sys.stderr)
    lock = threading.Lock(); t0 = time.time(); k = 0; tin = tout = nerr = 0
    with open(out, "a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = {ex.submit(do_item, client, deploy, a.arm, a.temperature, n, sysp, task, b, br): (task, b["id"]) for task, b, br in jobs}
        for fut in as_completed(futs):
            try:
                rec = fut.result()
            except Exception as e:
                task, rid = futs[fut]; rec = dict(id=rid, task=task, arm=a.arm, deploy=deploy, temperature=a.temperature, error=f"worker: {e}"[:300])
            with lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); k += 1
                tin += rec.get("input_tokens") or 0; tout += rec.get("output_tokens") or 0; nerr += bool(rec.get("error"))
                if k % 50 == 0 or k == len(jobs):
                    print(f"  {k}/{len(jobs)}  {time.time() - t0:.0f}s  tokens in/out {tin:,}/{tout:,}  errors so far: {nerr}", file=sys.stderr)
    print(f"finished {a.model}/{a.arm}: wrote {k} records to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
