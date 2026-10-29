"""
verify.py — Study 1. Post-event web verification of binary ground truth.

Three independent sub-pipelines, each checkpointed per item and each writing its
own JSONL. No sub-pipeline ever reads another's output, and none of them reads
or writes anything under study2_detection/.

  positives  : did the YES claim actually happen by its target date?
  negatives  : was the EXACT perturbed claim achieved by someone ELSE by then?
               (the source paper is named and explicitly excluded)
  soundness  : closed-book, no web access. Given the source paper's own reported
               result, does the perturbed claim as literally written already hold
               for that source? A 'yes' means the perturbation failed to make the
               claim false, so the NO label is wrong regardless of what anyone
               else did. This is a mislabelling route the web check cannot see,
               because the web check is required to exclude the source paper.

Usage
  python verify.py positives  [--limit N] [--workers K] [--model ID]
  python verify.py negatives  [--limit N] [--workers K] [--model ID]
  python verify.py soundness  [--limit N] [--workers K] [--model ID]
"""
from __future__ import annotations
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

from dotenv import load_dotenv
load_dotenv(C.ROOT / ".env")
import anthropic

VERIFY_MODEL = "claude-opus-4-8"
SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 8}
MAX_TOKENS = 8000
EFFORT = "high"

SYSTEM_WEB = (
    "You are a meticulous scientific fact-checker with live web access. You are working "
    "AFTER the fact: every target date below is in the past, so the record of what was or "
    "was not achieved is already public. Search the web before answering. Never rely on "
    "memory alone for a positive finding. You are rewarded for being correct, not for "
    "finding a match; answering 'not found' is the right answer whenever the evidence is "
    "absent, partial, or merely close."
)

SYSTEM_SOUND = (
    "You are a meticulous scientific editor. You judge only what the text in front of you "
    "says. You have no web access and must not speculate about outside work."
)

POS_PROMPT = """\
CLAIM (derived from a scientific advance):
{claim}

TARGET DATE: {target}
FIELD: {area}

TASK
Search the web and decide whether this claim was achieved and publicly reported \
ON OR BEFORE {target}.

RULES
1. CONFIRMED requires a specific public source -- journal paper, preprint, official \
technical report, or model card -- dated on or before {target}, reporting a result that \
meets the claim as stated.
2. A partial, weaker, or merely similar result does NOT confirm the claim.
3. If you cannot locate such a source, answer NOT_CONFIRMED. Do not guess, and do not \
confirm from memory alone.

Reply with ONLY a JSON object, no prose around it:
{{"verdict": "CONFIRMED" | "NOT_CONFIRMED",
  "confidence": <0.0-1.0>,
  "urls": ["..."],
  "supporting_passage": "verbatim sentence(s) from the source that support the verdict, or \\"\\" if none",
  "source_title": "...",
  "source_date": "YYYY-MM or YYYY-MM-DD or \\"\\"",
  "justification": "one or two sentences"}}"""

NEG_PROMPT = """\
PERTURBED CLAIM:
{claim}

TARGET DATE: {target}
FIELD: {area}

EXCLUDED SOURCE -- this paper, and any report of this same piece of work, must NOT be \
counted as achieving the claim:
  link: {link}
  topic: {topic}

TASK
Decide whether the EXACT claim above was achieved and publicly reported by some group \
OTHER than the excluded source, ON OR BEFORE {target}.

STRICTNESS RULES -- apply them literally, they decide the answer
1. If the claim states a numeric value, threshold, factor or range, it counts as ACHIEVED \
only if a reported result MEETS OR EXCEEDS that exact value in the direction the claim \
requires. A nearby, weaker, or approximately-equal result does NOT count.
2. If the claim adds a constraint, requirement or condition, it counts as ACHIEVED only if \
that constraint was actually satisfied. Achieving the underlying advance WITHOUT satisfying \
the constraint does NOT count.
3. The excluded source's own result never counts, in any venue or restatement.
4. The achievement must be dated ON OR BEFORE {target}. Later work does not count.
5. If the evidence is partial, ambiguous, or you simply cannot find it, answer NOT_ACHIEVED.

Reply with ONLY a JSON object, no prose around it:
{{"verdict": "ACHIEVED" | "NOT_ACHIEVED",
  "confidence": <0.0-1.0>,
  "urls": ["..."],
  "supporting_passage": "verbatim sentence(s) evidencing achievement, or \\"\\" if none",
  "source_title": "...",
  "source_date": "YYYY-MM or YYYY-MM-DD or \\"\\"",
  "exactness_justification": "one line naming the exact modified value or added constraint \
and stating whether it was met, and by whom"}}"""

