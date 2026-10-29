"""a7_common.py — shared paths, registry and loaders for study A7 (reasoning-trace analysis).
Read-only over stored JSONL and graded reports; nothing here modifies scoring code or outputs."""
from __future__ import annotations
import ast, hashlib, json, re
from pathlib import Path

ROOT = Path(".")
A = ROOT / "archive/model_outputs/benchmark_logs_model_outputs"
BK = Path("archive/backup_20260508/benchmark_logs")
FR = ROOT / "run_evaluation/frq_results"
STUDY = ROOT / "results/A7_reasoning_traces"
TRACES = STUDY / "traces.jsonl"
SUBSET = ROOT / "results_sonnet5_run1/subset500_ids.txt"
TASKS = ["binary", "binary_perturbed", "mcq", "date", "frq"]
FIELD = {"binary": "binary_question", "binary_perturbed": "binary_question_perturbed", "mcq": "mcq_question",
         "date": "date_prediction_prompt", "frq": "frq_prompt"}
CUTOFF = {"GPT-4o": "2023-10", "LLaMA 3.3 70B": "2023-12", "GPT-OSS 20B": "2024-06", "DeepSeek-R1": "2024-07",
          "Claude S4.5": "2025-01", "GPT-5.4": "2025-08", "Claude Sonnet 5": "2026-01", "GPT-5.6 Sol": "2026-02",
          "DeepSeek-V4-Pro": "2026-04", "Claude Opus 4.8": "2026-01"}
MODEL_KEY = {"GPT-4o": "gpt4o", "LLaMA 3.3 70B": "llama33", "GPT-OSS 20B": "gptoss20b", "DeepSeek-R1": "deepseek_r1",
             "Claude S4.5": "sonnet45", "GPT-5.4": "gpt54", "Claude Sonnet 5": "sonnet5", "GPT-5.6 Sol": "sol",
             "DeepSeek-V4-Pro": "dsv4pro", "Claude Opus 4.8": "opus48"}
