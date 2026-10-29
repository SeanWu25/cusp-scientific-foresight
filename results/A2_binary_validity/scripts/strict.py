"""
strict.py — a demanding re-adjudication of every candidate mislabelled negative.

The first-pass verdicts (verify.py) ask "is this claim true". That admits a
judgement call whenever a perturbed claim contains an irreducibly vague element
-- "high potency", "sufficient specificity", "reduce tumour burden" -- because
such an element can be argued satisfied by almost any related result. This pass
removes that latitude by forcing the referee to decompose the claim and produce,
element by element, a verbatim quote and a reported value.

Two gates, both of which must pass before an item counts as demonstrably
mislabelled:

  DECIDABLE  every element of the claim is checkable: a number, a named
             threshold or benchmark, or a discrete stated fact. One element that
             is only a vague qualifier, with no number anywhere in the claim,
             makes the claim undecidable -- it can be neither verified nor
             falsified, which is itself a defect but NOT evidence of a wrong
             label.
  EVIDENCED  every element is satisfied, each with a verbatim quote from ONE
             named source and, where the element names a quantity, the reported
             value. No combining sources, no qualitative stand-in for a number,
             no "greatly exceeded" without the figure.

Modes
  binding   closed-book, all 200 sampled negatives. Does the SOURCE paper's own
            reported result satisfy the perturbed claim as literally written?
  achieved  with web search, the negatives the first pass called ACHIEVED. Did
            ONE named non-excluded work, dated on or before the target, satisfy
            every element?

Run each mode under two independent models; Tier A requires both to agree.
This pass can only lower the mislabelling rate, by construction: it re-examines
candidates for removal and never promotes a sound item to mislabelled. That
asymmetry is deliberate and is stated in the write-up.

Usage
  python strict.py binding  --model opus48 [--limit N] [--workers K]
  python strict.py achieved --model gpt55  [--limit N] [--workers K]
"""
from __future__ import annotations
import argparse, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

from dotenv import load_dotenv
load_dotenv(C.ROOT / ".env")

REFEREES = {
    # default pair: cheap enough to run several times, and the gates below do the
    # work that an expensive judge would otherwise be trusted to do
    "sonnet5":   dict(provider="anthropic", model="claude-sonnet-5"),
    "gpt54mini": dict(provider="openai", model="gpt-5.4-mini"),
    # kept for the cross-check reported in the write-up
    "opus48": dict(provider="anthropic", model="claude-opus-4-8"),
    "gpt55":  dict(provider="openai", model="gpt-5.5"),
}

SCHEMA_NOTE = """\
Reply with ONLY a JSON object:
{{"elements": [
    {{"text": "the element, quoted from the claim",
      "kind": "numeric" | "discrete_fact" | "vague",
      "satisfied": true | false | "not_reported",
      "reported_value": "the value the source actually reports, or \\"\\"",
      "evidence_quote": "verbatim sentence from the source, or \\"\\""}}],
  "decidable": true | false,
  "verdict": "WRONG_LABEL" | "LABEL_STANDS" | "UNDECIDABLE",
  "source_name": "the ONE work relied on, or \\"\\"",
  "source_date": "YYYY-MM or YYYY-MM-DD or \\"\\"",
  "reason": "one sentence naming the decisive element and its value"}}"""

RULES = """\
RULES -- apply them literally and without charity
1. Decompose the claim into every separately checkable element: each quantity, \
threshold, benchmark, condition and added constraint is its own element.
2. Mark an element "numeric" if it names a number, rate, factor or threshold; \
"discrete_fact" if it asserts a specific thing that is either reported or not; \
"vague" if it is only a qualifier such as high, significant, sufficient, robust, \
strong, improved, effective, with no number attached anywhere in the claim.
2a. Your decomposition must be EXHAUSTIVE. Every number that appears anywhere in \
the claim must appear in the text of at least one element. A claim stating three \
values needs at least three numeric elements. An incomplete decomposition is a \
failure, not a shortcut: if you cannot enumerate every element, answer LABEL_STANDS.
2b. Quote exactly. Every evidence_quote must be copied character for character \
from the source text given to you. Do not paraphrase, do not reconstruct from \
memory, do not stitch fragments together. A quote that is not literally present in \
the source invalidates that element, and the quotes are checked mechanically.
2c. Every element must be satisfied. Not most of them. One element left \
unsatisfied, unreported or unquoted means the whole claim is LABEL_STANDS.
3. Set decidable=false if ANY element is "vague". A claim with a vague element \
cannot be shown true or false, so it is UNDECIDABLE. Do not argue such an \
element satisfied.
4. An element counts satisfied ONLY with a verbatim quote from the source, and \
for a numeric element you must fill reported_value with the actual figure the \
source states, and that figure must meet or exceed the claim in the direction the \
claim requires. A qualitative statement never satisfies a numeric element, and an \
empty reported_value on a numeric element is a failure.
5. WRONG_LABEL requires decidable=true AND every element satisfied by ONE named \
source. If you need a second source for a different element, answer LABEL_STANDS.
6. Anything short of that is LABEL_STANDS. When in doubt, LABEL_STANDS."""

