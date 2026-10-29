"""
a8_common.py — shared registry and loaders for study A8 (base-rate injection sweep,
Reviewer 2 concern C5).

Nothing here modifies the benchmark, scoring code, or stored model outputs. The
no-injection baseline is read from the stored, already-graded evaluation reports
(the same files run_evaluation/full_corpus_tables.PANEL uses); the sweep is read
from this study's own raw shards (raw/<model>.jsonl) and graded with the frozen
scripts/eval.py grader.
"""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path

ROOT  = Path(__file__).resolve().parents[3]
STUDY = ROOT / "results" / "A8_base_rate"
RAW, TABLES, FIGS, LOGS = STUDY / "raw", STUDY / "tables", STUDY / "figures", STUDY / "logs"
BENCH = [ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl",
         ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"]
SAMPLE = STUDY / "sample.json"
SEED = 8
XS = [10, 30, 50, 70, 90]

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "run_evaluation"))

# One entry per model in the published ten-model panel (full_corpus_tables.PANEL).
# `run` is the live configuration that reproduces each model's stored base run
# (provider, model id, decoding); `price` is USD per 1M tokens (input, output) —
# assumed list prices, flagged in MANIFEST.json, never verified against invoices.
MODELS = {
    "gpt4o":     dict(name="GPT-4o",          cutoff="2023-10", provider="azure",     model="gpt-4o",
                      decoding=dict(temperature=0.0), price=(2.50, 10.00), conc=8,
                      price_src="Azure OpenAI gpt-4o-2024-11-20 list price (calibration_study/prices.json), assumed",
                      tokens_from="results_extension_run2/raw/gpt4o_base.jsonl"),
    "llama33":   dict(name="LLaMA 3.3 70B",   cutoff="2023-12", provider="azure",     model="Llama-3.3-70B-Instruct",
                      decoding=dict(temperature=0.0), price=(0.71, 0.71), conc=8,
                      price_src="Azure AI Foundry serverless list price (calibration_study/prices.json), assumed",
                      tokens_from="results_extension_run2/raw/llama33_base.jsonl"),
    "gptoss20b": dict(name="GPT-OSS 20B",     cutoff="2024-06", provider="local",     model="gpt-oss-20b",
                      decoding=dict(temperature=0.0), price=(0.0, 0.0), conc=16,
                      price_src="served locally with vLLM on the lab GPUs (Azure deployment returns 404), no API cost",
                      tokens_from="results_extension_run2/raw/gptoss20b_base.jsonl"),
    "deepseek_r1": dict(name="DeepSeek-R1",   cutoff="2024-07", provider=None,        model="DeepSeek-R1",
                      decoding=dict(temperature=0.0), price=(1.35, 5.40), conc=0,
                      price_src="n/a — Azure deployment retired (HTTP 410 / 400 'dependent service'); cannot be run",
                      tokens_from=None),
    "sonnet45":  dict(name="Claude S4.5",     cutoff="2025-01", provider="anthropic", model="claude-sonnet-4-5",
                      decoding=dict(temperature=0.0), price=(3.00, 15.00), conc=12,
                      price_src="Anthropic list price for Claude Sonnet 4.5, assumed",
                      tokens_from="results_extension_run2/raw/sonnet45_base.jsonl"),
    "gpt54":     dict(name="GPT-5.4",         cutoff="2025-08", provider="openai",    model="gpt-5.4",
                      decoding=dict(effort="medium"), price=(1.25, 10.00), conc=10,
                      price_src="scripts/run_cusp.py PRICING, assumed; reasoning tokens bill as output",
                      tokens_from="results_extension_run2/raw/gpt54_base.jsonl",
                      note="original-corpus base run's reasoning_effort is not on record; effort=medium matches the extension-half base run"),
    "sonnet5":   dict(name="Claude Sonnet 5", cutoff="2026-01", provider="anthropic", model="claude-sonnet-5",
                      decoding=dict(effort="medium"), price=(2.00, 10.00), conc=14,
                      price_src="scripts/run_cusp.py PRICING, assumed",
                      tokens_from="results_sonnet5_run1/raw/base_medium_run1.jsonl"),
    "sol":       dict(name="GPT-5.6 Sol",     cutoff="2026-02", provider="openai",    model="gpt-5.6-sol",
                      decoding=dict(effort="medium"), price=(4.00, 20.00), conc=10,
                      price_src="scripts/run_cusp.py PRICING, assumed; reasoning tokens bill as output",
                      tokens_from="results_sol_run1/raw/base_medium_run1.jsonl"),
    "dsv4pro":   dict(name="DeepSeek-V4-Pro", cutoff="2026-04", provider="azure",     model="DeepSeek-V4-Pro",
                      decoding=dict(temperature=0.0), price=(1.74, 3.48), conc=8,
                      price_src="Azure AI Foundry price as listed by a third-party calculator (futureagi.com, verified Aug 2026), assumed",
                      tokens_from="results_dsv4pro_run1/raw/base_run1.jsonl"),
    "opus48":    dict(name="Claude Opus 4.8", cutoff="2026-01", provider="anthropic", model="claude-opus-4-8",
                      decoding=dict(effort="medium"), price=(5.00, 25.00), conc=8,
                      price_src="platform.claude.com Opus 4.8 overview ($5/$25), assumed",
                      tokens_from="results_opus48_run1/raw/base_medium_run1.jsonl"),
}
RUNNABLE = [k for k, m in MODELS.items() if m["provider"]]
ORDER = list(MODELS)  # panel order (by cutoff, as in full_corpus_tables.PANEL)

