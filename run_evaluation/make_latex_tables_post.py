"""
make_latex_tables_post.py — POST-CUTOFF-ONLY LaTeX tables for the CUSP benchmark.

This is a thin companion to ``make_latex_tables.py``. It produces the *exact same*
tables (same format, colours, columns, captions, compilable document) EXCEPT that
every metric is computed over **post-cutoff instances only** — i.e. only benchmark
papers published on/after each model's training cutoff (the "truly unseen" papers).

It does this by reusing all of the original table-builder and formatting functions
verbatim and simply handing them model dicts whose accumulators were filled from the
post-cutoff partition alone.

Tables produced (post-cutoff only)
----------------------------------
  post_table1_main_results.tex     Overall performance summary
  post_table2_binary_bias.tex      Binary response-bias analysis
  post_table2b_binary_extended.tex Binary extended metrics (precision/recall/F1/MCC)
  post_table3_date_stats.tex       Date prediction in-depth statistics
  post_table4_area_mcq.tex         MCQ accuracy by research area (heatmap)
  post_table5_area_date.tex        Date score by research area (heatmap)
  post_table5b_area_binary.tex     Binary merged accuracy by research area
  post_table7_calibration.tex      Confidence calibration (ECE, overconfidence)
  post_table_frq2_subdims.tex      FRQ sub-dimension profile
  post_table_frq3_by_area.tex      FRQ score by research area
  post_tables_all.tex              Standalone compilable document

The inherently *comparative* pre-vs-post tables from the original
(``table_pre_post_cutoff``, ``table_binary_pre_post_extended``, ``table_area_pre_post``,
``table_frq_pre_post``) are intentionally omitted: with the data restricted to
post-cutoff only there is nothing to compare against, so a "pre" column would be empty.

Because every row must be classified relative to a model's cutoff, ``--benchmark``
(which supplies per-instance publication dates) is REQUIRED here.

Usage
-----
  python make_latex_tables_post.py \\
      --results   model_results/ \\
      --benchmark benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \\
      [--output-dir tables_post/]

Requirements: numpy
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# Import the original module so we can reuse its table-builders and helpers.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_latex_tables as base   # noqa: E402


# ---------------------------------------------------------------------------
# Post-cutoff-only data loading
# ---------------------------------------------------------------------------

def load_model_post(filepath: str, cfg: dict, id_meta: dict) -> dict:
    """Like ``base.load_model`` but every accumulator/summary is restricted to
    post-cutoff instances (publication_date >= model cutoff).

    All headline numbers that the original pulls from ``task_metrics`` (which are
    computed over the *full* set) are instead recomputed here from the per-row
    ``results``, filtered to the post-cutoff partition, so the tables stay faithful.
    """
    with open(filepath, encoding="utf-8") as f:
        rep = json.load(f)

    nan = float("nan")
    cutoff_m = base._dm(cfg["cutoff"])

    # Binary / perturbed counts (post-cutoff)
    bin_n = bin_c = bp_n = bp_c = 0
    bin_conf_list: list[float] = []

    # MCQ
    mcq_n = mcq_c = 0
    mcq_conf_list: list[float] = []

    # Date
    date_scores:  list[float] = []
    date_conf_list: list[float] = []
    date_signed:  list[float] = []
    date_abs:     list[float] = []
    date_pred_m:  list[float] = []
    date_gt_m:    list[float] = []

    # FRQ
    frq_scores: list[float] = []

    # Per-area accumulators (post-cutoff)
    area_mcq:    dict[str, list] = defaultdict(list)
    area_binary: dict[str, list] = defaultdict(list)
    area_date:   dict[str, list] = defaultdict(list)
    area_frq:         dict[str, list] = defaultdict(list)
    area_frq_align:   dict[str, list] = defaultdict(list)
    area_frq_spec:    dict[str, list] = defaultdict(list)
    area_frq_novelty: dict[str, list] = defaultdict(list)
    area_frq_feas:    dict[str, list] = defaultdict(list)

    # Binary confusion matrix (binary GT=Yes, binary_perturbed GT=No)
    bin_tp = bin_fp = bin_tn = bin_fn = 0

    # Calibration pairs
    calib_binary: list[tuple[float, float]] = []
    calib_mcq:    list[tuple[float, float]] = []
    calib_date:   list[tuple[float, float]] = []

    for row in rep.get("results", []):
        rid   = row.get("id", "")
        meta  = id_meta.get(rid, {})
        area  = meta.get("main_area", "Unknown")
        pub_m = base._dm(meta.get("pub", ""))

        # Keep ONLY post-cutoff instances. Rows we cannot classify (missing pub
        # date or model cutoff) are skipped — they cannot be assigned to "post".
        if pub_m is None or cutoff_m is None or pub_m < cutoff_m:
            continue

        tasks = row.get("tasks", {})

        # Binary (original + perturbed)
        for key in ("binary", "binary_perturbed"):
            t = tasks.get(key)
            if t and not t.get("skipped"):
                correct = bool(t.get("correct"))
                v = int(correct)
                area_binary[area].append(v)
                conf = t.get("confidence")
                if key == "binary":
                    bin_n += 1
                    bin_c += v
                    if conf is not None:
                        bin_conf_list.append(float(conf))
                    if correct: bin_tp += 1
                    else:       bin_fn += 1
                else:
                    bp_n += 1
                    bp_c += v
                    if correct: bin_tn += 1
                    else:       bin_fp += 1
                if conf is not None:
                    calib_binary.append((float(conf), float(v)))

        # MCQ
        t = tasks.get("mcq")
        if t and not t.get("skipped"):
            v = int(bool(t.get("correct")))
            area_mcq[area].append(v)
            mcq_n += 1
            mcq_c += v
            conf = t.get("confidence")
            if conf is not None:
                mcq_conf_list.append(float(conf))
                calib_mcq.append((float(conf), float(v)))

        # Date
        t = tasks.get("date")
        if t and not t.get("skipped"):
            score = t.get("score")
            if score is not None:
                s = float(score)
                area_date[area].append(s)
                date_scores.append(s)
                conf = t.get("confidence")
                if conf is not None:
                    date_conf_list.append(float(conf))
                    calib_date.append((float(conf), s))
            pm = base._dm(t.get("parsed_date"))
            gm = base._dm(t.get("ground_truth"))
            if pm is not None and gm is not None:
                signed = float(pm - gm)
                date_signed.append(signed)
                date_abs.append(abs(signed))
                date_pred_m.append(float(pm))
                date_gt_m.append(float(gm))

        # FRQ
        t = tasks.get("frq")
        if t and not t.get("skipped") and t.get("score") is not None:
            s = float(t["score"])
            area_frq[area].append(s)
            frq_scores.append(s)
            if t.get("alignment") is not None:
                area_frq_align[area].append(float(t["alignment"]))
            if t.get("specificity") is not None:
                area_frq_spec[area].append(float(t["specificity"]))
            if t.get("novelty") is not None:
                area_frq_novelty[area].append(float(t["novelty"]))
            if t.get("feasibility") is not None:
                area_frq_feas[area].append(float(t["feasibility"]))

    merged_n = bin_n + bp_n
    abs_arr  = np.array(date_abs) if date_abs else np.array([])
    frq_arr  = np.array(frq_scores) if frq_scores else np.array([])

    return {
        "name":   cfg["name"],
        "short":  cfg["short"],
        "cutoff": cfg["cutoff"],
        "cutoff_months": cutoff_m,
        # Headline summary (recomputed, post-cutoff only)
        "binary_acc":           bin_c / bin_n if bin_n else nan,
        "binary_conf":          base._sm(bin_conf_list),
        "binary_perturbed_acc": bp_c / bp_n if bp_n else nan,
        "merged_binary_acc":    (bin_c + bp_c) / merged_n if merged_n else nan,
        "binary_n":             bin_n,
        "mcq_acc":              mcq_c / mcq_n if mcq_n else nan,
        "mcq_conf":             base._sm(mcq_conf_list),
        "mcq_n":                mcq_n,
        "date_score":           base._sm(date_scores),
        "date_n":               len(date_scores),
        "date_exact_rate":      float(np.mean(abs_arr == 0)) if abs_arr.size else nan,
        "date_median_dist":     float(np.median(abs_arr))    if abs_arr.size else nan,
        "date_conf":            base._sm(date_conf_list),
        # Per-row date
        "date_signed":  date_signed,
        "date_abs":     date_abs,
        "date_pred_m":  date_pred_m,
        "date_gt_m":    date_gt_m,
        # Per-area (post-cutoff)
        "area_mcq":    dict(area_mcq),
        "area_binary": dict(area_binary),
        "area_date":   dict(area_date),
        # FRQ summary (post-cutoff)
        "frq_mean":      base._sm(frq_scores),
        "frq_n":         len(frq_scores),
        "frq_pass_rate": float(np.mean(frq_arr >= 5)) if frq_arr.size else nan,
        "frq_align_mean":   base._sm([v for lst in area_frq_align.values()   for v in lst]),
        "frq_spec_mean":    base._sm([v for lst in area_frq_spec.values()    for v in lst]),
        "frq_novelty_mean": base._sm([v for lst in area_frq_novelty.values() for v in lst]),
        "frq_feas_mean":    base._sm([v for lst in area_frq_feas.values()    for v in lst]),
        "area_frq":          dict(area_frq),
        "area_frq_align":    dict(area_frq_align),
        "area_frq_spec":     dict(area_frq_spec),
        "area_frq_novelty":  dict(area_frq_novelty),
        "area_frq_feas":     dict(area_frq_feas),
        # Reasoning metrics (leakage flags are an inherently post-cutoff signal;
        # kept as-is from the report).
        "leakage_fail_rate": rep.get("reasoning_metrics", {}).get("leakage", {}).get("fail_rate", nan),
        "leakage_pass_rate": rep.get("reasoning_metrics", {}).get("leakage", {}).get("pass_rate", nan),
        # Calibration pairs (post-cutoff)
        "calib_binary": calib_binary,
        "calib_mcq":    calib_mcq,
        "calib_date":   calib_date,
        # Binary confusion matrix (post-cutoff)
        "bin_tp": bin_tp, "bin_fp": bin_fp, "bin_tn": bin_tn, "bin_fn": bin_fn,
    }


def load_all_models_post(results_dir: str, benchmark_path: str) -> list[dict]:
    print(f"  Loading benchmark: {benchmark_path}")
    id_meta = base.load_benchmark_meta(benchmark_path)
    print(f"  {len(id_meta)} rows indexed")

    models: list[dict] = []
    for fn, cfg in base.MODEL_REGISTRY.items():
        fp = Path(results_dir) / fn
        if not fp.exists():
            print(f"  SKIP {fn}")
            continue
        print(f"  Loading {cfg['name']} (post-cutoff only) ...")
        models.append(load_model_post(str(fp), cfg, id_meta))

    models.sort(key=base._composite, reverse=True)   # best first
    return models


# ---------------------------------------------------------------------------
# FRQ sub-dimension table WITH feasibility
# ---------------------------------------------------------------------------

def table_frq_subdims_post(models: list[dict]) -> str:
    """Like ``base.table_frq_subdims`` but includes the fourth rubric
    sub-dimension, Feasibility, which the original tables omit."""
    sorted_m = sorted(models, key=lambda m: m["frq_align_mean"])

    data_rows = []
    for m in sorted_m:
        al = m["frq_align_mean"]
        sp = m["frq_spec_mean"]
        nv = m["frq_novelty_mean"]
        fe = m["frq_feas_mean"]
        gap = sp - al  # specificity−alignment gap: positive = detailed but misaligned
        data_rows.append(base._join_row([
            base._esc(m["short"]), base._cutoff_fmt(m["cutoff"]),
            base._cell_frq_align(al) + base._fmt(al, dp=2),
            base._cell_frq_align(sp) + base._fmt(sp, dp=2),
            base._cell_frq_align(nv) + base._fmt(nv, dp=2),
            base._cell_frq_align(fe) + base._fmt(fe, dp=2),
            base._fmt(gap, dp=2, signed=True),
            base._fmt(m["frq_mean"], dp=2),
        ]))

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{FRQ sub-dimension profile. "
        r"\textbf{Alignment}: match with the actual paper method. "
        r"\textbf{Specificity}: technical concreteness. "
        r"\textbf{Novelty}: non-obvious insight. "
        r"\textbf{Feasibility}: practical plausibility of the proposed approach. "
        r"\textbf{Spec.\,$-$\,Align.\ gap}: positive values indicate models that "
        r"write technically detailed responses but miss the specific paper approach "
        r"--- a signature of plausible-sounding hallucination. "
        r"Models sorted from lowest to highest alignment.}",
        r"\label{tab:frq_subdims}",
        base._adjustbox_open(),
        r"\small\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{@{}ll rrrrrr r@{}}",
        r"\toprule",
        base._join_row([r"\textbf{Model}", r"\textbf{Cutoff}",
                        r"\textbf{Align.\,$\uparrow$}",
                        r"\textbf{Spec.\,$\uparrow$}",
                        r"\textbf{Nov.\,$\uparrow$}",
                        r"\textbf{Feas.\,$\uparrow$}",
                        r"\textbf{Spec.\,$-$\,Align.\ gap}",
                        r"\textbf{Overall score}"]),
        r"\midrule",
        *data_rows,
        r"\bottomrule",
        r"\end{tabular}",
        base._adjustbox_close(),
        base._minipage_note(
            r"All sub-dimensions scored 0--10 by the LLM rubric judge. "
            r"Colour shading on Alignment, Specificity, Novelty, and Feasibility uses the same "
            r"scale: red $<$ 2, orange 2--3, yellow 3--4, light green 4--5, "
            r"medium green 5--6.5, dark green $\geq$ 6.5."
        ),
        r"\end{table}",
    ])


# ---------------------------------------------------------------------------
# Relabel the reused tables as post-cutoff-only
# ---------------------------------------------------------------------------

def _postify(tex: str) -> str:
    """Annotate a reused table's caption so it is unambiguously post-cutoff only."""
    # The main-results caption hardcodes the full benchmark size; that count does
    # not apply when restricted to post-cutoff (and differs per model anyway).
    tex = tex.replace(r"($n=4{,}760$ instances)", "(post-cutoff instances only)")
    # Prepend a clear marker to the (single) caption of the table.
    tex = tex.replace(r"\caption{", r"\caption{\textbf{[Post-cutoff instances only]}~", 1)
    return tex


