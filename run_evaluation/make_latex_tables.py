"""
make_latex_tables.py — Publication-quality LaTeX tables for the CUSP benchmark.

Tables produced
---------------
  table1_main_results.tex     Overall performance summary
  table2_binary_bias.tex      Binary response-bias analysis
  table3_date_stats.tex       Date prediction in-depth statistics
  table4_area_mcq.tex         MCQ accuracy by research area (heatmap)
  table5_area_date.tex        Date score by research area (heatmap)
  table6_pre_post_cutoff.tex  Performance before vs. after training cutoff
  table7_calibration.tex      Confidence calibration (ECE, overconfidence)
  tables_all.tex              Standalone compilable document

All tables use \\adjustbox{max width=\\textwidth} so they never overflow the
page regardless of font size or column count.

Usage
-----
  python make_latex_tables.py \\
      --results   model_results/ \\
      --benchmark benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \\
      [--output-dir tables/]

Requirements: numpy
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Model registry  (keep in sync with compare_models.py)
# ---------------------------------------------------------------------------

MODEL_REGISTRY: dict[str, dict] = {
    "claude_sonnet.json": {
        "name":   "Claude Sonnet 4.5",
        "short":  "Claude S4.5",
        "cutoff": "2025-01",
        "color":  "#0072B2",   # Okabe deep blue
        "marker": "o",
        "ls":     "-",
    },
    "gpt_4o_reeval.json": {
        "name":   "GPT-4o",
        "short":  "GPT-4o",
        "cutoff": "2023-10",
        "color":  "#D55E00",   # Okabe vermillion
        "marker": "s",
        "ls":     "--",
    },
    "gpt_5_4_eval.json": {
        "name":   "GPT-5.4",
        "short":  "GPT-5.4",
        "cutoff": "2025-08",
        "color":  "#009E73",   # Okabe teal green
        "marker": "^",
        "ls":     "-.",
    },
    "deepseek_r1.json": {
        "name":   "DeepSeek R1",
        "short":  "DeepSeek R1",
        "cutoff": "2024-07",
        "color":  "#CC79A7",   # Okabe rose pink
        "marker": "D",
        "ls":     ":",
    },
    "gpt_oss_20B_reeval.json": {
        "name":   "GPT-OSS 20B",
        "short":  "GPT-OSS 20B",
        "cutoff": "2024-06",
        "color":  "#E69F00",   # Okabe amber
        "marker": "v",
        "ls":     "-",
    },
    "llama_3_3_full.json": {
        "name":   "LLaMA 3.3 70B",
        "short":  "LLaMA 3.3",
        "cutoff": "2023-12",
        "color":  "#56B4E9",   # Okabe sky blue
        "marker": "P",
        "ls":     "--",
    },
}

AREA_ORDER = [
    "Biology", "Artificial Intelligence", "Medicine", "Neuroscience",
    "Materials Science", "Physics", "Environmental Science", "Chemistry", "Other",
]
AREA_SHORT = {
    "Artificial Intelligence": "AI",
    "Environmental Science":   r"Env.\ Sci.",
    "Materials Science":       r"Mat.\ Sci.",
    "Neuroscience":            "Neurosci.",
    "Biology": "Biology", "Medicine": "Medicine",
    "Physics": "Physics", "Chemistry": "Chemistry", "Other": "Other",
}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _dm(s: str) -> float | None:
    try:
        p = str(s).split("-")
        return (int(p[0]) - 2020) * 12 + int(p[1])
    except Exception:
        return None


def _sm(lst: list) -> float:
    return float(np.mean(lst)) if lst else float("nan")


def load_benchmark_meta(path: str) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rid = row.get("id")
                if rid:
                    meta[rid] = {
                        "main_area": row.get("main_area", "Unknown"),
                        "pub":       row.get("publication_date", ""),
                    }
            except json.JSONDecodeError:
                pass
    return meta


def load_model(filepath: str, cfg: dict, id_meta: dict) -> dict:
    with open(filepath, encoding="utf-8") as f:
        rep = json.load(f)
    tm = rep.get("task_metrics", {})

    bin_n = tm.get("binary",           {}).get("count",   0)
    bin_c = tm.get("binary",           {}).get("correct", 0)
    bp_n  = tm.get("binary_perturbed", {}).get("count",   0)
    bp_c  = tm.get("binary_perturbed", {}).get("correct", 0)
    merged_n = bin_n + bp_n

    cutoff_m = _dm(cfg["cutoff"])

    # Per-area accumulators
    area_mcq:    dict[str, list] = defaultdict(list)
    area_binary: dict[str, list] = defaultdict(list)
    area_date:   dict[str, list] = defaultdict(list)
    area_frq:         dict[str, list] = defaultdict(list)
    area_frq_align:   dict[str, list] = defaultdict(list)
    area_frq_spec:    dict[str, list] = defaultdict(list)
    area_frq_novelty: dict[str, list] = defaultdict(list)

    # Per-row date stats
    date_signed:  list[float] = []
    date_abs:     list[float] = []
    date_pred_m:  list[float] = []
    date_gt_m:    list[float] = []

    # Pre / post cutoff splits (keyed by 'pre' / 'post')
    split_binary: dict[str, list] = {"pre": [], "post": []}
    split_mcq:    dict[str, list] = {"pre": [], "post": []}
    split_date:   dict[str, list] = {"pre": [], "post": []}
    split_frq:    dict[str, list] = {"pre": [], "post": []}
    split_frq_align:  dict[str, list] = {"pre": [], "post": []}

    # Area × pre/post splits — nested: area -> bucket -> list
    def _abucket() -> dict:
        return {"pre": [], "post": []}
    area_split_binary: dict[str, dict] = defaultdict(_abucket)
    area_split_mcq:    dict[str, dict] = defaultdict(_abucket)
    area_split_date:   dict[str, dict] = defaultdict(_abucket)
    area_split_frq:    dict[str, dict] = defaultdict(_abucket)

    # Calibration: (confidence, outcome) pairs per task
    calib_binary: list[tuple[float, float]] = []   # (conf, correct ∈ {0,1})
    calib_mcq:    list[tuple[float, float]] = []
    calib_date:   list[tuple[float, float]] = []   # (conf, score ∈ [0,1])

    for row in rep.get("results", []):
        rid   = row.get("id", "")
        meta  = id_meta.get(rid, {})
        area  = meta.get("main_area", "Unknown")
        pub_m = _dm(meta.get("pub", ""))
        bucket = None
        if pub_m is not None and cutoff_m is not None:
            bucket = "pre" if pub_m < cutoff_m else "post"

        tasks = row.get("tasks", {})

        # Binary (merged) — area + split + calibration
        for key in ("binary", "binary_perturbed"):
            t = tasks.get(key)
            if t and not t.get("skipped"):
                v = int(bool(t.get("correct")))
                area_binary[area].append(v)
                if bucket:
                    split_binary[bucket].append(v)
                    area_split_binary[area][bucket].append(v)
                conf = t.get("confidence")
                if conf is not None:
                    calib_binary.append((float(conf), float(v)))

        # MCQ
        t = tasks.get("mcq")
        if t and not t.get("skipped"):
            v = int(bool(t.get("correct")))
            area_mcq[area].append(v)
            if bucket:
                split_mcq[bucket].append(v)
                area_split_mcq[area][bucket].append(v)
            conf = t.get("confidence")
            if conf is not None:
                calib_mcq.append((float(conf), float(v)))

        # Date
        t = tasks.get("date")
        if t and not t.get("skipped"):
            score = t.get("score")
            if score is not None:
                area_date[area].append(float(score))
                if bucket:
                    split_date[bucket].append(float(score))
                    area_split_date[area][bucket].append(float(score))
            conf = t.get("confidence")
            if conf is not None and score is not None:
                calib_date.append((float(conf), float(score)))
            pm = _dm(t.get("parsed_date"))
            gm = _dm(t.get("ground_truth"))
            if pm is not None and gm is not None:
                signed = float(pm - gm)
                date_signed.append(signed)
                date_abs.append(abs(signed))
                date_pred_m.append(float(pm))
                date_gt_m.append(float(gm))

        # FRQ — score + sub-dimensions per area and pre/post split
        t = tasks.get("frq")
        if t and not t.get("skipped") and t.get("score") is not None:
            s = float(t["score"])
            area_frq[area].append(s)
            if t.get("alignment") is not None:
                area_frq_align[area].append(float(t["alignment"]))
            if t.get("specificity") is not None:
                area_frq_spec[area].append(float(t["specificity"]))
            if t.get("novelty") is not None:
                area_frq_novelty[area].append(float(t["novelty"]))
            if bucket:
                split_frq[bucket].append(s)
                area_split_frq[area][bucket].append(s)
                if t.get("alignment") is not None:
                    split_frq_align[bucket].append(float(t["alignment"]))

    return {
        "name":   cfg["name"],
        "short":  cfg["short"],
        "cutoff": cfg["cutoff"],
        "cutoff_months": cutoff_m,
        # Summary from task_metrics
        "binary_acc":           tm.get("binary",           {}).get("accuracy",   float("nan")),
        "binary_conf":          tm.get("binary",           {}).get("mean_confidence", float("nan")),
        "binary_perturbed_acc": tm.get("binary_perturbed", {}).get("accuracy",   float("nan")),
        "merged_binary_acc":    (bin_c + bp_c) / merged_n if merged_n > 0 else float("nan"),
        "binary_n":             bin_n,
        "mcq_acc":              tm.get("mcq",  {}).get("accuracy",              float("nan")),
        "mcq_conf":             tm.get("mcq",  {}).get("mean_confidence",       float("nan")),
        "mcq_n":                tm.get("mcq",  {}).get("count",                 0),
        "date_score":           tm.get("date", {}).get("mean_score",            float("nan")),
        "date_n":               tm.get("date", {}).get("count",                 0),
        "date_exact_rate":      tm.get("date", {}).get("exact_match_rate",      float("nan")),
        "date_median_dist":     tm.get("date", {}).get("median_month_distance", float("nan")),
        "date_conf":            tm.get("date", {}).get("mean_confidence",       float("nan")),
        # Per-row date
        "date_signed":  date_signed,
        "date_abs":     date_abs,
        "date_pred_m":  date_pred_m,
        "date_gt_m":    date_gt_m,
        # Per-area
        "area_mcq":    dict(area_mcq),
        "area_binary": dict(area_binary),
        "area_date":   dict(area_date),
        # Pre/post cutoff splits
        "split_binary": dict(split_binary),
        "split_mcq":    dict(split_mcq),
        "split_date":   dict(split_date),
        "split_frq":       dict(split_frq),
        "split_frq_align": dict(split_frq_align),
        "area_split_binary": {a: dict(v) for a, v in area_split_binary.items()},
        "area_split_mcq":    {a: dict(v) for a, v in area_split_mcq.items()},
        "area_split_date":   {a: dict(v) for a, v in area_split_date.items()},
        "area_split_frq":    {a: dict(v) for a, v in area_split_frq.items()},
        # FRQ summary from task_metrics
        "frq_mean":      tm.get("frq", {}).get("mean_score",  float("nan")),
        "frq_n":         tm.get("frq", {}).get("count",       0),
        "frq_pass_rate": tm.get("frq", {}).get("pass_rate",   float("nan")),
        # FRQ sub-dimension means (computed from per-row accumulation)
        "frq_align_mean":  _sm([v for lst in area_frq_align.values()   for v in lst]),
        "frq_spec_mean":   _sm([v for lst in area_frq_spec.values()    for v in lst]),
        "frq_novelty_mean":_sm([v for lst in area_frq_novelty.values() for v in lst]),
        # FRQ per-area dicts
        "area_frq":          dict(area_frq),
        "area_frq_align":    dict(area_frq_align),
        "area_frq_spec":     dict(area_frq_spec),
        "area_frq_novelty":  dict(area_frq_novelty),
        # Reasoning metrics
        "leakage_fail_rate": rep.get("reasoning_metrics", {}).get("leakage", {}).get("fail_rate", float("nan")),
        "leakage_pass_rate": rep.get("reasoning_metrics", {}).get("leakage", {}).get("pass_rate", float("nan")),
        # Calibration pairs
        "calib_binary": calib_binary,
        "calib_mcq":    calib_mcq,
        "calib_date":   calib_date,
    }


def _composite(m: dict) -> float:
    vals = [v for v in (m["merged_binary_acc"], m["mcq_acc"], m["date_score"])
            if not np.isnan(v)]
    frq = m.get("frq_mean", float("nan"))
    if not np.isnan(frq):
        vals.append(frq / 10.0)  # normalise FRQ 0–10 → 0–1
    return sum(vals) / len(vals) if vals else 0.0


def load_all_models(results_dir: str, benchmark_path: str | None) -> list[dict]:
    id_meta: dict[str, dict] = {}
    if benchmark_path:
        print(f"  Loading benchmark: {benchmark_path}")
        id_meta = load_benchmark_meta(benchmark_path)
        print(f"  {len(id_meta)} rows indexed")

    models: list[dict] = []
    for fn, cfg in MODEL_REGISTRY.items():
        fp = Path(results_dir) / fn
        if not fp.exists():
            print(f"  SKIP {fn}")
            continue
        print(f"  Loading {cfg['name']} ...")
        models.append(load_model(str(fp), cfg, id_meta))

    models.sort(key=_composite, reverse=True)   # best first
    return models


# ---------------------------------------------------------------------------
# ECE
# ---------------------------------------------------------------------------

def compute_ece(pairs: list[tuple[float, float]], n_bins: int = 10) -> float:
    """Expected Calibration Error over n_bins equal-width confidence bins."""
    if len(pairs) < 20:
        return float("nan")
    confs = np.array([p[0] for p in pairs])
    outs  = np.array([p[1] for p in pairs])
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece   = 0.0
    n     = len(confs)
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        mask = (confs >= lo) & (confs <= hi if i == n_bins - 1 else confs < hi)
        if mask.sum() == 0:
            continue
        ece += mask.sum() / n * abs(float(outs[mask].mean()) - float(confs[mask].mean()))
    return float(ece)


# ---------------------------------------------------------------------------
# LaTeX formatting helpers
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    for old, new in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                     ("#", r"\#"), ("_", r"\_")]:
        s = s.replace(old, new)
    return s


def _fmt(v: float, dp: int = 3, pct: bool = False,
         signed: bool = False, na: str = r"{\textemdash}") -> str:
    if isinstance(v, float) and np.isnan(v):
        return na
    if pct:
        return f"{v * 100:.1f}"
    if signed:
        return f"{v:+.1f}"
    return f"{v:.{dp}f}"


def _bold(s: str) -> str:
    return f"\\textbf{{{s}}}"


def _best_idx(vals: list[float], mode: str = "max") -> int:
    valid = [(i, v) for i, v in enumerate(vals) if not np.isnan(v)]
    if not valid:
        return -1
    if mode == "max":
        return max(valid, key=lambda x: x[1])[0]
    if mode == "min":
        return min(valid, key=lambda x: x[1])[0]
    return min(valid, key=lambda x: abs(x[1]))[0]   # "zero"


def _apply_best(strings: list[str], vals: list[float],
                mode: str = "max") -> list[str]:
    bi  = _best_idx(vals, mode)
    out = list(strings)
    if bi >= 0:
        out[bi] = _bold(out[bi])
    return out


def _cutoff_fmt(s: str) -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    try:
        y, m = s.split("-")
        return f"{months[int(m) - 1]} {y}"
    except Exception:
        return s


def _join_row(cells: list[str], indent: int = 4) -> str:
    return " " * indent + " & ".join(cells) + r" \\"


# Cell colour helpers
def _cell_mcq(v: float) -> str:
    if np.isnan(v): return ""
    if v < 0.40:    return r"\cellcolor{cellbad}"
    if v < 0.50:    return r"\cellcolor{cellworse}"
    if v < 0.60:    return r"\cellcolor{cellneutral}"
    if v < 0.70:    return r"\cellcolor{cellgood}"
    if v < 0.80:    return r"\cellcolor{cellbetter}"
    return                  r"\cellcolor{cellbest}"


def _cell_date(v: float, lo: float = 0.15, hi: float = 0.55) -> str:
    if np.isnan(v): return ""
    norm = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    if norm < 0.20: return r"\cellcolor{cellbad}"
    if norm < 0.35: return r"\cellcolor{cellworse}"
    if norm < 0.50: return r"\cellcolor{cellneutral}"
    if norm < 0.65: return r"\cellcolor{cellgood}"
    if norm < 0.80: return r"\cellcolor{cellbetter}"
    return                  r"\cellcolor{cellbest}"


def _cell_ece(v: float) -> str:
    if np.isnan(v): return ""
    if v < 0.05:    return r"\cellcolor{cellbest}"
    if v < 0.10:    return r"\cellcolor{cellgood}"
    if v < 0.15:    return r"\cellcolor{cellneutral}"
    if v < 0.25:    return r"\cellcolor{cellworse}"
    return                  r"\cellcolor{cellbad}"


def _cell_binary(v: float) -> str:
    """Colour for merged binary accuracy (chance = 0.50)."""
    if np.isnan(v): return ""
    if v < 0.44:    return r"\cellcolor{cellbad}"
    if v < 0.48:    return r"\cellcolor{cellworse}"
    if v < 0.52:    return r"\cellcolor{cellneutral}"
    if v < 0.56:    return r"\cellcolor{cellgood}"
    if v < 0.60:    return r"\cellcolor{cellbetter}"
    return                  r"\cellcolor{cellbest}"


def _cell_overconf(v: float) -> str:
    """Colour overconfidence (conf − acc): near 0 = good."""
    if np.isnan(v): return ""
    if abs(v) < 0.05:  return r"\cellcolor{cellbest}"
    if abs(v) < 0.15:  return r"\cellcolor{cellgood}"
    if abs(v) < 0.30:  return r"\cellcolor{cellneutral}"
    if abs(v) < 0.50:  return r"\cellcolor{cellworse}"
    return                     r"\cellcolor{cellbad}"


def _adjustbox_open() -> str:
    return r"\begin{adjustbox}{max width=\textwidth}"


def _adjustbox_close() -> str:
    return r"\end{adjustbox}"


def _minipage_note(text: str) -> str:
    return (
        r"\begin{minipage}{\textwidth}" + "\n"
        r"\smallskip\footnotesize\textit{" + text + "}\n"
        r"\end{minipage}"
    )


# ---------------------------------------------------------------------------
# Table 1 — Main performance summary
# ---------------------------------------------------------------------------

def table_main_results(models: list[dict]) -> str:
    sorted_m = sorted(models, key=lambda m: m["mcq_acc"], reverse=True)

    binary_v = [m["merged_binary_acc"] for m in sorted_m]
    mcq_v    = [m["mcq_acc"]           for m in sorted_m]
    date_v   = [m["date_score"]        for m in sorted_m]
    frq_v    = [m["frq_mean"]          for m in sorted_m]
    frq_pass = [m["frq_pass_rate"]     for m in sorted_m]

    s_bin   = _apply_best([_fmt(v)           for v in binary_v], binary_v, "max")
    s_mcq   = _apply_best([_fmt(v)           for v in mcq_v],    mcq_v,    "max")
    s_date  = _apply_best([_fmt(v)           for v in date_v],   date_v,   "max")
    s_frq   = _apply_best([_fmt(v, dp=2)     for v in frq_v],    frq_v,    "max")
    s_fpass = _apply_best([_fmt(v, pct=True) for v in frq_pass], frq_pass, "max")

    data_rows = [
        _join_row([_esc(m["short"]), _cutoff_fmt(m["cutoff"]),
                   s_bin[i], s_mcq[i], s_date[i],
                   s_frq[i], s_fpass[i]])
        for i, m in enumerate(sorted_m)
    ]

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Overall benchmark performance on \CUSP\ ($n=4{,}760$ instances). "
        r"\textbf{Binary}: merged accuracy on original and negation-flipped variants, "
        r"correcting for directional response bias (chance\,=\,0.50). "
        r"\textbf{MCQ}: 4-choice accuracy (chance\,=\,0.25). "
        r"\textbf{Date}: exponential-decay score $e^{-0.1|\Delta t|}$ (1.0\,=\,exact month). "
        r"\textbf{FRQ score}: LLM rubric score (0--10); "
        r"\textbf{FRQ pass\,\%}: fraction scoring $\geq\!5$. "
        r"Models sorted by MCQ accuracy. \textbf{Bold}: best per column.}",
        r"\label{tab:main_results}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll rrr rr@{}}",
        r"\toprule",
        r" & & \multicolumn{3}{c}{Closed-form tasks\,$\uparrow$}"
        r" & \multicolumn{2}{c}{Open-ended (FRQ)\,$\uparrow$} \\",
        r"\cmidrule(lr){3-5}\cmidrule(lr){6-7}",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}",
                   r"\textbf{Binary}$^a$",
                   r"\textbf{MCQ}$^b$",
                   r"\textbf{Date}$^c$",
                   r"\textbf{FRQ score}",
                   r"\textbf{FRQ pass\,\%}"]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"$^a$~Merged binary = $\tfrac{1}{2}$(\,binary acc.\ + perturbed acc.\,); "
            r"chance\,=\,0.50. \quad "
            r"$^b$~MCQ is 4-choice; chance\,=\,0.25. \quad "
            r"$^c$~Date: exponential-decay score; detail in Table~\ref{tab:date_stats}."
        ),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 2 — Binary response-bias analysis
# ---------------------------------------------------------------------------

def table_binary_bias(models: list[dict]) -> str:
    sorted_m = sorted(models,
                      key=lambda m: m["binary_acc"] - m["binary_perturbed_acc"])

    def _tendency(m: dict) -> str:
        bias = m["binary_acc"] - m["binary_perturbed_acc"]
        if abs(bias) < 0.10:  return "Balanced"
        if bias >  0.60:      return r'Strong ``Yes'' bias'
        if bias >  0.10:      return r'``Yes'' bias'
        if bias < -0.60:      return r'Strong ``No'' bias'
        return                        r'``No'' bias'

    bin_v    = [m["binary_acc"]           for m in sorted_m]
    bp_v     = [m["binary_perturbed_acc"] for m in sorted_m]
    bias_v   = [b - p for b, p in zip(bin_v, bp_v)]
    merged_v = [m["merged_binary_acc"]    for m in sorted_m]

    s_merged = _apply_best([_fmt(v) for v in merged_v], merged_v, "max")

    data_rows = [
        _join_row([_esc(m["short"]), _cutoff_fmt(m["cutoff"]),
                   _fmt(bin_v[i]), _fmt(bp_v[i]),
                   _fmt(bias_v[i], signed=True), s_merged[i],
                   _tendency(m)])
        for i, m in enumerate(sorted_m)
    ]

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Binary response-bias analysis. "
        r"\textbf{Bias index}\,=\,binary acc.\,$-$\,perturbed acc.; "
        r"$+1$\,=\,always ``Yes'', $-1$\,=\,always ``No'', $0$\,=\,unbiased. "
        r"\textbf{Merged}: bias-corrected forecasting accuracy "
        r"(chance\,=\,0.50). "
        r"Models sorted from most No-biased to most Yes-biased. "
        r"\textbf{Bold}: highest merged accuracy.}",
        r"\label{tab:binary_bias}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll rrrrl@{}}",
        r"\toprule",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}",
                   r"\textbf{Binary acc.}", r"\textbf{Perturbed acc.}",
                   r"\textbf{Bias index}", r"\textbf{Merged\,$\uparrow$}",
                   r"\textbf{Response tendency}"]),
        r"\midrule",
        *data_rows,
        r"\addlinespace[0.5em]",
        r"    \textit{Chance (random)} & & 0.500 & 0.500 & 0.000 & 0.500 & --- \\",
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 3 — Date prediction in-depth
# ---------------------------------------------------------------------------

def table_date_stats(models: list[dict]) -> str:
    def w12(m):
        errs = m["date_abs"]
        return float(np.mean(np.array(errs) <= 12)) if errs else 0.0

    sorted_m = sorted(models, key=w12, reverse=True)

    def _mean_pred(m: dict) -> str:
        if not m["date_pred_m"]: return r"{\textemdash}"
        mm  = float(np.mean(m["date_pred_m"]))
        yr  = 2020 + int(mm // 12)
        mo  = int(mm % 12) + 1
        return f"{yr}-{mo:02d}"

    def _thr(m: dict, t: float) -> str:
        errs = m["date_abs"]
        return f"{np.mean(np.array(errs) <= t) * 100:.1f}" if errs else r"{\textemdash}"

    all_gt  = [v for m in sorted_m for v in m["date_gt_m"]]
    gt_label = ""
    if all_gt:
        gm = float(np.mean(all_gt))
        gt_label = f"{2020 + int(gm // 12)}-{int(gm % 12) + 1:02d}"

    w12_v   = [w12(m)          for m in sorted_m]
    score_v = [m["date_score"] for m in sorted_m]
    s_w12   = _apply_best([f"{v*100:.1f}" for v in w12_v], w12_v, "max")
    s_score = _apply_best([_fmt(v) for v in score_v],      score_v, "max")

    data_rows = []
    for i, m in enumerate(sorted_m):
        signed = m["date_signed"]
        cells = [
            _esc(m["short"]),
            _cutoff_fmt(m["cutoff"]),
            str(m["date_n"]),
            _mean_pred(m),
            _fmt(float(np.mean(signed)),   signed=True) if signed else r"{\textemdash}",
            _fmt(float(np.median(signed)), signed=True) if signed else r"{\textemdash}",
            _thr(m, 3),
            _thr(m, 6),
            s_w12[i],
            _thr(m, 24),
            s_score[i],
        ]
        data_rows.append(_join_row(cells))

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Date prediction performance in depth. "
        r"\textbf{Mean pred.}: mean predicted publication date "
        r"(ground-truth mean: " + gt_label + r"). "
        r"\textbf{Signed error}: predicted\,$-$\,actual (months); "
        r"positive\,=\,model predicts \emph{later} than truth. "
        r"\textbf{Within\,$N$\,months}: fraction of predictions within $N$ calendar "
        r"months of the ground truth. "
        r"All models exhibit positive signed error, "
        r"i.e.\ they systematically over-estimate how recently papers are published. "
        r"\textbf{Bold}: best per column.}",
        r"\label{tab:date_stats}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll r r r r r r r r r@{}}",
        r"\toprule",
        r" & & & & \multicolumn{2}{c}{Signed error (mo)}"
        r" & \multicolumn{4}{c}{Within $N$ months (\%)\,$\uparrow$} & \\",
        r"\cmidrule(lr){5-6}\cmidrule(lr){7-10}",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}", r"$n$",
                   r"\makecell[r]{\textbf{Mean}\\\textbf{pred.}}",
                   r"\textbf{Mean}", r"\textbf{Median}",
                   r"$\leq 3$", r"$\leq 6$", r"$\leq 12$", r"$\leq 24$",
                   r"\textbf{Score\,$\uparrow$}"]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 4 — MCQ accuracy by research area
# ---------------------------------------------------------------------------

def table_area_mcq(models: list[dict]) -> str:
    n_m = len(models)
    mat: dict[str, list[float]] = {
        area: [_sm(m["area_mcq"].get(area, [])) for m in models]
        for area in AREA_ORDER
    }
    area_n = {area: max((len(m["area_mcq"].get(area, [])) for m in models), default=0)
              for area in AREA_ORDER}
    row_means = {a: _sm([v for v in mat[a] if not np.isnan(v)]) for a in AREA_ORDER}

    hdrs = [r"\makecell[r]{\textbf{" + _esc(m["short"]) + r"}}" for m in models]
    data_rows = []
    for area in AREA_ORDER:
        vals   = mat[area]
        best_i = _best_idx(vals, "max")
        cells  = [AREA_SHORT.get(area, area), str(area_n[area])]
        for j, v in enumerate(vals):
            s = (_bold(_fmt(v)) if j == best_i else _fmt(v))
            cells.append(_cell_mcq(v) + s)
        rm = row_means[area]
        cells.append(_cell_mcq(rm) + _fmt(rm))
        data_rows.append(_join_row(cells))

    col_vals = [_sm([mat[a][j] for a in AREA_ORDER if not np.isnan(mat[a][j])])
                for j in range(n_m)]
    best_col = _best_idx(col_vals, "max")
    bottom   = ([r"\textit{Mean}", ""]
                + [(_bold(_fmt(v)) if j == best_col else _fmt(v)) for j, v in enumerate(col_vals)]
                + [_fmt(_sm([v for a in AREA_ORDER for v in mat[a] if not np.isnan(v)]))])

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{MCQ accuracy (\%) by research area. "
        r"Chance level = 0.25 (4-choice). "
        r"$n$: MCQ questions per area. "
        r"\textbf{Bold}: best model per row. "
        r"Colour scale: "
        r"\colorbox{cellbad}{\strut\,$<$0.18\,} "
        r"\colorbox{cellworse}{\strut\,0.18--0.23\,} "
        r"\colorbox{cellneutral}{\strut\,0.23--0.25\,} "
        r"(white: 0.25--0.29) "
        r"\colorbox{cellgood}{\strut\,0.29--0.33\,} "
        r"\colorbox{cellbetter}{\strut\,0.33--0.38\,} "
        r"\colorbox{cellbest}{\strut\,$>$0.38\,}.}",
        r"\label{tab:area_mcq}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.20}",
        r"\begin{tabular}{@{}lr " + "r" * n_m + r" r@{}}",
        r"\toprule",
        _join_row([r"\textbf{Research area}", r"$n$"] + hdrs + [r"\textbf{Mean}"]),
        r"\midrule",
        *data_rows,
        r"\midrule",
        _join_row(bottom),
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 5 — Date score by research area
# ---------------------------------------------------------------------------

def table_area_date(models: list[dict]) -> str:
    n_m = len(models)
    mat: dict[str, list[float]] = {
        area: [_sm(m["area_date"].get(area, [])) for m in models]
        for area in AREA_ORDER
    }
    area_n = {area: max((len(m["area_date"].get(area, [])) for m in models), default=0)
              for area in AREA_ORDER}
    all_finite = [v for a in AREA_ORDER for v in mat[a] if not np.isnan(v)]
    lo = float(np.percentile(all_finite, 5))  if all_finite else 0.15
    hi = float(np.percentile(all_finite, 95)) if all_finite else 0.55
    row_means  = {a: _sm([v for v in mat[a] if not np.isnan(v)]) for a in AREA_ORDER}

    hdrs = [r"\makecell[r]{\textbf{" + _esc(m["short"]) + r"}}" for m in models]
    data_rows = []
    for area in AREA_ORDER:
        vals   = mat[area]
        best_i = _best_idx(vals, "max")
        cells  = [AREA_SHORT.get(area, area), str(area_n[area])]
        for j, v in enumerate(vals):
            s = (_bold(_fmt(v)) if j == best_i else _fmt(v))
            cells.append(_cell_date(v, lo, hi) + s)
        rm = row_means[area]
        cells.append(_cell_date(rm, lo, hi) + _fmt(rm))
        data_rows.append(_join_row(cells))

    col_vals = [_sm([mat[a][j] for a in AREA_ORDER if not np.isnan(mat[a][j])])
                for j in range(n_m)]
    best_col = _best_idx(col_vals, "max")
    bottom   = ([r"\textit{Mean}", ""]
                + [(_bold(_fmt(v)) if j == best_col else _fmt(v)) for j, v in enumerate(col_vals)]
                + [_fmt(_sm(all_finite))])

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Date prediction score by research area. "
        r"Score uses exponential decay (1.0\,=\,exact month). "
        r"$n$: date-prediction questions per area. "
        r"\textbf{Bold}: best model per row. "
        r"Colours reflect the observed score range across this table "
        r"(5th--95th percentile).}",
        r"\label{tab:area_date}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.20}",
        r"\begin{tabular}{@{}lr " + "r" * n_m + r" r@{}}",
        r"\toprule",
        _join_row([r"\textbf{Research area}", r"$n$"] + hdrs + [r"\textbf{Mean}"]),
        r"\midrule",
        *data_rows,
        r"\midrule",
        _join_row(bottom),
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 5b — Binary merged accuracy by research area
# ---------------------------------------------------------------------------

def table_area_binary(models: list[dict]) -> str:
    n_m = len(models)
    mat: dict[str, list[float]] = {
        area: [_sm(m["area_binary"].get(area, [])) for m in models]
        for area in AREA_ORDER
    }
    area_n = {area: max((len(m["area_binary"].get(area, [])) for m in models), default=0)
              for area in AREA_ORDER}
    row_means  = {a: _sm([v for v in mat[a] if not np.isnan(v)]) for a in AREA_ORDER}
    all_finite = [v for a in AREA_ORDER for v in mat[a] if not np.isnan(v)]

    hdrs = [r"\makecell[r]{\textbf{" + _esc(m["short"]) + r"}}" for m in models]
    data_rows = []
    for area in AREA_ORDER:
        vals   = mat[area]
        best_i = _best_idx(vals, "max")
        cells  = [AREA_SHORT.get(area, area), str(area_n[area])]
        for j, v in enumerate(vals):
            s = (_bold(_fmt(v)) if j == best_i else _fmt(v))
            cells.append(_cell_binary(v) + s)
        rm = row_means[area]
        cells.append(_cell_binary(rm) + _fmt(rm))
        data_rows.append(_join_row(cells))

    col_vals = [_sm([mat[a][j] for a in AREA_ORDER if not np.isnan(mat[a][j])])
                for j in range(n_m)]
    best_col = _best_idx(col_vals, "max")
    bottom   = ([r"\textit{Mean}", ""]
                + [(_bold(_fmt(v)) if j == best_col else _fmt(v)) for j, v in enumerate(col_vals)]
                + [_fmt(_sm(all_finite))])

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Binary merged accuracy by research area. "
        r"Binary merged\,=\,$\tfrac{1}{2}$(original acc.\,+\,perturbed acc.), "
        r"correcting for directional response bias; chance\,=\,0.50. "
        r"$n$: total binary question pairs (original\,+\,perturbed) per area. "
        r"\textbf{Bold}: best model per row. "
        r"Colour scale centred at chance (0.50): "
        r"\colorbox{cellbad}{\strut\,$<$0.44\,} "
        r"\colorbox{cellworse}{\strut\,0.44--0.48\,} "
        r"\colorbox{cellneutral}{\strut\,0.48--0.52\,} "
        r"\colorbox{cellgood}{\strut\,0.52--0.56\,} "
        r"\colorbox{cellbetter}{\strut\,0.56--0.60\,} "
        r"\colorbox{cellbest}{\strut\,$>$0.60\,}.}",
        r"\label{tab:area_binary}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.20}",
        r"\begin{tabular}{@{}lr " + "r" * n_m + r" r@{}}",
        r"\toprule",
        _join_row([r"\textbf{Research area}", r"$n$"] + hdrs + [r"\textbf{Mean}"]),
        r"\midrule",
        *data_rows,
        r"\midrule",
        _join_row(bottom),
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 6 — Pre-cutoff vs. post-cutoff performance
# ---------------------------------------------------------------------------

def table_pre_post_cutoff(models: list[dict]) -> str:
    """Compare all four tasks before vs. after each model's training cutoff."""

    def _arrow(pre: list, post: list, dp: int = 3) -> str:
        """Format as 'pre → post' with colour on the cell based on direction of change."""
        if not pre and not post:
            return r"{\textemdash}"
        pre_s  = _fmt(_sm(pre),  dp=dp) if pre  else r"{---}"
        post_s = _fmt(_sm(post), dp=dp) if post else r"{---}"
        if pre and post:
            d = _sm(post) - _sm(pre)
            if d > 0.05:    colour = r"\cellcolor{cellgood}"
            elif d < -0.10: colour = r"\cellcolor{cellbad}"
            elif d < -0.03: colour = r"\cellcolor{cellworse}"
            else:            colour = ""
        else:
            colour = ""
        return colour + pre_s + r"\,$\to$\," + post_s

    data_rows = []
    for m in models:
        cells = [
            _esc(m["short"]),
            _cutoff_fmt(m["cutoff"]),
            str(len(m["split_binary"]["pre"])) if m["split_binary"]["pre"] else r"{\textemdash}",
            _arrow(m["split_binary"]["pre"], m["split_binary"]["post"]),
            _arrow(m["split_mcq"]["pre"],    m["split_mcq"]["post"]),
            _arrow(m["split_frq"]["pre"],    m["split_frq"]["post"],  dp=2),
            _arrow(m["split_date"]["pre"],   m["split_date"]["post"]),
        ]
        data_rows.append(_join_row(cells))

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Performance on instances published \emph{before} "
        r"vs.\ \emph{after} each model's training cutoff (pre\,$\to$\,post). "
        r"Models with cutoff $\leq$ Dec 2023 (GPT-4o, LLaMA\,3.3) have no "
        r"pre-cutoff instances and show ``---\,$\to$\,post''. "
        r"Cell colour: \colorbox{cellgood}{\strut green}\,$>+0.05$ improvement; "
        r"\colorbox{cellworse}{\strut orange}\,$<-0.03$ degradation; "
        r"\colorbox{cellbad}{\strut red}\,$<-0.10$ strong degradation. "
        r"Binary/MCQ: accuracy (0--1); FRQ: rubric score (0--10); "
        r"Date: exponential-decay score.}",
        r"\label{tab:pre_post_cutoff}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll r cccc@{}}",
        r"\toprule",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}", r"$n_{\text{pre}}$",
                   r"\textbf{Binary} (pre\,$\to$\,post)",
                   r"\textbf{MCQ} (pre\,$\to$\,post)",
                   r"\textbf{FRQ} (pre\,$\to$\,post)",
                   r"\textbf{Date} (pre\,$\to$\,post)"]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"$n_{\text{pre}}$: number of binary-task instances in the pre-cutoff partition. "
            r"Benchmark papers span Jan 2024--Mar 2026; models with an earlier cutoff "
            r"contribute only post-cutoff instances. "
            r"FRQ sub-dimension breakdown in Table~\ref{tab:frq_subdims}."
        ),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table 7 — Confidence calibration