ENDPOINTS = {"azure": "env:AZURE_OPENAI_ENDPOINT (OpenAI-compatible /openai/v1 route of the lab's Azure resource)",
             "openai": "https://api.openai.com/v1", "local": "http://127.0.0.1:8077/v1 (vLLM)",
             "anthropic": "https://api.anthropic.com"}


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def months(ym: str) -> int:
    y, m = str(ym).split("-")[:2]
    return int(y) * 12 + int(m)


# CUTOFF_MONTH_PRE (default on; env CUTOFF_MONTH_PRE=0 restores the old rule):
#   on  -> post iff pub_month > cutoff_month (the cutoff month counts as pre), the rule the
#          manuscript now uses everywhere. Outputs go to tables_cmpre/, figures_cmpre/,
#          outputs_cmpre.jsonl so the stored old-rule files are never overwritten.
#   off -> old main-table rule: pre iff pub_month < cutoff_month (cutoff month counts as post).
# Only the pre/post partition slopes (tables/partition_slopes.md) depend on this rule.
CUTOFF_MONTH_PRE = os.environ.get("CUTOFF_MONTH_PRE", "1") != "0"
SUFFIX = "_cmpre" if CUTOFF_MONTH_PRE else ""
TABLES, FIGS = STUDY / f"tables{SUFFIX}", STUDY / f"figures{SUFFIX}"
OUTPUTS = STUDY / f"outputs{SUFFIX}.jsonl"


def partition(pub: str, cutoff: str) -> str:
    if CUTOFF_MONTH_PRE:
        return "post" if months(pub) > months(cutoff) else "pre"
    return "pre" if months(pub) < months(cutoff) else "post"


_bench = None
def load_bench() -> dict:
    global _bench
    if _bench is None:
        _bench = {}
        for p in BENCH:
            with open(p, encoding="utf-8") as f:
                for l in f:
                    if l.strip():
                        r = json.loads(l)
                        assert r["id"] not in _bench, f"duplicate id across halves: {r['id']}"
                        _bench[r["id"]] = r
    return _bench


def candidates() -> list[str]:
    """Events carrying BOTH the original and the perturbed binary question."""
    b = load_bench()
    return sorted(i for i, r in b.items() if r.get("binary_question") and r.get("binary_question_perturbed"))


def load_sample() -> dict:
    s = json.load(open(SAMPLE, encoding="utf-8"))
    assert len(s["ids"]) == 500 and len(set(s["ids"])) == 500
    return s


# ----------------------------------------------------------------------------- prompts
from test_LLM import BINARY_SYSTEM, parse_structured_response  # frozen base prompt + parser (never edited)

_HEAD = ("You are a scientific forecasting evaluator. Given a yes/no forecasting question about a "
         "future scientific or technical development, reason briefly then give your final answer and confidence.\n\n")
_TAIL = ('You MUST respond with valid JSON in exactly this format:\n'
         '{"reasoning": "<1-2 sentence justification>", "answer": "Yes or No", "confidence": <float 0.0-1.0>}')
assert BINARY_SYSTEM == _HEAD + _TAIL, "base binary prompt changed — stop"
BASE_PROMPT_SHA = sha(BINARY_SYSTEM)


def injected_sentence(x: int) -> str:
    return f"Historically, in this field, the probability of this kind of progress happening is {int(x)}%."


def injected_system(x: int) -> str:
    """The base binary system prompt with ONE sentence inserted between the task
    instruction and the JSON/confidence block. Everything else is byte-identical."""
    s = _HEAD + injected_sentence(x) + "\n\n" + _TAIL
    assert s.startswith(_HEAD) and s.endswith(_TAIL)
    assert s.replace(injected_sentence(x) + "\n\n", "", 1) == BINARY_SYSTEM
    return s


def user_prompt(task: str, row: dict) -> str:
    return row["binary_question"] if task == "binary" else row["binary_question_perturbed"]


# ----------------------------------------------------------------------------- baseline
def _panel_paths():
    from full_corpus_tables import PANEL
    return {name: (op, ep) for name, cut, op, ep in PANEL}


def load_baseline(model: str) -> dict:
    """Stored base-condition outputs for the sampled events: {(id, task): rec}.
    rec = answer ('yes'/'no'/None), confidence (float/None), correct (bool/None),
    valid_answer, valid_conf, source report path. Read only; never regenerated."""
    op, ep = _panel_paths()[MODELS[model]["name"]]
    ids = set(load_sample()["ids"])
    out = {}
    for p in (op, ep):
        if not p or not os.path.exists(ROOT / p):
            continue
        rep = json.load(open(ROOT / p, encoding="utf-8"))
        for r in rep["results"]:
            if r["id"] not in ids:
                continue
            for task in ("binary", "binary_perturbed"):
                t = r.get("tasks", {}).get(task)
                rec = dict(id=r["id"], task=task, answer=None, confidence=None, correct=None,
                           status="absent", source=p)
                if t is None:
                    pass
                elif t.get("skipped"):
                    rec["status"] = "skipped:" + str(t.get("skip_reason") or t.get("reason") or "")
                elif "correct" in t:
                    ans = str(t.get("parsed_answer", "")).lower()
                    rec.update(answer=(ans if ans in ("yes", "no") else None), correct=bool(t["correct"]),
                               confidence=(float(t["confidence"]) if t.get("confidence") is not None else None),
                               status="graded")
                out[(r["id"], task)] = rec
    for i in ids:
        for task in ("binary", "binary_perturbed"):
            out.setdefault((i, task), dict(id=i, task=task, answer=None, confidence=None, correct=None,
                                          status="absent", source=None))
    return out


def p_yes(answer, conf):
    if answer is None or conf is None:
        return None
    return float(conf) if answer == "yes" else 1.0 - float(conf)
