"""
compare_web_search.py — Nature-ready comparison across web-search conditions.

Compares four conditions on the same 500 matched questions:
  1. Baseline (GPT-4o, no web search)
  2. GPT-4o + Web Search (no cutoff)
  3. GPT-4o + Web Search (with cutoff)
  4. GPT-5.4 + Web Search (with cutoff)

Usage
-----
  python compare_web_search.py

Output (all written to frq_results/figures_web_search_comparison/):
  fig1_overview.{pdf,png}        — 4-condition grouped bars + delta chart
  fig2_frq_dimensions.{pdf,png}  — radar + grouped bars for FRQ sub-scores
  fig3_scatter.{pdf,png}         — per-sample scatter (baseline vs each condition)
  fig4_distributions.{pdf,png}   — violin distributions
  fig5_binary_detail.{pdf,png}   — binary task deep-dive
  table1_main.tex                — main metrics, 4 condition columns
  table2_frq_dimensions.tex      — FRQ sub-dimensions, 4 condition columns

Requirements: matplotlib, numpy, scipy
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.gridspec import GridSpec
from scipy import stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DIR = Path(__file__).parent
FR  = DIR / "frq_results"
OUT_DIR = FR / "figures_web_search_comparison"


# ---------------------------------------------------------------------------
# Condition definitions — all share the same 500-question ID pool
# ---------------------------------------------------------------------------

@dataclass
class Condition:
    key:          str
    label:        str        # short display label
    label_long:   str        # longer caption label
    color:        str
    path:         Path
    is_reference: bool = False


CONDITIONS: list[Condition] = [
    Condition(
        key="base", label="Baseline",
        label_long="GPT-4o Baseline",
        color="#648FFF",
        path=FR / "gpt_4o_reeval.json",
        is_reference=True,
    ),
    Condition(
        key="4o_ws", label="4o+WS",
        label_long="GPT-4o + Web Search",
        color="#FE6100",
        path=FR / "gpt_4o_web_search_no_cutoff_500.json",
    ),
    Condition(
        key="4o_ws_cut", label="4o+WS+Cut",
        label_long="GPT-4o + WS + Cutoff",
        color="#DC267F",
        path=FR / "gpt-4o_web_search_with_cutoff_500.json",
    ),
    Condition(
        key="54_ws_cut", label="5.4+WS+Cut",
        label_long="GPT-5.4 + WS + Cutoff",
        color="#785EF0",
        path=FR / "gpt_5_4_500_web_cutoff.json",
    ),
]

# Conditions to compare against reference (all non-reference ones)
TREATMENT_CONDS = [c for c in CONDITIONS if not c.is_reference]
REF_COND        = next(c for c in CONDITIONS if c.is_reference)


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

def apply_nature_style() -> None:
    plt.rcParams.update({
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size":         8,
        "axes.labelsize":    8,
        "axes.titlesize":    8,
        "axes.titleweight":  "bold",
        "xtick.labelsize":   7,
        "ytick.labelsize":   7,
        "legend.fontsize":   6.5,
        "legend.frameon":    False,
        "figure.dpi":        300,
        "axes.linewidth":    0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size":  3,
        "ytick.major.size":  3,
        "lines.linewidth":   1.2,
        "axes.spines.right": False,
        "axes.spines.top":   False,
        "savefig.bbox":      "tight",
        "savefig.dpi":       300,
        "pdf.fonttype":      42,
        "ps.fonttype":       42,
    })


def save_fig(fig: plt.Figure, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}.pdf / .png")


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def paired_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    mask  = ~(np.isnan(a_arr) | np.isnan(b_arr))
    if mask.sum() < 3:
        return float("nan"), float("nan")
    t, p = stats.ttest_rel(a_arr[mask], b_arr[mask])
    return float(t), float(p)


def mcnemar_test(base_pass: list[int], other_pass: list[int]) -> tuple[float, float]:
    """McNemar's test with continuity correction; exact binomial for small n."""
    b   = np.array(base_pass,  dtype=int)
    w   = np.array(other_pass, dtype=int)
    n01 = int(((b == 0) & (w == 1)).sum())
    n10 = int(((b == 1) & (w == 0)).sum())
    nd  = n01 + n10
    if nd == 0:
        return float("nan"), float("nan")
    if nd < 25:
        p    = 2 * min(stats.binom.cdf(min(n01, n10), nd, 0.5),
                       1 - stats.binom.cdf(max(n01, n10) - 1, nd, 0.5))
        chi2 = (n01 - n10) ** 2 / nd
        return float(chi2), float(p)
    chi2 = (abs(n01 - n10) - 1.0) ** 2 / nd
    return float(chi2), float(stats.chi2.sf(chi2, df=1))


