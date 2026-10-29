"""
verify_neg_strict.py — Study 1, negatives, strict re-verification.

The first pass (verify.py negatives) asked whether the perturbed claim "was
achieved" by someone other than the source paper. That question is too easy to
answer yes to: a nearby result, the same advance in a different system, or a
qualitative restatement of a numeric threshold can all be argued into a match.

This pass re-runs all 200 sampled negatives under a harder standard. A negative
is mislabelled ONLY if the EXACT perturbed claim actually happened in the real
world by the target date. Anything less is NOT ACHIEVED.

The six rules are enforced twice: once in the prompt, and once in code
(neg_gates.py) against the referee's own record. An ACHIEVED verdict that cannot
produce the exact reported value or satisfied constraint, the date, the source
URL and a quoted passage showing it is invalid, and is downgraded with the
failing gates logged.

Previous outputs are never touched. This writes negatives_verdicts_strict.jsonl
and evidence/negatives_strict/ alongside them.

Usage
  python verify_neg_strict.py [--model sonnet5] [--limit N] [--workers K]
"""
from __future__ import annotations
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import neg_gates as G

from dotenv import load_dotenv
load_dotenv(C.ROOT / ".env")

# The first pass ran on claude-opus-4-8 at $80.93 for 200 items. The gates below
# do the work that an expensive referee would otherwise be trusted to do on its
# own word, so the referee itself can be a cheaper model.
REFEREES = {
    "haiku45":   dict(provider="anthropic", model="claude-haiku-4-5-20251001"),
    "sonnet5":   dict(provider="anthropic", model="claude-sonnet-5"),
    "gpt54mini": dict(provider="openai", model="gpt-5.4-mini"),
    "gpt55":     dict(provider="openai", model="gpt-5.5"),
    "opus48":    dict(provider="anthropic", model="claude-opus-4-8"),
}

SYSTEM = (
    "You are a meticulous scientific fact-checker with live web access, working after the "
    "fact: every target date below is in the past, so the record is already public. Your job "
    "is to resist a match, not to find one. You are rewarded for being correct. NOT_ACHIEVED "
    "is the right answer whenever the evidence is absent, partial, indirect, ambiguous, or "
    "merely close, and it is the answer you should reach for by default."
)

PROMPT = """\
PERTURBED CLAIM:
{claim}

TARGET DATE: {target}
FIELD: {area}

EXCLUDED SOURCE -- this paper, and any report, preprint, press release or restatement \
of this same piece of work, can NEVER count as achieving the claim:
  link: {link}
  topic: {topic}

TASK
Search the web. Decide whether the EXACT claim above actually happened in the real world, \
achieved and publicly reported by a group OTHER than the excluded source, ON OR BEFORE \
{target}.

RULES -- apply them literally. They decide the answer, and they are checked in code \
afterwards against what you write below.

1. EXACT VALUE. If the claim states a numeric value, threshold, factor, rate or range, it \
counts as ACHIEVED only if a reported result MEETS OR EXCEEDS that exact modified value in \
the direction the claim requires. Close, comparable, approaching, "on the same order", \
"essentially equivalent" or "restored to normal levels" do NOT count. A qualitative \
statement never satisfies a numeric requirement.

2. EXACT CONSTRAINT. If the claim adds a constraint, requirement or condition, it counts as \
ACHIEVED only if that exact constraint was actually satisfied. Achieving the underlying \
advance WITHOUT satisfying the constraint does NOT count.

3. SAME SETTING. The achievement must be for the SAME task, system, model, material, \
organism, cohort or measurement as the claim. A similar result in a different setting does \
NOT count -- not a different benchmark, not a different cell line, not a different assay, \
not a different patient population, not in vitro for an in vivo claim.

4. ON TIME. The work must be publicly reported ON OR BEFORE {target}. Later does not count, \
however small the gap.

5. NOT THE SOURCE. The excluded source above never counts, in any venue or restatement.

6. DEFAULT TO NO. If the evidence is partial, indirect, ambiguous, or you cannot find it, \
the verdict is NOT_ACHIEVED. Answer ACHIEVED only on direct evidence meeting every \
condition above.

EVIDENCE REQUIRED FOR ACHIEVED
An ACHIEVED verdict is invalid unless you supply ALL of:
  (a) the exact reported value (for a numeric claim) or the exact satisfied constraint;
  (b) the date the achieving work was publicly reported;
  (c) the URL of that work;
  (d) a verbatim quoted passage from that work stating the value or the constraint.
The quoted passage must be copied character for character and must itself contain the \
figure or the condition -- a title, an abstract summary that omits the number, or your own \
paraphrase is not acceptable. ONE source must satisfy the whole claim; if you need to \
combine two works, the verdict is NOT_ACHIEVED.

Reply with ONLY a JSON object, no prose around it:
{{"verdict": "ACHIEVED" | "NOT_ACHIEVED",
  "confidence": <0.0-1.0>,
  "claim_requirement": "the exact modified value or added constraint the claim demands, quoted from the claim",
  "requirement_kind": "numeric" | "constraint",
  "reported_value": "the exact figure the achieving work reports, with units, or \\"\\"",
  "satisfied_constraint": "the exact constraint and how the work satisfies it, or \\"\\"",
  "source_name": "the ONE achieving work relied on, or \\"\\"",
  "source_url": "its URL, or \\"\\"",
  "source_date": "YYYY-MM or YYYY-MM-DD, or \\"\\"",
  "quoted_passage": "verbatim passage from that work stating the value or constraint, or \\"\\"",
  "same_setting": true | false,
  "same_setting_note": "one line: is this the same task/system/measurement as the claim, or a different one?",
  "excluded_source_distinct": true | false,
  "urls": ["..."],
  "reason": "one sentence naming the exact requirement and whether it was met, and by whom"}}"""