# ---------------------------------------------------------------------------

def table_calibration(models: list[dict]) -> str:
    """Per-model, per-task calibration: mean confidence, accuracy, overconfidence, ECE."""

    tasks_def = [
        ("Binary",  "calib_binary", "calib_binary", "binary_conf",  "merged_binary_acc", "Acc.",  0.50),
        ("MCQ",     "calib_mcq",    "calib_mcq",    "mcq_conf",     "mcq_acc",           "Acc.",  0.25),
        ("Date",    "calib_date",   "calib_date",   "date_conf",    "date_score",         "Score", None),
    ]

    header_task = r" & ".join(
        r"\multicolumn{4}{c}{\textbf{" + task + r"}}"
        for task, *_ in tasks_def
    )
    header_sub  = r" & ".join(
        r"\textbf{Conf.} & \textbf{" + lbl + r"} & \textbf{Over-conf.} & \textbf{ECE}"
        for _, _k, _ck, _conf_k, _acc_k, lbl, _ in tasks_def
    )
    n_task_cols = 4 * len(tasks_def)

    data_rows = []
    for m in models:
        cells = [_esc(m["short"])]
        for _, key, calib_key, conf_key, acc_key, _, chance in tasks_def:
            pairs   = m[calib_key]
            conf_v  = m[conf_key]
            acc_v   = m[acc_key]
            ece_v   = compute_ece(pairs)
            overconf= (conf_v - acc_v) if not (np.isnan(conf_v) or np.isnan(acc_v)) else float("nan")

            s_conf  = _fmt(conf_v)
            s_acc   = _fmt(acc_v)
            s_over  = _cell_overconf(overconf) + _fmt(overconf, signed=True)
            s_ece   = _cell_ece(ece_v)         + _fmt(ece_v)
            cells  += [s_conf, s_acc, s_over, s_ece]
        data_rows.append(_join_row(cells))

    col_spec = r"@{}l " + " rrrr" * len(tasks_def) + r"@{}"
    cmidrules = r" ".join(
        r"\cmidrule(lr){" + str(2 + 4 * i) + r"-" + str(5 + 4 * i) + r"}"
        for i in range(len(tasks_def))
    )

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Confidence calibration across tasks. "
        r"\textbf{Conf.}: mean self-reported confidence (0--1). "
        r"\textbf{Acc.}/\textbf{Score}: mean accuracy or date score. "
        r"\textbf{Over-conf.}: confidence\,$-$\,accuracy; "
        r"positive\,=\,overconfident, 0\,=\,perfectly calibrated. "
        r"\textbf{ECE}: Expected Calibration Error (10 bins); "
        r"lower is better. "
        r"All models are severely overconfident on MCQ and date tasks. "
        r"Cell colours for ECE: "
        r"\colorbox{cellbest}{\strut\,$<$0.05\,} "
        r"\colorbox{cellgood}{\strut\,0.05--0.10\,} "
        r"\colorbox{cellneutral}{\strut\,0.10--0.15\,} "
        r"\colorbox{cellworse}{\strut\,0.15--0.25\,} "
        r"\colorbox{cellbad}{\strut\,$>$0.25\,}. "
        r"Same scale for overconfidence magnitude.}",
        r"\label{tab:calibration}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{" + col_spec + r"}",
        r"\toprule",
        r"    \textbf{Model} & " + header_task + r" \\",
        cmidrules,
        r"    & " + header_sub + r" \\",
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"ECE computed over 10 equal-width bins. "
            r"Overconfidence\,=\,mean confidence\,$-$\,mean accuracy/score."
        ),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Table — Pre/post cutoff by research area (all tasks)
