"""
adjudicate.py — independent second pass over the items Study 1 flagged.

Run with a different provider and a different search index (GPT-5.5 with OpenAI's
native web_search tool) so the check does not inherit the first verifier's search
results. GPT-5.5 is outside the evaluated panel and is not a Study 2 judge.

  negatives : every ACHIEVED negative is decided again, independently. The first
              verifier's evidence is shown so it can be checked, but the second
              reviewer answers the underlying question in the same vocabulary as
              the first pass, and may rely on different evidence.
              -> ACHIEVED / NOT_ACHIEVED / UNCERTAIN
  positives : every NOT_CONFIRMED positive is searched again from scratch, with
              no sight of the first verifier's reasoning, to separate a search
              failure from a genuinely unverifiable item.
              -> FOUND / NOT_FOUND

Outputs feed the strict (both-agree) and permissive (either) bounds on the
mislabelling rate. Nothing here is written back into the first-pass JSONLs.

Usage
  python adjudicate.py negatives [--workers K]
  python adjudicate.py positives [--workers K]
"""
from __future__ import annotations
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

from dotenv import load_dotenv
load_dotenv(C.ROOT / ".env")
from openai import OpenAI

ADJ_MODEL = "gpt-5.5"

NEG_PROMPT = """\
A benchmark labels the claim below FALSE, on the grounds that nobody achieved it by the \
target date. A first reviewer searched the web and reported that it WAS in fact achieved \
by another group. You are the second reviewer. Decide the underlying question yourself, \
strictly and independently.

CLAIM: {claim}

TARGET DATE: {target}

EXCLUDED SOURCE (this paper's own result can never count): {link}

The first reviewer's evidence is reproduced so you can check it. It may be correct, \
overstated, or about a different result. You are NOT scoring the reviewer -- you are \
deciding the underlying question, and you may rely on different evidence than they did.
  FIRST REVIEWER'S CONCLUSION: {just}
  CITED SOURCE: {title} ({date})
  CITED PASSAGE: {passage}
  URLS: {urls}

TASK
Search the web yourself. Then answer this single question:

  Did some group OTHER than the excluded source achieve and publicly report the EXACT \
claim above, on or before {target}?

RULES -- apply them literally, they decide the answer
1. A numeric value, threshold, factor or range counts only if a reported result MEETS OR \
EXCEEDS that exact value in the direction the claim requires. Close, weaker, or \
approximately-equal does NOT count.
2. An added constraint, requirement or condition counts only if it was actually \
satisfied. Achieving the underlying advance WITHOUT satisfying the constraint does NOT \
count.
3. The excluded source's own result never counts, in any venue or restatement.
4. The work must be dated ON OR BEFORE {target}. Later work does not count.
5. A qualitative match standing in for a quantitative threshold is NOT sufficient. If the \
claim names a number and no work you can find reports that number, the answer is not ACHIEVED.
6. If the evidence is partial, ambiguous, or you cannot find it, answer NOT_ACHIEVED.

Reply with ONLY a JSON object:
{{"verdict": "ACHIEVED" | "NOT_ACHIEVED" | "UNCERTAIN",
  "first_reviewer_evidence_holds": true | false,
  "confidence": <0.0-1.0>,
  "urls": ["..."],
  "source_title": "the work you are relying on, if any",
  "source_date": "YYYY-MM or YYYY-MM-DD or \\"\\"",
  "reason": "one or two sentences naming the exact value or constraint, which work meets \
it, and its date"}}"""

