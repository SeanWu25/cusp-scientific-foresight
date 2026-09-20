#!/usr/bin/env python3
"""
full_corpus_tables.py — panel results over the ENTIRE CUSP corpus.

Pools the original corpus (Jan 2024 - Mar 2026, 4,760 events) with the
April-August 2026 extension (815 events) for a 5,575-event view per model.

The two halves are pooled at the *report* level, not re-scored: each half was
graded by the frozen scoring_v1 graders, and the per-event task records carry
identical keys for every closed-form task. Event IDs are disjoint by
construction (checked here, not assumed).

Neither half is prospective. The extension is uncontaminated by training data
because it postdates every cutoff, but its outcomes had all resolved before the
models ran.

FRQ quality scores are omitted: the stage-2 rubric is under revision, and the
extension half has no rubric scores at all, so pooling them would be
incoherent even if the rubric were settled.
"""

from __future__ import annotations

import argparse, json, math, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from binary_extended import _binary_metrics  # noqa: E402

# display name -> (cutoff, original-corpus report, extension report)
PANEL = [
    ("GPT-4o",          "2023-10", "run_evaluation/frq_results/gpt_4o_reeval.json",
                                   "results_extension_run2/reports/gpt4o_base.json"),
    ("LLaMA 3.3 70B",   "2023-12", "run_evaluation/frq_results/llama_3_3_full.json",
                                   "results_extension_run2/reports/llama33_base.json"),
    ("GPT-OSS 20B",     "2024-06", "run_evaluation/frq_results/gpt_oss_20B_reeval.json",
                                   "results_extension_run2/reports/gptoss20b_base.json"),
    ("DeepSeek-R1",     "2024-07", "run_evaluation/frq_results/deepseek_r1.json", None),
    ("Claude S4.5",     "2025-01", "run_evaluation/frq_results/claude_sonnet.json",
                                   "results_extension_run2/reports/sonnet45_base.json"),
    ("GPT-5.4",         "2025-08", "run_evaluation/frq_results/gpt_5_4_eval.json",
                                   "results_extension_run2/reports/gpt54_base.json"),
    ("Claude Sonnet 5", "2026-01", "results_sonnet5_run1/reports/base_medium_run1.json",
                                   "results_extension_run2/reports/sonnet5_base_run1.json"),
    ("GPT-5.6 Sol",     "2026-02", "results_sol_run1/reports/base_medium_run1.json",
                                   "results_extension_run2/reports/sol_base.json"),
    ("DeepSeek-V4-Pro", "2026-04", "results_dsv4pro_run1/reports/base_run1.json",
                                   "results_extension_run2/reports/deepseekv4pro_base.json"),
]


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
    return c - h, c + h


def norm_ci(vals, z=1.96):
    n = len(vals)
    if n < 2:
        return float("nan"), float("nan")
    m = sum(vals) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))
    h = z * sd / math.sqrt(n)
    return m - h, m + h


def load_dates(paths):
    pub = {}
    for p in paths:
        if not os.path.exists(p):
            print(f"  WARN benchmark missing: {p}", file=sys.stderr)
            continue
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                pub[r["id"]] = str(r.get("publication_date", ""))[:7]
    return pub


def pool(name, cutoff, orig_path, ext_path, pub, rule="main"):
    """Return per-partition accumulators over the union of both halves."""
    halves = []
    for tag, p in (("original", orig_path), ("extension", ext_path)):
        if p and os.path.exists(p):
            halves.append((tag, json.load(open(p, encoding="utf-8"))))
        elif p:
            print(f"  WARN {name}: {tag} report missing ({p})", file=sys.stderr)
    if not halves:
        return None

    seen, dupes = set(), 0
    cm = mo(cutoff)
    acc = defaultdict(lambda: defaultdict(list))          # task -> part -> [score]
    cmat = {p: dict(tp=0, fp=0, tn=0, fn=0) for p in ("all", "pre", "post")}
    n_half = {}

    for tag, rep in halves:
        n_half[tag] = len(rep.get("results", []))
        for r in rep.get("results", []):
            rid = r.get("id")
            if rid in seen:
                dupes += 1
                continue
            seen.add(rid)
            pm = mo(pub.get(rid, ""))
            if pm is None or cm is None:
                part = None
            elif rule == "main":
                part = "pre" if pm < cm else "post"
            else:
                part = "pre" if pm <= cm else "post"
            parts = ["all"] + ([part] if part else [])
            t = r.get("tasks", {})

            for task in ("binary", "binary_perturbed", "mcq"):
                v = t.get(task)
                if v and not v.get("skipped") and "correct" in v:
                    for p in parts:
                        acc[task][p].append(1.0 if v["correct"] else 0.0)
                    if task == "binary":
                        for p in parts:
                            cmat[p]["tp" if v["correct"] else "fn"] += 1
                    elif task == "binary_perturbed":
                        for p in parts:
                            cmat[p]["tn" if v["correct"] else "fp"] += 1

            d = t.get("date")
            if d and not d.get("skipped") and d.get("score") is not None:
                for p in parts:
                    acc["date_score"][p].append(float(d["score"]))
                md = d.get("month_distance")
                if md is not None:
                    for p in parts:
                        acc["date_abs_months"][p].append(abs(float(md)))

    return {"acc": acc, "cmat": cmat, "n_events": len(seen), "dupes": dupes,
            "halves": n_half}