# ---------------------------------------------------------------------------

def table_area_pre_post(models: list[dict]) -> str:
    """Pre- vs. post-cutoff performance for every task, broken down by research area.

    Delta values are computed as the mean of per-model (post − pre) deltas,
    restricted to models that have instances in both partitions for that area.
    Pre/Post columns show the mean of per-model means for the respective partition.
    This avoids the model-selection bias that arises from pooling raw values across
    models with different cutoffs (weaker models may appear only in the post pool).
    """
    areas = [a for a in AREA_ORDER
             if any(a in m.get("area_frq", {}) or a in m.get("area_mcq", {})
                    for m in models)]

    def _within_model_stats(key: str, area: str, dp: int = 3):
        """Return (pre_display, post_display, delta_display) using within-model averaging.

        All three values are derived from the SAME restricted set of models —
        only those with instances in BOTH partitions for this area. This ensures
        Pre, Post, and Δ are mutually consistent and free of model-selection bias.
        """
        pre_means, post_means, deltas = [], [], []
        for m in models:
            ab = m.get(key, {}).get(area, {})
            pre_lst  = ab.get("pre",  [])
            post_lst = ab.get("post", [])
            if pre_lst and post_lst:   # only models with BOTH partitions
                pre_means.append(_sm(pre_lst))
                post_means.append(_sm(post_lst))
                deltas.append(_sm(post_lst) - _sm(pre_lst))

        pre_str  = _fmt(_sm(pre_means),  dp=dp) if pre_means  else r"{\textemdash}"
        post_str = _fmt(_sm(post_means), dp=dp) if post_means else r"{\textemdash}"

        if not deltas:
            delta_str = r"{\textemdash}"
        else:
            d = _sm(deltas)
            if d > 0.05:    colour = r"\cellcolor{cellgood}"
            elif d < -0.15: colour = r"\cellcolor{cellbad}"
            elif d < -0.05: colour = r"\cellcolor{cellworse}"
            else:            colour = ""
            delta_str = colour + _fmt(d, dp=dp, signed=True)

        return pre_str, post_str, delta_str

    header = _join_row([
        r"\textbf{Area}",
        r"\multicolumn{3}{c}{\textbf{Binary (acc.)}}",
        r"\multicolumn{3}{c}{\textbf{MCQ (acc.)}}",
        r"\multicolumn{3}{c}{\textbf{FRQ (0--10)}}",
        r"\multicolumn{3}{c}{\textbf{Date (score)}}",
    ])
    subheader = _join_row([
        "",
        r"\textit{Pre}", r"\textit{Post}", r"$\Delta$",
        r"\textit{Pre}", r"\textit{Post}", r"$\Delta$",
        r"\textit{Pre}", r"\textit{Post}", r"$\Delta$",
        r"\textit{Pre}", r"\textit{Post}", r"$\Delta$",
    ])

    data_rows = []
    for area in areas:
        bin_pre,  bin_post,  bin_d  = _within_model_stats("area_split_binary", area)
        mcq_pre,  mcq_post,  mcq_d  = _within_model_stats("area_split_mcq",    area)
        frq_pre,  frq_post,  frq_d  = _within_model_stats("area_split_frq",    area, dp=2)
        date_pre, date_post, date_d = _within_model_stats("area_split_date",   area)

        data_rows.append(_join_row([
            _esc(AREA_SHORT.get(area, area)),
            bin_pre,  bin_post,  bin_d,
            mcq_pre,  mcq_post,  mcq_d,
            frq_pre,  frq_post,  frq_d,
            date_pre, date_post, date_d,
        ]))

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Pre- vs.\ post-cutoff performance by research area. "
        r"Pre-cutoff: papers published before a model's training cutoff (potentially seen). "
        r"Post-cutoff: papers published after (truly unseen). "
        r"Pre and Post columns show the mean of per-model means for each partition; "
        r"$\Delta$\,=\,mean within-model (post\,$-$\,pre), averaged only over models "
        r"with instances in \emph{both} partitions for that area---this avoids "
        r"confounding model quality with temporal effects. "
        r"\colorbox{cellgood}{\strut green}: $\Delta > +0.05$; "
        r"\colorbox{cellworse}{\strut orange}: $\Delta < -0.05$; "
        r"\colorbox{cellbad}{\strut red}: $\Delta < -0.15$.}",
        r"\label{tab:area_pre_post}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}l rrr rrr rrr rrr@{}}",
        r"\toprule",
        header + r" \\",
        r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}\cmidrule(lr){11-13}",
        subheader,
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"$\Delta$ is computed as the mean of per-model (post\,$-$\,pre) differences "
            r"to avoid model-selection bias: models with no pre-cutoff instances "
            r"(GPT-4o, LLaMA\,3.3; cutoff $\leq$ Dec\,2023) are excluded from $\Delta$ "
            r"and Pre columns but contribute to Post. "
            r"Binary: merged accuracy; chance\,=\,0.50. "
            r"MCQ: 4-choice; chance\,=\,0.25. "
            r"FRQ: rubric score (0--10). Date: exponential-decay score."
        ),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# FRQ Tables