POS_PROMPT = """\
CLAIM (derived from a scientific advance):
{claim}

TARGET DATE: {target}
FIELD: {area}

TASK
Search the web and decide whether this claim was achieved and publicly reported ON OR \
BEFORE {target}.

RULES
1. FOUND requires a specific public source -- journal paper, preprint, official technical \
report, or model card -- dated on or before {target}, reporting a result that meets the \
claim as stated.
2. A partial, weaker, or merely similar result does NOT count.
3. If you cannot locate such a source, answer NOT_FOUND. Do not guess and do not answer \
from memory alone.

Reply with ONLY a JSON object:
{{"verdict": "FOUND" | "NOT_FOUND",
  "confidence": <0.0-1.0>,
  "urls": ["..."],
  "source_title": "...",
  "source_date": "YYYY-MM or YYYY-MM-DD or \\"\\"",
  "reason": "one or two sentences"}}"""

# The first verifier's safety classifier declined a small number of benign
# biomedical negatives outright, so there is no first-reviewer opinion to check and
# NEG_PROMPT's framing does not apply. This variant asks the same underlying
# question under the same rules, with the first-reviewer block removed, so those
# items are decided rather than silently dropped from the denominator.
NEG_PROMPT_FRESH = """\
A benchmark labels the claim below FALSE, on the grounds that nobody achieved it by the \
target date. No prior reviewer reached a conclusion on it. Decide the underlying question \
yourself, strictly and independently.

CLAIM: {claim}

TARGET DATE: {target}

EXCLUDED SOURCE (this paper's own result can never count): {link}

TASK
Search the web. Then answer this single question:

  Did some group OTHER than the excluded source achieve and publicly report the EXACT \
claim above, on or before {target}?

RULES -- apply them literally, they decide the answer
1. A numeric value, threshold, factor or range counts only if a reported result MEETS OR \
EXCEEDS that exact value in the direction the claim requires. Close, weaker, or \
approximately-equal does NOT count.
2. An added constraint, requirement or condition counts only if it was actually \
satisfied. Achieving the underlying advance WITHOUT satisfying the constraint does NOT \
count.
3. The excluded source's own result never counts, in any venue or restatement.
4. The work must be dated ON OR BEFORE {target}. Later work does not count.
5. A qualitative match standing in for a quantitative threshold is NOT sufficient. If the \
claim names a number and no work you can find reports that number, the answer is not ACHIEVED.
6. If the evidence is partial, ambiguous, or you cannot find it, answer NOT_ACHIEVED.

Reply with ONLY a JSON object:
{{"verdict": "ACHIEVED" | "NOT_ACHIEVED" | "UNCERTAIN",
  "confidence": <0.0-1.0>,
  "urls": ["..."],
  "source_title": "...",
  "source_date": "YYYY-MM or YYYY-MM-DD or \\"\\"",
  "first_reviewer_evidence_holds": null,
  "reason": "one or two sentences naming the decisive element"}}"""


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
2. Answer CONTRADICTED if the paper's result fails the modified claim -- the modification \
did its job and the FALSE label is sound.
3. Answer SELF_SATISFIED if the paper's own result already satisfies the modified claim as \
literally written, so the FALSE label is wrong on its face. This happens when a generator \
negates the wrong side, writes "fail to achieve X" where it meant "achieve X", weakens a \
threshold instead of strengthening it, or drops the constrained quantity altogether.
4. Answer UNDECIDABLE if the modified claim is too vague or garbled to evaluate.
5. Ignore the date entirely. Do not search the web.