SOUND_PROMPT = """\
A benchmark item was built from one paper. The paper's real reported outcome is given \
first. A modified ("perturbed") version of the claim was then generated, and the benchmark \
labels that modified claim FALSE for this paper.

PAPER'S REPORTED RESULT:
{result}

PAPER'S ABSTRACT:
{abstract}

MODIFIED CLAIM, labelled FALSE:
{claim}

INTENDED MODIFICATION (what the generator says it did):
{detail}

TASK
Read the modified claim LITERALLY, exactly as written. Decide whether the paper's own \
reported result already satisfies it.

RULES
1. Judge only the wording of the modified claim. Ignore the intended modification if the \
wording does not actually implement it.
2. Answer CONTRADICTED if the paper's result fails the modified claim -- i.e. the \
modification did its job and the FALSE label is sound.
3. Answer SELF_SATISFIED if the paper's own result already satisfies the modified claim as \
literally written, so the FALSE label is wrong on its face. This happens when a generator \
negates the wrong side, writes "fail to achieve X" where it meant "achieve X", weakens a \
threshold instead of strengthening it, or drops the constrained quantity altogether.
4. Answer UNDECIDABLE if the modified claim is too vague or garbled to evaluate.
5. Ignore the date entirely.

Reply with ONLY a JSON object, no prose around it:
{{"verdict": "CONTRADICTED" | "SELF_SATISFIED" | "UNDECIDABLE",
  "confidence": <0.0-1.0>,
  "failure_mode": "" | "negation_flipped" | "threshold_weakened" | "constraint_dropped" | "garbled" | "other",
  "justification": "one or two sentences quoting the decisive wording"}}"""

_lock = threading.Lock()


def extract_json(text: str) -> dict | None:
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.split("```")[1] if "```" in t[3:] else t
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


def call_model(client, model: str, system: str, prompt: str, use_search: bool) -> dict:
    """One verification call. Handles pause_turn continuation for server tools."""
    kw = dict(model=model, max_tokens=MAX_TOKENS, system=system,
              thinking={"type": "adaptive"}, output_config={"effort": EFFORT})
    if use_search:
        kw["tools"] = [SEARCH_TOOL]
    msgs = [{"role": "user", "content": prompt}]
    usage = dict(input_tokens=0, output_tokens=0, web_search_requests=0)
    searches, blocks, rounds = [], [], 0
    while True:
        rounds += 1
        resp = client.messages.create(messages=msgs, **kw)
        u = resp.usage
        usage["input_tokens"] += getattr(u, "input_tokens", 0) or 0
        usage["output_tokens"] += getattr(u, "output_tokens", 0) or 0
        st = getattr(u, "server_tool_use", None)
        if st is not None:
            usage["web_search_requests"] += getattr(st, "web_search_requests", 0) or 0
        for b in resp.content:
            bt = getattr(b, "type", "")
            if bt == "web_search_tool_result":
                cont = getattr(b, "content", None)
                if isinstance(cont, list):
                    for r in cont:
                        searches.append(dict(url=getattr(r, "url", None),
                                             title=getattr(r, "title", None),
                                             page_age=getattr(r, "page_age", None)))
                else:
                    searches.append(dict(error=str(getattr(cont, "error_code", cont))))
            elif bt == "server_tool_use":
                blocks.append(dict(kind="query", value=(getattr(b, "input", {}) or {}).get("query")))
            elif bt == "text":
                blocks.append(dict(kind="text", value=b.text))
        if resp.stop_reason == "pause_turn" and rounds < 6:
            msgs = msgs + [{"role": "assistant", "content": resp.content}]
            continue
        text = "".join(b["value"] for b in blocks if b["kind"] == "text" and b["value"])
        # dynamic filtering runs the search from inside code execution, so some
        # server_tool_use blocks carry no `query` field; drop those placeholders.
        return dict(text=text, usage=usage, searches=searches,
                    queries=[b["value"] for b in blocks if b["kind"] == "query" and b["value"]],
                    stop_reason=resp.stop_reason, rounds=rounds, model=resp.model)


def build(kind: str, it: dict) -> tuple[str, str, bool]:
    if kind == "positives":
        return SYSTEM_WEB, POS_PROMPT.format(
            claim=it["binary_question"], target=it["target_human"],
            area=it.get("main_area") or "unspecified"), True
    if kind == "negatives":
        return SYSTEM_WEB, NEG_PROMPT.format(
            claim=it["binary_question_perturbed"], target=it["target_human"],
            area=it.get("main_area") or "unspecified",
            link=it.get("paper_link") or "(not recorded)",
            topic=(it.get("problem_statement") or "(not recorded)")[:400]), True
    return SYSTEM_SOUND, SOUND_PROMPT.format(
        result=(it.get("results_and_metrics") or "(not recorded)")[:1800],
        abstract=(it.get("source_abstract") or "(not recorded)")[:2500],
        claim=it["binary_question_perturbed"],
        detail=it.get("binary_perturbation_detail") or "(not recorded)"), False


VALID = {
    "positives": {"CONFIRMED", "NOT_CONFIRMED"},
    "negatives": {"ACHIEVED", "NOT_ACHIEVED"},
    "soundness": {"CONTRADICTED", "SELF_SATISFIED", "UNDECIDABLE"},
}