def fmt_prop(vals):
    n = len(vals)
    if n == 0:
        return f"{'--':>26}"
    k = int(round(sum(vals)))
    lo, hi = wilson(k, n)
    return f"{k/n:.3f}[{lo:.2f},{hi:.2f}] n={n}".rjust(26)


def fmt_mean(vals):
    n = len(vals)
    if n == 0:
        return f"{'--':>26}"
    m = sum(vals) / n
    lo, hi = norm_ci(vals)
    return f"{m:.3f}[{lo:.2f},{hi:.2f}] n={n}".rjust(26)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", action="append", default=[
        "archive/data/canonical/merged_validated_cusp_fixed.jsonl",
        "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"])
    ap.add_argument("--rule", choices=["main", "gap"], default="main",
                    help="main: cutoff month counts as POST (matches make_latex_tables.py)")
    ap.add_argument("--out")
    a = ap.parse_args()

    pub = load_dates(a.benchmark)
    print("=" * 108)
    print("FULL CUSP CORPUS: original (Jan 2024-Mar 2026) + extension (Apr-Aug 2026)")
    print(f"publication dates loaded for {len(pub)} events; partition rule = {a.rule} "
          f"(cutoff month counts as POST)")
    print("NOT PROSPECTIVE: every outcome in both halves had resolved before the models ran.")
    print("FRQ quality scores omitted throughout (stage-2 rubric under revision).")
    print("=" * 108)

    out = {}
    rows = []
    for name, cutoff, op, ep in PANEL:
        r = pool(name, cutoff, op, ep, pub, a.rule)
        if r is None:
            print(f"  SKIP {name}: no reports found", file=sys.stderr)
            continue
        rows.append((name, cutoff, r))
        out[name] = {
            "cutoff": cutoff, "n_events": r["n_events"], "halves": r["halves"],
            "duplicate_ids_dropped": r["dupes"],
        }

    for part, title in (("all", "ENTIRE CORPUS"), ("post", "POST-CUTOFF ONLY"),
                        ("pre", "PRE-CUTOFF ONLY (retrospective)")):
        print(f"\n=== {title} ===")
        print(f"{'model':<17}{'cutoff':<9}{'merged binary':>26}{'MCQ':>26}"
              f"{'date score':>26}")
        for name, cutoff, r in rows:
            b = r["acc"]["binary"][part]
            bp = r["acc"]["binary_perturbed"][part]
            merged = b + bp
            mcq = r["acc"]["mcq"][part]
            ds = r["acc"]["date_score"][part]
            print(f"{name:<17}{cutoff:<9}{fmt_prop(merged)}{fmt_prop(mcq)}"
                  f"{fmt_mean(ds)}")
            out.setdefault(name, {}).setdefault("partitions", {})[part] = {
                "merged_binary": {"k": int(round(sum(merged))), "n": len(merged)},
                "mcq": {"k": int(round(sum(mcq))), "n": len(mcq)},
                "date_score_mean": (sum(ds) / len(ds)) if ds else None,
                "date_score_n": len(ds),
            }

    print("\n=== BIAS-IMMUNE BINARY METRICS (post-cutoff, full corpus) ===")
    print(f"{'model':<17}{'n':>7}{'bias':>8}{'bal_acc':>9}{'macroF1':>9}{'MCC':>8}")
    for name, cutoff, r in rows:
        c = r["cmat"]["post"]
        n = sum(c.values())
        if n == 0:
            continue
        m = _binary_metrics(**c)
        bias = ((c["tp"] + c["fp"]) - (c["tn"] + c["fn"])) / n
        print(f"{name:<17}{n:>7}{bias:>+8.3f}{m['balanced_acc']:>9.3f}"
              f"{m['macro_f1']:>9.3f}{m['mcc']:>+8.3f}")
        out[name]["post_cutoff_binary"] = {"n": n, "bias": bias, **{
            k: v for k, v in m.items() if isinstance(v, (int, float))}}

    print("\n=== COVERAGE ===")
    print(f"{'model':<17}{'original':>10}{'extension':>11}{'union':>8}{'dupes':>7}")
    for name, cutoff, r in rows:
        h = r["halves"]
        print(f"{name:<17}{h.get('original', 0):>10}{h.get('extension', 0):>11}"
              f"{r['n_events']:>8}{r['dupes']:>7}")

    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
