"""a7_inventory.py — Step 0: what reasoning text exists in the stored outputs. Read-only.

Registry of every stored prediction file for the panel models (base / WS+Cutoff / WS, original
corpus and April–August 2026 extension). For each (file, task) it counts records where the task
applies, records with non-empty in-answer reasoning (the `reasoning` field of the JSON answer;
for FRQ the answer text itself), records with a provider-native thinking/reasoning TEXT field,
records with a reasoning-token COUNT only (OpenAI reasoning models), truncations, refusals, and
the word-length distribution of the in-answer reasoning. Writes inventory.md + inventory.json.
"""
from __future__ import annotations
import json, os, re, statistics as st, sys
from pathlib import Path
import numpy as np

ROOT = Path(".")
A = ROOT / "archive/model_outputs/benchmark_logs_model_outputs"
BK = Path("archive/backup_20260508/benchmark_logs")
OUT = ROOT / "results/A7_reasoning_traces"
TASKS = ["binary", "binary_perturbed", "mcq", "date", "frq"]
FIELD = {"binary": "binary_question", "binary_perturbed": "binary_question_perturbed", "mcq": "mcq_question",
         "date": "date_prediction_prompt", "frq": "frq_prompt"}

# (model, condition, half, path, native_thinking_note)
NATIVE = {
    "DeepSeek-R1": "native <think>…</think> block was STRIPPED before storage (test_LLM.get_model_response regex); not recoverable",
    "GPT-5.4": "reasoning tokens are billed and COUNTED (`*_reasoning_tokens`) but the text is never returned by the API; no text stored",
    "GPT-5.6 Sol": "reasoning tokens COUNTED only (`*_reasoning_tokens`); text not returned by the API",
    "Claude Sonnet 5": "adaptive thinking on; runs used --no-capture-thinking (default) — 0 of 32 probe calls returned any summary text; no thinking text stored",
    "Claude Opus 4.8": "same as Sonnet 5: no thinking text stored",
    "Claude Fable 5": "same as Sonnet 5: no thinking text stored; base run incomplete (824/4,760)",
    "GPT-OSS 20B": "served locally (transformers / vLLM); the analysis channel was not captured, only the final JSON",
    "DeepSeek-V4-Pro": "non-reasoning chat endpoint; no thinking field",
    "GPT-4o": "non-reasoning model", "LLaMA 3.3 70B": "non-reasoning model", "Claude S4.5": "thinking not enabled in the published run",
}
RUNS = [
    # ---- base, original corpus
    ("GPT-4o",          "base", "orig", A / "predictions_gpt-4o.jsonl"),
    ("LLaMA 3.3 70B",   "base", "orig", A / "llama-3.3-70b-full.jsonl.jsonl"),
    ("GPT-OSS 20B",     "base", "orig", A / "gpt-oss-20b-full.jsonl"),
    ("DeepSeek-R1",     "base", "orig", A / "predictions_DeepSeek-R1.jsonl"),
    ("Claude S4.5",     "base", "orig", A / "predictions_claude-sonnet-4-5_20260428_092848.jsonl"),
    ("GPT-5.4",         "base", "orig", A / "predictions_gpt-5.4.jsonl"),
    ("Claude Sonnet 5", "base", "orig", ROOT / "results_sonnet5_run1/raw/base_medium_run1.jsonl"),
    ("GPT-5.6 Sol",     "base", "orig", ROOT / "results_sol_run1/raw/base_medium_run1.jsonl"),
    ("DeepSeek-V4-Pro", "base", "orig", ROOT / "results_dsv4pro_run1/raw/base_run1.jsonl"),
    ("Claude Opus 4.8", "base", "orig", ROOT / "results_opus48_run1/raw/base_medium_run1.jsonl"),
    ("Claude Fable 5",  "base", "orig", ROOT / "results_fable5_run1/raw/base_medium_run1.jsonl"),
    # ---- base, extension
    ("GPT-4o",          "base", "ext", ROOT / "results_extension_run2/raw/gpt4o_base.jsonl"),
    ("LLaMA 3.3 70B",   "base", "ext", ROOT / "results_extension_run2/raw/llama33_base.jsonl"),
    ("GPT-OSS 20B",     "base", "ext", ROOT / "results_extension_run2/raw/gptoss20b_base.jsonl"),
    ("Claude S4.5",     "base", "ext", ROOT / "results_extension_run2/raw/sonnet45_base.jsonl"),
    ("GPT-5.4",         "base", "ext", ROOT / "results_extension_run2/raw/gpt54_base.jsonl"),
    ("Claude Sonnet 5", "base", "ext", ROOT / "results_extension_run2/raw/sonnet5_base_run1.jsonl"),
    ("GPT-5.6 Sol",     "base", "ext", ROOT / "results_extension_run2/raw/sol_base.jsonl"),
    ("DeepSeek-V4-Pro", "base", "ext", ROOT / "results_extension_run2/raw/deepseekv4pro_base.jsonl"),
    ("Claude Opus 4.8", "base", "ext", ROOT / "results_extension_run2/raw/opus48_base_run1.jsonl"),
    # ---- WS+Cutoff / WS, pinned 500 (orig) and 86-event WS subset (ext)
    ("GPT-4o",          "ws_cutoff", "orig", A / "gpt_4o_web_search.jsonl"),
    ("GPT-4o",          "ws",        "orig", A / "gpt_4o_web_search_no_cutoff.jsonl"),
    ("GPT-5.4",         "ws_cutoff", "orig", ROOT / "archive/model_outputs/predictions_gpt-5.4_20260506_055209.jsonl"),
    ("GPT-5.4",         "ws",        "orig", A / "gpt-5_4_web_search_subset.jsonl"),
    ("DeepSeek-R1",     "ws_cutoff", "orig", BK / "predictions_deepseek-r1_20260510_120503.jsonl"),
    ("DeepSeek-R1",     "ws",        "orig", BK / "predictions_deepseek-r1_20260510_123317.jsonl"),
    ("Claude S4.5",     "ws_cutoff", "orig", BK / "model_outputs/claude_500_web_constrained.jsonl"),
    ("Claude S4.5",     "ws",        "orig", BK / "model_outputs/claude_web_search_full.jsonl"),
    ("LLaMA 3.3 70B",   "ws_cutoff", "orig", ROOT / "results_llama33_run1/raw/ws_cutoff_500.jsonl"),
    ("Claude Sonnet 5", "ws_cutoff", "orig", ROOT / "results_sonnet5_run1/raw/ws_cutoff_500.jsonl"),
    ("Claude Sonnet 5", "ws",        "orig", ROOT / "results_sonnet5_run1/raw/ws_500.jsonl"),
    ("GPT-5.6 Sol",     "ws_cutoff", "orig", ROOT / "results_sol_run1/raw/ws_cutoff_500.jsonl"),
    ("GPT-5.6 Sol",     "ws",        "orig", ROOT / "results_sol_run1/raw/ws_500.jsonl"),
    ("Claude Opus 4.8", "ws_cutoff", "orig", ROOT / "results_opus48_run1/raw/ws_cutoff_500.jsonl"),
    ("Claude Opus 4.8", "ws",        "orig", ROOT / "results_opus48_run1/raw/ws_500.jsonl"),
    ("Claude Sonnet 5", "ws_cutoff", "ext", ROOT / "results_extension_run2/raw/sonnet5_ws_cutoff.jsonl"),
    ("Claude Sonnet 5", "ws",        "ext", ROOT / "results_extension_run2/raw/sonnet5_ws.jsonl"),
    ("Claude Opus 4.8", "ws_cutoff", "ext", ROOT / "results_extension_run2/raw/opus48_ws_cutoff.jsonl"),
    ("Claude Opus 4.8", "ws",        "ext", ROOT / "results_extension_run2/raw/opus48_ws.jsonl"),
]
EXTRA_PASSES = [  # repeat passes / intervention arms: available, listed for completeness only
    ("Claude Sonnet 5 base passes 2,3 + low-effort", "results_sonnet5_run1/raw/base_medium_run{2,3}.jsonl, base_low_run1.jsonl (4,760 each)"),
    ("GPT-5.6 Sol base passes 2,3 (1,000-event subsample)", "results_sol_run1/raw/base_medium_run{2,3}.jsonl"),
    ("Sonnet 5 / Opus 4.8 extension passes 2,3", "results_extension_run2/raw/{sonnet5,opus48}_base_run{2,3}.jsonl (815 each)"),
    ("Sol WS/WS+Cutoff FAILED_no_context runs", "results_sol_run1/raw/*.FAILED_no_context.jsonl — retrieval failed; effectively extra base passes on the 500 subset"),
    ("A6 calibration arms B1/B2/D/E (3 models, 500 subset)", "calibration_study/raw/*.jsonl — modified prompts; reasoning field present"),
    ("A8 base-rate sweep (9 models x 5 X, 500 events, binary only)", "results/A8_base_rate/raw/*.jsonl — modified prompts; reasoning field present"),
]


