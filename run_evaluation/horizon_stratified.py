#!/usr/bin/env python3
"""
horizon_stratified.py — forecast-horizon-stratified performance for ALL models.

Bins every benchmark instance by the signed number of months between a model's
knowledge cutoff and the event's first publicly observable date, then reports
score and CI per bin, plus signed error per bin for the date task.

Horizon h = months(publication_date) - months(cutoff).
  h <  0 : event was inside the training window (retrospective)
  h >= 0 : event is post-cutoff (prospective)

"First publicly observable date" is `publication_date` in the CUSP schema; the
benchmark carries no separate preprint/observable field, so the two coincide.
This is stated explicitly rather than silently assumed.

Binomial proportions use Wilson intervals; means use a normal-approximation CI.
Cells below --min-n are suppressed rather than printed as point estimates.

Usage:
  python run_evaluation/horizon_stratified.py \
      --results run_evaluation/frq_results \
      --benchmark archive/data/canonical/merged_validated_cusp_fixed.jsonl \
      --extra "Claude Sonnet 5=2026-01=results_sonnet5_run1/eval/run1.json" \
      --out results_sonnet5_run1/tables/horizon_stratified.json
"""

from __future__ import annotations

import argparse, json, math, os, statistics, sys
from collections import defaultdict

# The six published models: filename -> (display name, cutoff YYYY-MM).
# Values mirror MODEL_REGISTRY in make_latex_tables.py / compare_models.py.
PUBLISHED = {
    "gpt_5_4_eval.json":       ("GPT-5.4",      "2025-08"),
    "claude_sonnet.json":      ("Claude S4.5",  "2025-01"),
    "deepseek_r1.json":        ("DeepSeek R1",  "2024-07"),
    "gpt_oss_20B_reeval.json": ("GPT-OSS 20B",  "2024-06"),
    "llama_3_3_full.json":     ("LLaMA 3.3",    "2023-12"),
    "gpt_4o_reeval.json":      ("GPT-4o",       "2023-10"),
}

DEFAULT_BINS = [(-999, -25), (-24, -13), (-12, -7), (-6, -1),
                (0, 2), (3, 5), (6, 11), (12, 23), (24, 999)]


def months(ym: str) -> int | None:
    try:
        y, m = str(ym).split("-")[:2]
        return int(y) * 12 + int(m)
    except Exception:
        return None


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - hw), min(1.0, c + hw)


def mean_ci(vals: list[float], z: float = 1.96) -> tuple[float, float, float]:
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    m = statistics.fmean(vals)
    if n < 2:
        return m, float("nan"), float("nan")
    se = statistics.stdev(vals) / math.sqrt(n)
    return m, m - z * se, m + z * se


def bin_label(lo: int, hi: int) -> str:
    if lo <= -999:
        return f"<= {hi}"
    if hi >= 999:
        return f">= {lo}"
    return f"{lo}..{hi}"


def collect(report_path: str, cutoff: str, pub: dict, bins) -> dict:
    """Bin one model's stored per-row results by forecast horizon."""
    with open(report_path, encoding="utf-8") as f:
        rep = json.load(f)
    cm = months(cutoff)
    acc: dict = defaultdict(lambda: defaultdict(list))
    for r in rep.get("results", []):
        pm = months(pub.get(r["id"], ""))
        if pm is None or cm is None:
            continue
        h = pm - cm
        b = next((bin_label(lo, hi) for lo, hi in bins if lo <= h <= hi), None)
        if b is None:
            continue
        t = r.get("tasks", {})
        for key in ("binary", "binary_perturbed", "mcq"):
            d = t.get(key)
            if d and not d.get("skipped") and "correct" in d:
                hit = 1 if d["correct"] else 0
                acc[key][b].append(hit)
                if key in ("binary", "binary_perturbed"):
                    # merged binary = pooled correct counts across both variants,
                    # matching make_latex_tables.py
                    acc["merged_binary"][b].append(hit)
        d = t.get("frq")
        if d and not d.get("skipped") and d.get("score") is not None:
            acc["frq"][b].append(float(d["score"]))
        d = t.get("date")
        if d and not d.get("skipped"):
            if d.get("score") is not None:
                acc["date_score"][b].append(float(d["score"]))
            pd_, gt = d.get("parsed_date"), d.get("ground_truth")
            if pd_ and gt:
                pm2, gm = months(pd_), months(gt)
                if pm2 is not None and gm is not None:
                    acc["date_signed_error"][b].append(pm2 - gm)
                    acc["date_abs_error"][b].append(abs(pm2 - gm))
    return acc


def summarise(acc: dict, bins, min_n: int) -> dict:
    prop = {"binary", "binary_perturbed", "mcq", "merged_binary"}
    out: dict = {}
    for metric, per_bin in acc.items():
        out[metric] = {}
        for lo, hi in bins:
            b = bin_label(lo, hi)
            vals = per_bin.get(b, [])
            n = len(vals)
            cell = {"n": n, "horizon_lo": lo, "horizon_hi": hi}
            if n < min_n:
                cell["suppressed"] = True
                cell["reason"] = f"n < {min_n}"
            elif metric in prop:
                k = sum(vals)
                lo_ci, hi_ci = wilson(k, n)
                cell.update(correct=k, value=k / n, ci_low=lo_ci, ci_high=hi_ci,
                            ci_method="wilson")
            else:
                m, l, h = mean_ci([float(v) for v in vals])
                cell.update(value=m, ci_low=l, ci_high=h, ci_method="normal-approx")
            out[metric][b] = cell
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="run_evaluation/frq_results")
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--extra", action="append", default=[],
                    help="Additional model as 'Name=YYYY-MM=path/to/report.json'")
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    pub = {}
    for l in open(a.benchmark, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            pub[r["id"]] = r.get("publication_date", "")

    models = []
    for fn, (name, cut) in PUBLISHED.items():
        p = os.path.join(a.results, fn)
        if os.path.exists(p):
            models.append((name, cut, p))
        else:
            print(f"  SKIP {fn} (not found)", file=sys.stderr)
    for spec in a.extra:
        name, cut, path = spec.split("=", 2)
        if os.path.exists(path):
            models.append((name, cut, path))
        else:
            print(f"  SKIP extra {name} ({path} not found)", file=sys.stderr)

    bins = DEFAULT_BINS
    report = {"bins": [bin_label(lo, hi) for lo, hi in bins],
              "min_n": a.min_n,
              "horizon_definition":
                  "months(publication_date) - months(model cutoff); "
                  "negative = inside training window",
              "observable_date_field": "publication_date",
              "models": {}}

    for name, cut, path in models:
        acc = collect(path, cut, pub, bins)
        report["models"][name] = {"cutoff": cut, "source": path,
                                  "metrics": summarise(acc, bins, a.min_n)}

    for metric in ("merged_binary", "mcq", "frq", "date_score", "date_signed_error"):
        print(f"\n=== {metric} by forecast horizon (months after cutoff) ===")
        hdr = f"{'model':14s}{'cutoff':>9s}  " + "".join(
            f"{bin_label(lo,hi):>14s}" for lo, hi in bins)
        print(hdr)
        for name, cut, _ in models:
            cells = report["models"][name]["metrics"].get(metric, {})
            row = f"{name:14s}{cut:>9s}  "
            for lo, hi in bins:
                c = cells.get(bin_label(lo, hi), {})
                if not c or c.get("suppressed") or c.get("n", 0) == 0:
                    row += f"{('n=' + str(c.get('n', 0))):>14s}"
                else:
                    row += f"{c['value']:>9.3f}({c['n']:>3d})"
            print(row)

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