def p_stars(p: float) -> str:
    if np.isnan(p): return "n.s."
    if p < 0.001:   return "***"
    if p < 0.01:    return "**"
    if p < 0.05:    return "*"
    return "n.s."


def cohen_d(a: list[float], b: list[float]) -> float:
    diff = np.array(a, dtype=float) - np.array(b, dtype=float)
    return float(np.mean(diff) / (np.std(diff, ddof=1) + 1e-12))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all_conditions() -> dict[str, dict[str, dict]]:
    """Load all conditions; returns {cond.key: {id: result_dict}}."""
    data: dict[str, dict[str, dict]] = {}
    for cond in CONDITIONS:
        with open(cond.path, encoding="utf-8") as f:
            report = json.load(f)
        data[cond.key] = {r["id"]: r for r in report["results"]}
        print(f"  {cond.key:15s}: {len(data[cond.key])} rows  ({cond.path.name})")
    return data


def get_shared_ids(data: dict[str, dict[str, dict]]) -> list[str]:
    ids = set.intersection(*(set(v.keys()) for v in data.values()))
    ids = sorted(ids)
    print(f"  Shared IDs across all conditions: {len(ids)}")
    return ids


def extract_metrics(data: dict[str, dict[str, dict]], ids: list[str]) -> dict:
    """
    Returns {metric_key: {cond_key: [float, ...]}} for all conditions.
    Only includes positions where ALL conditions have a non-null value.
    """
    cond_keys = list(data.keys())

    def _collect_task(tid: str, task: str, field: str = "score") -> list | None:
        vals = []
        for ck in cond_keys:
            v = data[ck].get(tid, {}).get("tasks", {}).get(task, {}).get(field)
            if v is None:
                return None
            vals.append(float(v))
        return vals

    def _collect_top(tid: str, field: str) -> list | None:
        vals = []
        for ck in cond_keys:
            v = data[ck].get(tid, {}).get(field)
            if v is None:
                return None
            vals.append(float(v))
        return vals

    def _collect_flag(tid: str, field: str) -> list:
        return [float(int(bool(data[ck].get(tid, {}).get(field)))) for ck in cond_keys]

    buckets: dict[str, dict[str, list]] = {}

    def _add(key: str, vals: list) -> None:
        if key not in buckets:
            buckets[key] = {ck: [] for ck in cond_keys}
        for ck, v in zip(cond_keys, vals):
            buckets[key][ck].append(v)

    for tid in ids:
        # Per-task binary/MCQ scores
        for task in ("binary", "binary_perturbed", "mcq"):
            v = _collect_task(tid, task, "score")
            if v:
                _add(task, v)

        # FRQ sub-dimensions
        for sub in ("score", "alignment", "specificity", "novelty", "feasibility"):
            v = _collect_task(tid, "frq", sub)
            if v:
                _add(f"frq_{sub}", v)

        # Date
        v = _collect_task(tid, "date", "score")
        if v:
            _add("date_score", v)
        v = _collect_task(tid, "date", "month_distance")
        if v:
            _add("date_month_dist", v)

        # Overall composite
        v = _collect_top(tid, "overall_score")
        if v:
            _add("overall", v)

        # Pass flags
        _add("joint_pass",   _collect_flag(tid, "joint_pass"))
        _add("outcome_pass", _collect_flag(tid, "outcome_pass"))

    return buckets


# ---------------------------------------------------------------------------
# Helpers for computing stats vs. reference
# ---------------------------------------------------------------------------

def cond_mean(m: dict, key: str, cond_key: str, norm: float = 1.0) -> float:
    if key not in m or cond_key not in m[key]:
        return float("nan")
    return float(np.mean(m[key][cond_key])) / norm


def cond_se(m: dict, key: str, cond_key: str, norm: float = 1.0) -> float:
    if key not in m or cond_key not in m[key]:
        return 0.0
    arr = np.array(m[key][cond_key]) / norm
    return float(np.std(arr, ddof=1) / np.sqrt(len(arr)))


def cond_delta(m: dict, key: str, treat_key: str, ref_key: str, norm: float = 1.0) -> float:
    return cond_mean(m, key, treat_key, norm) - cond_mean(m, key, ref_key, norm)


def cond_pval(m: dict, key: str, treat_key: str, ref_key: str,
              test: str = "auto") -> float:
    if key not in m:
        return float("nan")
    ref_vals   = m[key][ref_key]
    treat_vals = m[key][treat_key]
    binary_keys = {"binary", "binary_perturbed", "mcq", "joint_pass", "outcome_pass",
                   "date_exact"}
    if test == "auto":
        test = "mcnemar" if key in binary_keys else "ttest"
    if test == "mcnemar":
        _, p = mcnemar_test([int(v) for v in ref_vals], [int(v) for v in treat_vals])
    else:
        _, p = paired_ttest(ref_vals, treat_vals)
    return p


