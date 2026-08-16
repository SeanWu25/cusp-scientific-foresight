"""
make_web_search_cutoff_table.py

Generates a LaTeX table extending the existing web-search comparison with a new
"WS + Cutoff" column for both GPT-4o and GPT-5.4.

Output columns per model section:
  Baseline | Web Search | Δ(WS) | p(WS) | WS+Cutoff | Δ(WS+Cut) | p(WS+Cut)

Output: frq_results/figures_web_search_comparison/table_web_search_cutoff.tex
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DIR    = Path(__file__).parent
FR     = DIR / "frq_results"
OUT    = FR  / "figures_web_search_comparison" / "table_web_search_cutoff.tex"

PATHS = {
    "gpt4o_base":  FR / "gpt_4o_reeval.json",
    "gpt4o_ws":    FR / "gpt_4o_web_search_no_cutoff_500.json",
    "gpt4o_wscut": FR / "gpt-4o_web_search_with_cutoff_500.json",
    "gpt54_base":  FR / "gpt_5_4_eval.json",
    "gpt54_ws":    FR / "gpt_5_4_web_subset_eval.json",
    "gpt54_wscut": FR / "gpt_5_4_500_web_cutoff.json",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_by_id(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)["results"]}


def shared_ids(*dicts: dict) -> list[str]:
    return sorted(set.intersection(*(set(d.keys()) for d in dicts)))


# ---------------------------------------------------------------------------
# Metric extraction helpers
# ---------------------------------------------------------------------------

def get_task_field(result: dict, task: str, field: str):
    return result.get("tasks", {}).get(task, {}).get(field)


def collect_paired(base_d: dict, other_d: dict, ids: list[str],
                   task: str, field: str) -> tuple[list, list]:
    """Return (base_vals, other_vals) for IDs where both are non-null."""
    bv, ov = [], []
    for rid in ids:
        b = get_task_field(base_d.get(rid, {}), task, field)
        o = get_task_field(other_d.get(rid, {}), task, field)
        if b is not None and o is not None:
            bv.append(float(b))
            ov.append(float(o))
    return bv, ov


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def paired_ttest(a: list[float], b: list[float]) -> float:
    arr_a = np.array(a); arr_b = np.array(b)
    if len(arr_a) < 3:
        return float("nan")
    _, p = stats.ttest_rel(arr_a, arr_b)
    return float(p)


def mcnemar_p(base: list[int], other: list[int]) -> float:
    b  = np.array(base,  dtype=int)
    o  = np.array(other, dtype=int)
    n01 = int(((b == 0) & (o == 1)).sum())
    n10 = int(((b == 1) & (o == 0)).sum())
    nd  = n01 + n10
    if nd == 0:
        return float("nan")
    if nd < 25:
        p = 2 * min(
            stats.binom.cdf(min(n01, n10), nd, 0.5),
            1 - stats.binom.cdf(max(n01, n10) - 1, nd, 0.5),
        )
        return float(p)
    chi2 = (abs(n01 - n10) - 1.0) ** 2 / nd
    return float(stats.chi2.sf(chi2, df=1))


def p_str(p: float) -> str:
    if math.isnan(p):
        return "---"
    if p < 0.001:
        return r"$< 0.001$~\textbf{***}"
    if p < 0.01:
        return rf"${p:.3f}$~\textbf{{**}}"
    if p < 0.05:
        return rf"${p:.3f}$~\textbf{{*}}"
    return rf"${p:.3f}$"


def fmt_mean_se(vals: list[float]) -> str:
    a  = np.array(vals)
    mu = a.mean()
    se = a.std(ddof=1) / math.sqrt(len(a))
    return rf"${mu:.3f} \pm {se:.3f}$"


def fmt_delta(base: list[float], other: list[float]) -> str:
    d = np.mean(other) - np.mean(base)
    sign = "+" if d >= 0 else ""
    return rf"${sign}{d:.3f}$"


# ---------------------------------------------------------------------------
# Row computation
# ---------------------------------------------------------------------------

ROW_SPECS = [
    # (display_label,       task,              field,           test_type)
    ("Binary (original)",   "binary",          "score",         "mcnemar"),
    ("Binary (perturbed)",  "binary_perturbed","score",         "mcnemar"),
    ("MCQ",                 "mcq",             "score",         "mcnemar"),
    ("FRQ score (0--10)",   "frq",             "score",         "ttest"),
    ("Date score (0--1)",   "date",            "score",         "ttest"),
    ("Date exact match",    "date",            "exact_match",   "mcnemar"),
    ("Date month error",    "date",            "month_distance","ttest"),
]


def compute_rows(base_d, ws_d, wscut_d, ids) -> list[dict]:
    rows = []
    for display, task, field, test in ROW_SPECS:
        bv,  wsv  = collect_paired(base_d, ws_d,    ids, task, field)
        bv2, cutv = collect_paired(base_d, wscut_d, ids, task, field)

        # Use the intersection of both paired sets for consistency
        n_ws  = len(bv)
        n_cut = len(bv2)

        if not bv or not bv2:
            rows.append({"display": display, "empty": True})
            continue

        if test == "mcnemar":
            p_ws  = mcnemar_p([int(v) for v in bv],  [int(v) for v in wsv])
            p_cut = mcnemar_p([int(v) for v in bv2], [int(v) for v in cutv])
        else:
            p_ws  = paired_ttest(bv,  wsv)
            p_cut = paired_ttest(bv2, cutv)

        rows.append({
            "display":   r"\quad " + display,
            "empty":     False,
            "base_str":  fmt_mean_se(bv),
            "ws_str":    fmt_mean_se(wsv),
            "cut_str":   fmt_mean_se(cutv),
            "delta_ws":  fmt_delta(bv,  wsv),
            "delta_cut": fmt_delta(bv2, cutv),
            "p_ws":      p_str(p_ws),
            "p_cut":     p_str(p_cut),
        })
    return rows


# ---------------------------------------------------------------------------
# LaTeX table generation
# ---------------------------------------------------------------------------

def make_table() -> str:
    data = {k: load_by_id(v) for k, v in PATHS.items()}
    ids  = shared_ids(*data.values())
    print(f"  Shared IDs: {len(ids)}")

    gpt4o_rows = compute_rows(
        data["gpt4o_base"], data["gpt4o_ws"], data["gpt4o_wscut"], ids
    )
    gpt54_rows = compute_rows(
        data["gpt54_base"], data["gpt54_ws"], data["gpt54_wscut"], ids
    )

    # 9 columns: label | base | ws | Δws | pws | wscut | Δcut | pcut
    col_spec = r"lcccccccc"

    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{" + col_spec + r"}",
        r"\toprule",
        # Two-row header with multicolumn grouping
        r" & & \multicolumn{3}{c}{Web Search (no cutoff)} & \multicolumn{3}{c}{Web Search (with cutoff)} \\",
        r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}",
        r"Metric & Baseline & Value & $\Delta$ & $p$-value & Value & $\Delta$ & $p$-value \\",
        r"\midrule",
    ]

    for model_label, rows, icon in [
        (r"\llmicon{openai_logo.png} \textit{GPT-4o}",  gpt4o_rows, "openai"),
        (r"\llmicon{openai_logo.png} \textit{GPT-5.4}", gpt54_rows, "openai"),
    ]:
        lines.append(rf"\multicolumn{{8}}{{l}}{{{model_label}}} \\")
        lines.append(r"\addlinespace[2pt]")
        for row in rows:
            if row.get("empty"):
                lines.append(rf"{row['display']} & --- & --- & --- & --- & --- & --- & --- \\")
                continue
            lines.append(
                f"{row['display']} & {row['base_str']} & {row['ws_str']} & "
                f"{row['delta_ws']} & {row['p_ws']} & "
                f"{row['cut_str']} & {row['delta_cut']} & {row['p_cut']} \\\\"
            )
        lines.append(r"\addlinespace[4pt]")

    # Remove trailing \addlinespace before \bottomrule
    if lines[-1] == r"\addlinespace[4pt]":
        lines.pop()

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{Web-search augmentation across models on matched 500-question subsets. "
        r"Values are means $\pm$ SE. $\Delta$ is relative to the Baseline. "
        r"Significance: *** $p<0.001$, ** $p<0.01$, * $p<0.05$, n.s.\ not significant.}",
        r"\label{tab:combined_web_search_cutoff}",
        r"\end{table}",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Computing table...")
    tex = make_table()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(tex, encoding="utf-8")
    print(f"  Saved {OUT}")
    print("\n" + tex)


if __name__ == "__main__":
    main()