Reply with ONLY a JSON object:
{{"verdict": "CONTRADICTED" | "SELF_SATISFIED" | "UNDECIDABLE",
  "confidence": <0.0-1.0>,
  "failure_mode": "" | "negation_flipped" | "threshold_weakened" | "constraint_dropped" | "garbled" | "other",
  "reason": "one or two sentences quoting the decisive wording"}}"""

VALID = {"negatives": {"ACHIEVED", "NOT_ACHIEVED", "UNCERTAIN"}, "positives": {"FOUND", "NOT_FOUND"},
         "soundness": {"CONTRADICTED", "SELF_SATISFIED", "UNDECIDABLE"}}
_lock = threading.Lock()


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
    try:
        return json.loads(t[i:j + 1])
    except Exception:
        return None


def ask(client, prompt: str, use_search: bool = True):
    kw = dict(model=ADJ_MODEL, input=prompt)
    if use_search:
        kw["tools"] = [{"type": "web_search"}]
    r = client.responses.create(**kw)
    text = "".join(o.content[0].text for o in r.output
                   if getattr(o, "type", "") == "message" and getattr(o, "content", None))
    urls = []
    for o in r.output:
        if getattr(o, "type", "") == "web_search_call":
            q = getattr(o, "action", None)
            if q is not None:
                urls.append(str(getattr(q, "query", "") or ""))
    return text, dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens,
                      web_search_requests=sum(1 for o in r.output
                                              if getattr(o, "type", "") == "web_search_call")), urls, r.model


def run_one(client, kind: str, it: dict) -> dict:
    if kind == "soundness":
        prompt = SOUND_PROMPT.format(
            result=(it.get("results_and_metrics") or "(not recorded)")[:1800],
            abstract=(it.get("source_abstract") or "(not recorded)")[:2500],
            claim=it["claim"], detail=it.get("binary_perturbation_detail") or "(not recorded)")
    elif kind == "negatives" and it.get("first_verdict") == "REFUSED":
        prompt = NEG_PROMPT_FRESH.format(
            claim=it["claim"], target=it["target_human"],
            link=it.get("paper_link") or "(not recorded)")
    elif kind == "negatives":
        prompt = NEG_PROMPT.format(
            claim=it["claim"], target=it["target_human"], link=it.get("paper_link") or "(not recorded)",
            just=(it.get("justification") or "")[:700], title=(it.get("source_title") or "")[:200],
            date=it.get("source_date") or "", passage=(it.get("supporting_passage") or "")[:700],
            urls=", ".join((it.get("urls") or [])[:6]))
    else:
        prompt = POS_PROMPT.format(claim=it["claim"], target=it["target_human"],
                                   area=it.get("main_area") or "unspecified")
    t0, err, text, usage, served, queries = time.time(), None, None, None, None, []
    parsed = {}
    for attempt in range(3):
        try:
            text, usage, queries, served = ask(client, prompt, use_search=(kind != "soundness"))
            parsed = extract_json(text) or {}
            if str(parsed.get("verdict", "")).strip().upper() in VALID[kind]:
                err = None
                break
            err = "unparsed"
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        time.sleep(3 * (attempt + 1))
    v = str(parsed.get("verdict", "")).strip().upper()
    return dict(id=it["id"], kind=kind, verdict=v if v in VALID[kind] else None,
                confidence=parsed.get("confidence"),
                urls=[u for u in (parsed.get("urls") or []) if isinstance(u, str)][:20],
                reason=(parsed.get("reason") or "")[:800], failure_mode=parsed.get("failure_mode") or "",
                first_reviewer_evidence_holds=parsed.get("first_reviewer_evidence_holds"),
                source_title=parsed.get("source_title") or "", source_date=parsed.get("source_date") or "",
                main_area=it.get("main_area"), ptype=it.get("ptype"), corpus=it.get("corpus"),
                weight=it.get("weight"), target_human=it.get("target_human"),
                first_pass_verdict=it.get("first_verdict"), queries=queries,
                usage=usage, model=served, adjudicator=ADJ_MODEL,
                prompt_sha=C.sha(prompt), error=err, raw_text=(text or "")[:3000],
                ts=C.now_utc(), elapsed_s=round(time.time() - t0, 1))


def load(kind: str) -> list[dict]:
    sample = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    if kind == "soundness":
        corp = C.load_corpus()
        out = []
        for i in sample["negatives"]["items"]:
            r = corp[i["id"]]
            out.append(dict(i, claim=i["binary_question_perturbed"],
                            results_and_metrics=r.get("results_and_metrics"),
                            source_abstract=r.get("source_abstract"),
                            binary_perturbation_detail=i.get("binary_perturbation_detail"),
                            first_verdict=None))
        return out
    if kind == "negatives":
        items = {i["id"]: i for i in sample["negatives"]["items"]}
        out, settled = [], set()
        for r in C.read_jsonl(C.S1 / "negatives_verdicts.jsonl"):
            if r.get("verdict") in ("ACHIEVED", "NOT_ACHIEVED") and r["id"] in items:
                settled.add(r["id"])
        for r in C.read_jsonl(C.S1 / "negatives_verdicts.jsonl"):
            if r["id"] in items and r["id"] not in settled and (
                    r.get("verdict") == "REFUSED" or r.get("refused")
                    or (not r.get("verdict") and r.get("stop_reason") == "refusal")):
                out.append(dict(items[r["id"]],
                                claim=items[r["id"]]["binary_question_perturbed"],
                                first_verdict="REFUSED"))
        for r in C.read_jsonl(C.S1 / "negatives_verdicts.jsonl"):
            if r.get("verdict") == "ACHIEVED" and r["id"] in items:
                out.append(dict(items[r["id"]], claim=items[r["id"]]["binary_question_perturbed"],
                                justification=r.get("justification"), supporting_passage=r.get("supporting_passage"),
                                source_title=r.get("source_title"), source_date=r.get("source_date"),
                                urls=r.get("urls"), first_verdict="ACHIEVED"))
        return list({o["id"]: o for o in out}.values())
    # Two kinds of positive reach this pass. NOT_CONFIRMED: the first verifier
    # searched and did not find it, so a different provider's index gets a turn --
    # that is what lifted the confirmation rate from 81.1% to 96.9%. REFUSED: the
    # first verifier's safety classifier declined the prompt and never decided the
    # item at all, so it is missing from the denominator rather than counted
    # against us. Those are benign biomedical claims and the second provider has a
    # different refusal profile, so they are routed here too rather than written
    # off. POS_PROMPT is self-contained and never refers to a first verdict, so it
    # serves both cases unchanged.
    items = {i["id"]: i for i in sample["positives"]["items"]}
    decided, refused = {}, {}
    for r in C.read_jsonl(C.S1 / "positives_verdicts.jsonl"):
        if r["id"] not in items:
            continue
        if r.get("verdict") in ("CONFIRMED", "NOT_CONFIRMED"):
            decided[r["id"]] = r.get("verdict")
        elif r.get("verdict") == "REFUSED" or r.get("stop_reason") == "refusal":
            refused[r["id"]] = "REFUSED"
    out = []
    for i, v in decided.items():
        if v == "NOT_CONFIRMED":
            out.append(dict(items[i], claim=items[i]["binary_question"],
                            first_verdict="NOT_CONFIRMED"))
    for i in refused:
        if i not in decided:
            out.append(dict(items[i], claim=items[i]["binary_question"],
                            first_verdict="REFUSED"))
    return list({o["id"]: o for o in out}.values())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["negatives", "positives", "soundness"])
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args()
    items = load(a.kind)
    out = C.S1 / f"adjudication_{a.kind}.jsonl"
    done = {r["id"] for r in C.read_jsonl(out) if r.get("verdict")}
    todo = [it for it in items if it["id"] not in done]
    print(f"adjudicate {a.kind}: {len(items)} flagged, {len(done)} done, running {len(todo)} on {ADJ_MODEL}")
    if not todo:
        return
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=600.0, max_retries=3)
    tot = dict(input_tokens=0, output_tokens=0, web_search_requests=0)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_one, client, a.kind, it) for it in todo]
        for i, fu in enumerate(as_completed(futs), 1):
            rec = fu.result()
            with _lock:
                C.append_jsonl(out, rec)
            for k in tot:
                tot[k] += (rec.get("usage") or {}).get(k, 0)
            print(f"  [{i}/{len(todo)}] {rec['id'][:8]} -> {rec['verdict']}", flush=True)
    print(f"done. usage={tot}")


if __name__ == "__main__":
    main()
