"""
make_calibration_cutoff_table.py

Generates a LaTeX table of confidence-calibration metrics (ECE, Brier, Gap)
split by pre/post training-cutoff date for GPT-5.4, DeepSeek-R1, and
Claude Sonnet, across three retrieval conditions (no WS / WS / WS+Cutoff).

Layout mirrors make_web_search_cutoff_table.py:
  Rows  : 4 tasks × 3 metrics (ECE, Brier, Gap), grouped with \\multirow
  Cols  : Task | Metric | GPT-5.4 Pre | GPT-5.4 Post | DeepSeek Pre |
          DeepSeek Post | Claude Pre | Claude Post
  Cells : No-WS / WS / WS+Cut   (analogous to Base / WS / WS+Cut)

Output: frq_results/figures_web_search_comparison/table_calib_cutoff_split.tex
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from make_web_search_cutoff_table import (
    BENCH_500,
    FR,
    MODEL_CUTOFFS,
    MODEL_DISPLAY,
    MODEL_KEYS,
    PATHS,
    calibration_stats,
    collect_confidence,
    filter_ids_by_cutoff,
    load_by_id,
    load_pub_dates,
)

OUT = FR / "figures_web_search_comparison" / "table_calib_cutoff_split.tex"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CALIB_TASKS = [
    ("binary",           "Binary"),
    ("binary_perturbed", "Binary (pert.)"),
    ("mcq",              "MCQ"),
    ("date",             "Date"),
]

METRICS = [
    ("ece",      r"ECE$\downarrow$"),
    ("brier",    r"Brier$\downarrow$"),
    ("overconf", "Gap"),
]


# ---------------------------------------------------------------------------
# Cell formatter
# ---------------------------------------------------------------------------

def _fmt(v: float, metric: str) -> str:
    if math.isnan(v):
        return "---"
    if metric == "overconf":
        return rf"${'+' if v >= 0 else ''}{v:.3f}$"
    return rf"${v:.3f}$"


def fmt_triple_calib(
    data: dict,
    cond_keys: list[str],
    period_ids: list[str],
    task: str,
    metric: str,
) -> str:
    """Return 'no-ws / ws / ws+cut' cell for one model × period × task × metric."""
    parts = []
    for ck in cond_keys:
        conf, correct, _ = collect_confidence(data[ck], period_ids, task)
        s = calibration_stats(conf, correct)
        parts.append(_fmt(s[metric], metric))
    return " / ".join(parts)


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------

def make_calib_cutoff_table(
    data: dict[str, dict[str, dict]],
    ids: list[str],
    pub_dates: dict[str, str],
) -> str:
    model_items = list(MODEL_DISPLAY.items())   # [(key, (label, cutoff_label)), ...]
    n_models = len(model_items)

    # Pre/post splits per model
    splits: dict[str, tuple[list, list]] = {}
    for mk, _ in model_items:
        pre  = filter_ids_by_cutoff(pub_dates, ids, MODEL_CUTOFFS[mk], post=False)
        post = filter_ids_by_cutoff(pub_dates, ids, MODEL_CUTOFFS[mk], post=True)
        splits[mk] = (pre, post)
        print(f"  {mk}: pre={len(pre)}, post={len(post)}")

    # --- Header rows ---
    model_hdrs = " & ".join(
        rf"\multicolumn{{2}}{{c}}{{{ml} ({cl})}}"
        for _, (ml, cl) in model_items
    )
    cmidrules = " ".join(
        rf"\cmidrule(lr){{{3 + 2*i}-{4 + 2*i}}}"
        for i in range(n_models)
    )
    period_hdrs = " & ".join(
        rf"\textit{{Pre}} ($n={len(splits[mk][0])}$) & "
        rf"\textit{{Post}} ($n={len(splits[mk][1])}$)"
        for mk, _ in model_items
    )

    # 2 label cols (task + metric) + 2 × n_models data cols
    col_spec = "@{}ll " + "cc" * n_models + "@{}"

    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\setlength{\tabcolsep}{4pt}",
        r"\resizebox{\linewidth}{!}{",
        r"\begin{tabular}{" + col_spec + r"}",
        r"\toprule",
        rf"Task & Metric & {model_hdrs} \\",
        cmidrules,
        rf"& & {period_hdrs} \\",
        r"\midrule",
    ]

    n_metrics = len(METRICS)
    for ti, (task, task_label) in enumerate(CALIB_TASKS):
        for mi, (metric_key, metric_label) in enumerate(METRICS):
            # Task label spans all metric rows via \multirow
            task_col = (
                rf"\multirow{{{n_metrics}}}{{*}}{{{task_label}}}"
                if mi == 0 else ""
            )
            cells = []
            for mk, _ in model_items:
                cond_keys = list(MODEL_KEYS[mk])
                for period_ids in splits[mk]:
                    cells.append(
                        fmt_triple_calib(data, cond_keys, period_ids, task, metric_key)
                    )
            lines.append(
                rf"{task_col} & {metric_label} & {' & '.join(cells)} \\"
            )
        if ti < len(CALIB_TASKS) - 1:
            lines.append(r"\addlinespace[4pt]")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\caption{Confidence calibration split by each model's training cutoff. "
        r"Pre-cutoff: publication date $\leq$ training cutoff; "
        r"post-cutoff: publication date $>$ training cutoff "
        r"(all 500 questions classified via benchmark metadata). "
        r"Each cell shows No-WS / WS / WS+Cutoff values. "
        r"ECE = Expected Calibration Error; "
        r"Brier = Brier score; "
        r"Gap $= \bar{c} - \bar{a}$ (positive = overconfident). "
        r"$\downarrow$ lower is better.}",
        r"\label{tab:calib_cutoff_split}",
        r"\end{table}",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading data...")
    data      = {k: load_by_id(v) for k, v in PATHS.items()}
    ids       = sorted(set.intersection(*(set(d.keys()) for d in data.values())))
    pub_dates = load_pub_dates()
    print(f"  Shared IDs: {len(ids)}")

    print("\nComputing calibration cutoff split table...")
    tex = make_calib_cutoff_table(data, ids, pub_dates)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(tex, encoding="utf-8")
    print(f"  Saved {OUT}")
    print()
    print(tex)


if __name__ == "__main__":
    main()