# ---------------------------------------------------------------------------
# Figure 1: Overview — 4-condition grouped bars + delta chart
# ---------------------------------------------------------------------------

PANEL_METRICS = [
    ("Binary",           "binary",           1.0),
    ("Binary\nPerturbed","binary_perturbed",  1.0),
    ("MCQ",              "mcq",              1.0),
    ("FRQ\nScore",       "frq_score",        10.0),
    ("Overall",          "overall",          1.0),
    ("Joint\nPass",      "joint_pass",        1.0),
    ("Outcome\nPass",    "outcome_pass",      1.0),
]


def figure_overview(m: dict) -> None:
    apply_nature_style()

    labels = [pm[0] for pm in PANEL_METRICS]
    x      = np.arange(len(labels))
    bw     = 0.18   # width per bar; 4 bars fit in one group
    ek     = {"elinewidth": 0.6, "capsize": 1.5, "ecolor": "#333"}
    offsets = [-1.5 * bw, -0.5 * bw, 0.5 * bw, 1.5 * bw]

    fig = plt.figure(figsize=(7.2, 5.4))
    gs  = GridSpec(2, 1, figure=fig, hspace=0.58,
                   left=0.08, right=0.97, top=0.92, bottom=0.10)

    # ── Panel A: grouped bars ─────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    for i, cond in enumerate(CONDITIONS):
        means = [cond_mean(m, key, cond.key, norm) for _, key, norm in PANEL_METRICS]
        ses   = [cond_se(m, key, cond.key, norm)   for _, key, norm in PANEL_METRICS]
        ax_a.bar(x + offsets[i], means, bw, yerr=ses,
                 color=cond.color, alpha=0.85, label=cond.label,
                 error_kw=ek, edgecolor="white", linewidth=0.3)

    # significance stars over each metric group (each treatment vs reference)
    for xi, (_, key, norm) in enumerate(PANEL_METRICS):
        for i, cond in enumerate(TREATMENT_CONDS):
            p = cond_pval(m, key, cond.key, REF_COND.key)
            stars = p_stars(p)
            if stars != "n.s.":
                treat_mean = cond_mean(m, key, cond.key, norm)
                ref_mean   = cond_mean(m, key, REF_COND.key, norm)
                top = max(treat_mean if not np.isnan(treat_mean) else 0,
                          ref_mean   if not np.isnan(ref_mean)   else 0) + 0.04
                ci  = [c for c in CONDITIONS].index(cond)
                ax_a.text(xi + offsets[ci], top + 0.01 * ci,
                          stars, ha="center", va="bottom", fontsize=5.5, color=cond.color)

    ax_a.axhline(0.5, color="gray", linewidth=0.5, linestyle="--", alpha=0.35)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(labels, fontsize=7)
    ax_a.set_ylabel("Score / Accuracy (0–1)", fontsize=7)
    ax_a.set_ylim(0, 1.22)
    ax_a.legend(fontsize=6, loc="upper left", ncol=2)
    ax_a.set_title("A  All conditions — matched 500-question subset",
                   loc="left", fontweight="bold")

    # ── Panel B: delta bars (each treatment − reference) ──────────────────
    ax_b = fig.add_subplot(gs[1, 0])
    bw_d = 0.22
    off_d = [-(len(TREATMENT_CONDS) - 1) / 2 * bw_d + i * bw_d
             for i in range(len(TREATMENT_CONDS))]

    for i, cond in enumerate(TREATMENT_CONDS):
        deltas = [cond_delta(m, key, cond.key, REF_COND.key, norm)
                  for _, key, norm in PANEL_METRICS]
        cols   = [cond.color if d >= 0 else "#F44336" for d in deltas]
        ax_b.bar(x + off_d[i], deltas, bw_d, color=cols, alpha=0.82,
                 edgecolor="white", linewidth=0.3, label=f"Δ {cond.label}")
        for xi, d in enumerate(deltas):
            if np.isnan(d):
                continue
            yoff = 0.005 if d >= 0 else -0.02
            p = cond_pval(m, PANEL_METRICS[xi][1], cond.key, REF_COND.key)
            ax_b.text(x[xi] + off_d[i], d + yoff,
                      f"{p_stars(p)}", ha="center",
                      va="bottom" if d >= 0 else "top",
                      fontsize=5, color="#222")

    ax_b.axhline(0, color="#333", linewidth=0.8)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(labels, fontsize=7)
    ax_b.set_ylabel("Δ vs. Baseline", fontsize=7)
    ax_b.legend(fontsize=6, loc="upper right", ncol=3)
    ax_b.set_title("B  Improvement over baseline",
                   loc="left", fontweight="bold")

    fig.suptitle("Web-Search Augmentation Comparison — GPT-4o and GPT-5.4  (n=500)",
                 fontsize=9, fontweight="bold", y=0.98)
    save_fig(fig, "fig1_overview")