# ---------------------------------------------------------------------------

def _cell_frq_score(v: float) -> str:
    """Heatmap colour for FRQ scores (0–10 scale)."""
    if np.isnan(v): return ""
    if v < 3.0:  return r"\cellcolor{cellbad}"
    if v < 4.0:  return r"\cellcolor{cellworse}"
    if v < 5.0:  return r"\cellcolor{cellneutral}"
    if v < 6.0:  return r"\cellcolor{cellgood}"
    if v < 7.0:  return r"\cellcolor{cellbetter}"
    return               r"\cellcolor{cellbest}"


def _cell_frq_align(v: float) -> str:
    """Heatmap colour for alignment sub-scores (0–10)."""
    if np.isnan(v): return ""
    if v < 2.0:  return r"\cellcolor{cellbad}"
    if v < 3.0:  return r"\cellcolor{cellworse}"
    if v < 4.0:  return r"\cellcolor{cellneutral}"
    if v < 5.0:  return r"\cellcolor{cellgood}"
    if v < 6.5:  return r"\cellcolor{cellbetter}"
    return               r"\cellcolor{cellbest}"


def table_frq_overall(models: list[dict]) -> str:
    """Table FRQ-1: per-model FRQ headline metrics."""
    sorted_m = sorted(models, key=lambda m: m["frq_mean"], reverse=True)

    frq_v    = [m["frq_mean"]       for m in sorted_m]
    pass_v   = [m["frq_pass_rate"]  for m in sorted_m]
    align_v  = [m["frq_align_mean"] for m in sorted_m]
    spec_v   = [m["frq_spec_mean"]  for m in sorted_m]
    nov_v    = [m["frq_novelty_mean"] for m in sorted_m]
    leak_v   = [m["leakage_fail_rate"] for m in sorted_m]

    s_frq  = _apply_best([_fmt(v, dp=2) for v in frq_v],  frq_v,  "max")
    s_pass = _apply_best([_fmt(v, pct=True) for v in pass_v], pass_v, "max")

    data_rows = [
        _join_row([
            _esc(m["short"]), _cutoff_fmt(m["cutoff"]),
            str(m["frq_n"]),
            s_frq[i], s_pass[i],
            _fmt(align_v[i], dp=2),
            _fmt(spec_v[i],  dp=2),
            _fmt(nov_v[i],   dp=2),
            _fmt(leak_v[i],  pct=True),
        ])
        for i, m in enumerate(sorted_m)
    ]

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{FRQ performance summary. \textbf{Score}: mean rubric score "
        r"(0--10); \textbf{Pass\,\%}: fraction scoring $\geq 5$. "
        r"\textbf{Alignment}: how closely the response matches the actual paper "
        r"method (0--10). \textbf{Specificity}: technical concreteness (0--10). "
        r"\textbf{Novelty}: non-obvious insight (0--10). "
        r"\textbf{Leak\,\%}: fraction of responses flagged for post-cutoff leakage. "
        r"Models sorted by mean score (highest first). \textbf{Bold}: best per column.}",
        r"\label{tab:frq_overall}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll r rr rrr r@{}}",
        r"\toprule",
        r" & & & \multicolumn{2}{c}{Overall}"
        r" & \multicolumn{3}{c}{Sub-dimensions (0--10)}"
        r" & Reasoning \\",
        r"\cmidrule(lr){4-5}\cmidrule(lr){6-8}",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}", r"$n$",
                   r"\textbf{Score\,$\uparrow$}", r"\textbf{Pass\,\%\,$\uparrow$}",
                   r"\textbf{Align}", r"\textbf{Spec.}", r"\textbf{Nov.}",
                   r"\textbf{Leak\,\%\,$\downarrow$}"]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"Alignment, Specificity, and Novelty are sub-dimensions of the FRQ rubric judge "
            r"(each 0--10). A high Specificity with low Alignment indicates technically "
            r"detailed responses that nonetheless miss the actual paper methodology."
        ),
        r"\end{table}",
    ])