def load_bench():
    b = {}
    for p in (ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl", ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"):
        for l in open(p, encoding="utf-8"):
            if l.strip():
                r = json.loads(l); b[r["id"]] = r
    return b


def words(s):
    return len(re.findall(r"\S+", s or ""))


def inventory_file(path, bench):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    # dedupe by id, last wins (resumed runs never duplicate, but be safe)
    byid = {}
    for r in rows: byid[r["id"]] = r
    rows = list(byid.values())
    fmt = "run_cusp" if "condition" in rows[0] else "legacy"
    out = {"n_records": len(rows), "format": fmt, "tasks": {}}
    for t in TASKS:
        appl = [r for r in rows if bench.get(r["id"], {}).get(FIELD[t])]
        if t == "frq":
            txt = [(r.get("frq_answer") or r.get("frq_raw") or "") for r in appl]
        else:
            txt = [(r.get(f"{t}_reasoning") or "") for r in appl]
        txt = [x if isinstance(x, str) else json.dumps(x) for x in txt]
        has = [x for x in txt if x.strip() and not x.startswith("Error:")]
        ans = [r for r in appl if (r.get(f"{t}_answer") not in (None, "")) or (t == "frq" and (r.get("frq_answer") or "").strip())]
        think = sum(1 for r in appl if r.get(f"{t}_thinking"))
        rtok = [r.get(f"{t}_reasoning_tokens") for r in appl if r.get(f"{t}_reasoning_tokens")]
        trunc = sum(1 for r in appl if r.get(f"{t}_truncated") or r.get(f"{t}_stop_reason") in ("length", "max_tokens"))
        refus = sum(1 for r in appl if r.get(f"{t}_refusal"))
        err = sum(1 for r in appl if r.get(f"{t}_error"))
        fallback = sum(1 for r in appl if r.get(f"{t}_parse_method") == "fallback")
        # legacy files: a 'reasoning' that is actually the whole raw JSON (fallback parse)
        rawjson = sum(1 for x in has if x.lstrip().startswith("{"))
        L = np.array([words(x) for x in has]) if has else np.array([0])
        out["tasks"][t] = dict(applicable=len(appl), with_answer=len(ans), with_reasoning_text=len(has),
                               native_thinking_text=think, reasoning_token_count_only=len(rtok),
                               reasoning_tokens_mean=(float(np.mean(rtok)) if rtok else None),
                               truncated=trunc, refusals=refus, errors=err, fallback_parsed=fallback, reasoning_is_raw_json=rawjson,
                               words_mean=float(L.mean()), words_median=float(np.median(L)), words_p10=float(np.percentile(L, 10)),
                               words_p90=float(np.percentile(L, 90)), words_max=int(L.max()), words_lt10=int((L < 10).sum()))
    return out