# ---------------------------------------------------------------------------
# Figure 2: FRQ dimensions — radar + grouped bars
# ---------------------------------------------------------------------------

def figure_frq_dimensions(m: dict) -> None:
    apply_nature_style()

    dims       = ["alignment", "specificity", "novelty", "feasibility"]
    dim_labels = ["Alignment", "Specificity", "Novelty", "Feasibility"]
    max_score  = 10.0

    fig = plt.figure(figsize=(7.2, 3.2))
    gs  = GridSpec(1, 2, figure=fig, wspace=0.44,
                   left=0.05, right=0.97, top=0.84, bottom=0.14)

    # ── Panel A: Radar ─────────────────────────────────────────────────────
    ax_r = fig.add_subplot(gs[0, 0], projection="polar")
    N = len(dims)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    ac     = angles + [angles[0]]

    for cond in CONDITIONS:
        vals   = [cond_mean(m, f"frq_{d}", cond.key) / max_score for d in dims]
        vc     = vals + [vals[0]]
        ax_r.plot(ac, vc, "o-", color=cond.color,
                  linewidth=1.4, markersize=3.5, zorder=3, label=cond.label)
        ax_r.fill(ac, vc, alpha=0.10, color=cond.color)

    ax_r.set_xticks(angles)
    ax_r.set_xticklabels(dim_labels, size=6.5)
    ax_r.set_ylim(0, 1)
    ax_r.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_r.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], size=4.5)
    ax_r.spines["polar"].set_linewidth(0.5)
    ax_r.grid(linewidth=0.4, alpha=0.6)
    ax_r.legend(fontsize=5.5, loc="upper right", bbox_to_anchor=(1.45, 1.18))
    ax_r.set_title("A  FRQ dimension profile", size=8, pad=18, fontweight="bold")

    # ── Panel B: Grouped bars ─────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    x    = np.arange(len(dims))
    n    = len(CONDITIONS)
    bw   = 0.18
    ek   = {"elinewidth": 0.6, "capsize": 1.5, "ecolor": "#333"}
    offs = [-(n - 1) / 2 * bw + i * bw for i in range(n)]

    for i, cond in enumerate(CONDITIONS):
        means = [cond_mean(m, f"frq_{d}", cond.key) / max_score for d in dims]
        ses   = [cond_se(m, f"frq_{d}", cond.key, max_score) for d in dims]
        ax_b.bar(x + offs[i], means, bw, yerr=ses,
                 color=cond.color, alpha=0.85, label=cond.label,
                 error_kw=ek, edgecolor="white", linewidth=0.3)

    # Significance stars (each treatment vs baseline)
    for xi, d in enumerate(dims):
        key = f"frq_{d}"
        tops = [cond_mean(m, key, c.key) / max_score for c in CONDITIONS]
        top  = max(v for v in tops if not np.isnan(v)) + 0.05
        for i, cond in enumerate(TREATMENT_CONDS):
            p     = cond_pval(m, key, cond.key, REF_COND.key, "ttest")
            stars = p_stars(p)
            ci    = [c for c in CONDITIONS].index(cond)
            if stars != "n.s.":
                ax_b.text(xi + offs[ci], top + 0.01,
                          stars, ha="center", fontsize=5.5, color=cond.color)

    ax_b.set_xticks(x)
    ax_b.set_xticklabels(dim_labels, fontsize=7)
    ax_b.set_ylabel("Mean score (0–1)", fontsize=7)
    ax_b.set_ylim(0, 1.0)
    ax_b.legend(fontsize=5.5, loc="upper left")
    ax_b.set_title("B  FRQ sub-dimension scores", loc="left", fontweight="bold")

    fig.suptitle("Free-Response Question (FRQ) Dimensions — all conditions",
                 fontsize=9, fontweight="bold", y=1.0)
    save_fig(fig, "fig2_frq_dimensions")


# ---------------------------------------------------------------------------
# Figure 3: Per-sample scatter (baseline vs each treatment)
# ---------------------------------------------------------------------------

