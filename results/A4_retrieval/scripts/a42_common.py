"""Shared definitions for A4.2 / A4.3: the stored retrieval runs, event lookup, URL matching."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(".")
BK = Path("archive/backup_20260508/benchmark_logs")
A = ROOT / "archive/model_outputs/benchmark_logs_model_outputs"
OUT = ROOT / "results/A4_retrieval"
SUBSET = ROOT / "results_sonnet5_run1/subset500_ids.txt"
# A4.3 event sets: "main" = the first 500 (pinned subset), "ext500" = 500 added 2026-10-18 (a43_ext_sample.py)
A43_SETS = {"main": (SUBSET, OUT / "A4_3_fixed_queries"),
            "ext500": (OUT / "A4_3_fixed_queries/ext500/subset_ext500_ids.txt", OUT / "A4_3_fixed_queries/ext500")}
BENCH_FILES = [ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl", ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"]
# run key -> (model, condition, dataset, path, mechanism, cutoff YYYY-MM-DD used for freshness, run_date for WS re-query cap)
RUNS = {
    "gpt4o:ws_cutoff":   ("GPT-4o",          "ws_cutoff", "orig", A / "gpt_4o_web_search.jsonl",                              "youcom", "2023-10-01", None),
    "gpt4o:ws":          ("GPT-4o",          "ws",        "orig", A / "gpt_4o_web_search_no_cutoff.jsonl",                    "native", None,         None),
    "gpt54:ws_cutoff":   ("GPT-5.4",         "ws_cutoff", "orig", ROOT / "archive/model_outputs/predictions_gpt-5.4_20260506_055209.jsonl", "youcom", "2025-08-01", None),
    "gpt54:ws":          ("GPT-5.4",         "ws",        "orig", A / "gpt-5_4_web_search_subset.jsonl",                       "native", None,         None),
    "deepseek_r1:ws_cutoff": ("DeepSeek R1", "ws_cutoff", "orig", BK / "predictions_deepseek-r1_20260510_120503.jsonl",        "youcom", "2024-07-01", None),
    "deepseek_r1:ws":    ("DeepSeek R1",     "ws",        "orig", BK / "predictions_deepseek-r1_20260510_123317.jsonl",        "youcom", None,         "2026-05-11"),
    "claude45:ws_cutoff": ("Claude S4.5",    "ws_cutoff", "orig", BK / "model_outputs/claude_500_web_constrained.jsonl",       "youcom", "2025-01-01", None),
    "claude45:ws":       ("Claude S4.5",     "ws",        "orig", BK / "model_outputs/claude_web_search_full.jsonl",           "youcom", None,         "2026-05-11"),
    "sonnet5:ws_cutoff": ("Claude Sonnet 5", "ws_cutoff", "orig", ROOT / "results_sonnet5_run1/raw/ws_cutoff_500.jsonl",     "youcom", "2026-01-01", None),
    "sonnet5:ws":        ("Claude Sonnet 5", "ws",        "orig", ROOT / "results_sonnet5_run1/raw/ws_500.jsonl",            "youcom", None,         "2026-09-19"),
    "sonnet5:ws_cutoff:ext": ("Claude Sonnet 5", "ws_cutoff", "ext", ROOT / "results_extension_run2/raw/sonnet5_ws_cutoff.jsonl", "youcom", "2026-01-01", None),
    "sonnet5:ws:ext":    ("Claude Sonnet 5", "ws",        "ext",  ROOT / "results_extension_run2/raw/sonnet5_ws.jsonl",       "youcom", None,         "2026-09-19"),
    "sol:ws_cutoff":     ("GPT-5.6 Sol",     "ws_cutoff", "orig", ROOT / "results_sol_run1/raw/ws_cutoff_500.jsonl",         "youcom", "2026-02-01", None),
    "sol:ws":            ("GPT-5.6 Sol",     "ws",        "orig", ROOT / "results_sol_run1/raw/ws_500.jsonl",                "youcom", None,         "2026-09-20"),
    "llama33:ws_cutoff": ("LLaMA 3.3 70B",   "ws_cutoff", "orig", ROOT / "results_llama33_run1/raw/ws_cutoff_500.jsonl",     "youcom", "2023-12-01", None),
}
ARX = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})")
DOI = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+")


def load_events():
    ev = {}
    for p in (ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl", ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"):
        for l in open(p, encoding="utf-8"):
            if l.strip():
                r = json.loads(l); ev[r["id"]] = r
    return ev


def paper_key(row):
    link = row.get("paper_link") or ""
    m = ARX.search(link)
    if m: return ("arxiv", m.group(1))
    m = DOI.search(link)
    return ("doi", m.group(0).lower().rstrip("/.")) if m else (None, None)


def url_matches(kind, key, url):
    """arXiv: same identifier. DOI: full DOI in the URL, or the DOI suffix (e.g. s41586-024-07476-z)
    in the URL, which is how journal landing pages carry it (nature.com/articles/<suffix>)."""
    if not key: return False
    u = url.lower()
    if kind == "arxiv":
        m = ARX.search(u); return bool(m and m.group(1) == key)
    suf = key.split("/", 1)[1] if "/" in key else ""
    return (key in u) or (len(suf) >= 8 and suf in u)


def load_run(key):
    model, cond, ds, path, mech, cutoff, run_date = RUNS[key]
    sub = set(l.strip() for l in open(SUBSET) if l.strip()) if ds == "orig" else None
    rows = []
    for l in open(path, encoding="utf-8"):
        if not l.strip(): continue
        r = json.loads(l)
        if sub is not None and r["id"] not in sub: continue
        if mech == "youcom":
            if not r.get("web_search_urls"): continue
            rows.append(dict(run=key, id=r["id"], query=r.get("web_search_query"), urls=list(r["web_search_urls"])))
        else:
            per = {}
            for t in ("binary", "binary_perturbed", "mcq", "frq", "date"):
                u = r.get(f"{t}_web_search_urls"); q = r.get(f"{t}_web_search_queries")
                if u or q:
                    per[t] = dict(queries=q or [], urls=[x["url"] if isinstance(x, dict) else x for x in (u or [])])
            if per:
                rows.append(dict(run=key, id=r["id"], per_task=per, urls=sorted({u for t in per.values() for u in t["urls"]})))
    return rows
