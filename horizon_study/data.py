"""
data.py — item-level loader for the A4 horizon study.

Everything is read from stored, already-scored reports (eval.py schema). No
inference, no judge, no scoring code is touched. Date arithmetic and the
post-cutoff assertion live here.

Definitions
-----------
first_obs : first publicly observable month of the event.
            Original corpus: `publication_date`, which the build pipeline had
            already replaced by the earliest date found across Crossref /
            bioRxiv / medRxiv / Semantic Scholar / Europe PMC (verified: the
            cached lookup equals `publication_date` for all 3,642 DOI events);
            for arXiv-linked events the earlier of `publication_date` and the
            month encoded in the arXiv identifier.
            Extension: `first_date_found` where present, else `publication_date`.
doi_date  : the journal / listing date. Original: the journal `date_published`
            recovered from the build-stage CSVs (3,150 of 3,642 DOI events); for
            arXiv events the HF-listing month; else first_obs. Extension:
            `original_publication_date`.
horizon h : months(first_obs) - months(cutoff). POST-CUTOFF means h >= 1: the
            cutoff month itself (h = 0) is ambiguous at month resolution (Sol's
            cutoff is Feb 16) and is excluded from the primary analysis; a
            sensitivity run includes it.
"""
from __future__ import annotations
import csv, glob, json, math, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FR = ROOT / "run_evaluation" / "frq_results"
STUDY = ROOT / "horizon_study"
BENCH_ORIG = ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl"
BENCH_EXT = ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"
SUBSET500 = ROOT / "results_sonnet5_run1/subset500_ids.txt"

# cutoff: value used by the published tables; cutoff_source: what was verified on 2026-09-20;
# cutoff_alt: alternative for the sensitivity run where the source is ambiguous.
MODELS = {
    "gpt4o":      dict(name="GPT-4o",          cutoff="2023-10", cutoff_alt=None,
                       cutoff_source="developers.openai.com models/gpt-4o: 'Oct 01, 2023 knowledge cutoff' (verified)",
                       orig=FR / "gpt_4o_reeval.json", ext="gpt4o_base.json", ws=FR / "gpt-4o_web_search_with_cutoff_500.json"),
    "llama33":    dict(name="LLaMA 3.3 70B",   cutoff="2023-12", cutoff_alt=None,
                       cutoff_source="huggingface.co meta-llama/Llama-3.3-70B-Instruct model card: 'December 2023' (verified)",
                       orig=FR / "llama_3_3_full.json", ext="llama33_base.json", ws=ROOT / "results_llama33_run1/reports/ws_cutoff_500.json"),  # generated 2026-09-20
    "gptoss20b":  dict(name="GPT-OSS 20B",     cutoff="2024-06", cutoff_alt=None,
                       cutoff_source="developers.openai.com models/gpt-oss-20b: 'Jun 01, 2024 knowledge cutoff' (verified)",
                       orig=FR / "gpt_oss_20B_reeval.json", ext="gptoss20b_base.json", ws=None),
    "deepseek_r1": dict(name="DeepSeek R1",    cutoff="2024-07", cutoff_alt="2023-12",
                       cutoff_source="NOT VERIFIABLE: DeepSeek publishes no cutoff. 2024-07 follows the V3 system-prompt reports; the model self-reports Oct/Dec 2023. Sensitivity uses 2023-12.",
                       orig=FR / "deepseek_r1.json", ext=None, ws=FR / "deepseek_r1_500_web_cutoff.json"),
    "claude45":   dict(name="Claude S4.5",     cutoff="2025-01", cutoff_alt="2025-07",
                       cutoff_source="platform.claude.com models/sonnet-4-5: reliable knowledge cutoff Jan 2025 (used); training data cutoff Jul 2025 (sensitivity)",
                       orig=FR / "claude_sonnet.json", ext="sonnet45_base.json", ws=FR / "claude_500_with_cutoff.json"),
    "gpt54":      dict(name="GPT-5.4",         cutoff="2025-08", cutoff_alt=None,
                       cutoff_source="developers.openai.com models/gpt-5.4: 'Aug 31, 2025 knowledge cutoff' (verified)",
                       orig=FR / "gpt_5_4_eval.json", ext="gpt54_base.json", ws=FR / "gpt_5_4_500_web_cutoff.json"),
    "sonnet5":    dict(name="Claude Sonnet 5", cutoff="2026-01", cutoff_alt=None,
                       cutoff_source="platform.claude.com models/overview: reliable and training cutoff Jan 2026 (verified)",
                       orig=ROOT / "results_sonnet5_run1/reports/base_medium_run1.json", ext="sonnet5_base_run1.json",
                       ws=ROOT / "results_sonnet5_run1/reports/ws_cutoff_500.json", ws_ext="sonnet5_ws_cutoff.json"),
    "sol":        dict(name="GPT-5.6 Sol",     cutoff="2026-02", cutoff_alt=None,
                       cutoff_source="developers.openai.com models/gpt-5.6-sol: 'Feb 16, 2026 knowledge cutoff' (verified; mid-month, so h=0 is excluded)",
                       orig=ROOT / "results_sol_run1/reports/base_medium_run1.json", ext="sol_base.json",
                       ws=ROOT / "results_sol_run1/reports/ws_cutoff_500.json",  # re-run 2026-09-20 after the temperature fix in scripts/web_search.py; the original run had no retrieval context
                       ),
    "dsv4pro":    dict(name="DeepSeek-V4-Pro", cutoff="2026-04", cutoff_alt=None,
                       cutoff_source="NOT VERIFIABLE: no cutoff on the HF card; 2026-04 is inferred from the 2026-04-24 release. Original corpus is entirely pre-cutoff for it.",
                       orig=ROOT / "results_dsv4pro_run1/reports/base_run1.json", ext="deepseekv4pro_base.json", ws=None),
}
EXT_REPORTS = ROOT / "results_extension_run2/reports"
MODEL_ORDER = list(MODELS)
PRIMARY_BINS = [(1, 3), (4, 6), (7, 12), (13, 24), (25, 999)]
BINS_2M = [(k, k + 1) for k in range(1, 33, 2)]
BINS_6M = [(1, 6), (7, 12), (13, 18), (19, 24), (25, 30), (31, 999)]
TASKS = ["binary_merged", "mcq", "date"]


