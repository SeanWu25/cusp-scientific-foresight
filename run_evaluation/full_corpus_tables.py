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

    out["_horizon_mcc"] = horizon_mcc(pub, PANEL)
    out["_discrimination_gap"] = discrimination_gap(pub, PANEL)
    out["_stratified_mcq_delta"] = stratified_mcq_delta(PANEL)

    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")




def horizon_mcc(pub, panel, bins=((0, 2), (3, 5), (6, 11), (12, 23), (24, 999)),
                min_n=50, boots=800, seed=7):
    """MCC by forecast horizon over the pooled corpus, post-cutoff only.

    Reported as MCC rather than accuracy on purpose: accuracy also declines
    across horizon bins, but that is base-rate drift interacting with response
    bias, not skill decay. CIs are bootstrapped over EVENTS, not task
    instances, because an event's binary and perturbed items are not
    independent.
    """
    import random
    lab = lambda b: f"{b[0]}-{b[1]}" if b[1] < 999 else ">=24"
    print("\n=== MCC BY FORECAST HORIZON (pooled corpus, post-cutoff only) ===")
    print(f"{'model':<17}" + "".join(f"{lab(b):>24}" for b in bins))
    out = {}
    for name, cutoff, op, ep in panel:
        cm = mo(cutoff)
        ev = {}
        for p in (op, ep):
            if not p or not os.path.exists(p):
                continue
            for x in json.load(open(p, encoding="utf-8")).get("results", []):
                pm = mo(pub.get(x["id"], ""))
                if pm is None or cm is None or pm - cm < 0:
                    continue
                bk = next((b for b in bins if b[0] <= pm - cm <= b[1]), None)
                if bk is None:
                    continue
                t = x.get("tasks", {})
                cells = []
                b = t.get("binary")
                if b and not b.get("skipped") and "correct" in b:
                    cells.append("tp" if b["correct"] else "fn")
                bp = t.get("binary_perturbed")
                if bp and not bp.get("skipped") and "correct" in bp:
                    cells.append("tn" if bp["correct"] else "fp")
                if cells:
                    ev.setdefault(bk, []).append(cells)
        line, row = "", {}
        for bk in bins:
            e = ev.get(bk)
            n = sum(len(x) for x in e) if e else 0
            if n < min_n:
                line += f"{'--':>24}"
                continue

            def mcc(sample):
                c = dict(tp=0, fp=0, tn=0, fn=0)
                for x in sample:
                    for k in x:
                        c[k] += 1
                return _binary_metrics(**c)["mcc"]

            pt = mcc(e)
            rng = random.Random(seed)
            bs = sorted(mcc([e[rng.randrange(len(e))] for _ in e]) for _ in range(boots))
            lo, hi = bs[int(.025 * boots)], bs[int(.975 * boots) - 1]
            line += f"{pt:+.3f}[{lo:+.2f},{hi:+.2f}] {n}".rjust(24)
            row[lab(bk)] = {"mcc": pt, "ci": [lo, hi], "n": n, "events": len(e)}
        print(f"{name:<17}{line}")
        out[name] = row
    print(f"\ncell = MCC [95% event-clustered bootstrap CI] n; bins with n<{min_n} suppressed")
    return out


def discrimination_gap(pub, panel, post_only=True, boots=2000, seed=11):
    """P(yes | real finding) - P(yes | corrupted finding), PAIRED within event.

    Can the model tell a real finding from a plausible fake? Immune to the
    class-balance problem (rates conditioned separately) and to response bias
    (a uniform shift in yes-rate cancels).

    PAIRING IS MANDATORY. Only 2,289 of 5,575 events carry both a real and a
    perturbed binary question; the rest have one or the other. Computing the
    two rates over all available items compares different papers in different
    domains, and the question forms differ systematically -- real questions are
    long conjunctive claims bundling many exact numbers, perturbed ones are
    short single claims. Unpaired, five models appear significantly
    ANTI-discriminating; paired, none do. That difference is entirely artifact.

    Residual confound, not fixable in analysis: even within pairs the real
    question runs longer than the perturbed one (median 176 vs 131 chars), so
    part of a positive gap may be length or specificity rather than truth
    discrimination. Testing that needs length-matched perturbations, i.e. a
    dataset change.

    CIs are bootstrapped over event pairs.
    """
    import random
    print("\n=== PAIRED DISCRIMINATION GAP: P(yes|real) - P(yes|corrupted) ==="
          + ("  [post-cutoff only]" if post_only else "  [all]"))
    print("    paired within event; only events carrying BOTH questions count")
    print(f"{'model':<17}{'P(yes|real)':>13}{'P(yes|corrupt)':>16}"
          f"{'gap':>9}{'95% CI':>18}{'pairs':>8}")
    out = {}
    for name, cutoff, op, ep in panel:
        cm = mo(cutoff)
        ev = []
        for p_ in (op, ep):
            if not p_ or not os.path.exists(p_):
                continue
            for x in json.load(open(p_, encoding="utf-8")).get("results", []):
                pm = mo(pub.get(x["id"], ""))
                if post_only and (pm is None or cm is None or pm < cm):
                    continue
                t = x.get("tasks", {})
                b, q = t.get("binary"), t.get("binary_perturbed")
                # paired only: the event must carry BOTH questions
                if not (b and q) or b.get("skipped") or q.get("skipped"):
                    continue
                if "correct" not in b or "correct" not in q:
                    continue
                ev.append((1 if b["correct"] else 0,      # correct on real == said yes
                           0 if q["correct"] else 1))     # wrong on corrupted == said yes
        if len(ev) < 50:
            continue

        def gap(sample):
            n = len(sample)
            if not n:
                return None
            return sum(a for a, _ in sample) / n, sum(b for _, b in sample) / n

        pr, pc = gap(ev)
        rng = random.Random(seed)
        bs = []
        for _ in range(boots):
            g = gap([ev[rng.randrange(len(ev))] for _ in ev])
            if g:
                bs.append(g[0] - g[1])
        bs.sort()
        lo, hi = bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1]
        sig = "" if lo <= 0 <= hi else "  *"
        print(f"{name:<17}{pr:>13.3f}{pc:>16.3f}{pr-pc:>+9.3f}"
              f"{f'[{lo:+.3f},{hi:+.3f}]':>18}{len(ev):>8}{sig}")
        out[name] = {"p_yes_real": pr, "p_yes_corrupted": pc, "gap": pr - pc,
                     "ci": [lo, hi], "n_pairs": len(ev), "paired": True,
                     "excludes_zero": not (lo <= 0 <= hi)}
    print("  * = CI excludes zero. Negative gap means the model endorses the")
    print("  fabricated finding MORE readily than the genuine one.")
    return out


