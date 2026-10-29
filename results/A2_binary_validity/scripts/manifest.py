"""
manifest.py — MANIFEST.json: models, served snapshot ids, dates, seeds, prompt
hashes, token/search usage and measured cost, plus the git SHA.

Prices are the public list rates in force on the run date (USD per 1M tokens,
web search per 1,000 searches). They are recorded here so the cost figures can be
recomputed if rates change.
"""
from __future__ import annotations
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

PRICES = {
    "claude-opus-4-8": dict(input=5.00, output=25.00),
    "gpt-5.4":         dict(input=2.50, output=15.00),
    "gpt-5.5":         dict(input=5.00, output=30.00),
    "claude-sonnet-5": dict(input=2.00, output=10.00),
    "gpt-5.4-mini":    dict(input=0.75, output=4.50),
}
WEB_SEARCH_PER_1K = 10.00
ADJ_NOTE = "gpt-5.5"
PRICE_SOURCE = dict(
    anthropic="https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool "
              "($10 / 1,000 searches) and the Claude model pricing table",
    openai="https://developers.openai.com/api/docs/pricing",
    checked="2026-09-20")

FILES = [
    ("study1_verification/positives_verdicts.jsonl", "study1.positives"),
    ("study1_verification/negatives_verdicts.jsonl", "study1.negatives"),
    ("study1_verification/negatives_soundness.jsonl", "study1.soundness"),
    ("study2_detection/judgments.jsonl", "study2.detection"),
    ("study1_verification/adjudication_negatives.jsonl", "study1.adjudication.negatives"),
    ("study1_verification/adjudication_positives.jsonl", "study1.adjudication.positives"),
    ("study1_verification/adjudication_soundness.jsonl", "study1.adjudication.soundness"),
    ("study1_verification/strict_binding_opus48.jsonl", "study1.strict.binding.opus48"),
    ("study1_verification/strict_binding_gpt55.jsonl", "study1.strict.binding.gpt55"),
    ("study1_verification/strict_achieved_opus48.jsonl", "study1.strict.achieved.opus48"),
    ("study1_verification/strict_achieved_gpt55.jsonl", "study1.strict.achieved.gpt55"),
    ("study1_verification/strict_binding_sonnet5.jsonl", "study1.strict.binding.sonnet5"),
    ("study1_verification/strict_binding_gpt54mini.jsonl", "study1.strict.binding.gpt54mini"),
    ("study1_verification/strict_achieved_sonnet5.jsonl", "study1.strict.achieved.sonnet5"),
    ("study1_verification/strict_achieved_gpt54mini.jsonl", "study1.strict.achieved.gpt54mini"),
]


def cost_of(model: str, usage: dict) -> float:
    p = PRICES.get(model)
    if not p:
        return 0.0
    return (usage.get("input_tokens", 0) * p["input"] / 1e6
            + usage.get("output_tokens", 0) * p["output"] / 1e6
            + usage.get("web_search_requests", 0) * WEB_SEARCH_PER_1K / 1000)


def template_hashes() -> dict:
    """sha256-16 of each prompt TEMPLATE (the per-item hashes in each record cover the
    filled-in prompt; these identify the template the whole run used)."""
    import importlib
    out = {}
    try:
        v = importlib.import_module("verify")
        out |= {"verify.system_web": C.sha(v.SYSTEM_WEB),
                "verify.system_soundness": C.sha(v.SYSTEM_SOUND),
                "verify.positives": C.sha(v.POS_PROMPT),
                "verify.negatives": C.sha(v.NEG_PROMPT),
                "verify.soundness": C.sha(v.SOUND_PROMPT)}
    except Exception as e:
        out["verify.error"] = str(e)
    try:
        d = importlib.import_module("detect")
        out |= {"detect.system": C.sha(d.SYSTEM), "detect.prompt": C.sha(d.PROMPT)}
    except Exception as e:
        out["detect.error"] = str(e)
    try:
        a = importlib.import_module("adjudicate")
        st = importlib.import_module("strict")
        out |= {"strict.rules": C.sha(st.RULES), "strict.schema": C.sha(st.SCHEMA_NOTE),
                "strict.binding": C.sha(st.BINDING_PROMPT), "strict.achieved": C.sha(st.ACHIEVED_PROMPT)}
    except Exception as e:
        out["strict.error"] = str(e)
    try:
        a = importlib.import_module("adjudicate")
        out |= {"adjudicate.negatives": C.sha(a.NEG_PROMPT),
                "adjudicate.positives": C.sha(a.POS_PROMPT),
                "adjudicate.soundness": C.sha(a.SOUND_PROMPT)}
    except Exception as e:
        out["adjudicate.error"] = str(e)
    return out


def panel_counts() -> dict:
    """Per-model counts of stored, non-refused binary answers actually read by this study.

    Other evaluation jobs were writing to some of these report files while A2 ran, so these
    counts pin exactly what the corrected-accuracy table was computed against. They were
    identical at the start and at the end of the run: those jobs touch FRQ judgements, not
    the binary task."""
    from collections import Counter as _C
    pa = C.load_panel_answers()
    c = _C((k[0], k[2]) for k in pa)
    return {m: dict(binary=c[(m, "binary")], binary_perturbed=c[(m, "binary_perturbed")])
            for m in C.MODEL_ORDER}