def months(ym) -> int | None:
    try:
        y, m = str(ym).strip().split("-")[:2]
        return int(y) * 12 + int(m)
    except Exception:
        return None


def bin_label(lo, hi):
    return f"{lo}-{hi}" if hi < 999 else f"{lo}+"


def assign_bin(h, bins):
    for lo, hi in bins:
        if lo <= h <= hi:
            return bin_label(lo, hi)
    return None


# ----------------------------------------------------------------------------- dates
_ARX = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{2})(\d{2})\.\d{4,5}")
_DOI = re.compile(r"10\.\d{4,9}/[^\s]+")


def _doimap() -> dict:
    """DOI -> journal date (YYYY-MM) from the build-stage CSVs."""
    csv.field_size_limit(10 ** 9)
    out = {}
    files = glob.glob(str(ROOT / "archive/scientific_findings/scientific_findings/*/*_with_dates.csv")) + \
            glob.glob(str(ROOT / "archive/scientific_findings/scientific_findings/*/sub_files/*first_date*.csv"))
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            m = _DOI.search((r.get("doi") or "").lower())
            if not m:
                continue
            jd = r.get("date_published_dont_use") or r.get("date_published") or r.get("date")
            if jd and months(jd[:7]) is not None:
                out.setdefault(m.group(0).rstrip("/"), jd[:7])
    return out


def load_events() -> pd.DataFrame:
    doimap = _doimap()
    rows = []
    for l in open(BENCH_ORIG, encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l); pub = r["publication_date"]; link = r.get("paper_link") or ""
        first, doi, kind = pub, pub, "other"
        m = _ARX.search(link)
        if m:
            kind = "arxiv"; am = f"20{m.group(1)}-{m.group(2)}"
            first = am if months(am) < months(pub) else pub; doi = pub
        else:
            m = _DOI.search(link)
            if m:
                kind = "doi"; jd = doimap.get(m.group(0).lower().rstrip("/"))
                doi = jd if (jd and months(jd) >= months(pub)) else pub
        rows.append(dict(id=r["id"], corpus="orig", first_obs=first, doi_date=doi, doi_known=(kind == "doi" and doi != pub) or kind == "arxiv",
                         link_kind=kind, area=r["main_area"], source=r["source"],
                         has_binary=bool(r.get("binary_question")), has_pert=bool(r.get("binary_question_perturbed")),
                         has_mcq=bool(r.get("mcq_question")), has_date=bool(r.get("date_prediction_prompt"))))
    for l in open(BENCH_EXT, encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l); pub = r["publication_date"]
        first = r.get("first_date_found") or pub; doi = r.get("original_publication_date") or pub
        rows.append(dict(id=r["id"], corpus="ext", first_obs=first, doi_date=doi, doi_known=bool(r.get("first_date_found")),
                         link_kind=("arxiv" if "arxiv" in (r.get("paper_link") or "") else "doi"), area=r["main_area"], source=r["source"],
                         has_binary=bool(r.get("binary_question")), has_pert=bool(r.get("binary_question_perturbed")),
                         has_mcq=bool(r.get("mcq_question")), has_date=bool(r.get("date_prediction_prompt")) and not re.fullmatch(r"\d{4}-\d{2}", str(r.get("date_prediction_prompt")))))
    ev = pd.DataFrame(rows)
    ev["first_m"] = ev.first_obs.map(months); ev["doi_m"] = ev.doi_date.map(months)
    assert ev.id.is_unique
    return ev