_lock = threading.Lock()
VALID = {"ACHIEVED", "NOT_ACHIEVED"}


def extract_json(text: str):
    t = (text or "").strip()
    if "```" in t:
        parts = t.split("```")
        if len(parts) > 1:
            t = parts[1]
            t = t[4:] if t.lower().startswith("json") else t
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    for end in (j, *[k for k in range(len(t) - 1, i, -1) if t[k] == "}"][:6]):
        try:
            return json.loads(t[i:end + 1])
        except Exception:
            continue
    return None


# Adaptive thinking, output_config and the dynamic-filtering web-search tool all
# landed with the 4.6 generation. A 4.5 model rejects them with a 400 rather than
# ignoring them, so it gets the basic search tool and no thinking block.
def _pre46(model: str) -> bool:
    return any(t in model for t in ("haiku-4-5", "sonnet-4-5", "opus-4-5"))


def ask_anthropic(model, system, prompt):
    import anthropic
    cl = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=900.0, max_retries=3)
    kw = dict(model=model, max_tokens=8000, system=system)
    if _pre46(model):
        kw["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}]
    else:
        kw |= dict(thinking={"type": "adaptive"}, output_config={"effort": "high"},
                   tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}])
    msgs = [{"role": "user", "content": prompt}]
    usage = dict(input_tokens=0, output_tokens=0, web_search_requests=0)
    text, searches, queries, rounds = "", [], [], 0
    while True:
        rounds += 1
        r = cl.messages.create(messages=msgs, **kw)
        usage["input_tokens"] += r.usage.input_tokens or 0
        usage["output_tokens"] += r.usage.output_tokens or 0
        st = getattr(r.usage, "server_tool_use", None)
        if st is not None:
            usage["web_search_requests"] += getattr(st, "web_search_requests", 0) or 0
        for b in r.content:
            bt = getattr(b, "type", "")
            if bt == "text":
                text += b.text
            elif bt == "server_tool_use":
                q = (getattr(b, "input", {}) or {}).get("query")
                if q:
                    queries.append(q)
            elif bt == "web_search_tool_result":
                cont = getattr(b, "content", None)
                if isinstance(cont, list):
                    for x in cont:
                        searches.append(dict(url=getattr(x, "url", None),
                                             title=getattr(x, "title", None)))
        if r.stop_reason == "pause_turn" and rounds < 6:
            msgs = msgs + [{"role": "assistant", "content": r.content}]
            continue
        return text, usage, r.model, r.stop_reason, searches, queries, rounds


def ask_openai(model, system, prompt):
    from openai import OpenAI
    cl = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=900.0, max_retries=3)
    r = cl.responses.create(model=model, instructions=system, input=prompt,
                            tools=[{"type": "web_search"}])
    text = "".join(o.content[0].text for o in r.output
                   if getattr(o, "type", "") == "message" and getattr(o, "content", None))
    searches = [dict(url=None, title=None) for o in r.output
                if getattr(o, "type", "") == "web_search_call"]
    usage = dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens,
                 web_search_requests=len(searches))
    return text, usage, r.model, "end_turn", searches, [], 1