def table_frq_subdims(models: list[dict]) -> str:
    """Table FRQ-2: alignment vs specificity vs novelty gap per model."""
    sorted_m = sorted(models, key=lambda m: m["frq_align_mean"])

    data_rows = []
    for m in sorted_m:
        al = m["frq_align_mean"]
        sp = m["frq_spec_mean"]
        nv = m["frq_novelty_mean"]
        gap = sp - al  # specificity−alignment gap: positive = detailed but misaligned
        data_rows.append(_join_row([
            _esc(m["short"]), _cutoff_fmt(m["cutoff"]),
            _cell_frq_align(al) + _fmt(al, dp=2),
            _cell_frq_align(sp) + _fmt(sp, dp=2),
            _cell_frq_align(nv) + _fmt(nv, dp=2),
            _fmt(gap, dp=2, signed=True),
            _fmt(m["frq_mean"], dp=2),
        ]))

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{FRQ sub-dimension profile. "
        r"\textbf{Alignment}: match with the actual paper method. "
        r"\textbf{Specificity}: technical concreteness. "
        r"\textbf{Novelty}: non-obvious insight. "
        r"\textbf{Spec.\,$-$\,Align.\ gap}: positive values indicate models that "
        r"write technically detailed responses but miss the specific paper approach "
        r"--- a signature of plausible-sounding hallucination. "
        r"Models sorted from lowest to highest alignment.}",
        r"\label{tab:frq_subdims}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll rrrrrr@{}}",
        r"\toprule",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}",
                   r"\textbf{Align.\,$\uparrow$}",
                   r"\textbf{Spec.\,$\uparrow$}",
                   r"\textbf{Nov.\,$\uparrow$}",
                   r"\textbf{Spec.\,$-$\,Align.\ gap}",
                   r"\textbf{Overall score}"]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"All sub-dimensions scored 0--10 by the LLM rubric judge. "
            r"Colour shading on Alignment, Specificity, and Novelty uses the same "
            r"scale: red $<$ 3, orange 3--4, yellow 4--5, light green 5--6, "
            r"medium green 6--6.5, dark green $\geq$ 6.5."
        ),
        r"\end{table}",
    ])


