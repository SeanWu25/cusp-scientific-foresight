#!/usr/bin/env python3
"""
main_tables.py — Table 1, the retrospective-ceiling block, FRQ sub-dimensions,
and run-to-run variance, for the whole seven-model panel.

Every figure carries an explicit N and a 95% interval. Post-cutoff cells below
--min-n are suppressed rather than printed as a point estimate.

Metric definitions are the published ones:
  merged binary = pooled correct counts, (c_orig + c_pert) / (n_orig + n_pert)
  MCQ           = 4-choice accuracy
  FRQ           = mean of the 0-10 rubric; pass = score >= 5.0
  date score    = mean exp(-0.1 * |months off|)
  signed error  = predicted month - true month (positive = predicted too late)
"""

from __future__ import annotations

import argparse, json, math, os, statistics, sys
from collections import defaultdict

PUBLISHED = {
    "gpt_5_4_eval.json":       ("GPT-5.4",      "2025-08"),
    "claude_sonnet.json":      ("Claude S4.5",  "2025-01"),
    "deepseek_r1.json":        ("DeepSeek R1",  "2024-07"),
    "gpt_oss_20B_reeval.json": ("GPT-OSS 20B",  "2024-06"),
    "llama_3_3_full.json":     ("LLaMA 3.3",    "2023-12"),
    "gpt_4o_reeval.json":      ("GPT-4o",       "2023-10"),
}


def months(ym):
    try:
        y, m = str(ym).split("-")[:2]
        return int(y) * 12 + int(m)
    except Exception:
        return None


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - hw), min(1.0, c + hw)


def mean_ci(v, z=1.96):
    n = len(v)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    m = statistics.fmean(v)
    if n < 2:
        return m, float("nan"), float("nan")
    se = statistics.stdev(v) / math.sqrt(n)
    return m, m - z * se, m + z * se


def collect(path, cutoff, pub, rule="main"):
    rep = json.load(open(path, encoding="utf-8"))
    cm = months(cutoff)
    acc = defaultdict(lambda: defaultdict(list))
    for r in rep.get("results", []):
        pm = months(pub.get(r["id"], ""))
        if pm is None or cm is None:
            part = None
        elif rule == "main":
            part = "pre" if pm < cm else "post"
        else:
            part = "pre" if pm <= cm else "post"
        parts = ["all"] + ([part] if part else [])
        t = r.get("tasks", {})
        for key in ("binary", "binary_perturbed"):
            d = t.get(key)
            if d and not d.get("skipped") and "correct" in d:
                for p in parts:
                    acc["merged_binary"][p].append(1 if d["correct"] else 0)
                    acc[key][p].append(1 if d["correct"] else 0)
        d = t.get("mcq")
        if d and not d.get("skipped") and "correct" in d:
            for p in parts:
                acc["mcq"][p].append(1 if d["correct"] else 0)
        d = t.get("frq")
        if d and not d.get("skipped") and d.get("score") is not None:
            for p in parts:
                acc["frq"][p].append(float(d["score"]))
                acc["frq_pass"][p].append(1 if d["score"] >= 5.0 else 0)
                for sub in ("alignment", "specificity", "novelty", "feasibility"):
                    if d.get(sub) is not None:
                        acc[f"frq_{sub}"][p].append(float(d[sub]))
        d = t.get("date")
        if d and not d.get("skipped"):
            for p in parts:
                if d.get("score") is not None:
                    acc["date_score"][p].append(float(d["score"]))
                pd_, gt = d.get("parsed_date"), d.get("ground_truth")
                if pd_ and gt:
                    a_, b_ = months(pd_), months(gt)
                    if a_ is not None and b_ is not None:
                        acc["date_signed"][p].append(a_ - b_)
                        acc["date_abs"][p].append(abs(a_ - b_))
                        acc["date_pred_month"][p].append(a_)
    return acc, rep


PROPORTIONS = {"merged_binary", "binary", "binary_perturbed", "mcq", "frq_pass"}