BINDING_PROMPT = """\
A benchmark labels the claim below FALSE for the paper it was built from. Decide \
whether the paper's OWN reported result already satisfies the claim as literally \
written, which would make that FALSE label wrong.

PAPER'S REPORTED RESULT:
{result}

PAPER'S ABSTRACT:
{abstract}

CLAIM, labelled FALSE:
{claim}

WHAT THE GENERATOR SAYS IT DID:
{detail}

TASK
Judge only the wording of the claim. Ignore the generator's stated intent where \
the wording does not implement it. Ignore dates. Do not use outside knowledge: \
the only source here is this paper.

{rules}
7. Here the "one named source" is this paper itself.

{schema}"""

ACHIEVED_PROMPT = """\
A benchmark labels the claim below FALSE, on the grounds that nobody achieved it \
by the target date. Decide whether ONE named group OTHER than the excluded source \
demonstrably achieved every element of it, on or before that date.

CLAIM: {claim}

TARGET DATE: {target}

EXCLUDED SOURCE -- never counts, in any venue or restatement: {link}

A previous reviewer concluded this claim WAS achieved elsewhere, citing:
  {prev}
Treat that as a lead to check, not as a finding. It may be overstated.

TASK
Search the web. Then decompose the claim and test it element by element.

{rules}
7. The work must be dated ON OR BEFORE {target}.
8. The excluded source's own result never satisfies any element.

{schema}"""

_lock = threading.Lock()
VALID = {"WRONG_LABEL", "LABEL_STANDS", "UNDECIDABLE"}


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


def ask_anthropic(model, prompt, search):
    import anthropic
    cl = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=900.0, max_retries=3)
    kw = dict(model=model, max_tokens=8000, thinking={"type": "adaptive"},
              output_config={"effort": "high"},
              messages=[{"role": "user", "content": prompt}])
    if search:
        kw["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}]
    msgs, usage, text, rounds = kw.pop("messages"), dict(input_tokens=0, output_tokens=0, web_search_requests=0), "", 0
    while True:
        rounds += 1
        r = cl.messages.create(messages=msgs, **kw)
        usage["input_tokens"] += r.usage.input_tokens or 0
        usage["output_tokens"] += r.usage.output_tokens or 0
        st = getattr(r.usage, "server_tool_use", None)
        if st is not None:
            usage["web_search_requests"] += getattr(st, "web_search_requests", 0) or 0
        text += "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        if r.stop_reason == "pause_turn" and rounds < 6:
            msgs = msgs + [{"role": "assistant", "content": r.content}]
            continue
        return text, usage, r.model, r.stop_reason


def ask_openai(model, prompt, search):
    from openai import OpenAI
    cl = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=900.0, max_retries=3)
    kw = dict(model=model, input=prompt)
    if search:
        kw["tools"] = [{"type": "web_search"}]
    r = cl.responses.create(**kw)
    text = "".join(o.content[0].text for o in r.output
                   if getattr(o, "type", "") == "message" and getattr(o, "content", None))
    return text, dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens,
                      web_search_requests=sum(1 for o in r.output
                                              if getattr(o, "type", "") == "web_search_call")), r.model, "end_turn"


def build(mode: str, it: dict) -> tuple[str, bool]:
    if mode == "binding":
        return BINDING_PROMPT.format(
            result=(it.get("results_and_metrics") or "(not recorded)")[:1800],
            abstract=(it.get("source_abstract") or "(not recorded)")[:2500],
            claim=it["binary_question_perturbed"],
            detail=it.get("binary_perturbation_detail") or "(not recorded)",
            rules=RULES, schema=SCHEMA_NOTE), False
    return ACHIEVED_PROMPT.format(
        claim=it["binary_question_perturbed"], target=it["target_human"],
        link=it.get("paper_link") or "(not recorded)",
        prev=(it.get("prev_justification") or "(none)")[:500],
        rules=RULES, schema=SCHEMA_NOTE), True