def table_frq_by_area(models: list[dict]) -> str:
    """Table FRQ-3: mean FRQ score by research area × model (heatmap)."""
    areas = [a for a in AREA_ORDER if any(a in m["area_frq"] for m in models)]

    header = _join_row(
        [r"\textbf{Area}", r"$n$"] +
        [r"\textbf{" + _esc(m["short"]) + r"}" for m in models] +
        [r"\textbf{Mean}"]
    )

    data_rows = []
    for area in areas:
        ns   = [len(m["area_frq"].get(area, [])) for m in models]
        n    = max(ns) if ns else 0
        vals = [_sm(m["area_frq"].get(area, [])) for m in models]
        row_mean = _sm([v for v in vals if not np.isnan(v)])
        cells = (
            [_esc(AREA_SHORT.get(area, area)), str(n)] +
            [_cell_frq_score(v) + _fmt(v, dp=2) for v in vals] +
            [_cell_frq_score(row_mean) + _fmt(row_mean, dp=2)]
        )
        data_rows.append(_join_row(cells))

    # Bottom row: per-model overall means + grand mean
    means = [m["frq_mean"] for m in models]
    grand_mean = _sm([v for v in means if not np.isnan(v)])
    mean_cells = (
        [r"\textit{Overall}", ""] +
        [r"\textit{" + _fmt(v, dp=2) + r"}" for v in means] +
        [r"\textit{" + _fmt(grand_mean, dp=2) + r"}"]
    )
    col_spec = "@{}lr" + "r" * len(models) + "r@{}"

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Mean FRQ score (0--10) by research area and model. "
        r"$n$: number of FRQ instances in the area (max across models). "
        r"Colour: red $<$ 3, orange 3--4, yellow 4--5, "
        r"light green 5--6, medium green 6--7, dark green $\geq$ 7.}",
        r"\label{tab:frq_by_area}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        header,
        r"\midrule",
        *data_rows,
        r"\midrule",
        _join_row(mean_cells) + r"  % overall row",
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"Chemistry and Physics consistently show lower FRQ alignment, "
            r"reflecting higher domain specificity and fewer overlapping "
            r"concepts with general pretraining data."
        ),
        r"\end{table}",
    ])


