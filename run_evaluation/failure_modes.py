"""
failure_modes.py — Nature-quality "failure mode" figures for the CUSP benchmark.

Reuses the data-loading, styling, and helper machinery from compare_models.py and
produces four publication-quality figures, **post-cutoff questions only**
(offset >= 0, i.e. genuine forecasting beyond each model's training cutoff):

  fm1_yesno_bias            : binary Yes/No answer distribution per model, split by
                              ground-truth condition (reveals response bias)
  fm2_frq_criteria          : FRQ failure — per-model small-multiple violins of
                              all four criteria (alignment/specificity/novelty/
                              feasibility) with the alignment->feasibility gap
  fm2b_alignment_feasibility_gap : per-model dumbbell of the alignment-feasibility
                              gap (mean-based; medians collapse on integer scores)
  fm3_calibration           : confidence-calibration failure — reliability
                              small-multiples with ECE / overconfidence
  fm4_date_failure          : date-prediction failure — per-model signed-error
                              distribution histograms (directional / anchoring bias)

Usage
-----
  python failure_modes.py \\
      --results   frq_results/ \\
      --benchmark ../benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \\
      [--output-dir failure_mode_figures/] [--show]

The --benchmark JSONL is required: post-cutoff partitioning needs each question's
publication date.  Edit MODEL_REGISTRY in compare_models.py to change models,
cutoffs, colours, and markers — this script inherits all of it.

Requirements: matplotlib >= 3.5, numpy
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Inherit the entire infrastructure from the sibling comparison script.
from compare_models import (
    apply_nature_style,
    _panel_label,
    save_fig,
    _open_file,
    load_all_models,
    _composite,
    _reliability_curve,
    _ece,
)

# ---------------------------------------------------------------------------
# Palette / constants (failure-mode emphasis)
# ---------------------------------------------------------------------------

YES_COLOR = "#B2182B"   # deep red   — "Yes" / over-prediction
NO_COLOR  = "#2166AC"   # deep blue  — "No"
GAP_COLOR = "#E74C3C"   # alarm red  — gap shading
GOOD_BAND = "#1A9850"   # green      — acceptable zone

BIN_COL = "#1A6FAF"     # binary calibration curve
MCQ_COL = "#C0392B"     # mcq calibration curve

FRQ_NORM = 10.0         # all FRQ sub-dimensions are scored 0-10


# ---------------------------------------------------------------------------
# Small post-cutoff metric helpers
# ---------------------------------------------------------------------------

def _post_models(models: list[dict], need: str = "any") -> list[dict]:
    """Filter to models that actually have post-cutoff data for a given mode."""
    def has(m: dict) -> bool:
        if need == "binary":
            return (m.get("bin_n_post", 0) + m.get("bp_n_post", 0)) > 0
        if need == "frq":
            return bool(m.get("frq_alignment")) and bool(m.get("frq_feasibility"))
        if need == "calib":
            return bool(m.get("binary_post_calib")) or bool(m.get("mcq_post_calib"))
        if need == "date":
            return bool(m.get("date_signed_post"))
        return True
    return [m for m in models if has(m)]


# ---------------------------------------------------------------------------
# Failure mode 1 — Binary Yes/No response bias
# ---------------------------------------------------------------------------

def figure_yesno_bias(models: list[dict], out_dir: Path) -> None:
    """
    Single figure (post-cutoff): Yes/No answer distribution per model, broken out
    by the ground-truth condition.  Each model gets two 100%-stacked bars —

      upper bar  : questions whose truth is "Yes"
      lower bar  : questions whose truth is "No"

    coloured by the model's answer (red = answered "Yes", blue = answered "No").
    An unbiased, discriminating model would make the upper bar mostly red and the
    lower bar mostly blue.  A biased model makes BOTH bars the same colour —
    answering one way regardless of the truth.  Models are ordered by overall
    P(Yes), from most "No"-leaning (bottom) to most "Yes"-leaning (top).
    """
    apply_nature_style()
    ms = _post_models(models, "binary")
    if not ms:
        print("  Skipping fm1 — no post-cutoff binary data")
        return

    def _p_yes(m: dict) -> float:
        ny, nn = m["bin_n_post"], m["bp_n_post"]
        say_yes = m["bin_c_post"] + (nn - m["bp_c_post"])
        return say_yes / (ny + nn) if (ny + nn) else float("nan")

    ms = sorted(ms, key=_p_yes)              # most "No"-leaning first → bottom
    n  = len(ms)

    fig, ax = plt.subplots(figsize=(9.5, max(3.2, 0.72 * n + 1.0)),
                           gridspec_kw={"left": 0.13, "right": 0.985,
                                        "top": 0.84, "bottom": 0.13})

    BH  = 0.34                                # bar height
    GAP = 0.40                                # half-gap between the two condition bars

    for i, m in enumerate(ms):
        # truth = "Yes": fraction answered Yes (correct) vs No (wrong)
        ty_yes = m["binary_acc_post"]
        # truth = "No": fraction answered Yes (wrong) vs No (correct)
        tn_yes = 1.0 - m["binary_perturbed_acc_post"]

        for sub_y, p_yes, cond in ((i + GAP / 2, ty_yes, "Yes"),
                                   (i - GAP / 2, tn_yes, "No")):
            p_no = 1.0 - p_yes
            ax.barh(sub_y, p_yes, BH, color=YES_COLOR, alpha=0.88,
                    edgecolor="white", linewidth=0.5, zorder=3)
            ax.barh(sub_y, p_no, BH, left=p_yes, color=NO_COLOR, alpha=0.88,
                    edgecolor="white", linewidth=0.5, zorder=3)
            # in-bar percentage labels
            if p_yes >= 0.12:
                ax.text(p_yes / 2, sub_y, f"{p_yes:.0%}", ha="center",
                        va="center", fontsize=5.4, color="white",
                        fontweight="bold", zorder=4)
            if p_no >= 0.12:
                ax.text(p_yes + p_no / 2, sub_y, f"{p_no:.0%}", ha="center",
                        va="center", fontsize=5.4, color="white",
                        fontweight="bold", zorder=4)
            # condition tag to the left of each bar
            ax.text(-0.015, sub_y, f"truth = {cond}", ha="right", va="center",
                    fontsize=5.0, color="#666666")
            # mark the cell that is the CORRECT answer for this condition
            correct_x = (p_yes / 2) if cond == "Yes" else (p_yes + p_no / 2)
            ax.text(correct_x, sub_y + BH / 2 + 0.015, "✓", ha="center",
                    va="bottom", fontsize=4.6, color="#222222", zorder=5)

    # 50 % reference
    ax.axvline(0.5, color="#333333", lw=0.7, ls=":", alpha=0.55, zorder=2)

    ax.set_yticks(range(n))
    ax.set_yticklabels([m["short"] for m in ms], fontsize=7.5, fontweight="bold")
    ax.tick_params(axis="y", length=0, pad=42)   # leave room for the condition tags
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=6)
    ax.set_xlabel("Share of answers", fontsize=7)
    ax.spines["left"].set_visible(False)

    # Legend (answer colour) + reading guide
    handles = [
        plt.matplotlib.patches.Patch(color=YES_COLOR, alpha=0.88,
                                     label='Answered "Yes"'),
        plt.matplotlib.patches.Patch(color=NO_COLOR, alpha=0.88,
                                     label='Answered "No"'),
        plt.Line2D([0], [0], marker="$✓$", ls="none", color="#222222",
                   markersize=5, label="Correct answer"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.005),
              ncol=3, fontsize=6, frameon=False, handlelength=1.3,
              handletextpad=0.4, columnspacing=1.3)

    fig.suptitle("Failure mode I — binary Yes/No answer distribution  (post-cutoff)",
                 fontsize=8.5, fontweight="bold", y=0.965, x=0.5)
    save_fig(fig, out_dir, "fm1_yesno_bias")


# ---------------------------------------------------------------------------
# Failure mode 2 — FRQ alignment / feasibility gap
# ---------------------------------------------------------------------------

# The four FRQ scoring criteria — all on a 0-10 scale (overall FRQ = their mean)
_FRQ_DIMS = [
    ("frq_alignment",   "Alignment",   "#C0392B"),
    ("frq_specificity", "Specificity", "#E67E22"),
    ("frq_novelty",     "Novelty",     "#5B9BD5"),
    ("frq_feasibility", "Feasibility", "#1A9850"),
]


def figure_frq_criteria(models: list[dict], out_dir: Path) -> None:
    """
    Small-multiples violins (post-cutoff): one panel per model showing the full
    distribution of all four FRQ criteria (alignment, specificity, novelty,
    feasibility) on the 0-10 scale.  A bracket marks the alignment->feasibility
    gap (mean-based) within each panel.  The violins reveal that the gap is real
    and continuous — not the artefact of equal integer medians.
    """
    apply_nature_style()
    ms = sorted(_post_models(models, "frq"), key=_composite, reverse=True)  # best first
    if not ms:
        print("  Skipping fm2 — no post-cutoff FRQ data")
        return

    pos    = np.arange(len(_FRQ_DIMS))
    labels = [d[1] for d in _FRQ_DIMS]
    n_m    = len(ms)
    n_cols = 3
    n_rows = int(np.ceil(n_m / n_cols))

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(9.8, 2.5 * n_rows + 0.8),
        sharex=True, sharey=True,
        gridspec_kw={"hspace": 0.40, "wspace": 0.12,
                     "left": 0.06, "right": 0.98, "top": 0.90, "bottom": 0.17},
    )
    axes_flat = np.array(axes).ravel()

    for idx, m in enumerate(ms):
        ax  = axes_flat[idx]
        row = idx // n_cols
        col = idx % n_cols

        means = {}
        for p, (key, lbl, col_t) in zip(pos, _FRQ_DIMS):
            data = np.asarray(m.get(key, []), dtype=float)
            data = data[~np.isnan(data)]
            if len(data) == 0:
                continue
            means[key] = float(np.mean(data))
            vp = ax.violinplot(data, positions=[p], widths=0.78,
                               showmedians=True, showextrema=False)
            for pc in vp["bodies"]:
                pc.set_facecolor(col_t)
                pc.set_edgecolor(col_t)
                pc.set_alpha(0.48)
            vp["cmedians"].set_color("white")
            vp["cmedians"].set_linewidth(1.6)
            vp["cmedians"].set_zorder(5)
            # mean marker (diamond) + label — means separate the models
            ax.scatter(p, means[key], marker="D", s=14, color=col_t,
                       edgecolors="white", linewidths=0.4, zorder=6)
            ax.text(p, 10.4, f"{means[key]:.2f}", ha="center", va="bottom",
                    fontsize=4.8, color=col_t, fontweight="bold")

        ax.axhline(5.0, color="#999999", lw=0.6, ls=":", alpha=0.6, zorder=1)

        # Alignment -> feasibility gap bracket (mean-based)
        if "frq_alignment" in means and "frq_feasibility" in means:
            al, fe = means["frq_alignment"], means["frq_feasibility"]
            xb = 3.62
            ax.plot([xb, xb], [al, fe], color="#888888", lw=0.8, ls="-", zorder=6)
            ax.plot([xb - 0.10, xb], [al, al], color=_FRQ_DIMS[0][2], lw=1.1, zorder=6)
            ax.plot([xb - 0.10, xb], [fe, fe], color=_FRQ_DIMS[3][2], lw=1.1, zorder=6)
            ax.text(xb + 0.06, (al + fe) / 2, f"Δμ={fe - al:+.2f}",
                    ha="left", va="center", fontsize=5.4,
                    color=GAP_COLOR, fontweight="bold")

        ax.set_title(m["short"], fontsize=7.0, fontweight="bold",
                     color="black", pad=4)
        ax.set_xticks(pos)
        if row == n_rows - 1:
            ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=6.0,
                               fontweight="bold")
        else:
            ax.set_xticklabels([])
        if col == 0:
            ax.set_ylabel("FRQ score (0–10)", fontsize=6.5)
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)
            sp.set_color("#cccccc")
        ax.tick_params(length=2, width=0.5, color="#bbbbbb")

    for idx in range(n_m, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    axes_flat[0].set_ylim(0, 11.2)
    axes_flat[0].set_xlim(-0.6, 4.0)

    fig.suptitle("Failure mode II — FRQ criteria distributions per model  "
                 "(post-cutoff; ◆ = mean, white bar = median)",
                 fontsize=8.5, fontweight="bold", y=0.97)
    save_fig(fig, out_dir, "fm2_frq_criteria")


def figure_alignment_feasibility_gap(models: list[dict], out_dir: Path) -> None:
    """
    Dumbbell plot (post-cutoff): per model, MEAN Alignment vs MEAN Feasibility
    (0-10).  Means are used rather than medians because FRQ scores are integers,
    so medians collapse onto a few identical values; means separate the models.
    Sorted by gap magnitude.
    """
    apply_nature_style()
    ms = _post_models(models, "frq")
    if not ms:
        print("  Skipping fm2b — no post-cutoff FRQ data")
        return

    rows = []
    for m in ms:
        al = float(np.mean(m["frq_alignment"]))
        fe = float(np.mean(m["frq_feasibility"]))
        rows.append((m["short"], m["color"], al, fe, al - fe))
    rows.sort(key=lambda r: r[4])   # ascending signed gap

    n = len(rows)
    y = np.arange(n)
    fig, ax = plt.subplots(figsize=(9.5, max(2.8, 0.55 * n + 1.3)),
                           gridspec_kw={"left": 0.12, "right": 0.93,
                                        "top": 0.86, "bottom": 0.16})
    fig.suptitle("Failure mode II — FRQ alignment-feasibility gap  (post-cutoff)",
                 fontsize=8.5, fontweight="bold", y=0.99)

    for i, (name, col, al, fe, gap) in enumerate(rows):
        lo, hi = min(al, fe), max(al, fe)
        ax.plot([lo, hi], [i, i], color="#bbbbbb", lw=2.2, alpha=0.7,
                zorder=2, solid_capstyle="round")
        ax.plot([fe, al], [i, i], color=GAP_COLOR, lw=2.2, alpha=0.18,
                zorder=1, solid_capstyle="round")
        ax.scatter(al, i, s=70, color=_FRQ_DIMS[0][2], zorder=4,
                   edgecolors="white", linewidths=0.6,
                   label="Alignment" if i == 0 else None)
        ax.scatter(fe, i, s=70, color=_FRQ_DIMS[3][2], zorder=4,
                   edgecolors="white", linewidths=0.6,
                   label="Feasibility" if i == 0 else None)
        ax.text(10.25, i, f"Δ={gap:+.2f}", va="center", ha="left",
                fontsize=5.5, color="#555555", fontweight="bold")

    ax.axvline(5.0, color="#888888", lw=0.7, ls=":", alpha=0.6, zorder=0)
    ax.text(5.0, n - 0.45, "pass = 5", ha="center", va="bottom",
            fontsize=4.8, color="#888888")

    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=7)
    ax.set_xlim(0, 10)
    ax.set_xlabel("FRQ sub-dimension score (mean, 0–10)", fontsize=7)
    ax.set_ylim(-0.6, n - 0.4)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="lower right", fontsize=6, handletextpad=0.3,
              borderpad=0.5, framealpha=0.92, edgecolor="#cccccc")

    save_fig(fig, out_dir, "fm2b_alignment_feasibility_gap")


# ---------------------------------------------------------------------------
# Failure mode 3 — Confidence calibration
# ---------------------------------------------------------------------------

def figure_calibration(models: list[dict], out_dir: Path) -> None:
    """
    Reliability small-multiples (post-cutoff): one panel per model, binary
    (blue) and MCQ (red) curves vs the perfect-calibration diagonal.  Curves
    below the diagonal = overconfidence.  ECE annotated per task.
    """
    apply_nature_style()
    MIN_N = 20

    ms = sorted(_post_models(models, "calib"), key=_composite, reverse=True)
    if not ms:
        print("  Skipping fm3 — no post-cutoff calibration data")
        return

    n_m    = len(ms)
    n_cols = 3
    n_rows = int(np.ceil(n_m / n_cols))

    fig = plt.figure(figsize=(9.8, 2.7 * n_rows + 0.6))
    gs  = fig.add_gridspec(n_rows, n_cols, hspace=0.55, wspace=0.16,
                           left=0.06, right=0.98, top=0.90, bottom=0.16)

    ax0 = None
    for idx, m in enumerate(ms):
        r, c = divmod(idx, n_cols)
        kw   = dict(sharex=ax0, sharey=ax0) if ax0 is not None else {}
        ax   = fig.add_subplot(gs[r, c], **kw)
        if ax0 is None:
            ax0 = ax
        is_bottom = (r == n_rows - 1)
        is_left   = (c == 0)

        for g in (0.0, 0.25, 0.50, 0.75, 1.0):
            ax.axhline(g, color="#f0f0f0", lw=0.45, zorder=0)
        ax.plot([0.0, 1.02], [0.0, 1.02], ls="--", color="#bbbbbb",
                lw=0.85, alpha=0.9, zorder=2)

        ece_entries = []
        for key, x_lo, col_t, mk, lbl in (
            ("binary_post_calib", 0.50, BIN_COL, "o", "Binary"),
            ("mcq_post_calib",    0.25, MCQ_COL, "s", "MCQ"),
        ):
            calib = m.get(key, [])
            if not calib:
                continue
            xs, ys, ns, lo_ci, hi_ci = _reliability_curve(
                calib, x_lo, 1.0, n_bins=6, min_n=MIN_N)
            if not xs:
                continue
            ax.fill_between(xs, lo_ci, hi_ci, alpha=0.08, color=col_t,
                            linewidth=0, zorder=1)
            ax.plot(xs, ys, marker=mk, ls="-", color=col_t, lw=1.4, ms=4.2,
                    markeredgecolor="white", markeredgewidth=0.55, zorder=4,
                    solid_capstyle="round", solid_joinstyle="round")
            ece_entries.append((lbl, _ece(calib, x_lo, 1.0), col_t))

        for k, (lbl, ev, ct) in enumerate(ece_entries):
            ax.text(0.05, 0.96 - k * 0.15, f"{lbl}  ECE = {ev:.3f}",
                    transform=ax.transAxes, ha="left", va="top",
                    fontsize=4.6, color=ct, fontweight="semibold")

        ax.set_xlim(0.20, 1.04)
        ax.set_ylim(0.0, 1.04)
        ax.set_xticks([0.25, 0.50, 0.75, 1.00])
        ax.set_yticks([0.0, 0.25, 0.50, 0.75, 1.00])
        ax.set_xticklabels(["0.25", "0.50", "0.75", "1.00"] if is_bottom else [],
                           fontsize=5.2)
        ax.set_yticklabels(["0", "0.25", "0.50", "0.75", "1.00"] if is_left else [],
                           fontsize=5.2)
        if is_bottom:
            ax.set_xlabel("Stated confidence", fontsize=6.0, labelpad=3)
        if is_left:
            ax.set_ylabel("Fraction correct", fontsize=6.0, labelpad=3)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_linewidth(0.5)
            ax.spines[sp].set_color("#999999")
        ax.tick_params(length=2.5, width=0.5, color="#999999")
        ax.set_title(m["short"], fontsize=7.0, fontweight="bold",
                     color="black", pad=5)

    fig.legend(handles=[
        plt.Line2D([0], [0], marker="o", ls="-", color=BIN_COL, lw=1.4, ms=4.5,
                   markeredgecolor="white", markeredgewidth=0.5, label="Binary"),
        plt.Line2D([0], [0], marker="s", ls="-", color=MCQ_COL, lw=1.4, ms=4.5,
                   markeredgecolor="white", markeredgewidth=0.5, label="MCQ"),
        plt.Line2D([0], [0], ls="--", color="#bbbbbb", lw=0.9,
                   label="Perfect calibration"),
    ], loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=3, fontsize=6.5,
       handlelength=1.6, handletextpad=0.5, columnspacing=1.8, frameon=False)

    fig.suptitle("Failure mode III — confidence calibration  (post-cutoff; "
                 "below diagonal = overconfident)",
                 fontsize=8.5, fontweight="bold", y=0.97)
    save_fig(fig, out_dir, "fm3_calibration")


# ---------------------------------------------------------------------------
# Failure mode 4 — Date prediction
# ---------------------------------------------------------------------------

def figure_date_failure(models: list[dict], out_dir: Path) -> None:
    """
    Small-multiples histograms (post-cutoff): one panel per model showing the
    distribution of signed date errors (predicted − actual, months).
    +ve = predicted too late, −ve = too early.  Shared bins/axes; a vertical
    line at 0 marks no-bias, a dashed line marks the mean, and the green band
    is the ±6-month acceptable zone.  Median, mean and the fraction of
    predictions within ±12 months are annotated per panel.
    """
    apply_nature_style()
    ms = _post_models(models, "date")
    if not ms:
        print("  Skipping fm4 — no post-cutoff date data")
        return

    ms = sorted(ms, key=lambda m: float(np.mean(np.clip(m["date_signed_post"], -60, 60))))
    n_m    = len(ms)
    CLIP   = 60          # display window (months)
    BIN_W  = 4           # months per bin
    bins   = np.arange(-CLIP, CLIP + BIN_W, BIN_W)
    n_cols = 3
    n_rows = int(np.ceil(n_m / n_cols))

    # Shared y-max: largest single-bin fraction across all models
    y_top = 0.0
    for m in ms:
        d = np.clip(m["date_signed_post"], -CLIP, CLIP)
        h, _ = np.histogram(d, bins=bins, density=False)
        if len(d):
            y_top = max(y_top, (h / len(d)).max())
    y_top *= 1.18

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(9.8, 2.4 * n_rows + 0.8),
        sharex=True, sharey=True,
        gridspec_kw={"hspace": 0.42, "wspace": 0.12,
                     "left": 0.06, "right": 0.98, "top": 0.90, "bottom": 0.16},
    )
    axes_flat = np.array(axes).ravel()

    for idx, m in enumerate(ms):
        ax  = axes_flat[idx]
        row = idx // n_cols
        col = idx % n_cols

        raw  = np.asarray(m["date_signed_post"], dtype=float)
        data = np.clip(raw, -CLIP, CLIP)
        w    = np.ones_like(data) / len(data)   # normalise to fractions

        ax.axhspan(0, 1, xmin=(- 6 - bins[0]) / (bins[-1] - bins[0]),
                   xmax=(6 - bins[0]) / (bins[-1] - bins[0]),
                   color=GOOD_BAND, alpha=0.08, zorder=0)
        ax.hist(data, bins=bins, weights=w, color=m["color"], alpha=0.85,
                edgecolor="white", linewidth=0.25, zorder=3)
        ax.axvline(0, color="#333333", lw=0.9, zorder=4)

        med  = float(np.median(raw))
        mean = float(np.mean(data))
        w12  = float(np.mean(np.array(m["date_abs_err_post"]) <= 12)) \
            if m.get("date_abs_err_post") else float("nan")
        ax.axvline(mean, color="#222222", lw=0.9, ls="--", alpha=0.8, zorder=5)

        ax.text(0.04, 0.95,
                f"median {med:+.0f} mo\nmean {mean:+.1f} mo\n≤12 mo: {w12:.0%}",
                transform=ax.transAxes, ha="left", va="top", fontsize=4.8,
                color="#222222", linespacing=1.3)

        ax.set_title(m["short"], fontsize=7.0, fontweight="bold",
                     color="black", pad=4)
        if row == n_rows - 1:
            ax.set_xlabel("Signed error (months)\n+ = predicted too late",
                          fontsize=6.0)
        if col == 0:
            ax.set_ylabel("Fraction of predictions", fontsize=6.5)
        ax.set_xlim(-CLIP, CLIP)
        for sp in ax.spines.values():
            sp.set_linewidth(0.5)
            sp.set_color("#cccccc")
        ax.tick_params(length=2, width=0.5, color="#bbbbbb", labelsize=5.2)

    for idx in range(n_m, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    axes_flat[0].set_ylim(0, y_top)

    fig.legend(handles=[
        plt.Line2D([0], [0], color="#333333", lw=0.9, label="No bias (0)"),
        plt.Line2D([0], [0], color="#222222", lw=0.9, ls="--", label="Mean error"),
        plt.matplotlib.patches.Patch(color=GOOD_BAND, alpha=0.25,
                                     label="±6 mo acceptable"),
    ], loc="lower center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=6,
       frameon=False, handlelength=1.6, columnspacing=1.6)

    fig.suptitle("Failure mode IV — date-prediction error distribution per model  "
                 f"(post-cutoff; clipped to ±{CLIP} mo)",
                 fontsize=8.5, fontweight="bold", y=0.97)
    save_fig(fig, out_dir, "fm4_date_failure")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CUSP — Nature-quality failure-mode figures (post-cutoff only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python failure_modes.py \\\n"
            "      --results   frq_results/ \\\n"
            "      --benchmark ../benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl\n"
        ),
    )
    p.add_argument("--results", default="frq_results/",
                   help="Directory containing model result JSON files")
    p.add_argument("--benchmark",
                   default="../benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl",
                   help="Benchmark JSONL — required for post-cutoff partitioning")
    p.add_argument("--output-dir", default="failure_mode_figures",
                   help="Output directory (default: failure_mode_figures/)")
    p.add_argument("--show", action="store_true",
                   help="Open generated PNGs after saving")
    return p


def main() -> None:
    args    = build_parser().parse_args()
    out_dir = Path(args.output_dir)

    if not args.benchmark:
        print("ERROR: --benchmark is required (post-cutoff partitioning needs "
              "publication dates).")
        return

    models = load_all_models(args.results, args.benchmark)
    if not models:
        print("No model results found. Check --results and MODEL_REGISTRY.")
        return

    print(f"\nLoaded {len(models)} models. Generating failure-mode figures "
          f"(post-cutoff only) → {out_dir}/\n")

    figure_yesno_bias(models, out_dir)
    figure_frq_criteria(models, out_dir)
    figure_alignment_feasibility_gap(models, out_dir)
    figure_calibration(models, out_dir)
    figure_date_failure(models, out_dir)

    print("\nDone.")

    if args.show:
        for name in ("fm1_yesno_bias", "fm2_frq_criteria",
                     "fm2b_alignment_feasibility_gap",
                     "fm3_calibration", "fm4_date_failure"):
            p = out_dir / f"{name}.png"
            if p.exists():
                _open_file(p)


if __name__ == "__main__":
    main()