def stratified_mcq_delta(panel, min_cell=10):
    """MCQ extension-vs-original delta, crude and domain-stratified.

    The two corpora do NOT share a domain mix (chi2=212.3, df=8: the AI share
    falls 24.0% -> 16.3% and 'Other' grows 1.3% -> 6.6%), so a crude difference
    of post-cutoff MCQ accuracy confounds performance with item population.
    Stratifying within main_area and pooling per-area deltas with weights
    n_o*n_e/(n_o+n_e) cancels the mix.

    In practice the two agree here -- the largest shift is 0.018 against CI
    half-widths near 0.041 -- but that is a measured result, not an assumption,
    and the mix difference is large enough that it had to be checked.
    """
    import math
    meta = {}
    for path in ("archive/data/canonical/merged_validated_cusp_fixed.jsonl",
                 "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"):
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                meta[r["id"]] = (r.get("main_area") or "Unknown",
                                 mo(r.get("publication_date", "")))
    print("\n=== MCQ EXTENSION-vs-ORIGINAL DELTA: crude vs domain-stratified ===")
    print("    post-cutoff only; stratified pools per-area deltas, so mix cancels")
    print(f"{'model':<17}{'crude':>20}{'domain-stratified':>22}{'areas':>7}")
    out = {}
    for name, cutoff, op, ep in panel:
        cm = mo(cutoff)
        o, e = {}, {}
        for path, bucket in ((op, o), (ep, e)):
            if not path or not os.path.exists(path):
                continue
            for x in json.load(open(path, encoding="utf-8")).get("results", []):
                m = meta.get(x["id"])
                if not m:
                    continue
                area, pm = m
                if pm is None or cm is None or pm < cm:
                    continue
                t = (x.get("tasks") or {}).get("mcq")
                if not t or t.get("skipped") or "correct" not in t:
                    continue
                bucket.setdefault(area, []).append(1.0 if t["correct"] else 0.0)
        allo = [v for vs in o.values() for v in vs]
        alle = [v for vs in e.values() for v in vs]
        if len(allo) < 50 or len(alle) < 50:
            continue
        po_, pe_ = sum(allo) / len(allo), sum(alle) / len(alle)
        crude = pe_ - po_
        se_c = math.sqrt(pe_ * (1 - pe_) / len(alle) + po_ * (1 - po_) / len(allo))
        num = den = varn = 0.0
        k = 0
        for a in set(o) & set(e):
            no, ne = len(o[a]), len(e[a])
            if no < min_cell or ne < min_cell:
                continue
            pa, pb = sum(o[a]) / no, sum(e[a]) / ne
            w = no * ne / (no + ne)
            num += w * (pb - pa); den += w; k += 1
            varn += w * w * (pb * (1 - pb) / ne + pa * (1 - pa) / no)
        if not den:
            continue
        strat, se_s = num / den, math.sqrt(varn) / den
        print(f"{name:<17}{f'{crude:+.3f}+/-{1.96*se_c:.3f}':>20}"
              f"{f'{strat:+.3f}+/-{1.96*se_s:.3f}':>22}{k:>7}")
        out[name] = {"crude": crude, "crude_ci_halfwidth": 1.96 * se_c,
                     "stratified": strat, "stratified_ci_halfwidth": 1.96 * se_s,
                     "areas": k}
    print("    report the stratified column; the crude one belongs in the supplement")
    return out


if __name__ == "__main__":
    main()