def table_frq_pre_post(models: list[dict]) -> str:
    """Table FRQ-4: FRQ score and alignment pre- vs. post-cutoff."""

    def _acc(lst: list) -> str:
        return _fmt(_sm(lst), dp=2) if lst else r"{\textemdash}"

    def _delta(pre: list, post: list) -> str:
        if not pre or not post:
            return r"{\textemdash}"
        return _fmt(_sm(post) - _sm(pre), dp=2, signed=True)

    def _n(lst: list) -> str:
        return str(len(lst)) if lst else r"{\textemdash}"

    data_rows = []
    for m in models:
        pre_s  = m["split_frq"]["pre"]
        post_s = m["split_frq"]["post"]
        pre_a  = m["split_frq_align"]["pre"]
        post_a = m["split_frq_align"]["post"]
        data_rows.append(_join_row([
            _esc(m["short"]), _cutoff_fmt(m["cutoff"]),
            # Pre-cutoff
            _n(pre_s), _acc(pre_s), _acc(pre_a),
            # Post-cutoff
            _n(post_s), _acc(post_s), _acc(post_a),
            # Deltas
            _delta(pre_s, post_s),
            _delta(pre_a, post_a),
        ]))

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{FRQ score and alignment for papers published \emph{before} "
        r"vs.\ \emph{after} each model's training cutoff. "
        r"A drop in alignment on post-cutoff papers indicates the model cannot "
        r"leverage memorised knowledge of the specific methodology. "
        r"$\Delta$\,=\,post\,$-$\,pre; negative\,=\,worse on unseen papers. "
        r"Models with cutoff predating Jan 2024 have no pre-cutoff rows.}",
        r"\label{tab:frq_pre_post}",
        _adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll rrr rrr rr@{}}",
        r"\toprule",
        r" & & \multicolumn{3}{c}{Pre-cutoff (seen)}"
        r" & \multicolumn{3}{c}{Post-cutoff (unseen)}"
        r" & \multicolumn{2}{c}{$\Delta$ (post$-$pre)} \\",
        r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}\cmidrule(lr){9-10}",
        _join_row([r"\textbf{Model}", r"\textbf{Cutoff}",
                   r"$n$", r"\textbf{Score}", r"\textbf{Align.}",
                   r"$n$", r"\textbf{Score}", r"\textbf{Align.}",
                   r"$\Delta$\,Score", r"$\Delta$\,Align."]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        _adjustbox_close(),
        _minipage_note(
            r"Benchmark papers span Jan 2024--Mar 2026. "
            r"Models whose cutoff $\leq$ Dec 2023 (GPT-4o, LLaMA 3.3) "
            r"have all papers in the post-cutoff partition and show ``---'' for pre-cutoff."
        ),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Compilation document
# ---------------------------------------------------------------------------

PREAMBLE = r"""\documentclass[11pt, a4paper]{article}

\usepackage[a4paper, top=2.2cm, bottom=2.2cm, left=2.0cm, right=2.0cm]{geometry}
\usepackage{booktabs}
\usepackage[table]{xcolor}
\usepackage{colortbl}
\usepackage{multirow}
\usepackage{makecell}
\usepackage{caption}
\usepackage{amsmath}
\usepackage{microtype}
\usepackage{array}
\usepackage{adjustbox}   % \begin{adjustbox}{max width=\textwidth}
\usepackage{threeparttable}

%% Cell colour palette: green = good, yellow/red = poor
\definecolor{cellbest}   {rgb}{0.47, 0.85, 0.55}
\definecolor{cellbetter} {rgb}{0.67, 0.91, 0.72}
\definecolor{cellgood}   {rgb}{0.82, 0.95, 0.84}
\definecolor{cellneutral}{rgb}{0.99, 0.97, 0.83}
\definecolor{cellworse}  {rgb}{0.98, 0.82, 0.77}
\definecolor{cellbad}    {rgb}{0.96, 0.61, 0.55}

\captionsetup{font=small, labelfont=bf, width=0.97\linewidth}
\setlength{\tabcolsep}{5pt}

\title{\textbf{CUSP Benchmark --- Supplementary Tables}\\[0.4em]
  \large Multi-model evaluation: binary, MCQ, and date prediction}
\date{}

\begin{document}
\maketitle
\tableofcontents
\clearpage
"""

POSTAMBLE = r"\end{document}" + "\n"


def write_compilation(tables: dict[str, str], out_dir: Path) -> None:
    with open(out_dir / "tables_all.tex", "w", encoding="utf-8") as f:
        f.write(PREAMBLE)
        for title, tex in tables.items():
            f.write(f"\n\\section{{{title}}}\n\n{tex}\n\n\\clearpage\n")
        f.write(POSTAMBLE)
    print("  Saved tables_all.tex")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate LaTeX tables for CUSP benchmark results")
    p.add_argument("--results",    default="model_results/")
    p.add_argument("--benchmark",  default=None,
                   help="Benchmark JSONL — required for area tables and pre/post cutoff")
    p.add_argument("--output-dir", default=None)
    return p


def main() -> None:
    args    = build_parser().parse_args()
    out_dir = (Path(args.output_dir) if args.output_dir
               else Path(args.results) / "tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading model results...")
    models = load_all_models(args.results, args.benchmark)
    if not models:
        print("No models found. Check --results and MODEL_REGISTRY.")
        return

    print(f"\nLoaded {len(models)} models:")
    for m in models:
        print(f"  {m['short']:15s}  merged-binary={m['merged_binary_acc']:.3f}  "
              f"mcq={m['mcq_acc']:.3f}  date={m['date_score']:.3f}")

    print(f"\nGenerating tables → {out_dir}/\n")

    TABLE_DEFS: list[tuple[str, str, str]] = [
        ("table1_main_results.tex",   "Overall Performance Summary",       table_main_results(models)),
        ("table2_binary_bias.tex",    "Binary Response-Bias Analysis",     table_binary_bias(models)),
        ("table3_date_stats.tex",     "Date Prediction Statistics",        table_date_stats(models)),
        ("table7_calibration.tex",    "Confidence Calibration",            table_calibration(models)),
    ]

    if args.benchmark:
        TABLE_DEFS += [
            ("table4_area_mcq.tex",       "MCQ Accuracy by Research Area",           table_area_mcq(models)),
            ("table5_area_date.tex",       "Date Score by Research Area",             table_area_date(models)),
            ("table5b_area_binary.tex",    "Binary Merged Accuracy by Research Area", table_area_binary(models)),
            ("table6_pre_post_cutoff.tex", "Pre- vs. Post-Cutoff Performance",       table_pre_post_cutoff(models)),
            ("table_area_pre_post.tex",    "Pre- vs. Post-Cutoff by Research Area",                        table_area_pre_post(models)),
            ("table_frq2_subdims.tex",     "FRQ Sub-dimension Profile (Alignment / Specificity / Novelty)", table_frq_subdims(models)),
            ("table_frq3_by_area.tex",     "FRQ Score by Research Area",                                   table_frq_by_area(models)),
        ]
    else:
        print("  Note: --benchmark not provided; skipping tables 4, 5, 6, and FRQ tables.")

    tables_doc: dict[str, str] = {}
    for fname, title, tex in TABLE_DEFS:
        path = out_dir / fname
        path.write_text(tex + "\n", encoding="utf-8")
        print(f"  Saved {fname}")
        tables_doc[title] = tex

    write_compilation(tables_doc, out_dir)

    print(f"\nDone. Compile the preview with:")
    print(f"  cd {out_dir}")
    print(f"  pdflatex tables_all.tex && pdflatex tables_all.tex")


if __name__ == "__main__":
    main()