def figure_scatter(m: dict) -> None:
    apply_nature_style()

    n_treat = len(TREATMENT_CONDS)
    fig, axes = plt.subplots(2, n_treat, figsize=(7.2, 5.0))
    fig.suptitle("Per-sample comparison: baseline vs. each web-search condition",
                 fontsize=9, fontweight="bold", y=1.01)

    scatter_keys = [
        ("overall",   "Overall Score",  1.0),
        ("frq_score", "FRQ Score",      10.0),
    ]

    for row, (key, title, norm) in enumerate(scatter_keys):
        for col, cond in enumerate(TREATMENT_CONDS):
            ax = axes[row, col]
            if key not in m:
                ax.text(0.5, 0.5, "No data", ha="center", va="center",
                        transform=ax.transAxes, color="gray")
                continue

            ref_key = REF_COND.key
            if ref_key not in m[key] or cond.key not in m[key]:
                ax.text(0.5, 0.5, "No data", ha="center", va="center",
                        transform=ax.transAxes, color="gray")
                continue

            bv    = np.array(m[key][ref_key]) / norm
            wv    = np.array(m[key][cond.key]) / norm
            delta = wv - bv
            cs    = np.where(delta > 0.05, cond.color,
                    np.where(delta < -0.05, "#F44336", "#BDBDBD"))

            ax.scatter(bv, wv, c=cs, s=12, alpha=0.60,
                       edgecolors="white", linewidths=0.3, zorder=3)

            lo = max(0, min(bv.min(), wv.min()) - 0.02)
            hi = min(1, max(bv.max(), wv.max()) + 0.02)
            ax.plot([lo, hi], [lo, hi], "--", color="gray",
                    linewidth=0.9, alpha=0.7, zorder=2)

            if len(bv) >= 4:
                z  = np.polyfit(bv, wv, 1)
                xf = np.linspace(bv.min(), bv.max(), 100)
                ax.plot(xf, np.polyval(z, xf), "-", color="#444",
                        linewidth=1.0, zorder=4)

            r, p_r = stats.pearsonr(bv, wv)
            ax.text(0.04, 0.96,
                    f"r={r:.2f}  Mean Δ={float(np.mean(delta)):+.3f}",
                    transform=ax.transAxes, va="top", fontsize=5.5,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor="#ccc", alpha=0.85))

            ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
            if row == len(scatter_keys) - 1:
                ax.set_xlabel(f"Baseline", fontsize=7)
            if col == 0:
                ax.set_ylabel(f"{title}", fontsize=7)
            letter = chr(ord("A") + row * n_treat + col)
            ax.set_title(f"{letter}  {cond.label}", loc="left",
                         fontweight="bold", fontsize=7)

    fig.tight_layout()
    save_fig(fig, "fig3_scatter")


# ---------------------------------------------------------------------------
# Figure 4: Score distributions (violins)
# ---------------------------------------------------------------------------

def figure_distributions(m: dict) -> None:
    apply_nature_style()

    panels = [
        ("overall",        "Overall Score",   1.0,  "A"),
        ("frq_score",      "FRQ Score",       10.0, "B"),
        ("frq_alignment",  "FRQ Alignment",   10.0, "C"),
        ("frq_specificity","FRQ Specificity", 10.0, "D"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2))
    fig.suptitle("Score distributions — all conditions",
                 fontsize=9, fontweight="bold", y=1.02)

    for ax, (key, title, norm, letter) in zip(axes.ravel(), panels):
        if key not in m:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color="gray")
            continue

        positions = list(range(1, len(CONDITIONS) + 1))
        arrs      = [np.array(m[key].get(c.key, [])) / norm for c in CONDITIONS]
        colors    = [c.color for c in CONDITIONS]

        valid_arrs = [a for a in arrs if len(a) > 0]
        if not valid_arrs:
            continue

        parts = ax.violinplot(valid_arrs, positions=positions[:len(valid_arrs)],
                              showmedians=True, showextrema=False)
        for pc, color in zip(parts["bodies"], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.50)
            pc.set_edgecolor("none")
        parts["cmedians"].set_color("#333")
        parts["cmedians"].set_linewidth(1.5)

        for xi, (arr, color) in enumerate(zip(valid_arrs, colors), start=1):
            jitter = np.random.default_rng(42).uniform(-0.09, 0.09, len(arr))
            ax.scatter(xi + jitter, arr, s=5, color=color, alpha=0.28,
                       edgecolors="none", zorder=3)
            ax.text(xi, float(arr.mean()), f"{arr.mean():.3f}",
                    ha="center", va="bottom", fontsize=5, color=color,
                    fontweight="bold")

        # significance brackets vs baseline
        ref_arr = arrs[0]
        top = max(a.max() for a in valid_arrs if len(a) > 0) + 0.04
        for i, cond in enumerate(TREATMENT_CONDS, start=1):
            if i >= len(valid_arrs):
                continue
            t, p = paired_ttest(list(ref_arr), list(valid_arrs[i]))
            d    = cohen_d(list(valid_arrs[i]), list(ref_arr))
            stars = p_stars(p)
            if stars != "n.s.":
                ax.plot([1, i + 1], [top + 0.02 * i, top + 0.02 * i],
                        color="#888", linewidth=0.7)
                ax.text((1 + i + 1) / 2, top + 0.02 * i + 0.008,
                        f"{stars} d={d:.2f}", ha="center", fontsize=5, color="#333")

        ax.set_xticks(positions[:len(valid_arrs)])
        ax.set_xticklabels([c.label for c in CONDITIONS[:len(valid_arrs)]],
                           fontsize=5.5, rotation=15, ha="right")
        ax.set_ylabel("Score (0–1)", fontsize=7)
        ymax = min(top + 0.15, 1.15)
        ax.set_ylim(0, ymax)
        ax.set_title(f"{letter}  {title}", loc="left", fontweight="bold")

    fig.tight_layout()
    save_fig(fig, "fig4_distributions")


