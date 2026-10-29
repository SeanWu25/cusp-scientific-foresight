#!/usr/bin/env python3
"""
extension_tables.py — outputs for the April-August 2026 extension corpus.

The extension is 100% post-cutoff for every model except DeepSeek-V4-Pro
(cutoff 2026-04, which overlaps April), so these tables print NO pre/post split.

Emits:
  1. full-panel extension table, closed-form tasks, N and 95% CI
  2. extension vs original-corpus POST-CUTOFF comparison, per model per task
  4. date analysis against the constant-guess baseline
  7. cost accounting per model

FRQ quality is reported when --frq report is passed and the reports carry
stage-2 scores; otherwise only generation counts and stage-1 leakage appear.
The rubric is the published one (judge_frq_combined, sha256 fc24e69d...), four
dimensions on 0-10, pass at >= 5.0.

This corpus is NOT prospective: every outcome resolved before the models ran.
It is uncontaminated by training data but it is not the Time Capsule.
"""

from __future__ import annotations

import argparse, json, math, os, statistics, sys
from collections import defaultdict

# tag -> (display name, cutoff, results-dir basename)
PANEL = [
    ("gpt4o_base",          "GPT-4o",          "2023-10"),
    ("llama33_base",        "LLaMA 3.3 70B",   "2023-12"),
    ("gptoss20b_base",      "GPT-OSS 20B",     "2024-06"),
    ("sonnet45_base",       "Claude S4.5",     "2025-01"),
    ("gpt54_base",          "GPT-5.4",         "2025-08"),
    ("sonnet5_base_run1",   "Claude Sonnet 5", "2026-01"),
    ("sol_base",            "GPT-5.6 Sol",     "2026-02"),
    ("deepseekv4pro_base",  "DeepSeek-V4-Pro", "2026-04"),
    ("opus48_base_run1",    "Claude Opus 4.8", "2026-01"),
]
# original-corpus reports, for the post-cutoff comparison
ORIG = {
    "GPT-4o":          "run_evaluation/frq_results/gpt_4o_reeval.json",
    "LLaMA 3.3 70B":   "run_evaluation/frq_results/llama_3_3_full.json",
    "GPT-OSS 20B":     "run_evaluation/frq_results/gpt_oss_20B_reeval.json",
    "Claude S4.5":     "run_evaluation/frq_results/claude_sonnet.json",
    "GPT-5.4":         "run_evaluation/frq_results/gpt_5_4_eval.json",
    "Claude Sonnet 5": "results_sonnet5_run1/reports/base_medium_run1.json",
    "GPT-5.6 Sol":     "results_sol_run1/reports/base_medium_run1.json",
    "Claude Opus 4.8": "results_opus48_run1/reports/base_medium_run1.json",
}


def mo(s):
    try:
        y, m = str(s).split("-")[:2]
        return int(y) * 12 + int(m)
    except Exception:
        return None


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def mci(v, z=1.96):
    n = len(v)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    m = statistics.fmean(v)
    if n < 2:
        return m, float("nan"), float("nan")
    se = statistics.stdev(v) / math.sqrt(n)
    return m, m - z * se, m + z * se


def harvest(path, pub, only_after=None):
    """Pull per-instance outcomes from an eval-schema report."""
    rep = json.load(open(path, encoding="utf-8"))
    acc = defaultdict(list)
    for r in rep.get("results", []):
        if only_after:
            pm = mo(pub.get(r["id"], ""))
            if pm is None or pm <= mo(only_after):
                continue
        t = r.get("tasks", {})
        for k in ("binary", "binary_perturbed"):
            d = t.get(k)
            if d and not d.get("skipped") and "correct" in d:
                acc["merged_binary"].append(1 if d["correct"] else 0)
                acc[k].append(1 if d["correct"] else 0)
        d = t.get("mcq")
        if d and not d.get("skipped") and "correct" in d:
            acc["mcq"].append(1 if d["correct"] else 0)
        d = t.get("date")
        if d and not d.get("skipped"):
            if d.get("score") is not None:
                acc["date_score"].append(float(d["score"]))
            p_, g_ = d.get("parsed_date"), d.get("ground_truth")
            if p_ and g_:
                a_, b_ = mo(p_), mo(g_)
                if a_ and b_:
                    acc["date_signed"].append(a_ - b_)
                    acc["date_abs"].append(abs(a_ - b_))
        d = t.get("frq")
        if d and not d.get("skipped"):
            acc["frq_generated"].append(1)
            if d.get("score") is not None:
                acc["frq_score"].append(float(d["score"]))
                for dim in ("alignment", "specificity", "novelty", "feasibility"):
                    if d.get(dim) is not None:
                        acc[f"frq_{dim}"].append(float(d[dim]))
        lk = (r.get("reasoning") or {}).get("leakage") or {}
        if lk.get("reason") not in (None, "not judged", "No FRQ response to assess"):
            acc["leak_fail"].append(1 if lk.get("verdict") == "fail" else 0)
            acc["leak_unclear"].append(1 if lk.get("verdict") == "unclear" else 0)
    acc["_refusals"] = [rep.get("refusals", {}).get("total", 0)]
    acc["_cost"] = [rep.get("run_metadata", {}).get("cost_usd", float("nan"))]
    return acc