# (model, condition, half, raw path, graded report path)
RUNS = [
    ("GPT-4o",          "base", "orig", A / "predictions_gpt-4o.jsonl",                          FR / "gpt_4o_reeval.json"),
    ("LLaMA 3.3 70B",   "base", "orig", A / "llama-3.3-70b-full.jsonl.jsonl",                    FR / "llama_3_3_full.json"),
    ("GPT-OSS 20B",     "base", "orig", A / "gpt-oss-20b-full.jsonl",                            FR / "gpt_oss_20B_reeval.json"),
    ("DeepSeek-R1",     "base", "orig", A / "predictions_DeepSeek-R1.jsonl",                     FR / "deepseek_r1.json"),
    ("Claude S4.5",     "base", "orig", A / "predictions_claude-sonnet-4-5_20260428_092848.jsonl", FR / "claude_sonnet.json"),
    ("GPT-5.4",         "base", "orig", A / "predictions_gpt-5.4.jsonl",                         FR / "gpt_5_4_eval.json"),
    ("Claude Sonnet 5", "base", "orig", ROOT / "results_sonnet5_run1/raw/base_medium_run1.jsonl", ROOT / "results_sonnet5_run1/reports/base_medium_run1.json"),
    ("GPT-5.6 Sol",     "base", "orig", ROOT / "results_sol_run1/raw/base_medium_run1.jsonl",     ROOT / "results_sol_run1/reports/base_medium_run1.json"),
    ("DeepSeek-V4-Pro", "base", "orig", ROOT / "results_dsv4pro_run1/raw/base_run1.jsonl",        ROOT / "results_dsv4pro_run1/reports/base_run1.json"),
    ("Claude Opus 4.8", "base", "orig", ROOT / "results_opus48_run1/raw/base_medium_run1.jsonl",  ROOT / "results_opus48_run1/reports/base_medium_run1.json"),
    ("GPT-4o",          "base", "ext", ROOT / "results_extension_run2/raw/gpt4o_base.jsonl",        ROOT / "results_extension_run2/reports/gpt4o_base.json"),
    ("LLaMA 3.3 70B",   "base", "ext", ROOT / "results_extension_run2/raw/llama33_base.jsonl",      ROOT / "results_extension_run2/reports/llama33_base.json"),
    ("GPT-OSS 20B",     "base", "ext", ROOT / "results_extension_run2/raw/gptoss20b_base.jsonl",    ROOT / "results_extension_run2/reports/gptoss20b_base.json"),
    ("Claude S4.5",     "base", "ext", ROOT / "results_extension_run2/raw/sonnet45_base.jsonl",     ROOT / "results_extension_run2/reports/sonnet45_base.json"),
    ("GPT-5.4",         "base", "ext", ROOT / "results_extension_run2/raw/gpt54_base.jsonl",        ROOT / "results_extension_run2/reports/gpt54_base.json"),
    ("Claude Sonnet 5", "base", "ext", ROOT / "results_extension_run2/raw/sonnet5_base_run1.jsonl", ROOT / "results_extension_run2/reports/sonnet5_base_run1.json"),
    ("GPT-5.6 Sol",     "base", "ext", ROOT / "results_extension_run2/raw/sol_base.jsonl",          ROOT / "results_extension_run2/reports/sol_base.json"),
    ("DeepSeek-V4-Pro", "base", "ext", ROOT / "results_extension_run2/raw/deepseekv4pro_base.jsonl", ROOT / "results_extension_run2/reports/deepseekv4pro_base.json"),
    ("Claude Opus 4.8", "base", "ext", ROOT / "results_extension_run2/raw/opus48_base_run1.jsonl",  ROOT / "results_extension_run2/reports/opus48_base_run1.json"),
    ("GPT-4o",          "ws_cutoff", "orig", A / "gpt_4o_web_search.jsonl",                       FR / "gpt-4o_web_search_with_cutoff.json"),
    ("GPT-4o",          "ws",        "orig", A / "gpt_4o_web_search_no_cutoff.jsonl",             FR / "gpt_4o_web_search_no_cutoff_500.json"),
    ("GPT-5.4",         "ws_cutoff", "orig", ROOT / "archive/model_outputs/predictions_gpt-5.4_20260506_055209.jsonl", FR / "gpt_5_4_500_web_cutoff.json"),
    ("GPT-5.4",         "ws",        "orig", A / "gpt-5_4_web_search_subset.jsonl",                FR / "gpt_5_4_web_subset_eval.json"),
    ("DeepSeek-R1",     "ws_cutoff", "orig", BK / "predictions_deepseek-r1_20260510_120503.jsonl", FR / "deepseek_r1_500_web_cutoff.json"),
    ("DeepSeek-R1",     "ws",        "orig", BK / "predictions_deepseek-r1_20260510_123317.jsonl", FR / "deepseek_r1_500_no_cutoff.json"),
    ("Claude S4.5",     "ws_cutoff", "orig", BK / "model_outputs/claude_500_web_constrained.jsonl", FR / "claude_500_with_cutoff.json"),
    ("Claude S4.5",     "ws",        "orig", BK / "model_outputs/claude_web_search_full.jsonl",     FR / "claude_500_with_full.json"),
    ("LLaMA 3.3 70B",   "ws_cutoff", "orig", ROOT / "results_llama33_run1/raw/ws_cutoff_500.jsonl", ROOT / "results_llama33_run1/reports/ws_cutoff_500.json"),
    ("Claude Sonnet 5", "ws_cutoff", "orig", ROOT / "results_sonnet5_run1/raw/ws_cutoff_500.jsonl", ROOT / "results_sonnet5_run1/reports/ws_cutoff_500.json"),
    ("Claude Sonnet 5", "ws",        "orig", ROOT / "results_sonnet5_run1/raw/ws_500.jsonl",        ROOT / "results_sonnet5_run1/reports/ws_500.json"),
    ("GPT-5.6 Sol",     "ws_cutoff", "orig", ROOT / "results_sol_run1/raw/ws_cutoff_500.jsonl",     ROOT / "results_sol_run1/reports/ws_cutoff_500.json"),
    ("GPT-5.6 Sol",     "ws",        "orig", ROOT / "results_sol_run1/raw/ws_500.jsonl",            ROOT / "results_sol_run1/reports/ws_500.json"),
    ("Claude Opus 4.8", "ws_cutoff", "orig", ROOT / "results_opus48_run1/raw/ws_cutoff_500.jsonl",  ROOT / "results_opus48_run1/reports/ws_cutoff_500.json"),
    ("Claude Opus 4.8", "ws",        "orig", ROOT / "results_opus48_run1/raw/ws_500.jsonl",         ROOT / "results_opus48_run1/reports/ws_500.json"),
    ("Claude Sonnet 5", "ws_cutoff", "ext", ROOT / "results_extension_run2/raw/sonnet5_ws_cutoff.jsonl", ROOT / "results_extension_run2/reports/sonnet5_ws_cutoff.json"),
    ("Claude Sonnet 5", "ws",        "ext", ROOT / "results_extension_run2/raw/sonnet5_ws.jsonl",        ROOT / "results_extension_run2/reports/sonnet5_ws.json"),
    ("Claude Opus 4.8", "ws_cutoff", "ext", ROOT / "results_extension_run2/raw/opus48_ws_cutoff.jsonl",  ROOT / "results_extension_run2/reports/opus48_ws_cutoff.json"),
    ("Claude Opus 4.8", "ws",        "ext", ROOT / "results_extension_run2/raw/opus48_ws.jsonl",         ROOT / "results_extension_run2/reports/opus48_ws.json"),
]


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def months(ym):
    try:
        y, m = str(ym).split("-")[:2]; return int(y) * 12 + int(m)
    except Exception:
        return None


def partition(pub, cutoff):
    a, b = months(pub), months(cutoff)
    return None if a is None or b is None else ("pre" if a < b else "post")


_bench = None
def load_bench():
    global _bench
    if _bench is None:
        _bench = {}
        for p in (ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl", ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"):
            for l in open(p, encoding="utf-8"):
                if l.strip():
                    r = json.loads(l); _bench[r["id"]] = r
    return _bench


def load_subset():
    return {l.strip() for l in open(SUBSET) if l.strip()}


def words(s):
    return len(re.findall(r"\S+", s or ""))


def mcq_choices(raw_row):
    sc = raw_row.get("mcq_shuffled_choices")
    if isinstance(sc, str):
        try: sc = ast.literal_eval(sc)
        except Exception: sc = None
    return sc if isinstance(sc, dict) else None


def iter_traces(filter_fn=None):
    with open(TRACES, encoding="utf-8") as f:
        for l in f:
            if l.strip():
                r = json.loads(l)
                if filter_fn is None or filter_fn(r):
                    yield r


# Fields a coder may NEVER see. Enforced by a7_code.blind_view().
FORBIDDEN_FOR_CODER = {"model", "model_key", "condition", "half", "correct", "score", "ground_truth", "parsed_answer",
                       "month_distance", "signed_error_months", "frq_score", "confidence", "partition", "cutoff",
                       "publication_date", "raw_path", "report_path", "answer_raw"}