# ---------------------------------------------------------------------------
# Compilation document (post-cutoff variant of the original preamble)
# ---------------------------------------------------------------------------

PREAMBLE_POST = (
    base.PREAMBLE
    .replace(r"CUSP Benchmark --- Supplementary Tables",
             r"CUSP Benchmark --- Supplementary Tables (Post-Cutoff Only)")
    .replace(r"\large Multi-model evaluation: binary, MCQ, and date prediction",
             r"\large \textbf{Post-cutoff instances only}: binary, MCQ, and date prediction")
)


def write_compilation_post(tables: dict[str, str], out_dir: Path) -> None:
    with open(out_dir / "post_tables_all.tex", "w", encoding="utf-8") as f:
        f.write(PREAMBLE_POST)
        for title, tex in tables.items():
            f.write(f"\n\\section{{{title}}}\n\n{tex}\n\n\\clearpage\n")
        f.write(base.POSTAMBLE)
    print("  Saved post_tables_all.tex")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate POST-CUTOFF-ONLY LaTeX tables for CUSP benchmark results")
    p.add_argument("--results",    default="model_results/")
    p.add_argument("--benchmark",  default=None,
                   help="Benchmark JSONL — REQUIRED (supplies per-instance publication "
                        "dates needed to identify post-cutoff instances)")
    p.add_argument("--output-dir", default=None)
    return p