def run_one(client, kind: str, model: str, it: dict) -> dict:
    system, prompt, use_search = build(kind, it)
    t0 = time.time()
    err, out = None, None
    for attempt in range(3):
        try:
            out = call_model(client, model, system, prompt, use_search)
            break
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            time.sleep(3 * (attempt + 1))
    if out is None:
        return dict(id=it["id"], kind=kind, verdict=None, error=err,
                    prompt_sha=C.sha(system + "\n" + prompt), model=model,
                    ts=C.now_utc(), elapsed_s=round(time.time() - t0, 1))
    parsed = extract_json(out["text"]) or {}
    verdict = str(parsed.get("verdict", "")).strip().upper().replace(" ", "_")
    if verdict not in VALID[kind]:
        verdict = None
    refused = out["stop_reason"] == "refusal"
    if refused:
        verdict = "REFUSED"          # terminal: the classifier declined, retrying re-bills
    rec = dict(
        id=it["id"], kind=kind, verdict=verdict,
        confidence=parsed.get("confidence"),
        urls=[u for u in (parsed.get("urls") or []) if isinstance(u, str)][:20],
        supporting_passage=parsed.get("supporting_passage") or "",
        source_title=parsed.get("source_title") or "",
        source_date=parsed.get("source_date") or "",
        justification=parsed.get("justification") or parsed.get("exactness_justification") or "",
        failure_mode=parsed.get("failure_mode") or "",
        main_area=it.get("main_area"), ptype=it.get("ptype"), corpus=it.get("corpus"),
        target_ym=it.get("target_ym"), target_human=it.get("target_human"),
        weight=it.get("weight"), stratum=it.get("stratum"),
        paper_link=it.get("paper_link"),
        searched_urls=[s.get("url") for s in out["searches"] if s.get("url")][:40],
        n_search_results=len(out["searches"]),
        queries=out["queries"][:20],
        usage=out["usage"], stop_reason=out["stop_reason"], rounds=out["rounds"],
        model=out["model"], prompt_sha=C.sha(system + "\n" + prompt), refused=refused,
        parse_ok=bool(parsed), raw_text=out["text"][:4000],
        ts=C.now_utc(), elapsed_s=round(time.time() - t0, 1), error=None,
    )
    ev = C.S1 / "evidence" / kind
    ev.mkdir(parents=True, exist_ok=True)
    (ev / f"{it['id']}.json").write_text(json.dumps(
        dict(id=it["id"], kind=kind, queries=out["queries"], results=out["searches"],
             parsed=parsed, raw_text=out["text"]), indent=2, ensure_ascii=False), encoding="utf-8")
    return rec


def load_items(kind: str) -> list[dict]:
    s = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    if kind == "positives":
        return s["positives"]["items"]
    items = s["negatives"]["items"]
    reps, replaced = C.load_replacements()
    if reps:
        items = [i for i in items if i["id"] not in replaced] + reps
    if kind == "soundness":                       # needs source fields the sample omits
        corp = C.load_corpus()
        out = []
        for it in items:
            r = corp[it["id"]]
            out.append(dict(it, results_and_metrics=r.get("results_and_metrics"),
                            source_abstract=r.get("source_abstract")))
        return out
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["positives", "negatives", "soundness"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=VERIFY_MODEL)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    items = load_items(a.kind)
    name = {"positives": "positives_verdicts.jsonl", "negatives": "negatives_verdicts.jsonl",
            "soundness": "negatives_soundness.jsonl"}[a.kind]
    out = Path(a.out) if a.out else (C.S1 / name)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"] for r in C.read_jsonl(out) if r.get("verdict") is not None}
    todo = [it for it in items if it["id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{a.kind}: {len(items)} sampled, {len(done)} already done, running {len(todo)} "
          f"on {a.model} with {a.workers} workers -> {out}")
    if not todo:
        return

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=900.0, max_retries=3)
    n_ok = n_bad = 0
    tot = dict(input_tokens=0, output_tokens=0, web_search_requests=0)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_one, client, a.kind, a.model, it): it for it in todo}
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with _lock:
                C.append_jsonl(out, rec)
            for k in tot:
                tot[k] += (rec.get("usage") or {}).get(k, 0)
            if rec.get("verdict"):
                n_ok += 1
            else:
                n_bad += 1
            if i % 10 == 0 or i == len(todo):
                el = time.time() - t0
                print(f"  [{i}/{len(todo)}] ok={n_ok} unparsed/err={n_bad} "
                      f"in={tot['input_tokens']:,} out={tot['output_tokens']:,} "
                      f"searches={tot['web_search_requests']} {el/60:.1f}min", flush=True)
    print(f"done {a.kind}: {n_ok} verdicts, {n_bad} failures, usage={tot}")


if __name__ == "__main__":
    main()