PROP = {"merged_binary", "binary", "binary_perturbed", "mcq"}


def cell(acc, metric):
    v = acc.get(metric, [])
    n = len(v)
    if n == 0:
        return None
    if metric in PROP:
        k = sum(v)
        lo, hi = wilson(k, n)
        return {"n": n, "value": k / n, "lo": lo, "hi": hi}
    m, lo, hi = mci([float(x) for x in v])
    return {"n": n, "value": m, "lo": lo, "hi": hi}


def f(c, dp=3):
    return "        ---       " if not c else f"{c['value']:.{dp}f}[{c['lo']:.2f},{c['hi']:.2f}] n={c['n']}"


def best_constant(targets):
    best = (None, -1.0)
    for g in range(min(targets) - 24, max(targets) + 25):
        s = statistics.fmean(math.exp(-0.1 * abs(g - x)) for x in targets)
        if s > best[1]:
            best = (g, s)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default="results_extension_run2/reports")
    ap.add_argument("--extension",
                    default="benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl")
    ap.add_argument("--original",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--deepseek-drop-april", action="store_true", default=True,
                    help="Report DeepSeek-V4-Pro on May-Aug only, since its 2026-04 "
                         "cutoff makes April in-window for it alone.")
    ap.add_argument("--frq", choices=["report", "diagnostics-only"],
                    default="diagnostics-only",
                    help="report: include stage-2 quality scores and the four "
                         "sub-dimensions, when the reports carry them. "
                         "diagnostics-only (default): generation counts and "
                         "stage-1 leakage only.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    epub, opub, targets = {}, {}, []
    for l in open(a.extension, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            epub[r["id"]] = r.get("publication_date", "")
            if r.get("ground_truth_date"):
                targets.append(mo(r["ground_truth_date"]))
    for l in open(a.original, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            opub[r["id"]] = r.get("publication_date", "")

    print("=" * 100)
    print("EXTENSION CORPUS: April-August 2026, 815 events")
    print("100% POST-CUTOFF for every model except DeepSeek-V4-Pro (cutoff 2026-04).")
    print("NOT PROSPECTIVE: all outcomes resolved before the models were run. The corpus")
    print("is uncontaminated by training data, but it is not the Time Capsule.")
    if a.frq == "report":
        print("FRQ quality REPORTED (published rubric, 4 dims, pass >= 5.0).")
        print("  Judge noise floor: re-grading the same response gives MAD 0.392,")
        print("  so differences below ~0.4 between models are not meaningful.")
        print("  Claude FRQ responses are truncated at their token caps (S4.5 99.6%,")
        print("  Sonnet 5 97.4%) while the rest of the panel answered to completion.")
        print("  Whether that depresses their scores is not established -- Sonnet 5")
        print("  scores specificity 5.40 on the original corpus despite 96% truncation.")
    else:
        print("FRQ quality scores are omitted (pass --frq report to include them).")
    print("=" * 100)

    data, out = {}, {"models": {}}
    print("\n=== 1. FULL PANEL ON THE EXTENSION (all post-cutoff) ===")
    print(f"{'model':17s}{'cutoff':>8s}{'merged binary':>26s}{'MCQ':>26s}{'date score':>26s}")
    for tag, name, cut in PANEL:
        p = os.path.join(a.reports, f"{tag}.json")
        if not os.path.exists(p):
            print(f"{name:17s}{cut:>8s}{'   (not yet run)':>26s}")
            continue
        drop = a.deepseek_drop_april and name == "DeepSeek-V4-Pro"
        acc = harvest(p, epub, only_after="2026-04" if drop else None)
        data[name] = (acc, cut)
        cells = {m: cell(acc, m) for m in ("merged_binary", "mcq", "date_score")}
        out["models"][name] = {"cutoff": cut, "april_dropped": drop,
                               **{k: v for k, v in cells.items()}}
        note = "  [May-Aug only]" if drop else ""
        print(f"{name:17s}{cut:>8s}{f(cells['merged_binary']):>26s}"
              f"{f(cells['mcq']):>26s}{f(cells['date_score']):>26s}{note}")

    print("\n=== 2. EXTENSION vs ORIGINAL POST-CUTOFF (same model, same task) ===")
    print("  MCQ is differenced (templates and generator verified identical).")
    print("  Binary is shown side by side. Date is NOT differenced -- see block 4.")
    print(f"\n{'model':17s}{'task':16s}{'original post':>24s}{'extension':>24s}{'delta':>18s}")
    for tag, name, cut in PANEL:
        if name not in data or name not in ORIG or not os.path.exists(ORIG[name]):
            continue
        eacc, _ = data[name]
        oacc = harvest(ORIG[name], opub, only_after=None)
        # original post-cutoff only
        orep = json.load(open(ORIG[name], encoding="utf-8"))
        opost = defaultdict(list)
        for r in orep.get("results", []):
            pm = mo(opub.get(r["id"], ""))
            if pm is None or pm < mo(cut):
                continue
            t = r.get("tasks", {})
            for k in ("binary", "binary_perturbed"):
                d = t.get(k)
                if d and not d.get("skipped") and "correct" in d:
                    opost["merged_binary"].append(1 if d["correct"] else 0)
            d = t.get("mcq")
            if d and not d.get("skipped") and "correct" in d:
                opost["mcq"].append(1 if d["correct"] else 0)
            d = t.get("date")
            if d and not d.get("skipped") and d.get("score") is not None:
                opost["date_score"].append(float(d["score"]))
        for met, diffable in (("merged_binary", False), ("mcq", True), ("date_score", False)):
            co, ce = cell(opost, met), cell(eacc, met)
            if not co or not ce:
                continue
            if diffable:
                d = ce["value"] - co["value"]
                se = math.sqrt(((co["hi"]-co["lo"])/3.92)**2 + ((ce["hi"]-ce["lo"])/3.92)**2)
                ds = f"{d:+.3f}+/-{1.96*se:.3f}"
            else:
                ds = "not differenced"
            print(f"{name:17s}{met:16s}{f(co):>24s}{f(ce):>24s}{ds:>18s}")

    print("\n=== 4. DATE TASK vs THE CONSTANT-GUESS BASELINE ===")
    g, s = best_constant(targets)
    ym = f"{(g-1)//12:04d}-{((g-1)%12)+1:02d}"
    print(f"  Extension targets span 5 months. Best constant guess = {ym}, score {s:.3f}.")
    print(f"  ANY model scoring at or below {s:.3f} has shown no date-forecasting skill here.")
    print(f"\n{'model':17s}{'date score':>14s}{'vs baseline':>14s}{'mean signed err':>18s}{'n':>7s}")
    for tag, name, cut in PANEL:
        if name not in data:
            continue
        acc, _ = data[name]
        c = cell(acc, "date_score")
        sg = acc.get("date_signed", [])
        if not c:
            continue
        print(f"{name:17s}{c['value']:14.3f}{c['value']-s:+14.3f}"
              f"{(statistics.fmean(sg) if sg else float('nan')):+18.1f}{c['n']:7d}")

    hdr = "generation + stage-1 leakage" if a.frq != "report" \
        else "quality, generation and stage-1 leakage"
    print(f"\n=== FRQ ({hdr}) ===")
    if a.frq == "report":
        print(f"{'model':17s}{'responses':>11s}{'score':>8s}{'pass%':>8s}"
              f"{'align':>8s}{'spec':>8s}{'novel':>8s}{'feas':>8s}{'n':>7s}")
        for tag, name, cut in PANEL:
            if name not in data:
                continue
            acc, _ = data[name]
            sc = acc.get("frq_score", [])
            if not sc:
                print(f"{name:17s}{len(acc.get('frq_generated',[])):11d}"
                      f"{'(not graded)':>55s}")
                continue
            dims = [sum(acc.get(d, [0])) / max(len(acc.get(d, [])), 1)
                    for d in ("frq_alignment", "frq_specificity",
                              "frq_novelty", "frq_feasibility")]
            print(f"{name:17s}{len(acc.get('frq_generated',[])):11d}"
                  f"{sum(sc)/len(sc):8.2f}"
                  f"{100*sum(1 for x in sc if x >= 5.0)/len(sc):8.1f}"
                  + "".join(f"{d:8.2f}" for d in dims) + f"{len(sc):7d}")
        print("  differences below ~0.4 are within the judge noise floor")
    print(f"\n{'model':17s}{'responses':>11s}{'leak fail%':>12s}"
          f"{'leak unclear%':>15s}{'n judged':>10s}")
    for tag, name, cut in PANEL:
        if name not in data:
            continue
        acc, _ = data[name]
        lf, lu = acc.get("leak_fail", []), acc.get("leak_unclear", [])
        print(f"{name:17s}{len(acc.get('frq_generated',[])):11d}"
              f"{(100*sum(lf)/len(lf) if lf else float('nan')):12.2f}"
              f"{(100*sum(lu)/len(lu) if lu else float('nan')):15.1f}{len(lf):10d}")

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2, default=str)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