def run_one(mode: str, key: str, it: dict) -> dict:
    cfg = REFEREES[key]
    prompt, search = build(mode, it)
    t0, err, text, usage, served, stop = time.time(), None, "", None, None, None
    parsed = {}
    for attempt in range(3):
        try:
            fn = ask_anthropic if cfg["provider"] == "anthropic" else ask_openai
            text, usage, served, stop = fn(cfg["model"], prompt, search)
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
    v = str(parsed.get("verdict", "")).strip().upper()
    els = parsed.get("elements") if isinstance(parsed.get("elements"), list) else []
    kinds = [str(e.get("kind", "")).lower() for e in els if isinstance(e, dict)]
    quoted = all((e.get("evidence_quote") or "").strip() for e in els if isinstance(e, dict)) and bool(els)
    return dict(
        id=it["id"], mode=mode, referee=key, referee_model=cfg["model"], served_model=served,
        verdict=v if v in VALID else None,
        decidable=parsed.get("decidable"),
        has_vague_element=("vague" in kinds),
        n_elements=len(els), all_elements_quoted=quoted,
        elements=els[:12], source_name=parsed.get("source_name") or "",
        source_date=parsed.get("source_date") or "", reason=(parsed.get("reason") or "")[:600],
        main_area=it.get("main_area"), ptype=it.get("ptype"), corpus=it.get("corpus"),
        weight=it.get("weight"), stratum=it.get("stratum"), target_human=it.get("target_human"),
        usage=usage, stop_reason=stop, error=err, refused=(stop == "refusal"),
        prompt_sha=C.sha(prompt), raw_text=(text or "")[:3000],
        ts=C.now_utc(), elapsed_s=round(time.time() - t0, 1))


def load(mode: str) -> list[dict]:
    sample = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    items = {i["id"]: i for i in sample["negatives"]["items"]}
    reps, replaced = C.load_replacements()
    for r in reps:
        items.pop(r["replaces"], None)
        items[r["id"]] = r
    corp = C.load_corpus()
    if mode == "binding":
        out = []
        for i, it in items.items():
            r = corp[i]
            out.append(dict(it, results_and_metrics=r.get("results_and_metrics"),
                            source_abstract=r.get("source_abstract")))
        return out
    prev = {}
    for r in C.read_jsonl(C.S1 / "negatives_verdicts.jsonl"):
        if r.get("verdict") == "ACHIEVED":
            prev[r["id"]] = r.get("justification") or ""
    return [dict(items[i], prev_justification=p) for i, p in prev.items() if i in items]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["binding", "achieved"])
    ap.add_argument("--model", required=True, choices=list(REFEREES))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    items = load(a.mode)
    out = C.S1 / f"strict_{a.mode}_{a.model}.jsonl"
    done = {r["id"] for r in C.read_jsonl(out) if r.get("verdict")}
    todo = [it for it in items if it["id"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"strict {a.mode} / {a.model}: {len(items)} items, {len(done)} done, running {len(todo)}")
    if not todo:
        return
    tot = dict(input_tokens=0, output_tokens=0, web_search_requests=0)
    n_wrong = n_und = n_stands = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_one, a.mode, a.model, it) for it in todo]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            with _lock:
                C.append_jsonl(out, rec)
            for k in tot:
                tot[k] += (rec.get("usage") or {}).get(k, 0)
            n_wrong += rec["verdict"] == "WRONG_LABEL"
            n_und += rec["verdict"] == "UNDECIDABLE"
            n_stands += rec["verdict"] == "LABEL_STANDS"
            if i % 20 == 0 or i == len(todo):
                print(f"  [{i}/{len(todo)}] wrong={n_wrong} undecidable={n_und} stands={n_stands} "
                      f"in={tot['input_tokens']:,} srch={tot['web_search_requests']}", flush=True)
    print(f"done {a.mode}/{a.model}: wrong={n_wrong} undecidable={n_und} stands={n_stands} usage={tot}")


if __name__ == "__main__":
    main()