# ---------------------------------------------------------------------------
# Figure 5: Binary task deep-dive (all conditions)
# ---------------------------------------------------------------------------

def figure_binary_detail(m: dict) -> None:
    apply_nature_style()

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8))
    fig.suptitle("Binary task outcomes — all conditions",
                 fontsize=9, fontweight="bold", y=1.03)

    # ── Panel A: accuracy bars ─────────────────────────────────────────────
    ax_a = axes[0]
    tasks = ["Binary\n(original)", "Binary\n(perturbed)", "MCQ"]
    keys  = ["binary", "binary_perturbed", "mcq"]
    x     = np.arange(len(tasks))
    n     = len(CONDITIONS)
    bw    = 0.18
    ek    = {"elinewidth": 0.6, "capsize": 1.5, "ecolor": "#333"}
    offs  = [-(n - 1) / 2 * bw + i * bw for i in range(n)]

    for i, cond in enumerate(CONDITIONS):
        means = [cond_mean(m, k, cond.key) for k in keys]
        ses   = [cond_se(m, k, cond.key)   for k in keys]
        ax_a.bar(x + offs[i], means, bw, yerr=ses,
                 color=cond.color, alpha=0.85, label=cond.label,
                 error_kw=ek, edgecolor="white", linewidth=0.3)

    # significance vs baseline
    for xi, k in enumerate(keys):
        vals = [cond_mean(m, k, c.key) for c in CONDITIONS]
        top  = max(v for v in vals if not np.isnan(v)) + 0.08
        for i, cond in enumerate(TREATMENT_CONDS):
            ci = [c for c in CONDITIONS].index(cond)
            p  = cond_pval(m, k, cond.key, REF_COND.key)
            stars = p_stars(p)
            if stars != "n.s.":
                ax_a.text(xi + offs[ci], top + 0.01 * i,
                          stars, ha="center", fontsize=5, color=cond.color)

    ax_a.axhline(0.5, color="gray", linewidth=0.5, linestyle="--", alpha=0.35)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(tasks, fontsize=7)
    ax_a.set_ylabel("Accuracy", fontsize=7)
    ax_a.set_ylim(0, 1.30)
    ax_a.legend(fontsize=5.5, loc="upper right", ncol=1)
    ax_a.set_title("A  Task accuracies", loc="left", fontweight="bold")

    # ── Panel B: flip matrix (binary original, baseline vs 4o+WS) ─────────
    ax_b = axes[1]
    ref_key  = REF_COND.key
    trt_cond = TREATMENT_CONDS[0]   # 4o+WS no cutoff vs baseline
    trt_key  = trt_cond.key
    if "binary" in m and ref_key in m["binary"] and trt_key in m["binary"]:
        b = np.array([int(v) for v in m["binary"][ref_key]])
        w = np.array([int(v) for v in m["binary"][trt_key]])
        n_tot = len(b)
        grid  = [[int(((b == 1) & (w == 1)).sum()), int(((b == 1) & (w == 0)).sum())],
                 [int(((b == 0) & (w == 1)).sum()), int(((b == 0) & (w == 0)).sum())]]
        lbels = [["Both\ncorrect", "Baseline\nonly"],
                 [f"{trt_cond.label}\nonly", "Both\nwrong"]]
        fcols = [[trt_cond.color, "#E0E0E0"],
                 [REF_COND.color,  "#F44336"]]
        alphs = [[0.75, 0.50], [0.50, 0.75]]

        for ri in range(2):
            for ci in range(2):
                rect = mpatches.FancyBboxPatch(
                    (ci + 0.05, ri + 0.05), 0.88, 0.88,
                    boxstyle="round,pad=0.02",
                    facecolor=fcols[ri][ci], alpha=alphs[ri][ci],
                    edgecolor="white", linewidth=1.5,
                    transform=ax_b.transData,
                )
                ax_b.add_patch(rect)
                cnt = grid[1 - ri][ci]   # flip row for visual layout
                ax_b.text(ci + 0.49, ri + 0.55, f"{cnt}\n({cnt/n_tot:.0%})",
                          ha="center", va="center", fontsize=7, color="black",
                          fontweight="bold")
                ax_b.text(ci + 0.49, ri + 0.14, lbels[1 - ri][ci],
                          ha="center", va="bottom", fontsize=5, color="#333")

        ax_b.set_xlim(0, 2); ax_b.set_ylim(0, 2)
        ax_b.set_xticks([0.5, 1.5])
        ax_b.set_xticklabels([f"{trt_cond.label}\ncorrect",
                               f"{trt_cond.label}\nincorrect"], fontsize=6)
        ax_b.set_yticks([0.5, 1.5])
        ax_b.set_yticklabels(["Base\nincorrect", "Base\ncorrect"], fontsize=6)
        ax_b.spines[["left", "bottom", "right", "top"]].set_visible(False)
        ax_b.tick_params(length=0)
    ax_b.set_title(f"B  Binary flip matrix\n(Base vs {trt_cond.label})",
                   loc="left", fontweight="bold", fontsize=7)

    # ── Panel C: MCQ accuracy across all conditions ───────────────────────
    ax_c = axes[2]
    if "mcq" in m:
        cond_labels = [c.label for c in CONDITIONS]
        mcq_means   = [cond_mean(m, "mcq", c.key) for c in CONDITIONS]
        mcq_cols    = [c.color for c in CONDITIONS]
        bars = ax_c.bar(range(len(CONDITIONS)), mcq_means,
                        color=mcq_cols, alpha=0.85,
                        edgecolor="white", linewidth=0.4, width=0.6)
        for xi, (bar, mv) in enumerate(zip(bars, mcq_means)):
            ax_c.text(bar.get_x() + bar.get_width() / 2,
                      mv + 0.02, f"{mv:.2f}",
                      ha="center", va="bottom", fontsize=6.5, color=mcq_cols[xi])
            if xi > 0:
                cond = CONDITIONS[xi]
                p = cond_pval(m, "mcq", cond.key, REF_COND.key)
                ax_c.text(bar.get_x() + bar.get_width() / 2,
                          mv + 0.07, p_stars(p),
                          ha="center", va="bottom", fontsize=6, color=cond.color)
        ax_c.axhline(0.25, color="gray", linewidth=0.6, linestyle="--", alpha=0.5,
                     label="Chance (25%)")
        ax_c.set_xticks(range(len(CONDITIONS)))
        ax_c.set_xticklabels(cond_labels, fontsize=6, rotation=15, ha="right")
        ax_c.set_ylabel("MCQ Accuracy", fontsize=7)
        ax_c.set_ylim(0, 1.15)
        ax_c.legend(fontsize=6, loc="upper left")
    ax_c.set_title("C  MCQ accuracy by condition", loc="left", fontweight="bold")

    fig.tight_layout()
    save_fig(fig, "fig5_binary_detail")