def main() -> None:
    args = build_parser().parse_args()

    if not args.benchmark:
        print("ERROR: --benchmark is required for post-cutoff-only tables "
              "(needed to classify each instance relative to a model's cutoff).")
        sys.exit(1)

    out_dir = (Path(args.output_dir) if args.output_dir
               else Path(args.results) / "tables_post")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading model results (post-cutoff only)...")
    models = load_all_models_post(args.results, args.benchmark)
    if not models:
        print("No models found. Check --results and MODEL_REGISTRY.")
        return

    print(f"\nLoaded {len(models)} models (post-cutoff partition):")
    for m in models:
        print(f"  {m['short']:15s}  n_binary(post)={m['binary_n']:5d}  "
              f"merged-binary={m['merged_binary_acc']:.3f}  "
              f"mcq={m['mcq_acc']:.3f}  date={m['date_score']:.3f}")

    print(f"\nGenerating post-cutoff tables → {out_dir}/\n")

    # Same tables as the original, MINUS the inherently pre-vs-post comparison
    # tables (which have no "pre" partition once we restrict to post-cutoff).
    TABLE_DEFS: list[tuple[str, str, str]] = [
        ("post_table1_main_results.tex",     "Overall Performance Summary (Post-Cutoff)",        base.table_main_results(models)),
        ("post_table2_binary_bias.tex",      "Binary Response-Bias Analysis (Post-Cutoff)",      base.table_binary_bias(models)),
        ("post_table2b_binary_extended.tex", "Binary Extended Metrics (Post-Cutoff)",            base.table_binary_extended(models)),
        ("post_table3_date_stats.tex",       "Date Prediction Statistics (Post-Cutoff)",         base.table_date_stats(models)),
        ("post_table7_calibration.tex",      "Confidence Calibration (Post-Cutoff)",             base.table_calibration(models)),
        ("post_table4_area_mcq.tex",         "MCQ Accuracy by Research Area (Post-Cutoff)",       base.table_area_mcq(models)),
        ("post_table5_area_date.tex",        "Date Score by Research Area (Post-Cutoff)",         base.table_area_date(models)),
        ("post_table5b_area_binary.tex",     "Binary Merged Accuracy by Research Area (Post-Cutoff)", base.table_area_binary(models)),
        ("post_table_frq2_subdims.tex",      "FRQ Sub-dimension Profile (Post-Cutoff)",           table_frq_subdims_post(models)),
        ("post_table_frq3_by_area.tex",      "FRQ Score by Research Area (Post-Cutoff)",          base.table_frq_by_area(models)),
    ]

    tables_doc: dict[str, str] = {}
    for fname, title, tex in TABLE_DEFS:
        tex = _postify(tex)
        path = out_dir / fname
        path.write_text(tex + "\n", encoding="utf-8")
        print(f"  Saved {fname}")
        tables_doc[title] = tex

    write_compilation_post(tables_doc, out_dir)

    print(f"\nDone. Compile the preview with:")
    print(f"  cd {out_dir}")
    print(f"  pdflatex post_tables_all.tex && pdflatex post_tables_all.tex")


if __name__ == "__main__":
    main()