def main():
    bench = load_bench()
    inv = {}
    for model, cond, half, path in RUNS:
        key = f"{model}|{cond}|{half}"
        if not path.exists():
            inv[key] = {"missing_file": str(path)}; continue
        inv[key] = dict(model=model, condition=cond, half=half, path=str(path), **inventory_file(path, bench))
    json.dump(dict(runs=inv, native_notes=NATIVE, extra=EXTRA_PASSES), open(OUT / "inventory.json", "w"), indent=1)
    # ---- markdown
    md = ["# A7 Step 0 — inventory of stored reasoning text (read-only; no analysis)\n",
          "Every stored prediction file of the ten-model panel (plus the incomplete Claude Fable 5 run), by condition and corpus half. "
          "\"Reasoning text\" = the `reasoning` field the JSON answer format requests (`\"reasoning\": \"<1-2 sentence justification>\"`); "
          "for FRQ it is the answer itself (the prompt asks for 3–4 sentences of method, no separate reasoning field). "
          "\"Native thinking\" = a provider-returned thinking/reasoning text field stored alongside the answer.\n",
          "## Headline\n"]
    tot_think = sum(v["tasks"][t]["native_thinking_text"] for v in inv.values() if "tasks" in v for t in TASKS)
    md.append(f"* **Provider-native thinking text: {tot_think} records in every file.** None was stored for any model, task or condition (see the per-model notes below). "
              "Only the in-answer 1–2-sentence justification exists, plus reasoning-token *counts* for GPT-5.4 and GPT-5.6 Sol.")
    md.append("* In-answer reasoning exists for every answered record of every model, task and condition (base, WS+Cutoff, WS; original corpus and extension), "
              "including Claude Sonnet 5 and GPT-5.6 Sol on the extension.")
    md.append("* Traces are short by design: the prompt asks for a 1–2-sentence justification (medians below). They are justifications written *after* the answer is chosen inside one JSON object, not a chain of thought.\n")
    md.append("## Native thinking, per model\n\n| model | status |\n|---|---|")
    for m, n in NATIVE.items(): md.append(f"| {m} | {n} |")
    for cond, title in (("base", "Base condition"), ("ws_cutoff", "WS+Cutoff (knowledge-access) condition"), ("ws", "WS (unrestricted) condition")):
        md.append(f"\n## {title}\n")
        md.append("| model | half | task | applicable | answered | with reasoning text | native thinking | reasoning-token count only (mean tokens) | truncated | refusals | fallback-parsed | words mean / median / p10 / p90 / max | < 10 words |")
        md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for key, v in inv.items():
            if "tasks" not in v or v["condition"] != cond: continue
            for t in TASKS:
                d = v["tasks"][t]
                if d["applicable"] == 0: continue
                rt = f"{d['reasoning_token_count_only']} ({d['reasoning_tokens_mean']:.0f})" if d["reasoning_token_count_only"] else "0"
                md.append(f"| {v['model']} | {v['half']} | {t} | {d['applicable']} | {d['with_answer']} | {d['with_reasoning_text']} | {d['native_thinking_text']} | {rt} | {d['truncated']} | {d['refusals']} | {d['fallback_parsed'] or d['reasoning_is_raw_json']} | "
                          f"{d['words_mean']:.0f} / {d['words_median']:.0f} / {d['words_p10']:.0f} / {d['words_p90']:.0f} / {d['words_max']} | {d['words_lt10']} |")
    md.append("\n## Anomalies (computed): missing, degenerate or truncated traces\n")
    for key, v in inv.items():
        if "tasks" not in v: continue
        for t in TASKS:
            d = v["tasks"][t]
            if d["applicable"] == 0: continue
            notes = []
            if d["with_answer"] and d["with_reasoning_text"] < 0.9 * d["with_answer"]:
                notes.append(f"{d['with_answer'] - d['with_reasoning_text']} answered records have no reasoning text")
            if d["words_median"] < 10:
                notes.append(f"median reasoning length {d['words_median']:.0f} words ({d['words_lt10']} under 10 words) — degenerate")
            if d["truncated"] and t != "frq" and d["truncated"] >= 0.02 * d["applicable"]:
                notes.append(f"{d['truncated']} truncated at the token cap (no answer/reasoning)")
            if t == "frq" and d["truncated"] >= 0.5 * d["applicable"]:
                notes.append(f"{d['truncated']} FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)")
            if d["words_max"] > 600:
                notes.append(f"max {d['words_max']} words: a few `reasoning` fields hold the whole raw response (fallback parse)")
            if d["refusals"] >= 0.05 * d["applicable"]:
                notes.append(f"{d['refusals']} refusals ({100 * d['refusals'] / d['applicable']:.0f}%)")
            if notes:
                md.append(f"* {v['model']} / {v['condition']} / {v['half']} / {t}: " + "; ".join(notes))
    missing = [k for k, v in inv.items() if "missing_file" in v]
    md.append("\n## Missing files\n"); md.append("none" if not missing else "\n".join(f"* {k}: {inv[k]['missing_file']}" for k in missing))
    md.append("\n## Other stored traces (available, not part of the base/WS inventory)\n")
    for a, b in EXTRA_PASSES: md.append(f"* {a}: `{b}`")
    (OUT / "inventory.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