# ---------------------------------------------------------------------------
# LaTeX tables
# ---------------------------------------------------------------------------

TABLE_ROWS = [
    ("Binary (original)",   "binary",          1.0, "mcnemar"),
    ("Binary (perturbed)",  "binary_perturbed", 1.0, "mcnemar"),
    ("MCQ",                 "mcq",             1.0, "mcnemar"),
    ("FRQ score (0–10)",    "frq_score",       1.0, "ttest"),
    ("Overall composite",   "overall",         1.0, "ttest"),
    ("Joint pass rate",     "joint_pass",       1.0, "mcnemar"),
    ("Outcome pass rate",   "outcome_pass",     1.0, "mcnemar"),
]

FRQ_ROWS = [
    ("FRQ Score (0–10)",    "frq_score",       1.0),
    ("Alignment (0–10)",    "frq_alignment",   1.0),
    ("Specificity (0–10)",  "frq_specificity", 1.0),
    ("Novelty (0–10)",      "frq_novelty",     1.0),
    ("Feasibility (0–10)",  "frq_feasibility", 1.0),
]


def pval_latex(p: float) -> str:
    if np.isnan(p): return "---"
    if p < 0.001:   return "$<\\!0.001$"
    return f"${p:.3f}$"


def _fmt_mean_se(m: dict, key: str, cond_key: str, norm: float = 1.0) -> str:
    if key not in m or cond_key not in m[key]:
        return "---"
    arr = np.array(m[key][cond_key]) / norm
    mu  = float(arr.mean())
    se  = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    return f"${mu:.3f}{{\\pm}}{se:.3f}$"


def _fmt_delta_p(m: dict, key: str, treat_key: str, ref_key: str,
                 norm: float, test: str) -> str:
    d = cond_delta(m, key, treat_key, ref_key, norm)
    p = cond_pval(m, key, treat_key, ref_key, test)
    if np.isnan(d):
        return "---"
    s = p_stars(p)
    p_str = pval_latex(p)
    if s != "n.s.":
        p_str = p_str + f"~\\textbf{{{s}}}"
    sign = "+" if d >= 0 else ""
    return f"${sign}{d:.3f}$ ({p_str})"