# ----------------------------------------------------------------------------- items
def _rows_from_report(path: Path, model: str, condition: str) -> list[dict]:
    rep = json.load(open(path, encoding="utf-8"))
    out = []
    for r in rep["results"]:
        t = r.get("tasks", {})
        for task in ("binary", "binary_perturbed", "mcq"):
            d = t.get(task)
            if d and not d.get("skipped") and not d.get("refused") and "correct" in d:
                conf = d.get("confidence")
                ans = str(d.get("parsed_answer", "")).lower()
                p_yes = None
                if task != "mcq" and conf is not None and ans in ("yes", "no"):
                    p_yes = float(conf) if ans == "yes" else 1 - float(conf)
                out.append(dict(model=model, condition=condition, id=r["id"], task=task, y=int(bool(d["correct"])),
                                conf=conf, p_yes=p_yes, pred_m=None))
        d = t.get("date")
        if d and not d.get("skipped") and not d.get("refused") and d.get("parsed_date"):
            pm = months(d["parsed_date"])
            if pm is not None:
                out.append(dict(model=model, condition=condition, id=r["id"], task="date", y=None, conf=d.get("confidence"),
                                p_yes=None, pred_m=pm, stored_score=d.get("score")))
    return out


def load_items(dataset: str, ev: pd.DataFrame, include_h0: bool = False, cutoffs: dict | None = None,
               date_field: str = "first_m") -> pd.DataFrame:
    """dataset in {'orig','ext','ws','merged'}; returns POST-CUTOFF items only (asserted)."""
    rows = []
    for m, cfg in MODELS.items():
        srcs = []
        if dataset in ("orig", "merged") and cfg["orig"] and Path(cfg["orig"]).exists():
            srcs.append((cfg["orig"], "base"))
        if dataset in ("ext", "merged") and cfg.get("ext") and (EXT_REPORTS / cfg["ext"]).exists():
            srcs.append((EXT_REPORTS / cfg["ext"], "base"))
        if dataset == "ws":
            if cfg.get("ws") and Path(cfg["ws"]).exists():
                srcs.append((cfg["ws"], "ws_cutoff"))
                srcs.append((cfg["orig"], "base"))   # paired base on the same subset
        for p, cond in srcs:
            rows += _rows_from_report(Path(p), m, cond)
    df = pd.DataFrame(rows)
    if dataset == "ws":
        sub = set(l.strip() for l in open(SUBSET500) if l.strip())
        df = df[df.id.isin(sub)]
    df = df.merge(ev, on="id", how="inner", validate="many_to_one")
    cut = {m: months((cutoffs or {}).get(m) or MODELS[m]["cutoff"]) for m in MODELS}
    df["cutoff_m"] = df.model.map(cut)
    df["h"] = df[date_field] - df.cutoff_m
    df["cal_m"] = df[date_field]
    lo = 0 if include_h0 else 1
    df = df[df.h >= lo].copy()
    # ---- the load-bearing assertion: nothing at or before the cutoff month enters
    assert (df.h >= lo).all() and (df[date_field] - df.cutoff_m >= lo).all(), "pre-cutoff items leaked into the analysis"
    if not include_h0:
        assert (df.h >= 1).all()
    # date task: errors relative to the SAME date field used for the horizon
    d = df.task == "date"
    df.loc[d, "signed_err"] = df.loc[d, "pred_m"] - df.loc[d, date_field]
    df.loc[d, "abs_err"] = df.loc[d, "signed_err"].abs()
    df.loc[d, "date_score"] = np.exp(-0.1 * df.loc[d, "abs_err"])
    df["task_group"] = df.task.replace({"binary": "binary_merged", "binary_perturbed": "binary_merged"})
    return df.reset_index(drop=True)


if __name__ == "__main__":
    ev = load_events()
    print("events:", ev.corpus.value_counts().to_dict())
    g = (ev.doi_m - ev.first_m)
    print("DOI - first_obs months, original:", g[ev.corpus == "orig"].value_counts().sort_index().to_dict())
    print("DOI - first_obs months, extension:", g[ev.corpus == "ext"].value_counts().sort_index().to_dict())
    for ds in ("orig", "ext", "ws", "merged"):
        df = load_items(ds, ev)
        n = df[df.condition == "base"].groupby(["model", "task_group"]).id.nunique().unstack(fill_value=0)
        print(f"\n== {ds}: post-cutoff events per model x task (base condition) ==")
        print(n.reindex(MODEL_ORDER).fillna(0).astype(int).to_string())
        if ds == "ws":
            n2 = df[df.condition == "ws_cutoff"].groupby(["model", "task_group"]).id.nunique().unstack(fill_value=0)
            print("-- ws_cutoff condition --"); print(n2.to_string())
        hs = df[df.condition == "base"].groupby("model").h.agg(["min", "max", "median"])
        print(hs.reindex(MODEL_ORDER).dropna().to_string())