def run_one(key: str, it: dict) -> dict:
    cfg = REFEREES[key]
    prompt = PROMPT.format(
        claim=it["binary_question_perturbed"], target=it["target_human"],
        area=it.get("main_area") or "unspecified",
        link=it.get("paper_link") or "(not recorded)",
        topic=(it.get("problem_statement") or "(not recorded)")[:400])
    t0, err, text, usage, served, stop = time.time(), None, "", None, None, None
    searches, queries, rounds, parsed = [], [], 0, {}
    for attempt in range(3):
        try:
            fn = ask_anthropic if cfg["provider"] == "anthropic" else ask_openai
            text, usage, served, stop, searches, queries, rounds = fn(cfg["model"], SYSTEM, prompt)
            parsed = extract_json(text) or {}
            if str(parsed.get("verdict", "")).strip().upper() in VALID:
                err = None
                break
            err = f"unparsed(stop={stop})"
            if stop == "refusal":
                break
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        time.sleep(3 * (attempt + 1))

    v = str(parsed.get("verdict", "")).strip().upper().replace(" ", "_")
    refused = (stop == "refusal")
    raw = v if v in VALID else ("REFUSED" if refused else None)

    rec = dict(
        id=it["id"], kind="negatives_strict", referee=key, referee_model=cfg["model"],
        served_model=served,
        raw_verdict=raw,
        confidence=parsed.get("confidence"),
        claim_requirement=parsed.get("claim_requirement") or "",
        requirement_kind=parsed.get("requirement_kind") or "",
        reported_value=parsed.get("reported_value") or "",
        satisfied_constraint=parsed.get("satisfied_constraint") or "",
        source_name=parsed.get("source_name") or "",
        source_url=parsed.get("source_url") or "",
        source_date=parsed.get("source_date") or "",
        quoted_passage=parsed.get("quoted_passage") or "",
        same_setting=parsed.get("same_setting"),
        same_setting_note=parsed.get("same_setting_note") or "",
        excluded_source_distinct=parsed.get("excluded_source_distinct"),
        urls=[u for u in (parsed.get("urls") or []) if isinstance(u, str)][:20],
        reason=(parsed.get("reason") or "")[:600],
        main_area=it.get("main_area"), ptype=it.get("ptype"), corpus=it.get("corpus"),
        target_ym=it.get("target_ym"), target_human=it.get("target_human"),
        weight=it.get("weight"), stratum=it.get("stratum"), paper_link=it.get("paper_link"),
        searched_urls=[s.get("url") for s in searches if s.get("url")][:40],
        n_search_results=len(searches), queries=queries[:20],
        usage=usage, stop_reason=stop, rounds=rounds, refused=refused,
        parse_ok=bool(parsed), error=err,
        prompt_sha=C.sha(SYSTEM + "\n" + prompt), raw_text=(text or "")[:4000],
        ts=C.now_utc(), elapsed_s=round(time.time() - t0, 1))

    # --- the gate, applied here so the stored record is already adjudicated ---
    final, gates, failed = G.adjudicate(dict(rec, verdict=raw), it)
    rec["gates"] = gates
    rec["failed_gates"] = failed
    rec["downgraded"] = bool(raw == "ACHIEVED" and failed)
    rec["verdict"] = final if raw in VALID else raw       # None/REFUSED pass through

    ev = C.S1 / "evidence" / "negatives_strict"
    ev.mkdir(parents=True, exist_ok=True)
    (ev / f"{it['id']}.json").write_text(json.dumps(
        dict(id=it["id"], referee=key, queries=queries, results=searches, parsed=parsed,
             gates=gates, failed_gates=failed, raw_text=text), indent=2, ensure_ascii=False),
        encoding="utf-8")
    return rec


def load_items() -> list[dict]:
    s = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    items = s["negatives"]["items"]
    reps, replaced = C.load_replacements()
    if reps:
        items = [i for i in items if i["id"] not in replaced] + reps
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku45", choices=list(REFEREES))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    items = load_items()
    out = Path(a.out) if a.out else (C.S1 / f"negatives_verdicts_strict_{a.model}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"] for r in C.read_jsonl(out) if r.get("raw_verdict") is not None}
    todo = [it for it in items if it["id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"negatives-strict / {a.model}: {len(items)} sampled, {len(done)} done, "
          f"running {len(todo)} with {a.workers} workers -> {out.name}")
    if not todo:
        return

    tot = dict(input_tokens=0, output_tokens=0, web_search_requests=0)
    n_ach = n_down = n_not = n_bad = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_one, a.model, it) for it in todo]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with _lock:
                C.append_jsonl(out, rec)
            for k in tot:
                tot[k] += (rec.get("usage") or {}).get(k, 0)
            n_ach += rec["verdict"] == "ACHIEVED"
            n_down += bool(rec.get("downgraded"))
            n_not += rec["verdict"] == "NOT_ACHIEVED"
            n_bad += rec.get("raw_verdict") is None
            if i % 10 == 0 or i == len(todo):
                print(f"  [{i}/{len(todo)}] achieved={n_ach} downgraded_by_gate={n_down} "
                      f"not_achieved={n_not} unparsed={n_bad} "
                      f"in={tot['input_tokens']:,} out={tot['output_tokens']:,} "
                      f"srch={tot['web_search_requests']} {(time.time()-t0)/60:.1f}min", flush=True)
    print(f"done: achieved={n_ach} downgraded={n_down} not_achieved={n_not} "
          f"unparsed={n_bad} usage={tot}")


if __name__ == "__main__":
    main()
