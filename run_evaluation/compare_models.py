"""
compare_models.py — Multi-model comparison plots for the CUSP benchmark.

Produces publication-quality figures:
  fig1_leaderboard           : ranked grouped bars + performance matrix
  fig2_radar                 : multi-model radar — task axes (Binary, MCQ, Date)
  fig3_area_heatmap          : MCQ / binary accuracy heatmap per area × model
  fig4_bias                  : binary response-bias scatter + bias-index bars
  fig5_cutoff_temporal       : MCQ accuracy vs publication date & months-since-cutoff
  fig6_area_radar            : small-multiple radars — research-area axes per model (MCQ)
  fig14_cusp_area_radar      : small-multiple radars — research-area axes per model (aggregate CUSP)
  fig7_date_errors           : date-prediction error deep-dive (CDF, violin, anchoring)
  fig8_date_predictions      : predicted vs ground-truth date hexbin scatter
  fig9_response_distributions: Yes/No rates, MCQ A–D frequency, date KDE, position heatmap

Usage
-----
  python compare_models.py \\
      --results   /path/to/model_results/ \\
      --benchmark /path/to/merged_validated_cusp_fixed.jsonl \\
      [--output-dir figures/comparison/] [--show]

Edit MODEL_REGISTRY below to adjust model names, training cutoffs (YYYY-MM),
colours, and marker styles.

Requirements: matplotlib ≥ 3.5, numpy  (pip install matplotlib numpy)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np

# ---------------------------------------------------------------------------
# Model registry — Okabe–Ito colorblind-safe palette
# ---------------------------------------------------------------------------
# Cutoff dates (YYYY-MM) are approximate training-data cutoffs, used in fig5.
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

# Task bar colours (ColorBrewer qualitative, print-safe)
TASK_COLORS = {
    "binary": "#2166AC",   # deep blue
    "mcq":    "#B2182B",   # deep red
    "date":   "#1A9850",   # deep green
}

# Research-area display ordering and short labels
AREA_ORDER = [
    "Biology",
    "Artificial Intelligence",
    "Medicine",
    "Neuroscience",
    "Materials Science",
    "Physics",
    "Environmental Science",
    "Chemistry",
    "Other",
]

AREA_SHORT = {
    "Artificial Intelligence": "AI",
    "Environmental Science":   "Env.\nSci.",
    "Materials Science":       "Mat.\nSci.",
    "Neuroscience":            "Neurosci.",
    "Biology":                 "Biology",
    "Medicine":                "Medicine",
    "Physics":                 "Physics",
    "Chemistry":               "Chemistry",
    "Other":                   "Other",
}

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

def apply_nature_style() -> None:
    """Apply Nature-journal-compatible matplotlib settings."""
    plt.rcParams.update({
        # Typography
        "font.family":          "sans-serif",
        "font.sans-serif":      ["Arial", "Helvetica Neue", "DejaVu Sans"],
        "font.size":            7,
        "axes.labelsize":       7,
        "axes.titlesize":       7.5,
        "axes.titleweight":     "bold",
        "axes.titlepad":        5,
        "xtick.labelsize":      6,
        "ytick.labelsize":      6,
        # Legend
        "legend.fontsize":      6,
        "legend.title_fontsize":6,
        "legend.frameon":       True,
        "legend.framealpha":    0.92,
        "legend.edgecolor":     "#cccccc",
        "legend.borderpad":     0.5,
        "legend.handlelength":  1.6,
        "legend.handleheight":  0.9,
        "legend.labelspacing":  0.35,
        "legend.columnspacing": 0.8,
        # Figure
        "figure.dpi":           300,
        "savefig.dpi":          300,
        "savefig.bbox":         "tight",
        "pdf.fonttype":         42,   # editable text in Illustrator / Inkscape
        "ps.fonttype":          42,
        # Axes
        "axes.linewidth":       0.6,
        "axes.labelpad":        3,
        "axes.spines.right":    False,
        "axes.spines.top":      False,
        "axes.grid":            False,
        # Ticks
        "xtick.major.width":    0.6,
        "ytick.major.width":    0.6,
        "xtick.major.size":     2.5,
        "ytick.major.size":     2.5,
        "xtick.direction":      "out",
        "ytick.direction":      "out",
        # Lines / markers
        "lines.linewidth":      1.2,
        "lines.markersize":     4,
        "lines.markeredgewidth":0.5,
    })


def _panel_label(ax: plt.Axes, letter: str,
                 x: float = -0.10, y: float = 1.06) -> None:
    """Add a bold panel label (A, B, …) in the upper-left of the axes."""
    ax.text(x, y, letter, transform=ax.transAxes,
            fontsize=9, fontweight="bold", va="top", ha="right",
            clip_on=False)


def save_fig(fig: plt.Figure, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(out_dir / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}.pdf / .png")


def _open_file(path: Path) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        elif system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _sm(lst: list) -> float:
    return float(np.mean(lst)) if lst else float("nan")


def _date_to_months(s: str) -> float | None:
    try:
        parts = str(s).split("-")
        return (int(parts[0]) - 2020) * 12 + int(parts[1])
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_benchmark_meta(benchmark_path: str) -> dict[str, dict]:
    id_meta: dict[str, dict] = {}
    with open(benchmark_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rid = row.get("id")
                if rid:
                    id_meta[rid] = {
                        "main_area":        row.get("main_area", "Unknown"),
                        "publication_date": row.get("publication_date", ""),
                    }
            except json.JSONDecodeError:
                pass
    return id_meta


def load_model(filepath: str, cfg: dict, id_meta: dict) -> dict:
    with open(filepath, encoding="utf-8") as f:
        report = json.load(f)

    tm = report.get("task_metrics", {})

    bin_n = tm.get("binary",           {}).get("count",   0)
    bin_c = tm.get("binary",           {}).get("correct", 0)
    bp_n  = tm.get("binary_perturbed", {}).get("count",   0)
    bp_c  = tm.get("binary_perturbed", {}).get("correct", 0)
    merged_n, merged_c = bin_n + bp_n, bin_c + bp_c

    cutoff_m = _date_to_months(cfg["cutoff"])

    area_binary: dict[str, list] = defaultdict(list)
    area_mcq:    dict[str, list] = defaultdict(list)
    area_date:   dict[str, list] = defaultdict(list)
    # Post-cutoff only (offset >= 0) area breakdowns
    area_mcq_post:    dict[str, list] = defaultdict(list)
    area_binary_post: dict[str, list] = defaultdict(list)
    abs_mcq:     dict[int, list] = defaultdict(list)
    abs_binary:  dict[int, list] = defaultdict(list)
    rel_mcq:     dict[int, list] = defaultdict(list)
    rel_binary:  dict[int, list] = defaultdict(list)
    # Date-prediction detail
    date_signed:     list[float] = []   # signed error: predicted − actual (months)
    date_pred_m:     list[float] = []   # predicted date in months-since-2020
    date_gt_m:       list[float] = []   # ground-truth date in months-since-2020
    date_abs_err:    list[float] = []   # |predicted − actual|
    rel_date_signed: dict[int, list] = defaultdict(list)   # offset → signed errors
    area_date_dist:  dict[str, list] = defaultdict(list)   # area → |errors|
    # MCQ response-option tracking (A/B/C/D chosen vs correct)
    mcq_choices:         dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0}
    mcq_correct_options: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0}
    # Calibration data: (confidence, correct_0_or_1) or (confidence, abs_error_months)
    binary_calib: list[tuple[float, int]]   = []
    mcq_calib:    list[tuple[float, int]]   = []
    date_calib:   list[tuple[float, float]] = []   # (confidence, |error| months)
    # Pre/post-cutoff calibration split (offset < 0 = pre, offset >= 0 = post)
    binary_pre_calib:  list[tuple[float, int]] = []
    binary_post_calib: list[tuple[float, int]] = []
    mcq_pre_calib:     list[tuple[float, int]] = []
    mcq_post_calib:    list[tuple[float, int]] = []
    # Date pre/post calibration: (confidence, within_12_months: 0/1)
    date_pre_calib:  list[tuple[float, int]] = []
    date_post_calib: list[tuple[float, int]] = []
    # FRQ data
    frq_scores:      list[float] = []
    frq_alignment:   list[float] = []
    frq_specificity: list[float] = []
    frq_novelty:     list[float] = []
    frq_feasibility: list[float] = []
    area_frq:        dict[str, list] = defaultdict(list)
    # Per-question MCQ-vs-FRQ pairing (for consistency analysis)
    frq_when_mcq_correct: list[float] = []
    frq_when_mcq_wrong:   list[float] = []

    for row in report.get("results", []):
        rid    = row.get("id", "")
        meta   = id_meta.get(rid, {})
        area   = meta.get("main_area", "Unknown")
        pub    = meta.get("publication_date", "")
        pub_m  = _date_to_months(pub)
        offset = (int(pub_m - cutoff_m)
                  if (pub_m is not None and cutoff_m is not None) else None)

        tasks = row.get("tasks", {})

        bin_vals: list[int] = []
        for key in ("binary", "binary_perturbed"):
            t = tasks.get(key)
            if t and not t.get("skipped"):
                v_bin = int(bool(t.get("correct")))
                bin_vals.append(v_bin)
                if t.get("confidence") is not None:
                    conf_bin = float(t["confidence"])
                    binary_calib.append((conf_bin, v_bin))
                    if offset is not None:
                        (binary_pre_calib if offset < 0 else binary_post_calib).append((conf_bin, v_bin))
        if bin_vals:
            area_binary[area].extend(bin_vals)
            if offset is not None and offset >= 0:
                area_binary_post[area].extend(bin_vals)
            if pub_m is not None:
                abs_binary[int(pub_m)].extend(bin_vals)
            if offset is not None:
                rel_binary[offset].extend(bin_vals)

        mcq_correct_this: bool | None = None
        t = tasks.get("mcq")
        if t and not t.get("skipped"):
            v = int(bool(t.get("correct")))
            mcq_correct_this = bool(t.get("correct"))
            area_mcq[area].append(v)
            if offset is not None and offset >= 0:
                area_mcq_post[area].append(v)
            if t.get("confidence") is not None:
                conf_mcq = float(t["confidence"])
                mcq_calib.append((conf_mcq, v))
                if offset is not None:
                    (mcq_pre_calib if offset < 0 else mcq_post_calib).append((conf_mcq, v))
            if pub_m is not None:
                abs_mcq[int(pub_m)].append(v)
            if offset is not None:
                rel_mcq[offset].append(v)
            # Track which option was chosen and which was correct
            for field in ("parsed_answer", "model_answer", "response", "answer",
                          "chosen", "selected"):
                raw = t.get(field)
                if raw is not None:
                    letter = str(raw).strip().upper()[:1]
                    if letter in "ABCD":
                        mcq_choices[letter] += 1
                        break
            for field in ("ground_truth", "correct_answer", "answer_key",
                          "correct_option", "gold"):
                raw = t.get(field)
                if raw is not None:
                    letter = str(raw).strip().upper()[:1]
                    if letter in "ABCD":
                        mcq_correct_options[letter] += 1
                        break

        t = tasks.get("date")
        if t and not t.get("skipped"):
            if t.get("score") is not None:
                area_date[area].append(float(t["score"]))
            pd_str = t.get("parsed_date")
            gt_str = t.get("ground_truth")
            dist   = t.get("month_distance")
            pm_d   = _date_to_months(pd_str)
            gm_d   = _date_to_months(gt_str)
            if pm_d is not None and gm_d is not None:
                signed = float(pm_d - gm_d)
                date_signed.append(signed)
                date_pred_m.append(float(pm_d))
                date_gt_m.append(float(gm_d))
                date_abs_err.append(abs(signed))
                if offset is not None:
                    rel_date_signed[offset].append(signed)
            if dist is not None:
                area_date_dist[area].append(float(dist))
                if t.get("confidence") is not None:
                    conf_d   = float(t["confidence"])
                    within12 = int(dist <= 12)
                    date_calib.append((conf_d, float(dist)))
                    if offset is not None:
                        (date_pre_calib if offset < 0 else date_post_calib).append((conf_d, within12))

        t = tasks.get("frq")
        if t and t.get("score") is not None:
            fs = float(t["score"])
            frq_scores.append(fs)
            area_frq[area].append(fs)
            for dim, lst in (
                ("alignment",   frq_alignment),
                ("specificity", frq_specificity),
                ("novelty",     frq_novelty),
                ("feasibility", frq_feasibility),
            ):
                if t.get(dim) is not None:
                    lst.append(float(t[dim]))
            if mcq_correct_this is True:
                frq_when_mcq_correct.append(fs)
            elif mcq_correct_this is False:
                frq_when_mcq_wrong.append(fs)

    return {
        "name":          cfg["name"],
        "short":         cfg["short"],
        "cutoff":        cfg["cutoff"],
        "cutoff_months": cutoff_m,
        "color":         cfg["color"],
        "marker":        cfg["marker"],
        "ls":            cfg["ls"],
        "binary_acc":           tm.get("binary",           {}).get("accuracy",   float("nan")),
        "binary_perturbed_acc": tm.get("binary_perturbed", {}).get("accuracy",   float("nan")),
        "merged_binary_acc":    merged_c / merged_n if merged_n > 0 else float("nan"),
        "mcq_acc":              tm.get("mcq",  {}).get("accuracy",   float("nan")),
        "date_score":           tm.get("date", {}).get("mean_score", float("nan")),
        "date_median_dist":     tm.get("date", {}).get("median_month_distance", float("nan")),
        "area_binary": dict(area_binary),
        "area_mcq":    dict(area_mcq),
        "area_date":   dict(area_date),
        "area_mcq_post":    dict(area_mcq_post),
        "area_binary_post": dict(area_binary_post),
        "abs_mcq":    dict(abs_mcq),
        "abs_binary": dict(abs_binary),
        "rel_mcq":    dict(rel_mcq),
        "rel_binary": dict(rel_binary),
        # Date prediction detail
        "date_signed":     date_signed,
        "date_pred_m":     date_pred_m,
        "date_gt_m":       date_gt_m,
        "date_abs_err":    date_abs_err,
        "rel_date_signed": dict(rel_date_signed),
        "area_date_dist":  dict(area_date_dist),
        # Binary count detail (for Yes/No rate computation)
        "bin_n": bin_n,
        "bin_c": bin_c,
        "bp_n":  bp_n,
        "bp_c":  bp_c,
        # MCQ option-level tracking
        "mcq_choices":         dict(mcq_choices),
        "mcq_correct_options": dict(mcq_correct_options),
        # Calibration data
        "binary_calib":      binary_calib,
        "mcq_calib":         mcq_calib,
        "date_calib":        date_calib,
        "binary_pre_calib":  binary_pre_calib,
        "binary_post_calib": binary_post_calib,
        "mcq_pre_calib":     mcq_pre_calib,
        "mcq_post_calib":    mcq_post_calib,
        "date_pre_calib":    date_pre_calib,
        "date_post_calib":   date_post_calib,
        # FRQ data
        "frq_scores":            frq_scores,
        "frq_alignment":         frq_alignment,
        "frq_specificity":       frq_specificity,
        "frq_novelty":           frq_novelty,
        "frq_feasibility":       frq_feasibility,
        "frq_mean":    float(np.mean(frq_scores))                           if frq_scores else float("nan"),
        "frq_pass":    sum(s >= 5.0 for s in frq_scores) / len(frq_scores) if frq_scores else float("nan"),
        "area_frq":    dict(area_frq),
        "frq_when_mcq_correct": frq_when_mcq_correct,
        "frq_when_mcq_wrong":   frq_when_mcq_wrong,
    }


def _composite(m: dict) -> float:
    vals = [v for v in (m["merged_binary_acc"], m["mcq_acc"], m["date_score"])
            if not np.isnan(v)]
    return sum(vals) / len(vals) if vals else 0.0


def load_all_models(results_dir: str, benchmark_path: str | None) -> list[dict]:
    results_dir = Path(results_dir)
    id_meta: dict[str, dict] = {}
    if benchmark_path:
        print(f"Loading benchmark metadata: {benchmark_path}")
        id_meta = load_benchmark_meta(benchmark_path)
        print(f"  {len(id_meta)} rows indexed")

    models: list[dict] = []
    for filename, cfg in MODEL_REGISTRY.items():
        fpath = results_dir / filename
        if not fpath.exists():
            print(f"  SKIP {filename} (not found)")
            continue
        print(f"Loading {cfg['name']} ...")
        models.append(load_model(str(fpath), cfg, id_meta))

    models.sort(key=_composite)   # ascending — best at top of horizontal bars
    return models


# ---------------------------------------------------------------------------
# Figure 1 — Leaderboard
# ---------------------------------------------------------------------------

def figure_leaderboard(models: list[dict], out_dir: Path) -> None:
    apply_nature_style()

    n  = len(models)
    y  = np.arange(n)
    bw = 0.22

    merged_b = np.array([m["merged_binary_acc"] for m in models])
    mcq_v    = np.array([m["mcq_acc"]           for m in models])
    date_v   = np.array([m["date_score"]         for m in models])
    names    = [m["short"] for m in models]

    fig = plt.figure(figsize=(7.2, max(3.2, 0.58 * n + 1.4)))
    gs  = GridSpec(1, 2, figure=fig, width_ratios=[2.8, 1.0], wspace=0.05,
                   left=0.20, right=0.96, top=0.90, bottom=0.13)
    ylim = (-0.55, n - 0.45)

    # ── A: Grouped horizontal bars ────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    _panel_label(ax_a, "A")

    kw = dict(edgecolor="white", linewidth=0.4, alpha=0.88)
    ax_a.barh(y + bw,  merged_b, bw, color=TASK_COLORS["binary"],
              label="Binary (merged)", **kw)
    ax_a.barh(y,       mcq_v,    bw, color=TASK_COLORS["mcq"],
              label="MCQ",            **kw)
    ax_a.barh(y - bw,  date_v,   bw, color=TASK_COLORS["date"],
              label="Date score",     **kw)

    # Chance reference lines — subtle dotted
    ax_a.axvline(0.50, color=TASK_COLORS["binary"], lw=0.6, ls=":",
                 alpha=0.35, zorder=0)
    ax_a.axvline(0.25, color=TASK_COLORS["mcq"],    lw=0.6, ls=":",
                 alpha=0.35, zorder=0)

    # Value annotations
    for i, (b, m, d) in enumerate(zip(merged_b, mcq_v, date_v)):
        for val, row_off in ((b, bw), (m, 0), (d, -bw)):
            if not np.isnan(val):
                ax_a.text(val + 0.010, i + row_off, f"{val:.2f}",
                          va="center", ha="left", fontsize=5.2,
                          color="#333333")

    ax_a.set_yticks(y)
    ax_a.set_yticklabels(names, fontsize=7)
    ax_a.set_xlabel("Accuracy / Score (0–1)", fontsize=7)
    ax_a.set_xlim(0, 0.80)
    ax_a.set_ylim(*ylim)
    ax_a.spines["left"].set_visible(False)
    ax_a.tick_params(axis="y", length=0)
    ax_a.legend(loc="lower right", ncol=1, fontsize=5.5,
                handlelength=1.0, handletextpad=0.4)
    ax_a.set_title("Task performance by model", loc="left")

    # Dotted vertical separators at chance levels — label them at top
    for xv, lbl, col in (
        (0.25, "MCQ chance",    TASK_COLORS["mcq"]),
        (0.50, "Binary chance", TASK_COLORS["binary"]),
    ):
        ax_a.text(xv, n - 0.42, lbl, ha="center", va="bottom",
                  fontsize=4.5, color=col, alpha=0.7, rotation=90)

    # ── B: Ranking matrix ─────────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    _panel_label(ax_b, "B", x=-0.06)

    data_mat  = np.column_stack([merged_b, mcq_v, date_v])
    rank_mat  = np.full_like(data_mat, np.nan)
    for j in range(3):
        col  = data_mat[:, j]
        vidx = np.where(~np.isnan(col))[0]
        order = vidx[np.argsort(-col[vidx])]
        for rk, idx in enumerate(order, 1):
            rank_mat[idx, j] = rk

    masked = np.ma.masked_invalid(rank_mat)
    ax_b.imshow(masked, cmap="RdYlGn_r", vmin=1, vmax=n,
                aspect="auto", interpolation="nearest")

    for i in range(n):
        for j in range(3):
            v  = data_mat[i, j]
            rk = rank_mat[i, j]
            if not np.isnan(v):
                fg = "white" if (not np.isnan(rk) and (rk <= 1.5 or rk >= n - 0.5)) else "#222"
                ax_b.text(j, i, f"#{int(rk)}\n{v:.2f}",
                          ha="center", va="center",
                          fontsize=4.6, color=fg, linespacing=1.2)

    ax_b.set_xticks([0, 1, 2])
    ax_b.set_xticklabels(["Binary\n(merged)", "MCQ", "Date\nscore"], fontsize=5.5)
    ax_b.set_yticks(range(n))
    ax_b.set_yticklabels([])
    ax_b.xaxis.set_tick_params(length=0)
    ax_b.yaxis.set_tick_params(length=0)
    ax_b.set_ylim(*ylim)
    for sp in ax_b.spines.values():
        sp.set_visible(False)
    ax_b.set_title("Rank\n(green = best)", loc="left", fontsize=6)

    fig.suptitle("CUSP Benchmark — Multi-model performance comparison",
                 fontsize=8.5, fontweight="bold", y=0.97)
    save_fig(fig, out_dir, "fig1_leaderboard")


# ---------------------------------------------------------------------------
# Figure 2 — Task radar (spokes = Binary / MCQ / Date)
# ---------------------------------------------------------------------------

def figure_radar(models: list[dict], out_dir: Path) -> None:
    apply_nature_style()

    spokes   = ["Binary\n(merged)", "MCQ", "Date\nscore"]
    N        = len(spokes)
    angles   = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles_c = angles + [angles[0]]

    fig = plt.figure(figsize=(5.6, 4.6))
    ax  = fig.add_subplot(111, projection="polar")

    for m in reversed(models):
        vals = [
            float(m["merged_binary_acc"]) if not np.isnan(m["merged_binary_acc"]) else 0.0,
            float(m["mcq_acc"])           if not np.isnan(m["mcq_acc"])           else 0.0,
            float(m["date_score"])        if not np.isnan(m["date_score"])        else 0.0,
        ]
        vals_c = vals + [vals[0]]
        ax.plot(angles_c, vals_c, linestyle=m["ls"], marker=m["marker"],
                color=m["color"], linewidth=1.5, markersize=5, zorder=3, alpha=0.92,
                label=f"{m['short']}  [{m['cutoff']}]")
        ax.fill(angles_c, vals_c, alpha=0.07, color=m["color"])

    # Chance reference rings (dotted)
    ax.plot(angles_c, [0.50] * (N + 1), ":", color=TASK_COLORS["binary"],
            lw=0.7, alpha=0.45)
    ax.plot(angles_c, [0.25] * (N + 1), ":", color=TASK_COLORS["mcq"],
            lw=0.7, alpha=0.45)

    ax.set_xticks(angles)
    ax.set_xticklabels(spokes, size=7.5, color="#222222")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], size=5, color="#777")
    ax.spines["polar"].set_linewidth(0.4)
    ax.grid(lw=0.35, alpha=0.45, color="#888888")

    fig.legend(loc="center right", bbox_to_anchor=(1.22, 0.50),
               fontsize=6, ncol=1, handlelength=1.8,
               title="Model  [cutoff]", title_fontsize=6)
    fig.suptitle("CUSP Benchmark — overall task performance by model",
                 fontsize=8.5, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 0.78, 1])
    save_fig(fig, out_dir, "fig2_radar")


# ---------------------------------------------------------------------------
# Figure 3 — Area × model heatmaps
# ---------------------------------------------------------------------------

def figure_area_heatmap(models: list[dict], out_dir: Path) -> None:
    apply_nature_style()

    n_m         = len(models)
    n_a         = len(AREA_ORDER)
    m_names     = [m["short"] for m in models]
    area_labels = [AREA_SHORT.get(a, a).replace("\n", " ") for a in AREA_ORDER]

    mat_mcq    = np.full((n_a, n_m), np.nan)
    mat_binary = np.full((n_a, n_m), np.nan)

    for j, m in enumerate(models):
        for i, area in enumerate(AREA_ORDER):
            if m["area_mcq"].get(area):
                mat_mcq[i, j]    = _sm(m["area_mcq"][area])
            if m["area_binary"].get(area):
                mat_binary[i, j] = _sm(m["area_binary"][area])

    fig, axes = plt.subplots(1, 2, figsize=(7.8, 5.8))
    fig.suptitle("Task accuracy by scientific domain — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=1.01)

    panels = [
        (axes[0], mat_mcq,    "A", "MCQ accuracy",          0.25),
        (axes[1], mat_binary, "B", "Binary merged accuracy", 0.50),
    ]

    for ax, mat, letter, title, chance in panels:
        _panel_label(ax, letter)
        masked = np.ma.masked_invalid(mat)
        im = ax.imshow(masked, aspect="auto", vmin=0, vmax=1,
                       cmap="RdYlGn", interpolation="nearest")

        for i in range(n_a):
            for j in range(n_m):
                v = mat[i, j]
                if not np.isnan(v):
                    # White text on dark cells, dark text on light cells
                    fg = "white" if (v < 0.22 or v > 0.72) else "#1a1a1a"
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                            fontsize=5.5, color=fg, fontweight="normal")
                    if v < chance:
                        # Subtle red border on below-chance cells
                        rect = plt.Rectangle(
                            (j - 0.49, i - 0.49), 0.98, 0.98,
                            fill=False, edgecolor="#CC3311",
                            linewidth=0.85, zorder=4,
                        )
                        ax.add_patch(rect)

        ax.set_xticks(range(n_m))
        ax.set_xticklabels(m_names, rotation=40, ha="right", fontsize=6)
        ax.set_yticks(range(n_a))
        ax.set_yticklabels(area_labels if ax is axes[0] else [], fontsize=6.5)
        ax.xaxis.set_tick_params(length=0)
        ax.yaxis.set_tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)

        cb = fig.colorbar(im, ax=ax, shrink=0.78, pad=0.03, aspect=22)
        cb.set_label("Accuracy (0–1)", fontsize=5.5)
        cb.ax.tick_params(labelsize=5)
        cb.outline.set_linewidth(0.4)
        if chance is not None:
            cb.ax.axhline(chance, color="#CC3311", linewidth=0.9)

        ax.set_title(title, loc="left", pad=4)
        ax.text(0.99, -0.11,
                f"Red border = below chance ({chance:.2f})",
                transform=ax.transAxes, ha="right",
                fontsize=4.8, color="#CC3311", style="italic")

    fig.tight_layout(w_pad=2.0)
    save_fig(fig, out_dir, "fig3_area_heatmap")


# ---------------------------------------------------------------------------
# Figure 4 — Binary response-bias analysis
# ---------------------------------------------------------------------------

def figure_bias(models: list[dict], out_dir: Path) -> None:
    apply_nature_style()

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.2, 3.2),
                                      gridspec_kw={"wspace": 0.38})
    fig.suptitle("Binary response-bias analysis — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=1.03)

    # ── A: Scatter ────────────────────────────────────────────────────────
    _panel_label(ax_a, "A")
    ax_a.set_title("Response-bias diagram", loc="left")

    xs = np.linspace(0, 1, 200)
    # Pure-bias anti-diagonal
    ax_a.plot(xs, 1 - xs, "--", color="#999999", lw=0.9, alpha=0.7, zorder=1)
    ax_a.fill_between(xs, 1 - xs, 1.0, alpha=0.04, color="#2166AC")   # "No" zone
    ax_a.fill_between(xs, 0,      1 - xs, alpha=0.04, color="#B2182B") # "Yes" zone

    # Merged iso-lines
    for mv, ls, al in ((0.60, ":", 0.25), (0.50, "--", 0.30), (0.40, ":", 0.25)):
        # x + y = 2*mv  →  y = 2*mv - x
        ax_a.plot(xs, np.clip(2 * mv - xs, 0, 1), ls=ls, color="#aaaaaa",
                  lw=0.55, alpha=al, zorder=1)
        # Label at right edge
        x_lbl = min(1.0, 2 * mv)
        ax_a.text(x_lbl - 0.02, max(0, 2 * mv - x_lbl) + 0.01,
                  f"merged={mv:.1f}", fontsize=4.2, color="#aaaaaa", ha="right")

    ax_a.axhline(0.5, color="#888", lw=0.45, ls=":", alpha=0.4)
    ax_a.axvline(0.5, color="#888", lw=0.45, ls=":", alpha=0.4)

    # Ideal corner star
    ax_a.scatter([1.0], [1.0], marker="*", s=90, color="#FFD700",
                 edgecolors="#888", linewidths=0.5, zorder=7)
    ax_a.text(0.97, 0.97, "Ideal", ha="right", va="top", fontsize=5, color="#555")

    # Per-model annotation positions (hand-tuned to avoid collisions)
    label_off = {
        "Claude S4.5":  (-0.04, +0.04),
        "GPT-4o":       (+0.03, -0.05),
        "GPT-5.4":      (+0.03, +0.03),
        "DeepSeek R1":  (-0.04, +0.04),
        "GPT-OSS 20B":  (+0.03, -0.05),
        "LLaMA 3.3":    (+0.03, +0.03),
    }

    for m in models:
        x, y = m["binary_acc"], m["binary_perturbed_acc"]
        if np.isnan(x) or np.isnan(y):
            continue
        ax_a.scatter(x, y, color=m["color"], marker=m["marker"],
                     s=72, zorder=5, edgecolors="white", linewidths=0.6,
                     label=m["short"])
        dx, dy = label_off.get(m["short"], (0.03, 0.03))
        ax_a.text(x + dx, y + dy, m["short"], fontsize=5, color=m["color"],
                  ha="left" if dx >= 0 else "right",
                  va="bottom" if dy >= 0 else "top")

    ax_a.text(0.05, 0.94, '"Yes" bias', transform=ax_a.transAxes,
              fontsize=5.5, color="#B2182B", style="italic", va="top")
    ax_a.text(0.94, 0.07, '"No" bias', transform=ax_a.transAxes,
              fontsize=5.5, color="#2166AC", style="italic", ha="right")

    ax_a.set_xlabel('Binary accuracy  (ground truth = "Yes")', fontsize=7)
    ax_a.set_ylabel('Perturbed accuracy  (ground truth = "No")', fontsize=7)
    ax_a.set_xlim(-0.04, 1.06)
    ax_a.set_ylim(-0.04, 1.06)
    ax_a.set_aspect("equal", adjustable="box")

    # ── B: Bias-index bars ────────────────────────────────────────────────
    _panel_label(ax_b, "B")
    ax_b.set_title("Bias index (binary − perturbed)", loc="left")

    bias_v   = [m["binary_acc"] - m["binary_perturbed_acc"] for m in models]
    merged_v = [m["merged_binary_acc"] for m in models]
    order    = np.argsort(bias_v)

    bias_s   = [bias_v[i]   for i in order]
    merged_s = [merged_v[i] for i in order]
    color_s  = [models[i]["color"]  for i in order]
    name_s   = [models[i]["short"]  for i in order]

    y = np.arange(len(models))
    bars = ax_b.barh(y, bias_s, color=color_s,
                     alpha=0.88, edgecolor="white", linewidth=0.4, height=0.58)
    ax_b.axvline(0, color="#333333", lw=0.8, zorder=3)
    for xv in (-0.5, +0.5):
        ax_b.axvline(xv, color="#aaaaaa", lw=0.5, ls=":", alpha=0.5, zorder=2)

    for bar, bv, mv in zip(bars, bias_s, merged_s):
        off, ha = (0.03, "left") if bv >= 0 else (-0.03, "right")
        ax_b.text(bv + off, bar.get_y() + bar.get_height() / 2,
                  f"  Δ={bv:+.2f}  merged={mv:.2f}",
                  va="center", ha=ha, fontsize=5)

    ax_b.set_yticks(y)
    ax_b.set_yticklabels(name_s, fontsize=7)
    ax_b.set_xlabel('Bias index\n(+1 = always "Yes",  −1 = always "No")', fontsize=6.5)
    ax_b.set_xlim(-1.30, 1.30)
    ax_b.spines["left"].set_visible(False)
    ax_b.tick_params(axis="y", length=0)

    save_fig(fig, out_dir, "fig4_bias")


# ---------------------------------------------------------------------------
# Figure 5 — Temporal / cutoff analysis
# ---------------------------------------------------------------------------

def figure_cutoff_temporal(models: list[dict], out_dir: Path) -> None:
    apply_nature_style()

    MIN_N    = 8
    BIN_SIZE = 6   # months per bin for the relative panel

    fig = plt.figure(figsize=(7.2, 5.6))
    gs  = GridSpec(2, 1, figure=fig, hspace=0.55,
                   left=0.10, right=0.96, top=0.92, bottom=0.10)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    # ── A: MCQ vs absolute publication date ──────────────────────────────
    _panel_label(ax_a, "A")
    ax_a.set_title("MCQ accuracy vs. publication date  "
                   "(dashed = model training cutoff)",
                   loc="left")

    all_abs: set[int] = set()
    for m in models:
        all_abs.update(m["abs_mcq"].keys())
    abs_sorted = sorted(all_abs)

    for m in models:
        xs, ys = [], []
        for mo in abs_sorted:
            v = m["abs_mcq"].get(mo, [])
            if len(v) >= MIN_N:
                xs.append(2020 + mo / 12)
                ys.append(_sm(v))
        if xs:
            ax_a.plot(xs, ys, linestyle=m["ls"], color=m["color"],
                      marker=m["marker"], markersize=4, linewidth=1.2,
                      label=m["short"], zorder=3, alpha=0.92,
                      markeredgecolor="white", markeredgewidth=0.5)

    # Per-model cutoff markers
    for m in models:
        cm = m["cutoff_months"]
        if cm is None:
            continue
        cy = 2020 + cm / 12
        if abs_sorted and (2020 + abs_sorted[0] / 12 - 0.5) <= cy <= (2020 + abs_sorted[-1] / 12 + 0.5):
            ax_a.axvline(cy, color=m["color"], lw=0.75, ls="--", alpha=0.5, zorder=2)

    ax_a.axhline(0.25, color="#888888", lw=0.65, ls=":", alpha=0.5, label="Chance (0.25)")

    tick_mos = sorted(m for m in abs_sorted if m % 3 == 0)
    ax_a.set_xticks([2020 + m / 12 for m in tick_mos])
    ax_a.set_xticklabels(
        [f"{2020 + m // 12}-{m % 12 + 1:02d}" for m in tick_mos],
        rotation=35, ha="right", fontsize=5.5,
    )
    if abs_sorted:
        ax_a.set_xlim(2020 + abs_sorted[0] / 12 - 0.15,
                      2020 + abs_sorted[-1] / 12 + 0.15)
    ax_a.set_ylim(0.05, 0.60)
    ax_a.set_xlabel("Publication date", fontsize=7)
    ax_a.set_ylabel("MCQ accuracy", fontsize=7)
    ax_a.legend(loc="upper left", ncol=2, fontsize=5.8,
                handlelength=1.5, handletextpad=0.4)

    # ── B: MCQ vs months since training cutoff ────────────────────────────
    _panel_label(ax_b, "B")
    ax_b.set_title(
        f"MCQ accuracy vs. months since training cutoff  ({BIN_SIZE}-month bins)",
        loc="left",
    )

    def bin_center(offset: int) -> int:
        return (offset // BIN_SIZE) * BIN_SIZE + BIN_SIZE // 2

    all_offsets: list[int] = []
    for m in models:
        bins: dict[int, list] = defaultdict(list)
        for offset, vals in m["rel_mcq"].items():
            bins[bin_center(offset)].extend(vals)

        xs, ys = [], []
        for bc in sorted(bins.keys()):
            v = bins[bc]
            if len(v) >= MIN_N:
                xs.append(bc)
                ys.append(_sm(v))
                all_offsets.append(bc)

        if xs:
            ax_b.plot(xs, ys, linestyle=m["ls"], color=m["color"],
                      marker=m["marker"], markersize=4, linewidth=1.2,
                      label=f"{m['short']}  [{m['cutoff']}]",
                      zorder=3, alpha=0.92,
                      markeredgecolor="white", markeredgewidth=0.5)

    ax_b.axvline(0, color="#CC3311", lw=1.2, ls="--", alpha=0.85,
                 zorder=6, label="Training cutoff")
    ax_b.axhline(0.25, color="#888888", lw=0.65, ls=":", alpha=0.5, label="Chance")

    if all_offsets:
        pad = BIN_SIZE + 4
        xl, xh = min(all_offsets) - pad, max(all_offsets) + pad
        ax_b.set_xlim(xl, xh)
        ax_b.axvspan(xl, 0, alpha=0.04, color="#2166AC", linewidth=0)
        ax_b.axvspan(0, xh,  alpha=0.04, color="#B2182B", linewidth=0)
        ax_b.text(0.01, 0.94, "Pre-cutoff\n(model may have seen)",
                  transform=ax_b.transAxes, fontsize=5.5,
                  color="#2166AC", va="top", style="italic")
        ax_b.text(0.99, 0.94, "Post-cutoff\n(true forecasting)",
                  transform=ax_b.transAxes, fontsize=5.5,
                  color="#B2182B", va="top", ha="right", style="italic")

    ax_b.set_ylim(0.05, 0.60)
    ax_b.set_xlabel("Months since training cutoff", fontsize=7)
    ax_b.set_ylabel("MCQ accuracy", fontsize=7)
    ax_b.legend(loc="upper right", ncol=2, fontsize=5.5,
                handlelength=1.5, handletextpad=0.4)

    fig.suptitle("Temporal analysis — knowledge-cutoff effects on forecasting accuracy",
                 fontsize=8.5, fontweight="bold", y=0.98)
    save_fig(fig, out_dir, "fig5_cutoff_temporal")


# ---------------------------------------------------------------------------
# Figure 6 — Area radar: small multiples (one per model, spokes = areas)
# ---------------------------------------------------------------------------

def figure_area_radar(models: list[dict], out_dir: Path) -> None:
    """
    2 × 3 grid of polar charts — one per model, 9 spokes = research areas,
    values = MCQ accuracy.  A grey reference polygon shows the cross-model
    mean, and a dotted ring marks the 4-choice chance level (0.25).
    """
    apply_nature_style()

    N         = len(AREA_ORDER)
    spoke_lbl = [AREA_SHORT.get(a, a) for a in AREA_ORDER]
    angles    = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    ang_c     = angles + [angles[0]]

    # Cross-model mean per area (reference polygon)
    area_mean_vals = []
    for area in AREA_ORDER:
        vs = [_sm(m["area_mcq"].get(area, [])) for m in models]
        vs = [v for v in vs if not np.isnan(v)]
        area_mean_vals.append(_sm(vs) if vs else 0.0)
    mean_c = area_mean_vals + [area_mean_vals[0]]

    # Axis limits — auto-scaled to data, minimum 0.40
    all_vals = [_sm(m["area_mcq"].get(a, []))
                for m in models for a in AREA_ORDER]
    all_vals = [v for v in all_vals if not np.isnan(v)]
    y_max    = max(max(all_vals) * 1.18, 0.40) if all_vals else 0.40
    y_ticks  = [v for v in [0.10, 0.20, 0.30, 0.40, 0.50] if v < y_max]

    ncols, nrows = 3, 2
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(7.2, 5.4),
        subplot_kw={"projection": "polar"},
    )
    axes_flat = np.array(axes).ravel()

    for idx, m in enumerate(models):
        ax    = axes_flat[idx]
        color = m["color"]

        # Reference (cross-model mean) — painted first so model polygon sits on top
        ax.fill(ang_c, mean_c, alpha=0.10, color="#999999", zorder=1)
        ax.plot(ang_c, mean_c, "-", color="#999999", lw=0.75, alpha=0.65, zorder=2)

        # Model polygon
        vals = [max(0.0, _sm(m["area_mcq"].get(a, [])) or 0.0) for a in AREA_ORDER]
        vals_c = vals + [vals[0]]
        ax.fill(ang_c, vals_c, alpha=0.18, color=color, zorder=3)
        ax.plot(ang_c, vals_c, "-", color=color, lw=1.5,
                marker=m["marker"], markersize=3, markeredgecolor="white",
                markeredgewidth=0.4, zorder=4)

        # Chance ring
        ax.plot(ang_c, [0.25] * (N + 1), ":", color="#999999", lw=0.65,
                alpha=0.55, zorder=2)

        # Axes
        ax.set_xticks(angles)
        ax.set_xticklabels(spoke_lbl, size=5, color="#333333")
        ax.set_ylim(0, y_max)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([f"{v:.2f}" for v in y_ticks], size=4, color="#888")
        ax.spines["polar"].set_linewidth(0.35)
        ax.grid(lw=0.3, alpha=0.45, color="#aaaaaa")

        # Panel title in model colour
        ax.set_title(
            f"{m['short']}\ncutoff: {m['cutoff']}",
            size=6.5, pad=9, fontweight="bold", color=color,
        )

    # Hide any unused subplot slots
    for idx in range(len(models), len(axes_flat)):
        axes_flat[idx].set_visible(False)

    # Shared legend — reference polygon + chance ring
    ref_patch    = mpatches.Patch(color="#999999", alpha=0.45,
                                  label="Cross-model mean")
    chance_line  = plt.Line2D([0], [0], ls=":", color="#999999", lw=0.9,
                              label="Chance (0.25)")
    fig.legend(handles=[ref_patch, chance_line],
               loc="lower center", ncol=2, fontsize=6,
               handlelength=1.4, handletextpad=0.5,
               bbox_to_anchor=(0.5, -0.06),
               framealpha=0.92, edgecolor="#cccccc")

    fig.suptitle(
        "MCQ accuracy by scientific domain — CUSP Benchmark\n"
        "(spokes = research areas; grey = cross-model mean; dotted = chance level)",
        fontsize=8.5, fontweight="bold", y=1.02,
    )
    fig.tight_layout(h_pad=1.8, w_pad=0.8)
    save_fig(fig, out_dir, "fig6_area_radar")


# ---------------------------------------------------------------------------
# Figure 14 — Small-multiple radars: aggregate CUSP score per area
# ---------------------------------------------------------------------------

def figure_cusp_area_radar(models: list[dict], out_dir: Path) -> None:
    """
    2 × 3 grid of polar charts — one per model, 9 spokes = research areas,
    values = aggregate CUSP score (mean of binary, MCQ, date, and FRQ scores,
    normalised to [0, 1]).  A grey reference polygon shows the cross-model mean.
    """
    apply_nature_style()

    N         = len(AREA_ORDER)
    spoke_lbl = [AREA_SHORT.get(a, a) for a in AREA_ORDER]
    angles    = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    ang_c     = angles + [angles[0]]

    def _cusp_area(m: dict, area: str) -> float:
        """Aggregate CUSP score for one model × area (NaN when no data at all)."""
        parts: list[float] = []
        b = _sm(m["area_binary"].get(area, []))
        if not np.isnan(b):
            parts.append(b)
        q = _sm(m["area_mcq"].get(area, []))
        if not np.isnan(q):
            parts.append(q)
        d = _sm(m["area_date"].get(area, []))
        if not np.isnan(d):
            parts.append(d)
        f = _sm(m["area_frq"].get(area, []))
        if not np.isnan(f):
            parts.append(f / 10.0)  # FRQ is scored 0–10; normalise to 0–1
        return float(np.mean(parts)) if parts else float("nan")

    # Cross-model mean per area (reference polygon)
    area_mean_vals = []
    for area in AREA_ORDER:
        vs = [_cusp_area(m, area) for m in models]
        vs = [v for v in vs if not np.isnan(v)]
        area_mean_vals.append(_sm(vs) if vs else 0.0)
    mean_c = area_mean_vals + [area_mean_vals[0]]

    # Axis limits — auto-scaled to data, minimum 0.40
    all_vals = [_cusp_area(m, a) for m in models for a in AREA_ORDER]
    all_vals = [v for v in all_vals if not np.isnan(v)]
    y_max    = max(max(all_vals) * 1.18, 0.40) if all_vals else 0.40
    y_ticks  = [v for v in [0.10, 0.20, 0.30, 0.40, 0.50] if v < y_max]

    ncols, nrows = 3, 2
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(7.2, 5.4),
        subplot_kw={"projection": "polar"},
    )
    axes_flat = np.array(axes).ravel()

    for idx, m in enumerate(models):
        ax    = axes_flat[idx]
        color = m["color"]

        # Reference (cross-model mean) — painted first so model polygon sits on top
        ax.fill(ang_c, mean_c, alpha=0.10, color="#999999", zorder=1)
        ax.plot(ang_c, mean_c, "-", color="#999999", lw=0.75, alpha=0.65, zorder=2)

        # Model polygon
        vals   = [max(0.0, _cusp_area(m, a) or 0.0) for a in AREA_ORDER]
        vals_c = vals + [vals[0]]
        ax.fill(ang_c, vals_c, alpha=0.18, color=color, zorder=3)
        ax.plot(ang_c, vals_c, "-", color=color, lw=1.5,
                marker=m["marker"], markersize=3, markeredgecolor="white",
                markeredgewidth=0.4, zorder=4)

        # Axes
        ax.set_xticks(angles)
        ax.set_xticklabels(spoke_lbl, size=5, color="#333333")
        ax.set_ylim(0, y_max)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([f"{v:.2f}" for v in y_ticks], size=4, color="#888")
        ax.spines["polar"].set_linewidth(0.35)
        ax.grid(lw=0.3, alpha=0.45, color="#aaaaaa")

        # Panel title in model colour
        ax.set_title(
            f"{m['short']}\ncutoff: {m['cutoff']}",
            size=6.5, pad=9, fontweight="bold", color=color,
        )

    # Hide any unused subplot slots
    for idx in range(len(models), len(axes_flat)):
        axes_flat[idx].set_visible(False)

    # Shared legend
    ref_patch = mpatches.Patch(color="#999999", alpha=0.45,
                               label="Cross-model mean")
    fig.legend(handles=[ref_patch],
               loc="lower center", ncol=1, fontsize=6,
               handlelength=1.4, handletextpad=0.5,
               bbox_to_anchor=(0.5, -0.02),
               framealpha=0.92, edgecolor="#cccccc")

    fig.suptitle(
        "Aggregate CUSP score by scientific domain — CUSP Benchmark\n"
        "(spokes = research areas; score = mean of binary, MCQ, date & FRQ; "
        "grey = cross-model mean)",
        fontsize=8.5, fontweight="bold", y=1.02,
    )
    fig.tight_layout(h_pad=1.8, w_pad=0.8)
    save_fig(fig, out_dir, "fig14_cusp_area_radar")


# ---------------------------------------------------------------------------
# Figure 7 — Date prediction error deep-dive
# ---------------------------------------------------------------------------

def _step_cdf(data: list[float]) -> tuple[np.ndarray, np.ndarray]:
    arr = np.sort(np.array(data, dtype=float))
    x   = np.concatenate([[0.], arr])
    y   = np.concatenate([[0.], np.arange(1, len(arr) + 1) / len(arr)])
    return x, y


def figure_date_errors(models: list[dict], out_dir: Path) -> None:
    """
    Four-panel deep-dive into date-prediction accuracy:
      A  CDF of absolute error (months)
      B  Within-N-months accuracy for N = 3, 6, 12, 24
      C  Signed-error violin plots (directional bias)
      D  Mean signed error vs months-since-cutoff (anchoring analysis)
    """
    apply_nature_style()

    # Sort models by mean signed error for panels C & D (ascending)
    models_se = sorted(models, key=lambda m: np.mean(m["date_signed"])
                       if m["date_signed"] else 0)

    fig = plt.figure(figsize=(7.2, 6.8))
    gs  = GridSpec(2, 2, figure=fig, hspace=0.52, wspace=0.40,
                   left=0.10, right=0.97, top=0.93, bottom=0.10)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # ── A: Absolute error CDF ─────────────────────────────────────────────
    _panel_label(ax_a, "A")
    ax_a.set_title("Cumulative absolute error distribution", loc="left")

    CAP = 72   # cap display at 6 years for readability
    for m in models:
        errs = m["date_abs_err"]
        if not errs:
            continue
        capped = [min(e, CAP) for e in errs]
        x, y = _step_cdf(capped)
        ax_a.plot(x, y, linestyle=m["ls"], color=m["color"],
                  linewidth=1.3, label=m["short"], alpha=0.92)

    for mo, lbl in ((6, "6 mo"), (12, "12 mo"), (24, "24 mo")):
        ax_a.axvline(mo, color="#aaaaaa", lw=0.6, ls=":", alpha=0.6, zorder=1)
        ax_a.text(mo + 0.5, 0.02, lbl, fontsize=4.8, color="#888", va="bottom")

    ax_a.set_xlim(0, CAP)
    ax_a.set_ylim(0, 1.02)
    ax_a.set_xlabel("Absolute error (months)", fontsize=7)
    ax_a.set_ylabel("Cumulative fraction of predictions", fontsize=7)
    ax_a.legend(loc="lower right", fontsize=5.8, handlelength=1.5)

    # ── B: Within-N-months accuracy ───────────────────────────────────────
    _panel_label(ax_b, "B")
    ax_b.set_title("Predictions within N months of ground truth", loc="left")

    thresholds = [3, 6, 12, 24]
    n_thresh   = len(thresholds)
    n_mod      = len(models)
    bw         = 0.70 / n_mod
    x_pos      = np.arange(n_thresh)

    for j, m in enumerate(models):
        errs = m["date_abs_err"]
        if not errs:
            continue
        frac = [np.mean(np.array(errs) <= t) for t in thresholds]
        offset = (j - n_mod / 2 + 0.5) * bw
        ax_b.bar(x_pos + offset, frac, bw * 0.92,
                 color=m["color"], alpha=0.88,
                 edgecolor="white", linewidth=0.3, label=m["short"])

    ax_b.set_xticks(x_pos)
    ax_b.set_xticklabels([f"≤{t} mo" for t in thresholds], fontsize=7)
    ax_b.set_ylabel("Fraction of predictions", fontsize=7)
    ax_b.set_ylim(0, 1.05)
    ax_b.legend(loc="upper left", fontsize=5.5, ncol=2,
                handlelength=1.0, handletextpad=0.3, columnspacing=0.5)

    # ── C: Signed-error violin plots ──────────────────────────────────────
    _panel_label(ax_c, "C")
    ax_c.set_title("Signed error distribution  (+ = predicted too late)", loc="left")

    ax_c.axhline(0, color="#333333", lw=0.8, zorder=1)
    ax_c.axhspan(-6, 6, alpha=0.06, color="#1A9850", linewidth=0, zorder=0)

    positions = list(range(len(models_se)))
    for i, m in enumerate(models_se):
        data = m["date_signed"]
        if not data:
            continue
        vp = ax_c.violinplot(data, positions=[i], widths=0.72,
                             showmedians=True, showextrema=False)
        for pc in vp["bodies"]:
            pc.set_facecolor(m["color"])
            pc.set_edgecolor(m["color"])
            pc.set_alpha(0.55)
        vp["cmedians"].set_color("white")
        vp["cmedians"].set_linewidth(1.5)
        vp["cmedians"].set_zorder(4)

        # Annotate median value
        med = np.median(data)
        ax_c.text(i, med + 1.5, f"{med:+.0f}", ha="center", va="bottom",
                  fontsize=5, color=m["color"], fontweight="bold")

    ax_c.set_xticks(positions)
    ax_c.set_xticklabels([m["short"] for m in models_se],
                         rotation=30, ha="right", fontsize=6)
    ax_c.set_ylabel("Signed error (months)", fontsize=7)
    ax_c.tick_params(axis="x", length=0)
    ax_c.spines["bottom"].set_visible(False)

    # Annotate the ±6 mo band
    ax_c.text(len(models_se) - 0.05, 5.5, "±6 mo", ha="right",
              fontsize=5, color="#1A9850", style="italic")

    # ── D: Signed error vs months-since-cutoff ────────────────────────────
    _panel_label(ax_d, "D")
    ax_d.set_title("Prediction bias vs. time since training cutoff\n"
                   "(reveals cutoff-anchoring effect)", loc="left")

    BIN_SIZE = 6
    MIN_N    = 15

    def bin_center(o: int) -> int:
        return (o // BIN_SIZE) * BIN_SIZE + BIN_SIZE // 2

    all_offsets: list[int] = []
    for m in models:
        bins: dict[int, list] = defaultdict(list)
        for offset, vals in m["rel_date_signed"].items():
            bins[bin_center(offset)].extend(vals)

        xs, ys, ses = [], [], []
        for bc in sorted(bins.keys()):
            v = bins[bc]
            if len(v) >= MIN_N:
                xs.append(bc)
                ys.append(float(np.mean(v)))
                ses.append(float(np.std(v) / np.sqrt(len(v))))
                all_offsets.append(bc)

        if xs:
            xs_arr = np.array(xs)
            ys_arr = np.array(ys)
            se_arr = np.array(ses)
            ax_d.fill_between(xs_arr, ys_arr - se_arr, ys_arr + se_arr,
                              alpha=0.12, color=m["color"], linewidth=0)
            ax_d.plot(xs_arr, ys_arr, linestyle=m["ls"], color=m["color"],
                      marker=m["marker"], markersize=3.5, linewidth=1.2,
                      label=f"{m['short']}  [{m['cutoff']}]",
                      markeredgecolor="white", markeredgewidth=0.4)

    ax_d.axvline(0, color="#CC3311", lw=1.1, ls="--", alpha=0.8,
                 zorder=6, label="Training cutoff")
    ax_d.axhline(0, color="#333333", lw=0.7, zorder=1)
    ax_d.axhspan(-6, 6, alpha=0.06, color="#1A9850", linewidth=0)

    if all_offsets:
        pad = BIN_SIZE + 4
        xl, xh = min(all_offsets) - pad, max(all_offsets) + pad
        ax_d.set_xlim(xl, xh)
        ax_d.axvspan(xl, 0, alpha=0.04, color="#2166AC", linewidth=0)
        ax_d.axvspan(0, xh,  alpha=0.04, color="#B2182B", linewidth=0)

    ax_d.set_xlabel("Months since training cutoff", fontsize=7)
    ax_d.set_ylabel("Mean signed error (months)", fontsize=7)
    ax_d.legend(loc="upper left", fontsize=5.5, ncol=1,
                handlelength=1.5, handletextpad=0.4)

    fig.suptitle("Date prediction accuracy — in-depth analysis",
                 fontsize=8.5, fontweight="bold", y=0.98)
    save_fig(fig, out_dir, "fig7_date_errors")


# ---------------------------------------------------------------------------
# Figure 8 — Predicted vs ground-truth date scatter (one per model)
# ---------------------------------------------------------------------------

def figure_date_predictions(models: list[dict], out_dir: Path) -> None:
    """
    2 × 3 hexbin scatter — predicted date vs ground-truth date for each model.
    Reveals where each model's predictions cluster relative to the true dates,
    and whether models anchor predictions near their training cutoff.
    """
    from matplotlib.colors import LinearSegmentedColormap

    apply_nature_style()

    # Global GT date range (same for all models — benchmark is fixed)
    all_gt = np.concatenate([m["date_gt_m"] for m in models if m["date_gt_m"]])
    gt_lo, gt_hi = float(all_gt.min()) - 1, float(all_gt.max()) + 1

    # Predicted date display range: clip outliers symmetrically
    all_pred = np.concatenate([m["date_pred_m"] for m in models if m["date_pred_m"]])
    pred_lo  = max(float(np.percentile(all_pred, 2))  - 3, gt_lo - 24)
    pred_hi  = min(float(np.percentile(all_pred, 98)) + 3, gt_hi + 60)

    def _month_ticks(lo: float, hi: float, step: int = 6) -> list[float]:
        first = int(np.ceil(lo / step)) * step
        return [m for m in range(first, int(hi) + step, step) if lo <= m <= hi]

    def _tick_label(m: float) -> str:
        mi = int(round(m))
        return f"{2020 + mi // 12}·{mi % 12 + 1:02d}"

    ncols, nrows = 3, 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(7.2, 5.5),
                              gridspec_kw={"hspace": 0.50, "wspace": 0.35,
                                           "left": 0.09, "right": 0.97,
                                           "top": 0.90, "bottom": 0.10})
    axes_flat = np.array(axes).ravel()

    for idx, m in enumerate(models):
        ax  = axes_flat[idx]
        col = m["color"]

        pred = np.array(m["date_pred_m"])
        gt   = np.array(m["date_gt_m"])
        if len(pred) == 0:
            ax.set_visible(False)
            continue

        # Clip predictions to display range
        pred_clipped = np.clip(pred, pred_lo, pred_hi)
        n_clipped    = int(np.sum((pred < pred_lo) | (pred > pred_hi)))

        # Per-model white → model-colour colormap
        cmap = LinearSegmentedColormap.from_list("m", ["#f5f5f5", col])

        hb = ax.hexbin(gt, pred_clipped, gridsize=20, cmap=cmap,
                       mincnt=1, linewidths=0.08,
                       extent=[gt_lo, gt_hi, pred_lo, pred_hi])

        # Perfect-prediction diagonal
        diag = [max(gt_lo, pred_lo), min(gt_hi, pred_hi)]
        ax.plot(diag, diag, "--", color="#333333", lw=0.9, alpha=0.8,
                zorder=4, label="Perfect")

        # Model cutoff horizontal line
        cm = m["cutoff_months"]
        if cm is not None and pred_lo <= cm <= pred_hi:
            ax.axhline(cm, color=col, lw=0.75, ls=":", alpha=0.6, zorder=3)
            ax.text(gt_lo + 0.3, cm + 0.5, f"cutoff", fontsize=4.5,
                    color=col, alpha=0.8, va="bottom")

        # Stats annotation
        med_err = float(np.median(m["date_signed"])) if m["date_signed"] else float("nan")
        w12     = float(np.mean(np.array(m["date_abs_err"]) <= 12)) if m["date_abs_err"] else float("nan")
        ax.text(0.97, 0.03,
                f"median Δ = {med_err:+.0f} mo\n≤12 mo: {w12:.0%}",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=5, color="#222222",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                          edgecolor="#cccccc", linewidth=0.4, alpha=0.88))

        if n_clipped > 0:
            ax.text(0.97, 0.97,
                    f"{n_clipped} clipped ({n_clipped / len(pred):.0%})",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize=4.5, color="#888888")

        # Axes formatting
        x_ticks = _month_ticks(gt_lo, gt_hi, step=6)
        y_ticks = _month_ticks(pred_lo, pred_hi, step=12)
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([_tick_label(t) for t in x_ticks],
                           rotation=40, ha="right", fontsize=4.8)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([_tick_label(t) for t in y_ticks], fontsize=4.8)
        ax.set_xlim(gt_lo, gt_hi)
        ax.set_ylim(pred_lo, pred_hi)

        ax.set_title(f"{m['short']}  [cutoff {m['cutoff']}]",
                     fontsize=6.5, fontweight="bold", color=col, pad=4)
        if idx % ncols == 0:
            ax.set_ylabel("Predicted date", fontsize=6.5)
        if idx >= (nrows - 1) * ncols:
            ax.set_xlabel("Ground-truth date", fontsize=6.5)

        # Colorbar per panel
        cb = fig.colorbar(hb, ax=ax, shrink=0.70, pad=0.02, aspect=18)
        cb.set_label("Count", fontsize=4.5)
        cb.ax.tick_params(labelsize=4)
        cb.outline.set_linewidth(0.3)

    # Hide any unused panels
    for idx in range(len(models), len(axes_flat)):
        axes_flat[idx].set_visible(False)

    fig.suptitle(
        "Predicted vs. ground-truth publication date — each model's forecast distribution\n"
        "(diagonal = perfect; dotted horizontal = model training cutoff)",
        fontsize=8, fontweight="bold", y=0.97,
    )
    save_fig(fig, out_dir, "fig8_date_predictions")


# ---------------------------------------------------------------------------
# Figure 9 — Bias index summary (Binary Yes-bias / MCQ position / Date signed error)
# ---------------------------------------------------------------------------

def figure_response_distributions(models: list[dict], out_dir: Path) -> None:
    """
    fig9: Three-panel bias index — one row per model, shared y-axis.
      A  Binary Yes-bias index  (overall P(Yes) − 0.5)
      B  MCQ position bias      (selection rate − 0.25 per option A–D)
      C  Date anchoring bias    (mean signed error ± 1 SE, months)
    """
    apply_nature_style()

    OPTIONS    = list("ABCD")
    OPT_COLORS = {"A": "#4393C3", "B": "#F4A582", "C": "#74C476", "D": "#D6604D"}
    YES_COLOR  = "#B2182B"
    NO_COLOR   = "#2166AC"

    n_mod = len(models)
    # Reverse so best model (last in ascending-sorted list) appears at top
    models_r = list(reversed(models))
    names    = [m["short"] for m in models_r]
    y        = np.arange(n_mod)

    has_mcq = any(sum(m.get("mcq_choices", {}).values()) > 0 for m in models)

    # ── Bias computations ─────────────────────────────────────────────────
    yes_bias = []
    for m in models_r:
        bn, bc, bpn, bpc = m["bin_n"], m["bin_c"], m["bp_n"], m["bp_c"]
        total_n = bn + bpn
        yes_bias.append(
            (bc + (bpn - bpc)) / total_n - 0.5 if total_n > 0 else float("nan")
        )
    yes_bias = np.array(yes_bias)

    date_mean, date_se = [], []
    for m in models_r:
        data = m["date_signed"]
        if data:
            date_mean.append(float(np.mean(data)))
            date_se.append(float(np.std(data, ddof=1) / np.sqrt(len(data))))
        else:
            date_mean.append(float("nan"))
            date_se.append(float("nan"))
    date_mean = np.array(date_mean)
    date_se   = np.array(date_se)

    # ── Layout: 3 panels sharing y-axis ──────────────────────────────────
    fig = plt.figure(figsize=(7.2, max(2.8, 0.50 * n_mod + 1.2)))
    gs  = GridSpec(1, 3, figure=fig,
                   width_ratios=[1, 1.35, 1],
                   left=0.20, right=0.97, top=0.87, bottom=0.16,
                   wspace=0.06)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1], sharey=ax_a)
    ax_c = fig.add_subplot(gs[2], sharey=ax_a)

    ylim = (-0.6, n_mod - 0.4)

    # ── A: Binary Yes-bias index ──────────────────────────────────────────
    _panel_label(ax_a, "A", x=-0.08)
    ax_a.set_title("Binary\nYes-bias index", loc="center", pad=3)

    bar_colors_a = [YES_COLOR if v > 0 else NO_COLOR for v in yes_bias]
    ax_a.barh(y, yes_bias, 0.55, color=bar_colors_a, alpha=0.86,
              edgecolor="white", linewidth=0.4)
    ax_a.axvline(0, color="#333333", lw=0.9, zorder=4)
    ax_a.axvspan(-0.55, 0,    alpha=0.04, color=NO_COLOR,  linewidth=0)
    ax_a.axvspan(0,     0.55, alpha=0.04, color=YES_COLOR, linewidth=0)

    for i, v in enumerate(yes_bias):
        if not np.isnan(v):
            off = 0.018 if v >= 0 else -0.018
            ha  = "left"  if v >= 0 else "right"
            ax_a.text(v + off, i, f"{v:+.2f}", va="center", ha=ha,
                      fontsize=5.5, color="#222222")

    ax_a.set_xlim(-0.55, 0.55)
    ax_a.set_xticks([-0.5, -0.25, 0, 0.25, 0.5])
    ax_a.set_xticklabels(["-0.5", "-0.25", "0", "+0.25", "+0.5"], fontsize=5.5)
    ax_a.set_xlabel("P(Yes) − 0.5", fontsize=6.5, labelpad=4)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(names, fontsize=7)
    ax_a.tick_params(axis="y", length=0)
    ax_a.spines["left"].set_visible(False)

    ax_a.text(-0.27, -0.55, '"No" bias', ha="center", va="top",
              fontsize=5, color=NO_COLOR, style="italic",
              transform=ax_a.get_xaxis_transform())
    ax_a.text(+0.27, -0.55, '"Yes" bias', ha="center", va="top",
              fontsize=5, color=YES_COLOR, style="italic",
              transform=ax_a.get_xaxis_transform())

    # ── B: MCQ position bias ──────────────────────────────────────────────
    _panel_label(ax_b, "B", x=-0.05)
    ax_b.set_title("MCQ position bias\n(selection − 0.25)", loc="center", pad=3)

    if has_mcq:
        all_devs = []
        for m in models_r:
            choices = m.get("mcq_choices", {})
            total   = max(sum(choices.values()), 1)
            for opt in OPTIONS:
                all_devs.append(choices.get(opt, 0) / total - 0.25)
        x_abs = max(abs(min(all_devs)), abs(max(all_devs))) + 0.04
        x_abs = max(x_abs, 0.12)

        ax_b.axvline(0, color="#333333", lw=0.9, zorder=4)
        ax_b.axvspan(-x_abs, 0,     alpha=0.04, color=NO_COLOR,  linewidth=0)
        ax_b.axvspan(0,      x_abs, alpha=0.04, color=YES_COLOR, linewidth=0)

        for i, m in enumerate(models_r):
            choices = m.get("mcq_choices", {})
            total   = max(sum(choices.values()), 1)
            for opt in OPTIONS:
                dev = choices.get(opt, 0) / total - 0.25
                col = OPT_COLORS[opt]
                ax_b.plot([0, dev], [i, i], color=col, lw=0.8,
                          alpha=0.45, zorder=2)
                ax_b.scatter(dev, i, color=col, s=42, zorder=5,
                             edgecolors="white", linewidths=0.5)

        ax_b.set_xlim(-x_abs, x_abs)
        ax_b.set_xlabel("Selection rate − 0.25", fontsize=6.5, labelpad=4)

        opt_handles = [
            plt.Line2D([0], [0], marker="o", ls="none",
                       color=OPT_COLORS[opt], markersize=5,
                       markeredgecolor="white", markeredgewidth=0.4,
                       label=f"Option {opt}")
            for opt in OPTIONS
        ]
        ax_b.legend(handles=opt_handles, loc="lower right", fontsize=5.5,
                    ncol=2, handlelength=0.5, handletextpad=0.3,
                    columnspacing=0.5, borderpad=0.5)
    else:
        ax_b.text(0.5, 0.5, "MCQ option data\nnot available",
                  transform=ax_b.transAxes, ha="center", va="center",
                  fontsize=7, color="#888888", style="italic",
                  multialignment="center")
        ax_b.axvline(0, color="#333333", lw=0.9, zorder=4)
        ax_b.set_xlabel("Selection rate − 0.25", fontsize=6.5, labelpad=4)

    ax_b.tick_params(labelleft=False, left=False)
    ax_b.spines["left"].set_visible(False)

    # ── C: Date anchoring bias ────────────────────────────────────────────
    _panel_label(ax_c, "C", x=-0.05)
    ax_c.set_title("Date anchoring bias\n(mean signed error ± SE)", loc="center", pad=3)

    bar_colors_c = [m["color"] for m in models_r]
    ax_c.barh(y, date_mean, 0.55, color=bar_colors_c, alpha=0.82,
              edgecolor="white", linewidth=0.4)

    for i, (mn, se) in enumerate(zip(date_mean, date_se)):
        if not np.isnan(mn):
            ax_c.errorbar(mn, i, xerr=se, fmt="none",
                          ecolor="#333333", elinewidth=0.85,
                          capsize=3.0, capthick=0.7, zorder=6)

    ax_c.axvline(0, color="#333333", lw=0.9, zorder=4)
    ax_c.axvspan(-6, 6, alpha=0.08, color="#1A9850", linewidth=0, zorder=0)

    for i, (mn, se) in enumerate(zip(date_mean, date_se)):
        if not np.isnan(mn):
            gap = (se if not np.isnan(se) else 0) + 1.5
            gap = max(gap, 2.0)
            ha  = "left"  if mn >= 0 else "right"
            off = gap if mn >= 0 else -gap
            ax_c.text(mn + off, i, f"{mn:+.0f} mo", va="center", ha=ha,
                      fontsize=5.2, color="#222222")

    finite_d  = date_mean[~np.isnan(date_mean)]
    finite_se = date_se[~np.isnan(date_se)]
    half = max(abs(finite_d).max() + (finite_se.max() if len(finite_se) else 0) + 12, 30) if len(finite_d) else 36
    ax_c.set_xlim(-half, half)
    ax_c.set_xlabel("Mean signed error (months)", fontsize=6.5, labelpad=4)
    ax_c.text(0, -0.12, "±6 mo", ha="center", va="top",
              transform=ax_c.get_xaxis_transform(),
              fontsize=4.8, color="#1A9850", style="italic")

    ax_c.tick_params(labelleft=False, left=False)
    ax_c.spines["left"].set_visible(False)

    # ── Shared y-axis limits ──────────────────────────────────────────────
    ax_a.set_ylim(*ylim)

    fig.suptitle("Response bias indices — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=0.97)
    save_fig(fig, out_dir, "fig9_response_distributions")


# ---------------------------------------------------------------------------
# Figure 9b — Response distribution histograms (binary / perturbed / date)
# ---------------------------------------------------------------------------

def figure_response_histograms(models: list[dict], out_dir: Path) -> None:
    """
    fig9b: Two-panel binary response distribution.
      A  Binary (gt=Yes)          — 100 % stacked bar: Yes vs No per model
      B  Binary perturbed (gt=No) — same, flipped expectation
    Panels share a y-axis; no title.
    """
    apply_nature_style()

    YES_COL = "#B2182B"
    NO_COL  = "#2166AC"
    MIN_BAR = 0.13

    models_s = sorted(
        models,
        key=lambda m: m["binary_acc"] if not np.isnan(m["binary_acc"]) else 0,
    )
    n  = len(models_s)
    y  = np.arange(n)
    nm = [m["short"] for m in models_s]

    row_h = 0.62
    fig_h = max(3.6, row_h * n + 1.4)
    fig = plt.figure(figsize=(7.2, fig_h))
    gs  = GridSpec(1, 2, figure=fig,
                   width_ratios=[1, 1],
                   left=0.20, right=0.97,
                   top=1 - 0.45 / fig_h,
                   bottom=0.55 / fig_h,
                   wspace=0.10)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1], sharey=ax_a)

    bar_h = 0.58

    # ── A: Binary (gt = Yes) ──────────────────────────────────────────────
    _panel_label(ax_a, "A", x=-0.08)
    ax_a.set_title('Binary\n(ground truth = "Yes")', loc="center", pad=3)

    p_yes_a = np.array([m["binary_acc"] for m in models_s])
    p_no_a  = 1 - p_yes_a

    ax_a.barh(y, p_yes_a, bar_h, color=YES_COL, alpha=0.86,
              edgecolor="white", linewidth=0.4, label='"Yes"  ✓ correct')
    ax_a.barh(y, p_no_a,  bar_h, left=p_yes_a, color=NO_COL, alpha=0.86,
              edgecolor="white", linewidth=0.4, label='"No"   ✗ incorrect')

    for i, (py, pn) in enumerate(zip(p_yes_a, p_no_a)):
        if not np.isnan(py) and py >= MIN_BAR:
            ax_a.text(py / 2, i, f"{py:.0%}", ha="center", va="center",
                      fontsize=6, color="white", fontweight="bold")
        if not np.isnan(pn) and pn >= MIN_BAR:
            ax_a.text(py + pn / 2, i, f"{pn:.0%}", ha="center", va="center",
                      fontsize=6, color="white", fontweight="bold")

    ax_a.axvline(0.5, color="#888", lw=0.7, ls=":", alpha=0.45)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(nm, fontsize=7)
    ax_a.set_xlim(0, 1)
    ax_a.set_xticks([0, 0.5, 1.0])
    ax_a.set_xticklabels(["0 %", "50 %", "100 %"], fontsize=5.5)
    ax_a.set_xlabel("Response rate", fontsize=6.5, labelpad=4)
    ax_a.tick_params(axis="y", length=0)
    ax_a.spines["left"].set_visible(False)
    ax_a.legend(loc="lower right", fontsize=5.5, handlelength=0.9,
                handletextpad=0.3, borderpad=0.5)

    # ── B: Binary perturbed (gt = No) ─────────────────────────────────────
    _panel_label(ax_b, "B", x=-0.05)
    ax_b.set_title('Binary perturbed\n(ground truth = "No")', loc="center", pad=3)

    p_no_b  = np.array([m["binary_perturbed_acc"] for m in models_s])
    p_yes_b = 1 - p_no_b

    ax_b.barh(y, p_yes_b, bar_h, color=YES_COL, alpha=0.86,
              edgecolor="white", linewidth=0.4, label='"Yes"  ✗ incorrect')
    ax_b.barh(y, p_no_b,  bar_h, left=p_yes_b, color=NO_COL, alpha=0.86,
              edgecolor="white", linewidth=0.4, label='"No"   ✓ correct')

    for i, (py, pn) in enumerate(zip(p_yes_b, p_no_b)):
        if not np.isnan(py) and py >= MIN_BAR:
            ax_b.text(py / 2, i, f"{py:.0%}", ha="center", va="center",
                      fontsize=6, color="white", fontweight="bold")
        if not np.isnan(pn) and pn >= MIN_BAR:
            ax_b.text(py + pn / 2, i, f"{pn:.0%}", ha="center", va="center",
                      fontsize=6, color="white", fontweight="bold")

    ax_b.axvline(0.5, color="#888", lw=0.7, ls=":", alpha=0.45)
    ax_b.set_xlim(0, 1)
    ax_b.set_xticks([0, 0.5, 1.0])
    ax_b.set_xticklabels(["0 %", "50 %", "100 %"], fontsize=5.5)
    ax_b.set_xlabel("Response rate", fontsize=6.5, labelpad=4)
    ax_b.tick_params(labelleft=False, left=False)
    ax_b.spines["left"].set_visible(False)
    ax_b.legend(loc="lower right", fontsize=5.5, handlelength=0.9,
                handletextpad=0.3, borderpad=0.5)

    ax_a.set_ylim(-0.6, n - 0.4)

    save_fig(fig, out_dir, "fig9b_response_histograms")


# ---------------------------------------------------------------------------
# Helpers shared by fig10 and fig11
# ---------------------------------------------------------------------------

def _wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p     = k / n
    denom = 1 + z ** 2 / n
    ctr   = (p + z ** 2 / (2 * n)) / denom
    mar   = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return max(0.0, ctr - mar), min(1.0, ctr + mar)


def _reliability_curve(
    calib: list, x_lo: float, x_hi: float,
    n_bins: int = 8, min_n: int = 20,
) -> tuple:
    """Equal-width bins → (mean_conf, frac_correct, n, lo_ci, hi_ci)."""
    edges = np.linspace(x_lo, x_hi, n_bins + 1)
    xs, ys, ns, lo_cis, hi_cis = [], [], [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        pts = [(c, v) for c, v in calib if lo <= c < hi]
        if len(pts) < min_n:
            continue
        k = sum(v for _, v in pts)
        n = len(pts)
        lci, hci = _wilson_ci(k, n)
        xs.append(float(np.mean([c for c, _ in pts])))
        ys.append(k / n)
        ns.append(n)
        lo_cis.append(lci)
        hi_cis.append(hci)
    return xs, ys, ns, lo_cis, hi_cis


def _ece(calib: list, x_lo: float, x_hi: float, n_bins: int = 10) -> float:
    edges = np.linspace(x_lo, x_hi, n_bins + 1)
    total = len(calib)
    if total == 0:
        return float("nan")
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        pts = [(c, v) for c, v in calib if lo <= c < hi]
        if not pts:
            continue
        ece += (len(pts) / total) * abs(
            float(np.mean([v for _, v in pts])) -
            float(np.mean([c for c, _ in pts]))
        )
    return ece


# ---------------------------------------------------------------------------
# Figure 10 — Calibration reliability diagrams + ECE summary
# ---------------------------------------------------------------------------

def figure_calibration(models: list[dict], out_dir: Path) -> None:
    """
    fig10a: 2×3 small-multiples reliability diagrams, Nature publication style.
    Each panel: one model, binary (blue) and MCQ (red) calibration curves.
    Shared axes, all-black model titles, legend centred below the grid.
    """
    apply_nature_style()

    MIN_N   = 20
    BIN_COL = "#1A6FAF"   # deep steel blue  (print-safe)
    MCQ_COL = "#C0392B"   # muted crimson    (print-safe)

    models_s = sorted(models, key=_composite)
    n_m      = len(models_s)
    n_cols   = 3
    n_rows   = int(np.ceil(n_m / n_cols))

    fig = plt.figure(figsize=(7.2, 4.6))
    gs  = GridSpec(n_rows, n_cols, figure=fig,
                   hspace=0.60, wspace=0.22,
                   left=0.08, right=0.97,
                   top=0.91, bottom=0.18)

    ax0 = None
    sm_axes = []
    for idx in range(n_m):
        row, col = divmod(idx, n_cols)
        kw = dict(sharex=ax0, sharey=ax0) if ax0 is not None else {}
        ax = fig.add_subplot(gs[row, col], **kw)
        if ax0 is None:
            ax0 = ax
        sm_axes.append(ax)

    for idx in range(n_m, n_rows * n_cols):
        row, col = divmod(idx, n_cols)
        fig.add_subplot(gs[row, col]).set_visible(False)

    for idx, (ax, m) in enumerate(zip(sm_axes, reversed(models_s))):
        row, col = divmod(idx, n_cols)
        is_bottom = (row == n_rows - 1)
        is_left   = (col == 0)

        # ── Very subtle horizontal reference grid ─────────────────────────
        for g in [0.25, 0.50, 0.75, 1.0]:
            ax.axhline(g, color="#f0f0f0", lw=0.45, zorder=0)

        # ── Perfect calibration diagonal ──────────────────────────────────
        ax.plot([0.20, 1.02], [0.20, 1.02],
                ls="--", color="#bbbbbb", lw=0.85, alpha=0.90, zorder=2)

        # ── Reliability curves ────────────────────────────────────────────
        ece_entries = []
        for key, x_lo, col_t, marker, lw_ in (
            ("binary_calib", 0.50, BIN_COL, "o", 1.4),
            ("mcq_calib",    0.25, MCQ_COL, "s", 1.4),
        ):
            calib = m.get(key, [])
            if not calib:
                continue
            xs, ys, ns, lo_ci, hi_ci = _reliability_curve(
                calib, x_lo, 1.0, n_bins=6, min_n=MIN_N)
            if not xs:
                continue
            # Ghost CI band — barely-there
            ax.fill_between(xs, lo_ci, hi_ci,
                            alpha=0.08, color=col_t, linewidth=0, zorder=1)
            # Main curve
            ax.plot(xs, ys, marker=marker, ls="-",
                    color=col_t, lw=lw_, ms=4.2,
                    markeredgecolor="white", markeredgewidth=0.55,
                    zorder=4, solid_capstyle="round",
                    solid_joinstyle="round")
            ece_val = _ece(calib, x_lo, 1.0)
            lbl     = "Binary" if key == "binary_calib" else "MCQ"
            ece_entries.append((lbl, ece_val, col_t))

        # ── ECE annotation — upper-left, compact ─────────────────────────
        for k, (lbl, ev, ct) in enumerate(ece_entries):
            ax.text(0.05, 0.96 - k * 0.16,
                    f"{lbl}  ECE = {ev:.3f}",
                    transform=ax.transAxes,
                    ha="left", va="top",
                    fontsize=4.6, color=ct,
                    fontweight="semibold")

        # ── Axes ──────────────────────────────────────────────────────────
        ax.set_xlim(0.20, 1.04)
        ax.set_ylim(0.20, 1.04)
        ax.set_xticks([0.25, 0.50, 0.75, 1.00])
        ax.set_yticks([0.25, 0.50, 0.75, 1.00])
        xlbls = ["0.25", "0.50", "0.75", "1.00"] if is_bottom else []
        ylbls = ["0.25", "0.50", "0.75", "1.00"] if is_left   else []
        ax.set_xticklabels(xlbls, fontsize=5.2)
        ax.set_yticklabels(ylbls, fontsize=5.2)
        if is_bottom:
            ax.set_xlabel("Stated confidence", fontsize=6.0, labelpad=3)
        if is_left:
            ax.set_ylabel("Fraction correct",  fontsize=6.0, labelpad=3)

        # ── Spines & ticks ────────────────────────────────────────────────
        ax.spines["left"].set_linewidth(0.5)
        ax.spines["bottom"].set_linewidth(0.5)
        ax.spines["left"].set_color("#999999")
        ax.spines["bottom"].set_color("#999999")
        ax.tick_params(length=2.5, width=0.5, color="#999999")

        # ── Panel title — black, bold ──────────────────────────────────────
        ax.set_title(m["short"],
                     fontsize=7.0, fontweight="bold",
                     color="black", pad=5)

    # ── Shared legend — bottom centre, no frame ───────────────────────────
    fig.legend(handles=[
        plt.Line2D([0],[0], marker="o", ls="-", color=BIN_COL, lw=1.4,
                   ms=4.5, markeredgecolor="white", markeredgewidth=0.5,
                   label="Binary"),
        plt.Line2D([0],[0], marker="s", ls="-", color=MCQ_COL, lw=1.4,
                   ms=4.5, markeredgecolor="white", markeredgewidth=0.5,
                   label="MCQ"),
        plt.Line2D([0],[0], ls="--", color="#bbbbbb", lw=0.9,
                   label="Perfect calibration (diagonal)"),
    ], loc="lower center",
       bbox_to_anchor=(0.5, 0.005),
       ncol=3, fontsize=6.5,
       handlelength=1.6, handletextpad=0.5,
       columnspacing=1.8, frameon=False)

    fig.suptitle("Confidence calibration — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=0.98)
    save_fig(fig, out_dir, "fig10a_calibration_reliability")


def figure_calibration_prepost(models: list[dict], out_dir: Path) -> None:
    """
    tab10b: LaTeX booktabs table — overconfidence (confidence − accuracy)
    before and after training cutoff for Binary, MCQ, and Date tasks.
    Date accuracy = fraction of predictions within 12 months of ground truth.
    FRQ is excluded: no confidence field in FRQ task results.
    Saves tab10b_calibration_prepost.tex ready to \\input into any LaTeX doc.
    """
    MIN_N = 20

    def _oc(calib: list) -> float | None:
        """Overconfidence = mean(conf) − mean(accuracy). Returns None if n < MIN_N."""
        if len(calib) < MIN_N:
            return None
        return float(np.mean([c for c, _ in calib])) - float(np.mean([v for _, v in calib]))

    models_s = sorted(models, key=_composite, reverse=True)  # best first

    # ── Collect values ────────────────────────────────────────────────────
    rows = []
    for m in models_s:
        bp  = _oc(m.get("binary_pre_calib",  []))
        bpo = _oc(m.get("binary_post_calib", []))
        mp  = _oc(m.get("mcq_pre_calib",     []))
        mpo = _oc(m.get("mcq_post_calib",    []))
        dp  = _oc(m.get("date_pre_calib",    []))
        dpo = _oc(m.get("date_post_calib",   []))
        rows.append(dict(
            name = m["short"],
            bp=bp,   bpo=bpo,  bd=(bpo-bp)   if bp  is not None and bpo  is not None else None,
            mp=mp,   mpo=mpo,  md=(mpo-mp)   if mp  is not None and mpo  is not None else None,
            dp=dp,   dpo=dpo,  dd=(dpo-dp)   if dp  is not None and dpo  is not None else None,
        ))

    # ── Formatters ────────────────────────────────────────────────────────
    DASH = r"\text{---}"

    def fv(v: float | None) -> str:
        """Plain value — phantom minus for alignment."""
        if v is None:
            return DASH
        return rf"${v:.3f}$" if v < 0 else rf"$\phantom{{-}}{v:.3f}$"

    def fd(v: float | None) -> str:
        """Signed Δ — bold if positive (overconfidence worsened)."""
        if v is None:
            return DASH
        sign = "+" if v >= 0 else ""
        s = rf"${sign}{v:.3f}$"
        if v > 0.002:
            s = rf"\textbf{{{s}}}"
        return s

    # ── Build LaTeX ───────────────────────────────────────────────────────
    L = []
    L.append(r"% Auto-generated by compare_models.py  –  do not edit by hand")
    L.append(r"\begin{table}[htbp]")
    L.append(r"  \centering")
    L.append(r"  \caption{%")
    L.append(r"    Confidence calibration before and after the training knowledge cutoff")
    L.append(r"    for three task types.")
    L.append(r"    Overconfidence $= \bar{c} - \bar{a}$, where $\bar{c}$ is the mean stated")
    L.append(r"    confidence and $\bar{a}$ is task accuracy; zero indicates perfect calibration.")
    L.append(r"    For the date task, accuracy is defined as the fraction of predictions")
    L.append(r"    falling within 12~months of the ground truth.")
    L.append(r"    $\Delta = \text{post-cutoff} - \text{pre-cutoff}$;")
    L.append(r"    \textbf{bold positive~$\Delta$} indicates overconfidence \emph{increased}")
    L.append(r"    after the knowledge cutoff (``unknown unknowns'' effect).")
    L.append(r"    Dashes (---) indicate models whose training cutoff predates all benchmark")
    L.append(r"    questions, leaving no pre-cutoff partition.")
    L.append(r"    FRQ results are excluded: no confidence score is recorded for that task.%")
    L.append(r"  }")
    L.append(r"  \label{tab:calibration_prepost}")
    L.append(r"  \setlength{\tabcolsep}{5pt}")
    L.append(r"  \renewcommand{\arraystretch}{1.15}")
    L.append(r"  \small")
    # Wide table: wrap in resizebox so it always fits the text width
    L.append(r"  \resizebox{\textwidth}{!}{%")
    L.append(r"  \begin{tabular}{l rrr rrr rrr}")
    L.append(r"    \toprule")
    L.append(r"    & \multicolumn{3}{c}{\textit{Binary task}}")
    L.append(r"    & \multicolumn{3}{c}{\textit{MCQ task}}")
    L.append(r"    & \multicolumn{3}{c}{\textit{Date task} ($\leq$12\,mo)} \\")
    L.append(r"    \cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}")
    L.append(r"    \textbf{Model}")
    L.append(r"      & \textbf{Pre} & \textbf{Post} & $\boldsymbol{\Delta}$")
    L.append(r"      & \textbf{Pre} & \textbf{Post} & $\boldsymbol{\Delta}$")
    L.append(r"      & \textbf{Pre} & \textbf{Post} & $\boldsymbol{\Delta}$ \\")
    L.append(r"    \midrule")

    for r in rows:
        name = r["name"].replace(" ", "~")
        L.append(
            f"    {name}"
            f" & {fv(r['bp'])}  & {fv(r['bpo'])}  & {fd(r['bd'])}"
            f" & {fv(r['mp'])}  & {fv(r['mpo'])}  & {fd(r['md'])}"
            f" & {fv(r['dp'])}  & {fv(r['dpo'])}  & {fd(r['dd'])} \\\\"
        )

    L.append(r"    \bottomrule")
    L.append(r"  \end{tabular}}")   # closes resizebox
    L.append(r"\end{table}")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tab10b_calibration_prepost.tex"
    out_path.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"  Saved tab10b_calibration_prepost.tex")





def figure_pre_post_cutoff(models: list[dict], out_dir: Path) -> None:
    """
    fig11: Four-panel pre vs post training-cutoff analysis.
      A  MCQ accuracy paired comparison  (pre vs post)
      B  Binary accuracy paired comparison
      C  Date absolute error paired comparison
      D  Continuous MCQ accuracy vs months-since-cutoff (95 % CI bands)
    Panels A–C reveal the step-change at the knowledge boundary;
    panel D shows how performance decays continuously with time.
    """
    apply_nature_style()

    BIN_SIZE = 6
    MIN_N    = 10

    def _pp(offset_dict: dict) -> dict:
        pre  = [v for off, vs in offset_dict.items() if off <  0 for v in vs]
        post = [v for off, vs in offset_dict.items() if off >= 0 for v in vs]
        def _s(lst):
            if not lst:
                return float("nan"), 0.0, 0
            mu = float(np.mean(lst))
            se = float(np.std(lst, ddof=1) / np.sqrt(len(lst))) if len(lst) > 1 else 0.0
            return mu, se, len(lst)
        return {"pre": _s(pre), "post": _s(post)}

    pp_data = []
    for m in models:
        date_abs = {off: [abs(v) for v in vs]
                    for off, vs in m["rel_date_signed"].items()}
        pp_data.append({
            "name":   m["short"],
            "color":  m["color"],
            "marker": m["marker"],
            "mcq":    _pp(m["rel_mcq"]),
            "bin":    _pp(m["rel_binary"]),
            "date":   _pp(date_abs),
        })

    fig = plt.figure(figsize=(7.2, 6.0))
    gs  = GridSpec(2, 2, figure=fig, hspace=0.52, wspace=0.38,
                   left=0.09, right=0.97, top=0.91, bottom=0.10)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    def _paired(ax, letter, title, key, ylabel, chance, higher_better=True):
        _panel_label(ax, letter)
        ax.set_title(title, loc="left")

        for p_ in pp_data:
            pre_mu,  pre_se,  pre_n  = p_[key]["pre"]
            post_mu, post_se, post_n = p_[key]["post"]
            col = p_["color"]

            if not (np.isnan(pre_mu) or np.isnan(post_mu)):
                ax.plot([0, 1], [pre_mu, post_mu],
                        color=col, lw=1.3, alpha=0.70, zorder=2)

            for xp, mu, se, n in ((0, pre_mu,  pre_se,  pre_n),
                                   (1, post_mu, post_se, post_n)):
                if np.isnan(mu):
                    continue
                s = max(18, min(85, 3 * n ** 0.5))
                ax.scatter(xp, mu, color=col, s=s, marker=p_["marker"],
                           zorder=4, edgecolors="white", linewidths=0.55)
                ax.errorbar(xp, mu, yerr=se, fmt="none", ecolor=col,
                            elinewidth=0.8, capsize=2.5, capthick=0.65,
                            zorder=3, alpha=0.75)

            # Model label to the right
            ref = post_mu if not np.isnan(post_mu) else pre_mu
            if not np.isnan(ref):
                suffix = "" if not np.isnan(post_mu) else " (no post)"
                ax.text(1.07, ref, p_["name"] + suffix,
                        va="center", ha="left", fontsize=5, color=col,
                        style="normal" if not np.isnan(post_mu) else "italic")

        if chance is not None:
            ax.axhline(chance, color="#888888", lw=0.7, ls=":", alpha=0.5)
            ax.text(0.5, chance + 0.008, f"Chance ({chance})",
                    transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=4.8, color="#888888")

        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Pre-cutoff", "Post-cutoff"],
                           fontsize=7.5, fontweight="bold")
        ax.set_xlim(-0.30, 1.65)
        ax.set_ylabel(ylabel, fontsize=7)
        ax.tick_params(axis="x", length=0)
        ax.spines["bottom"].set_visible(False)
        ax.text(0.01, 0.01, "Dot size ∝ √n",
                transform=ax.transAxes, ha="left", va="bottom",
                fontsize=4.5, color="#999999", style="italic")

    _paired(ax_a, "A", "MCQ accuracy\npre vs post training cutoff",
            "mcq", "MCQ accuracy", 0.25)
    _paired(ax_b, "B", "Binary accuracy\npre vs post training cutoff",
            "bin", "Binary accuracy (merged)", 0.50)
    _paired(ax_c, "C", "Date absolute error\npre vs post training cutoff",
            "date", "Mean |date error| (months)", None, higher_better=False)

    # ── D: Continuous MCQ accuracy vs months since cutoff ─────────────────
    _panel_label(ax_d, "D")
    ax_d.set_title("MCQ accuracy vs months since training cutoff\n"
                   "(95 % CI shaded; each model aligned to its own cutoff)",
                   loc="left")

    def _bc(o): return (o // BIN_SIZE) * BIN_SIZE + BIN_SIZE // 2

    all_offsets: list[int] = []
    for m in models:
        bins: dict[int, list] = defaultdict(list)
        for off, vs in m["rel_mcq"].items():
            bins[_bc(off)].extend(vs)
        xs, ys, cis = [], [], []
        for bc in sorted(bins):
            vs = bins[bc]
            if len(vs) >= MIN_N:
                mu = float(np.mean(vs))
                se = float(np.std(vs, ddof=1) / np.sqrt(len(vs)))
                xs.append(bc); ys.append(mu); cis.append(1.96 * se)
                all_offsets.append(bc)
        if xs:
            xa, ya, ca = np.array(xs), np.array(ys), np.array(cis)
            ax_d.fill_between(xa, ya - ca, ya + ca,
                              alpha=0.11, color=m["color"], linewidth=0)
            ax_d.plot(xa, ya, linestyle=m["ls"], color=m["color"],
                      marker=m["marker"], markersize=3.5, linewidth=1.2,
                      label=f"{m['short']}  [{m['cutoff']}]",
                      markeredgecolor="white", markeredgewidth=0.4,
                      alpha=0.92)

    ax_d.axvline(0, color="#CC3311", lw=1.3, ls="--", alpha=0.85,
                 zorder=6, label="Training cutoff")
    ax_d.axhline(0.25, color="#888888", lw=0.65, ls=":", alpha=0.5,
                 label="MCQ chance (0.25)")

    if all_offsets:
        pad = BIN_SIZE + 4
        xl, xh = min(all_offsets) - pad, max(all_offsets) + pad
        ax_d.set_xlim(xl, xh)
        ax_d.axvspan(xl, 0, alpha=0.04, color="#2166AC", linewidth=0)
        ax_d.axvspan(0,  xh, alpha=0.04, color="#B2182B", linewidth=0)
        ax_d.text(0.01, 0.96, "Pre-cutoff", transform=ax_d.transAxes,
                  va="top", fontsize=5.5, color="#2166AC", style="italic")
        ax_d.text(0.99, 0.96, "Post-cutoff", transform=ax_d.transAxes,
                  va="top", ha="right", fontsize=5.5, color="#B2182B",
                  style="italic")

    ax_d.set_ylim(0.10, 0.75)
    ax_d.set_xlabel("Months since training cutoff", fontsize=7)
    ax_d.set_ylabel("MCQ accuracy", fontsize=7)
    ax_d.legend(loc="lower right", fontsize=5, ncol=1,
                handlelength=1.4, handletextpad=0.4)

    fig.suptitle(
        "Temporal knowledge boundary — pre vs post training-cutoff performance\n"
        "CUSP Benchmark",
        fontsize=8.5, fontweight="bold", y=0.98)
    save_fig(fig, out_dir, "fig11_pre_post_cutoff")


# ---------------------------------------------------------------------------
# Figure 12 — FRQ overview (leaderboard, distributions, radar, area heatmap)
# ---------------------------------------------------------------------------

# Grade bands for FRQ score (0–10 scale, pass ≥ 5)
_FRQ_BANDS = [
    (0.0,  2.0, "Poor",       "#8B0000"),
    (2.0,  4.0, "Partial",    "#D55E00"),
    (4.0,  5.0, "Near-pass",  "#E69F00"),
    (5.0,  7.5, "Pass",       "#1A9850"),
    (7.5, 11.0, "Excellent",  "#004D40"),
]
_FRQ_PASS = 5.0
_DIM_MAX  = {"alignment": 10.0, "specificity": 10.0,
             "novelty": 10.0,   "feasibility": 10.0}


def _frq_sorted(models: list[dict]) -> list[dict]:
    """Return models sorted ascending by frq_mean (best at top in horizontal bar)."""
    return sorted(models, key=lambda m: m["frq_mean"] if not np.isnan(m["frq_mean"]) else -1)


def figure_frq_overview(models: list[dict], out_dir: Path) -> None:
    """
    fig12: FRQ prediction quality overview.
      A  Sub-dimension radar — alignment / specificity / novelty / feasibility
      B  Score distributions — violin per model (full shape)
    """
    apply_nature_style()

    frq_models = [m for m in _frq_sorted(models) if m["frq_scores"]]
    if not frq_models:
        print("  Skipping fig12 — no FRQ data found.")
        return

    n_m   = len(frq_models)
    names = [m["short"] for m in frq_models]

    fig = plt.figure(figsize=(7.2, 3.8))
    gs  = GridSpec(1, 2, figure=fig, wspace=0.42,
                   left=0.08, right=0.97, top=0.88, bottom=0.14)
    ax_a = fig.add_subplot(gs[0, 0], projection="polar")
    ax_b = fig.add_subplot(gs[0, 1])

    # ── A: Sub-dimension radar ────────────────────────────────────────────
    _panel_label(ax_a, "A")
    DIM_LABELS = ["Alignment\n(/10)", "Specificity\n(/10)",
                  "Novelty\n(/10)", "Feasibility\n(/10)"]
    DIM_KEYS   = ["frq_alignment", "frq_specificity",
                  "frq_novelty",   "frq_feasibility"]
    DIM_NORMS  = [10.0, 10.0, 10.0, 10.0]
    N_spokes   = len(DIM_KEYS)
    angles     = np.linspace(0, 2 * np.pi, N_spokes, endpoint=False).tolist()
    angles_c   = angles + [angles[0]]

    for m in reversed(frq_models):
        vals = []
        for key, norm in zip(DIM_KEYS, DIM_NORMS):
            raw = m.get(key, [])
            vals.append(float(np.mean(raw)) / norm if raw else 0.0)
        vals_c = vals + [vals[0]]
        ax_a.plot(angles_c, vals_c, linestyle=m["ls"], marker=m["marker"],
                  color=m["color"], linewidth=1.4, markersize=4,
                  markeredgecolor="white", markeredgewidth=0.4,
                  label=m["short"], alpha=0.92, zorder=3)
        ax_a.fill(angles_c, vals_c, alpha=0.07, color=m["color"])

    ax_a.set_xticks(angles)
    ax_a.set_xticklabels(DIM_LABELS, size=6.5, color="#222222")
    ax_a.set_ylim(0, 1)
    ax_a.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_a.set_yticklabels(["0.25", "0.50", "0.75", "1.0"], size=4.5, color="#888")
    ax_a.spines["polar"].set_linewidth(0.4)
    ax_a.grid(lw=0.3, alpha=0.45, color="#aaaaaa")
    ax_a.set_title("Sub-dimension profile\n(normalized to dimension max)",
                   size=7, pad=12, fontweight="bold")
    ax_a.legend(loc="lower left", bbox_to_anchor=(-0.22, -0.18),
                fontsize=5.5, ncol=2, handlelength=1.4,
                handletextpad=0.3, columnspacing=0.6)

    # ── B: Score distribution violins ────────────────────────────────────
    _panel_label(ax_b, "B")
    ax_b.set_title("FRQ score distribution per model", loc="left")

    for lo, hi, lbl, col in _FRQ_BANDS:
        ax_b.axhspan(lo, hi, alpha=0.06, color=col, linewidth=0)
        ax_b.text(n_m - 0.05, (lo + hi) / 2, lbl,
                  va="center", ha="right", fontsize=4.5, color=col,
                  style="italic")

    positions = list(range(n_m))
    for i, m in enumerate(frq_models):
        if not m["frq_scores"]:
            continue
        vp = ax_b.violinplot(m["frq_scores"], positions=[i], widths=0.72,
                             showmedians=True, showextrema=False)
        for pc in vp["bodies"]:
            pc.set_facecolor(m["color"])
            pc.set_edgecolor(m["color"])
            pc.set_alpha(0.50)
        vp["cmedians"].set_color("white")
        vp["cmedians"].set_linewidth(1.6)
        vp["cmedians"].set_zorder(5)
        med = float(np.median(m["frq_scores"]))
        ax_b.text(i, med + 0.18, f"{med:.1f}", ha="center", va="bottom",
                  fontsize=5, color=m["color"], fontweight="bold")

    ax_b.axhline(_FRQ_PASS, color="#333333", lw=0.9, ls="--", alpha=0.6,
                 zorder=4, label="Pass threshold (5.0)")
    ax_b.set_xticks(positions)
    ax_b.set_xticklabels(names, rotation=30, ha="right", fontsize=6)
    ax_b.set_ylabel("FRQ score (0–10)", fontsize=7)
    ax_b.set_ylim(0, 10.5)
    ax_b.tick_params(axis="x", length=0)
    ax_b.spines["bottom"].set_visible(False)

    fig.suptitle("FRQ scientific prediction quality — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=0.98)
    save_fig(fig, out_dir, "fig12_frq_overview")


# ---------------------------------------------------------------------------
# Figure 13 — FRQ deep-dive (grades, dimensions, scatter, MCQ consistency)
# ---------------------------------------------------------------------------

def figure_frq_dimensions(models: list[dict], out_dir: Path) -> None:
    """
    fig13: FRQ sub-dimension deep-dive.
      A  Grade-band breakdown — % of predictions in each quality tier per model
      B  Normalized sub-dimension heatmap (model × dim, 0–1 scale, red=low blue=high)
    """
    apply_nature_style()

    frq_models = [m for m in _frq_sorted(models) if m["frq_scores"]]
    if not frq_models:
        print("  Skipping fig13 — no FRQ data found.")
        return

    n_m   = len(frq_models)
    names = [m["short"] for m in frq_models]
    y     = np.arange(n_m)

    fig = plt.figure(figsize=(7.2, 3.8))
    gs  = GridSpec(1, 2, figure=fig, wspace=0.42,
                   left=0.12, right=0.97, top=0.88, bottom=0.14)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    # ── A: Grade-band stacked horizontal bars ─────────────────────────────
    _panel_label(ax_a, "A")
    ax_a.set_title("Prediction quality grade distribution\n(% per model)", loc="left")

    lefts = np.zeros(n_m)
    for lo, hi, lbl, col in _FRQ_BANDS:
        fracs = np.array([
            np.mean([(lo <= s < hi) for s in m["frq_scores"]])
            if m["frq_scores"] else 0.0
            for m in frq_models
        ])
        ax_a.barh(y, fracs, 0.58, left=lefts,
                  color=col, alpha=0.88, edgecolor="white",
                  linewidth=0.3, label=lbl)
        for i, (frac, left) in enumerate(zip(fracs, lefts)):
            if frac > 0.08:
                ax_a.text(left + frac / 2, i, f"{frac:.0%}",
                          ha="center", va="center", fontsize=4.8,
                          color="white", fontweight="bold")
        lefts += fracs

    ax_a.axvline(0.5, color="#888888", lw=0.6, ls=":", alpha=0.5)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(names, fontsize=7)
    ax_a.set_xlabel("Fraction of predictions", fontsize=7)
    ax_a.set_xlim(0, 1.02)
    ax_a.tick_params(axis="y", length=0)
    ax_a.spines["left"].set_visible(False)
    ax_a.legend(loc="lower right", ncol=3, fontsize=5,
                handlelength=0.9, handletextpad=0.3,
                columnspacing=0.5, borderpad=0.4)

    # ── B: Normalized sub-dimension heatmap ───────────────────────────────
    _panel_label(ax_b, "B")
    ax_b.set_title("Sub-dimension scores (normalized 0–1)\nred = low  ·  blue = high",
                   loc="left")

    DIM_KEYS  = ["frq_alignment", "frq_specificity",
                 "frq_novelty",   "frq_feasibility"]
    DIM_NORMS = [10.0, 10.0, 10.0, 10.0]
    DIM_LBLS  = ["Alignment", "Specificity", "Novelty", "Feasibility"]

    mat_b = np.full((n_m, 4), np.nan)
    for i, m in enumerate(frq_models):
        for j, (key, norm) in enumerate(zip(DIM_KEYS, DIM_NORMS)):
            raw = m.get(key, [])
            if raw:
                mat_b[i, j] = float(np.mean(raw)) / norm

    masked_b = np.ma.masked_invalid(mat_b)
    im_b = ax_b.imshow(masked_b, cmap="RdBu", vmin=0, vmax=1,
                       aspect="auto", interpolation="nearest")

    for i in range(n_m):
        for j in range(4):
            v = mat_b[i, j]
            if not np.isnan(v):
                fg = "white" if (v < 0.25 or v > 0.75) else "#1a1a1a"
                raw_val = v * DIM_NORMS[j]
                ax_b.text(j, i, f"{raw_val:.1f}\n({v:.2f})",
                          ha="center", va="center", fontsize=4.8,
                          color=fg, linespacing=1.25)

    ax_b.set_xticks(range(4))
    ax_b.set_xticklabels(DIM_LBLS, fontsize=7)
    ax_b.set_yticks(range(n_m))
    ax_b.set_yticklabels(names, fontsize=7)
    ax_b.xaxis.set_tick_params(length=0)
    ax_b.yaxis.set_tick_params(length=0)
    for sp in ax_b.spines.values():
        sp.set_visible(False)

    cb_b = fig.colorbar(im_b, ax=ax_b, shrink=0.75, pad=0.03, aspect=20)
    cb_b.set_label("Normalized score", fontsize=5.5)
    cb_b.ax.tick_params(labelsize=5)
    cb_b.outline.set_linewidth(0.4)

    fig.suptitle("FRQ sub-dimension analysis — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=0.98)
    save_fig(fig, out_dir, "fig13_frq_dimensions")


# ---------------------------------------------------------------------------
# Figure 14 — Post-cutoff MCQ accuracy by research area (grouped bar chart)
# ---------------------------------------------------------------------------

def figure_area_bar_postcut(models: list[dict], out_dir: Path) -> None:
    """
    fig14: Grouped vertical bar chart — MCQ accuracy by research area,
    post-cutoff questions only (offset >= 0).  One bar per model per area,
    sorted by cross-model average difficulty (hardest area on the left).
    """
    apply_nature_style()

    # Only include models that have any post-cutoff MCQ data
    active = [m for m in models if any(m["area_mcq_post"].values())]
    if not active:
        print("  Skipping fig14 — no post-cutoff area data (pass --benchmark)")
        return

    active_sorted = sorted(active, key=_composite)   # ascending, colours match other figs

    # ── Per-area cross-model average (for sorting) ────────────────────────
    area_avgs = {}
    for area in AREA_ORDER:
        vals = [_sm(m["area_mcq_post"].get(area, [])) for m in active_sorted]
        vals = [v for v in vals if not np.isnan(v)]
        area_avgs[area] = float(np.mean(vals)) if vals else float("nan")

    # Sort areas ascending by avg accuracy (hardest → easiest left to right)
    areas_sorted = sorted(
        [a for a in AREA_ORDER if not np.isnan(area_avgs[a])],
        key=lambda a: area_avgs[a],
    )
    area_labels = [AREA_SHORT.get(a, a).replace("\n", " ") for a in areas_sorted]

    n_areas  = len(areas_sorted)
    n_models = len(active_sorted)
    total_w  = 0.75                     # total bar-group width per area
    bw       = total_w / n_models       # individual bar width

    fig_h = 3.8
    fig, ax = plt.subplots(figsize=(7.2, fig_h),
                           gridspec_kw={"left": 0.09, "right": 0.97,
                                        "top": 0.88, "bottom": 0.22})

    x = np.arange(n_areas)

    for j, m in enumerate(active_sorted):
        offset = (j - n_models / 2 + 0.5) * bw
        accs = np.array([
            _sm(m["area_mcq_post"].get(area, []))
            for area in areas_sorted
        ])
        ns = np.array([
            len(m["area_mcq_post"].get(area, []))
            for area in areas_sorted
        ])
        # 95 % Wilson CI half-widths for error bars
        errs = np.array([
            (1.96 * np.sqrt(max(p, 0) * (1 - max(p, 0)) / max(n, 1))
             if not np.isnan(p) and n > 0 else 0.0)
            for p, n in zip(accs, ns)
        ])

        bars = ax.bar(x + offset, accs, bw * 0.88,
                      color=m["color"], alpha=0.85,
                      edgecolor="white", linewidth=0.35,
                      label=m["short"], zorder=3)
        ax.errorbar(x + offset, accs, yerr=errs, fmt="none",
                    ecolor="#333333", elinewidth=0.65,
                    capsize=1.8, capthick=0.6, zorder=4, alpha=0.7)

    # Chance reference
    ax.axhline(0.25, color="#888888", lw=0.8, ls="--", alpha=0.55,
               zorder=2, label="MCQ chance (0.25)")

    # Cross-model average line
    avg_line = [area_avgs[a] for a in areas_sorted]
    ax.plot(x, avg_line, "D--", color="#333333", ms=4.5, lw=0.9,
            markeredgecolor="white", markeredgewidth=0.4,
            zorder=5, alpha=0.70, label="Cross-model mean")

    ax.set_xticks(x)
    ax.set_xticklabels(area_labels, rotation=35, ha="right", fontsize=6.5)
    ax.set_ylabel("MCQ accuracy (post-cutoff)", fontsize=7)
    ax.set_ylim(0, 0.78)
    ax.set_xlim(-0.55, n_areas - 0.45)
    ax.tick_params(axis="x", length=0)
    ax.spines["bottom"].set_visible(False)

    # Subtle vertical separators between area groups
    for xi in x[1:]:
        ax.axvline(xi - 0.5, color="#eeeeee", lw=0.5, zorder=1)

    ax.legend(loc="upper left", ncol=2, fontsize=5.8,
              handlelength=1.2, handletextpad=0.4, columnspacing=0.8,
              framealpha=0.92, edgecolor="#cccccc")

    ax.text(0.99, 0.98,
            "Areas sorted left → right by increasing cross-model accuracy\n"
            "(leftmost = hardest post-cutoff domain)",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=4.8, color="#555555", style="italic",
            multialignment="right")

    fig.suptitle("Post-cutoff MCQ accuracy by research domain — CUSP Benchmark",
                 fontsize=8.5, fontweight="bold", y=0.97)
    save_fig(fig, out_dir, "fig14_area_bar_postcut")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CUSP — Nature-quality multi-model comparison plots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python compare_models.py \\\n"
            "      --results  model_results/ \\\n"
            "      --benchmark benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl\n"
        ),
    )
    p.add_argument("--results",    default="model_results/",
                   help="Directory containing model result JSON files")
    p.add_argument("--benchmark",  default=None,
                   help="Benchmark JSONL — required for fig3 (area heatmap), "
                        "fig5 (cutoff), fig6 (area radar)")
    p.add_argument("--output-dir", default=None,
                   help="Output directory (default: <results>/comparison_figures/)")
    p.add_argument("--show", action="store_true",
                   help="Open generated PNGs after saving")
    return p


def main() -> None:
    args    = build_parser().parse_args()
    out_dir = (Path(args.output_dir) if args.output_dir
               else Path(args.results) / "comparison_figures")

    models = load_all_models(args.results, args.benchmark)
    if not models:
        print("No model results found. Check --results and MODEL_REGISTRY.")
        return

    print(f"\nLoaded {len(models)} models (ascending composite score):")
    has_frq = any(not np.isnan(m.get("frq_mean", float("nan"))) for m in models)
    for m in models:
        frq_str = (f"  frq={m['frq_mean']:.3f}  pass={m['frq_pass']:.1%}"
                   if not np.isnan(m.get("frq_mean", float("nan"))) else "")
        print(f"  {m['short']:15s}  merged-binary={m['merged_binary_acc']:.3f}  "
              f"mcq={m['mcq_acc']:.3f}  date={m['date_score']:.3f}  "
              f"cutoff={m['cutoff']}{frq_str}")

    print(f"\nGenerating figures → {out_dir}/\n")

    figure_leaderboard(models, out_dir)
    figure_radar(models, out_dir)
    figure_bias(models, out_dir)

    if args.benchmark:
        figure_area_heatmap(models, out_dir)
        figure_cutoff_temporal(models, out_dir)
        figure_area_radar(models, out_dir)
        figure_cusp_area_radar(models, out_dir)
        figure_area_bar_postcut(models, out_dir)   # fig14
    else:
        print("  Skipping fig3, fig5, fig6, fig14 (pass --benchmark)")

    # Date deep-dive figures (always run — data comes from result files)
    figure_date_errors(models, out_dir)
    figure_date_predictions(models, out_dir)

    # Response distribution bias index (fig9) + raw histograms (fig9b)
    figure_response_distributions(models, out_dir)
    figure_response_histograms(models, out_dir)

    # Calibration reliability small multiples (fig10a) + overconfidence pre/post (fig10b)
    figure_calibration(models, out_dir)
    figure_calibration_prepost(models, out_dir)
    figure_pre_post_cutoff(models, out_dir)

    # FRQ figures (when FRQ data is present in the result files)
    if has_frq:
        figure_frq_overview(models, out_dir)
        figure_frq_dimensions(models, out_dir)
    else:
        print("  Skipping fig12, fig13 (no FRQ data in result files)")

    print("\nDone.")

    if args.show:
        names = ["fig1_leaderboard", "fig2_radar", "fig4_bias",
                 "fig7_date_errors", "fig8_date_predictions",
                 "fig9_response_distributions",
                 "fig10_calibration", "fig11_pre_post_cutoff"]
        if has_frq:
            names += ["fig12_frq_overview", "fig13_frq_dimensions"]
        if args.benchmark:
            names += ["fig3_area_heatmap", "fig5_cutoff_temporal",
                      "fig6_area_radar", "fig14_cusp_area_radar"]
        for name in names:
            p = out_dir / f"{name}.png"
            if p.exists():
                _open_file(p)


if __name__ == "__main__":
    main()