def main() -> None:
    blocks, grand = {}, 0.0
    for rel, name in FILES:
        path = C.STUDY / rel
        recs = C.read_jsonl(path)
        if not recs:
            blocks[name] = dict(file=rel, records=0)
            continue
        dedup = {}
        for r in recs:
            k = (r.get("id") or r.get("pair_id"),
                 r.get("kind") or r.get("judge") or r.get("referee"),
                 r.get("order") or r.get("mode"))
            dedup[k] = r
        recs = list(dedup.values())
        usage = defaultdict(lambda: dict(input_tokens=0, output_tokens=0, web_search_requests=0, calls=0))
        for r in recs:
            m = r.get("model") or r.get("judge_model") or r.get("referee_model") or "unknown"
            for base in ("gpt-5.4-mini", "gpt-5.5", "gpt-5.4"):
                if m.startswith(base + "-2"):
                    m = base
            u = r.get("usage") or {}
            for k in ("input_tokens", "output_tokens", "web_search_requests"):
                usage[m][k] += u.get(k, 0) or 0
            usage[m]["calls"] += 1
        sub = 0.0
        models = {}
        for m, u in usage.items():
            c = cost_of(m, u)
            sub += c
            models[m] = dict(u, cost_usd=round(c, 2))
        grand += sub
        verdicts = Counter(r.get("verdict") or r.get("answer") for r in recs)
        blocks[name] = dict(
            file=rel, records=len(recs),
            served_models=sorted({(r.get("served_model") or r.get("model") or "") for r in recs}),
            requested_models=sorted({(r.get("judge_model") or r.get("referee_model")
                                      or r.get("model") or "") for r in recs}),
            prompt_shas=sorted({r.get("prompt_sha") for r in recs if r.get("prompt_sha")}),
            first_ts=min(r["ts"] for r in recs), last_ts=max(r["ts"] for r in recs),
            verdict_counts=dict(verdicts),
            refusals=sum(1 for r in recs if r.get("refused") or r.get("stop_reason") == "refusal"),
            errors=sum(1 for r in recs if r.get("error")),
            usage_by_model=models, cost_usd=round(sub, 2),
        )

    s1 = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8")) if (C.S1 / "sample.json").exists() else {}
    s2 = json.loads((C.S2 / "pairs.json").read_text(encoding="utf-8")) if (C.S2 / "pairs.json").exists() else {}

    man = dict(
        study="A2 — binary task validity (Reviewer 2, concern C2)",
        generated_utc=C.now_utc(), git_sha=C.git_sha(), git_branch=C.git_branch(),
        corpora=dict(
            original=dict(path=str(C.BENCH_ORIG.relative_to(C.ROOT)), events=4760),
            extension=dict(path=str(C.BENCH_EXT.relative_to(C.ROOT)), events=815)),
        frames=s1.get("frames", {}) | dict(paired=s2.get("frame")),
        seeds=dict(study1=s1.get("seeds"), study2_pairs=s2.get("seed"), study2_order=s2.get("order_seed")),
        allocation=dict(study1=s1.get("allocation_rule"), study2=s2.get("allocation_rule")),
        verifier=dict(model="claude-opus-4-8", web_search_tool="web_search_20260209",
                      max_uses=8, effort="high", thinking="adaptive"),
        strict_referees=dict(
            primary=["claude-sonnet-5", "gpt-5.4-mini"],
            crosscheck=["claude-opus-4-8", "gpt-5.5"],
            mechanical_gates="gates.py: quotes verified as literal substrings of the source "
                             "shown to the referee; every number in the claim present in the "
                             "decomposition; each numeric inequality recomputed in code; "
                             "achieved-route source dates parsed and compared",
            rule="both referees must certify: every claim element satisfied by one named source, "
                 "a verbatim quote per element, the reported value for any numeric element, no "
                 "vague element anywhere in the claim",
            direction="removal only: re-examines candidates, never promotes a sound item"),
        adjudicator=dict(model=ADJ_NOTE, provider="OpenAI Responses API + native web_search",
                         in_evaluated_panel=False, is_detection_judge=False),
        detection_judges=[dict(key="opus48", model="claude-opus-4-8", in_evaluated_panel=False,
                               note="outside the evaluated panel"),
                          dict(key="gpt54", model="gpt-5.4", in_evaluated_panel=True,
                               note="also one of the evaluated models")],
        evaluated_panel={k: dict(name=v["name"], cutoff=v["cutoff"]) for k, v in C.MODELS.items()},
        panel_answer_counts=panel_counts(),
        prices=dict(per_1m_tokens=PRICES, web_search_per_1k=WEB_SEARCH_PER_1K, source=PRICE_SOURCE),
        prompt_template_sha=template_hashes(),
        pipelines=blocks,
        total_cost_usd=round(grand, 2),
        constraints=dict(
            benchmark_modified=False, scoring_code_modified=False, model_outputs_modified=False,
            verification_and_detection_separated=True,
            note="verify.py and detect.py share only common.py (read-only loaders); neither reads "
                 "the other's outputs."),
    )
    (C.STUDY / "MANIFEST.json").write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"total measured cost ${grand:,.2f}")
    for k, v in blocks.items():
        print(f"  {k:22s} records={v.get('records',0):5d}  cost=${v.get('cost_usd',0):,.2f}")


if __name__ == "__main__":
    main()