def cell(acc, metric, part, min_n):
    v = acc[metric].get(part, [])
    n = len(v)
    if n == 0:
        return {"n": 0, "empty": True}
    if n < min_n:
        return {"n": n, "suppressed": True}
    if metric in PROPORTIONS:
        k = sum(v)
        lo, hi = wilson(k, n)
        return {"n": n, "value": k / n, "ci": (lo, hi), "k": k}
    m, lo, hi = mean_ci([float(x) for x in v])
    return {"n": n, "value": m, "ci": (lo, hi)}


def fmt(c, dp=3):
    if not c or c.get("empty"):
        return "     ---     "
    if c.get("suppressed"):
        return f"  [n={c['n']}]   "
    lo, hi = c.get("ci", (float("nan"), float("nan")))
    return f"{c['value']:.{dp}f}[{lo:.2f},{hi:.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="run_evaluation/frq_results")
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--extra", action="append", default=[],
                    help="'Name=YYYY-MM=path.json' — repeatable")
    ap.add_argument("--repeats", action="append", default=[],
                    help="'Name=path.json' — additional repeated runs of the SAME "
                         "model/config, for the run-to-run variance table")
    ap.add_argument("--rule", choices=["main", "gap"], default="main")
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--frq", choices=["report", "diagnostics-only"],
                    default="diagnostics-only",
                    help="diagnostics-only (default): omit FRQ quality scores, "
                         "pass rate and sub-dimensions entirely, because the "
                         "rubric is under revision. Reports generation counts "
                         "and leakage instead.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    pub = {}
    for l in open(a.benchmark, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            pub[r["id"]] = r.get("publication_date", "")

    models = [(n, c, os.path.join(a.results, f)) for f, (n, c) in PUBLISHED.items()
              if os.path.exists(os.path.join(a.results, f))]
    for spec in a.extra:
        n, c, p = spec.split("=", 2)
        if os.path.exists(p):
            models.append((n, c, p))
        else:
            print(f"  SKIP extra {n} ({p})", file=sys.stderr)

    data = {}
    for n, c, p in models:
        acc, rep = collect(p, c, pub, a.rule)
        data[n] = {"cutoff": c, "acc": acc, "report": rep, "path": p}

    out = {"rule": a.rule, "min_n": a.min_n, "table1": {}, "ceiling": {},
           "frq_subdims": {}, "date_stats": {}, "variance": {}}

    # ---------------- Table 1 (all instances) + pre->post delta ----------------
    show_frq = a.frq == "report"
    print("=== TABLE 1 — all instances, with 95% CI and N ===")
    if not show_frq:
        print("    FRQ quality scores omitted: rubric under revision. See the FRQ")
        print("    generation diagnostics block below.")
    hdr = (f"{'model':14s}{'cutoff':>9s}{'n_pre':>7s}{'n_post':>7s}"
           f"{'merged binary':>22s}{'MCQ':>22s}")
    if show_frq:
        hdr += f"{'FRQ mean':>22s}{'pass%':>22s}"
    print(hdr + f"{'date score':>22s}")
    for n, c, _ in models:
        acc = data[n]["acc"]
        npre = len(acc["merged_binary"].get("pre", []))
        npost = len(acc["merged_binary"].get("post", []))
        row = {m: cell(acc, m, "all", a.min_n)
               for m in ("merged_binary", "mcq", "frq", "frq_pass", "date_score")}
        out["table1"][n] = {"cutoff": c, "n_pre": npre, "n_post": npost, **row}
        line = (f"{n:14s}{c:>9s}{npre:7d}{npost:7d}"
                f"{fmt(row['merged_binary']):>22s}{fmt(row['mcq']):>22s}")
        if show_frq:
            line += f"{fmt(row['frq'],2):>22s}{fmt(row['frq_pass']):>22s}"
        print(line + f"{fmt(row['date_score']):>22s}")

    # ------------- Retrospective ceiling: pre vs post, and the ratio -------------
    print("\n=== RETROSPECTIVE CEILING — pre-cutoff is the in-weights ceiling ===")
    print("   ratio = post / pre. Below 1.0 means performance falls once the answer")
    print("   is no longer plausibly in the training data.")
    ceiling_metrics = [("merged_binary", 3), ("mcq", 3), ("date_score", 3)]
    if show_frq:
        ceiling_metrics.insert(2, ("frq", 2))
    for metric, dp in ceiling_metrics:
        print(f"\n-- {metric}")
        print(f"{'model':14s}{'cutoff':>9s}{'pre (ceiling)':>24s}{'post':>24s}"
              f"{'ratio':>9s}{'n_pre':>7s}{'n_post':>8s}")
        for n, c, _ in models:
            acc = data[n]["acc"]
            pre, post = cell(acc, metric, "pre", a.min_n), cell(acc, metric, "post", a.min_n)
            ratio = (post["value"] / pre["value"]
                     if pre.get("value") and post.get("value") else float("nan"))
            out["ceiling"].setdefault(n, {})[metric] = {
                "pre": pre, "post": post,
                "ratio": None if math.isnan(ratio) else ratio}
            rs = "  ---  " if math.isnan(ratio) else f"{ratio:7.3f}"
            print(f"{n:14s}{c:>9s}{fmt(pre,dp):>24s}{fmt(post,dp):>24s}{rs:>9s}"
                  f"{pre.get('n',0):7d}{post.get('n',0):8d}")

    # ---------------- FRQ sub-dimensions (Table S5 schema + feasibility) --------
    if not show_frq:
        print("\n=== FRQ GENERATION DIAGNOSTICS (no quality scores) ===")
        print(f"{'model':14s}{'responses':>11s}{'mean chars':>12s}{'truncated':>11s}"
              f"{'leak fail%':>12s}{'leak unclear%':>15s}{'n_judged':>9s}")
        for n, c, _ in models:
            rep = data[n]["report"]
            res = rep.get("results", [])
            fr = [r["tasks"]["frq"] for r in res
                  if (r.get("tasks") or {}).get("frq")
                  and not r["tasks"]["frq"].get("skipped")]
            gen = [f for f in fr if f.get("generated") or f.get("score") is not None]
            ch = [f.get("chars") for f in gen if f.get("chars")]
            tr = sum(1 for f in gen if f.get("truncated"))
            lk = [r["reasoning"]["leakage"] for r in res
                  if (r.get("reasoning") or {}).get("leakage")]
            SKIP = ("not judged", "No FRQ response to assess")
            lk = [x for x in lk if x.get("reason") not in SKIP]
            nf = sum(1 for x in lk if x.get("verdict") == "fail")
            nu = sum(1 for x in lk if x.get("verdict") == "unclear")
            mc = f"{statistics.fmean(ch):.0f}" if ch else "---"
            tc = str(tr) if ch else "---"
            print(f"{n:14s}{len(gen):11d}{mc:>12s}{tc:>11s}"
                  f"{(100*nf/len(lk) if lk else float('nan')):12.2f}"
                  f"{(100*nu/len(lk) if lk else float('nan')):15.1f}"
                  f"{len(lk):>9d}")
    else:
        print("\n=== FRQ SUB-DIMENSIONS (0-10 each; overall = mean of the four) ===")
        print(f"{'model':14s}{'cutoff':>9s}{'align':>8s}{'spec':>8s}{'novel':>8s}"
              f"{'feasib':>8s}{'spec-align':>12s}{'overall':>9s}{'n':>7s}")
    for n, c, _ in (models if show_frq else []):
        acc = data[n]["acc"]
        vals = {}
        for sub in ("alignment", "specificity", "novelty", "feasibility"):
            v = acc[f"frq_{sub}"].get("all", [])
            vals[sub] = statistics.fmean(v) if v else float("nan")
        ov = acc["frq"].get("all", [])
        nfr = len(ov)
        gap = vals["specificity"] - vals["alignment"]
        out["frq_subdims"][n] = {"cutoff": c, "n": nfr, "gap_spec_minus_align": gap, **vals,
                                 "overall": statistics.fmean(ov) if ov else None}
        f2 = lambda x: "  ---" if math.isnan(x) else f"{x:.2f}"
        print(f"{n:14s}{c:>9s}{f2(vals['alignment']):>8s}{f2(vals['specificity']):>8s}"
              f"{f2(vals['novelty']):>8s}{f2(vals['feasibility']):>8s}"
              f"{f2(gap):>12s}{f2(statistics.fmean(ov) if ov else float('nan')):>9s}{nfr:7d}")

    # ---------------- Date statistics ----------------
    print("\n=== DATE PREDICTION (signed error positive = predicted too late) ===")
    print(f"{'model':14s}{'cutoff':>9s}{'n':>6s}{'mean pred':>11s}{'mean err':>10s}"
          f"{'median':>9s}{'<=3mo':>8s}{'<=6mo':>8s}{'<=12mo':>8s}{'<=24mo':>8s}{'score':>8s}")
    for n, c, _ in models:
        acc = data[n]["acc"]
        sg = acc["date_signed"].get("all", [])
        ab = acc["date_abs"].get("all", [])
        pm = acc["date_pred_month"].get("all", [])
        sc = acc["date_score"].get("all", [])
        if not sg:
            continue
        mp = statistics.fmean(pm)
        mpred = f"{int(mp)//12:04d}-{int(round(mp))%12 or 12:02d}"
        thr = lambda t: 100 * sum(1 for x in ab if x <= t) / len(ab)
        out["date_stats"][n] = {
            "cutoff": c, "n": len(sg), "mean_pred_month": mpred,
            "mean_signed": statistics.fmean(sg), "median_signed": statistics.median(sg),
            "within_3": thr(3), "within_6": thr(6), "within_12": thr(12),
            "within_24": thr(24), "score": statistics.fmean(sc)}
        print(f"{n:14s}{c:>9s}{len(sg):6d}{mpred:>11s}{statistics.fmean(sg):+10.1f}"
              f"{statistics.median(sg):+9.1f}{thr(3):8.1f}{thr(6):8.1f}{thr(12):8.1f}"
              f"{thr(24):8.1f}{statistics.fmean(sc):8.3f}")

    # ---------------- Run-to-run variance ----------------
    if a.repeats:
        print("\n=== RUN-TO-RUN VARIANCE (mean +/- sd across repeated runs) ===")
        groups = defaultdict(list)
        for spec in a.repeats:
            nm, p = spec.split("=", 1)
            if os.path.exists(p):
                groups[nm].append(p)
            else:
                print(f"  SKIP repeat {nm} ({p})", file=sys.stderr)
        for nm, paths in groups.items():
            cut = dict((n, c) for n, c, _ in models).get(nm, "?")
            per = []
            for p in paths:
                acc, _ = collect(p, cut, pub, a.rule)
                per.append({m: (statistics.fmean([float(x) for x in acc[m].get("all", [])])
                                if acc[m].get("all") else float("nan"))
                            for m in ("merged_binary", "mcq", "frq", "date_score")})
            print(f"\n{nm}  ({len(per)} runs)")
            print(f"{'metric':18s}{'mean':>10s}{'sd':>10s}{'min':>10s}{'max':>10s}")
            out["variance"][nm] = {"n_runs": len(per), "metrics": {}}
            for m in ("merged_binary", "mcq", "frq", "date_score"):
                v = [d[m] for d in per if not math.isnan(d[m])]
                if not v:
                    continue
                sd = statistics.stdev(v) if len(v) > 1 else 0.0
                out["variance"][nm]["metrics"][m] = {
                    "mean": statistics.fmean(v), "sd": sd,
                    "min": min(v), "max": max(v), "runs": v}
                print(f"{m:18s}{statistics.fmean(v):10.4f}{sd:10.4f}{min(v):10.4f}{max(v):10.4f}")

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2, default=str)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