def make_latex_main_table(m: dict) -> None:
    """
    Table structure:
      Metric | n | Baseline | 4o+WS (Δ, p) | 4o+WS+Cut (Δ, p) | 5.4+WS+Cut (Δ, p)
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ref = REF_COND
    treats = TREATMENT_CONDS

    # Column spec: l c c | c c | c c | c c  (metric, n, baseline, then 2 cols per treatment)
    n_extra = len(treats)
    col_spec = "l c c " + " ".join(["c" for _ in range(n_extra)])

    header_conds = " & ".join(
        f"\\makecell{{{t.label_long}\\\\ $\\Delta$ (p)}}" for t in treats
    )

    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\caption{Performance on the matched 500-question subset across conditions. "
        r"Values are mean~$\pm$~SE. "
        r"$\Delta$ is relative to the Baseline. "
        r"Significance: *** $p<0.001$, ** $p<0.01$, * $p<0.05$, n.s.\ not significant.}",
        r"\label{tab:web_search_main}",
        r"\setlength{\tabcolsep}{4pt}",
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        f"Metric & $n$ & {ref.label_long} & " + header_conds + r" \\",
        r"\midrule",
    ]

    for display, key, norm, test in TABLE_ROWS:
        if key not in m:
            lines.append(f"{display} & --- & --- & " +
                         " & ".join(["---"] * n_extra) + r" \\")
            continue
        n_obs = len(m[key][ref.key])
        base_str = _fmt_mean_se(m, key, ref.key, norm)
        treat_strs = [_fmt_delta_p(m, key, t.key, ref.key, norm, test)
                      for t in treats]
        lines.append(f"{display} & {n_obs} & {base_str} & " +
                     " & ".join(treat_strs) + r" \\")

    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]

    path = OUT_DIR / "table1_main.tex"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Saved table1_main.tex")


def make_latex_frq_table(m: dict) -> None:
    """FRQ sub-dimensions table with all conditions."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ref    = REF_COND
    treats = TREATMENT_CONDS
    n_extra = len(treats)
    col_spec = "l c c " + " ".join(["c" for _ in range(n_extra)])

    header_conds = " & ".join(
        f"\\makecell{{{t.label_long}\\\\ $\\Delta$ (p, $d$)}}" for t in treats
    )

    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\small",
        r"\caption{FRQ sub-dimension scores (0–10) on the matched 500-question subset. "
        r"$\Delta$ is relative to Baseline; $d$ is Cohen's $d$ effect size. "
        r"Significance: *** $p<0.001$, ** $p<0.01$, * $p<0.05$.}",
        r"\label{tab:web_search_frq}",
        r"\setlength{\tabcolsep}{4pt}",
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        f"Dimension & $n$ & {ref.label_long} & " + header_conds + r" \\",
        r"\midrule",
    ]

    for display, key, norm in FRQ_ROWS:
        if key not in m:
            lines.append(f"{display} & --- & --- & " +
                         " & ".join(["---"] * n_extra) + r" \\")
            continue
        n_obs    = len(m[key][ref.key])
        base_str = _fmt_mean_se(m, key, ref.key, norm)

        treat_strs = []
        for t in treats:
            d_val = cond_delta(m, key, t.key, ref.key, norm)
            p_val = cond_pval(m, key, t.key, ref.key, "ttest")
            d_eff = cohen_d(
                [v / norm for v in m[key][t.key]],
                [v / norm for v in m[key][ref.key]],
            )
            if np.isnan(d_val):
                treat_strs.append("---")
                continue
            sign  = "+" if d_val >= 0 else ""
            p_str = pval_latex(p_val)
            stars = p_stars(p_val)
            if stars != "n.s.":
                p_str = p_str + f"~\\textbf{{{stars}}}"
            treat_strs.append(f"${sign}{d_val:.2f}$ ({p_str}, $d={d_eff:.2f}$)")

        lines.append(f"{display} & {n_obs} & {base_str} & " +
                     " & ".join(treat_strs) + r" \\")

    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]

    path = OUT_DIR / "table2_frq_dimensions.tex"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Saved table2_frq_dimensions.tex")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading all conditions...")
    cond_data = load_all_conditions()

    print("Finding shared IDs...")
    ids = get_shared_ids(cond_data)

    print("Extracting paired metrics...")
    m = extract_metrics(cond_data, ids)

    print("\nKey metrics by condition:")
    for key in sorted(m.keys()):
        row = "  " + f"{key:25s}"
        for cond in CONDITIONS:
            val = cond_mean(m, key, cond.key)
            row += f"  {cond.label:15s}={val:.4f}"
        print(row)

    print(f"\nGenerating figures → {OUT_DIR}/")
    figure_overview(m)
    figure_frq_dimensions(m)
    figure_scatter(m)
    figure_distributions(m)
    figure_binary_detail(m)

    print("\nGenerating LaTeX tables...")
    make_latex_main_table(m)
    make_latex_frq_table(m)

    print("\nDone.")


if __name__ == "__main__":
    main()
