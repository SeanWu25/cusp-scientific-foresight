"""
analyze2.py — Study 2 analysis: detection accuracy, order-swap consistency,
position bias, surface-artifact baselines, and the item-level join to the
evaluated panel's stored binary answers.

Judges are always reported separately, never pooled.
Reads only study2_detection/*; never reads anything under study1_verification/.
"""
from __future__ import annotations
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

B_BOOT = 10000          # bootstrap replicates for the stratum statistics
BOOT_SEED = 987654321


def _boot_xy(x, y, B=B_BOOT, seed=BOOT_SEED):
    """Vectorised pair bootstrap. Returns (phi_lo, phi_hi, diff_lo, diff_hi,
    det_lo, det_hi, und_lo, und_hi) as 95% percentile intervals."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = x.size
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    xs, ys = x[idx], y[idx]
    xm = xs.mean(1, keepdims=True)
    ym = ys.mean(1, keepdims=True)
    num = ((xs - xm) * (ys - ym)).sum(1)
    den = np.sqrt(((xs - xm) ** 2).sum(1) * ((ys - ym) ** 2).sum(1))
    with np.errstate(invalid="ignore", divide="ignore"):
        phis = np.where(den > 0, num / den, np.nan)
    nd = xs.sum(1)
    nu = n - nd
    sd = (xs * ys).sum(1)
    su = ys.sum(1) - sd
    with np.errstate(invalid="ignore", divide="ignore"):
        ad = np.where(nd > 0, sd / nd, np.nan)
        au = np.where(nu > 0, su / nu, np.nan)
    diffs = ad - au

    def q(a):
        a = a[~np.isnan(a)]
        return (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))) if a.size else (float("nan"),) * 2

    return q(phis) + q(diffs) + q(ad) + q(au)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
from analyze1 import fmt, pct, write_table

ORDERS = ("original_first", "perturbed_first")


def phi(pairs) -> float:
    """Pearson / phi correlation between two 0-1 vectors given as (x, y) tuples."""
    n = len(pairs)
    if n == 0:
        return float("nan")
    sx = sum(p[0] for p in pairs) / n
    sy = sum(p[1] for p in pairs) / n
    num = sum((p[0] - sx) * (p[1] - sy) for p in pairs)
    dx = math.sqrt(sum((p[0] - sx) ** 2 for p in pairs))
    dy = math.sqrt(sum((p[1] - sy) ** 2 for p in pairs))
    return num / (dx * dy) if dx > 0 and dy > 0 else float("nan")


def acc(v):
    return sum(v) / len(v) if v else float("nan")


def main() -> None:
    meta = json.loads((C.S2 / "pairs.json").read_text(encoding="utf-8"))
    pairs = {p["id"]: p for p in meta["pairs"]}
    judg = C.read_jsonl(C.S2 / "judgments.jsonl")

    # de-duplicate: last record wins per (pair, judge, order)
    by = {}
    for r in judg:
        by[(r["pair_id"], r["judge"], r["order"])] = r
    recs = list(by.values())
    judges = sorted({r["judge"] for r in recs})
    C.TABLES.mkdir(parents=True, exist_ok=True)

    # ---------------- per-judge headline ----------------
    head, per_judge = [], {}
    for j in judges:
        jr = [r for r in recs if r["judge"] == j]
        ans = [r for r in jr if r["answer"]]
        refused = sum(1 for r in jr if r.get("refused"))
        k = sum(1 for r in ans if r["correct"])
        lo, hi = C.wilson(k, len(ans))
        first = sum(1 for r in ans if r["chose_first"])
        flo, fhi = C.wilson(first, len(ans))
        head.append([j, jr[0]["judge_model"], len(jr), len(ans), refused,
                     k, fmt(k / len(ans)) if ans else "", fmt(lo), fmt(hi),
                     fmt(first / len(ans)) if ans else "", fmt(flo), fmt(fhi)])
        per_judge[j] = ans
    write_table(C.TABLES / "t5_detection_headline",
                ["judge", "model", "calls", "parsed", "refused", "correct", "accuracy",
                 "ci_lo", "ci_hi", "chose_first", "cf_lo", "cf_hi"], head,
                "Study 2: detection accuracy per judge (both orders pooled within judge)")

    # ---------------- baselines on the same pairs ----------------
    ids = sorted(pairs)
    shorter = [1 if pairs[i]["len_perturbed"] < pairs[i]["len_original"]
               else (0 if pairs[i]["len_perturbed"] > pairs[i]["len_original"] else 0.5) for i in ids]
    base = [["chance", len(ids), "0.500", "", ""],
            ["always pick the SHORTER claim", len(ids), fmt(sum(shorter) / len(shorter)),
             fmt(C.wilson(int(sum(shorter)), len(shorter))[0]), fmt(C.wilson(int(sum(shorter)), len(shorter))[1])]]
    write_table(C.TABLES / "t6_detection_baselines",
                ["baseline", "n_pairs", "accuracy", "ci_lo", "ci_hi"], base,
                "Study 2: surface-artifact baselines on the sampled pairs")

    # ---------------- order-swap consistency + per-pair detection ----------------
    det = defaultdict(dict)          # judge -> pair_id -> dict
    cons_rows = []
    for j in judges:
        n_both = n_cons = 0
        for i in ids:
            a = by.get((i, j, "original_first"))
            b = by.get((i, j, "perturbed_first"))
            if not a or not b or not a["answer"] or not b["answer"]:
                continue
            n_both += 1
            same_claim = (a["correct"] == b["correct"])      # same underlying claim chosen twice
            n_cons += same_claim
            det[j][i] = dict(strict=bool(a["correct"] and b["correct"]),
                             any=bool(a["correct"] or b["correct"]),
                             consistent=bool(same_claim), n_correct=int(a["correct"]) + int(b["correct"]),
                             conf=[a.get("confidence"), b.get("confidence")])
        lo, hi = C.wilson(n_cons, n_both)
        strict = sum(1 for v in det[j].values() if v["strict"])
        anyc = sum(1 for v in det[j].values() if v["any"])
        cons_rows.append([j, n_both, n_cons, fmt(n_cons / n_both) if n_both else "", fmt(lo), fmt(hi),
                          strict, fmt(strict / n_both) if n_both else "",
                          anyc, fmt(anyc / n_both) if n_both else ""])
    write_table(C.TABLES / "t7_order_consistency",
                ["judge", "pairs_with_both_orders", "consistent", "consistency_rate", "ci_lo", "ci_hi",
                 "detected_both_orders", "rate_strict", "detected_either_order", "rate_any"], cons_rows,
                "Study 2: order-swap consistency (detection separated from position bias)")

    # ---------------- breakdowns ----------------
    br = []
    for j in judges:
        for keyname, keyfn in (("domain", lambda i: pairs[i]["main_area"] or "Unknown"),
                               ("ptype", lambda i: pairs[i]["ptype"]),
                               ("corpus", lambda i: pairs[i]["corpus"])):
            g = defaultdict(list)
            for i, v in det[j].items():
                g[keyfn(i)].append(v["strict"])
            for gk in sorted(g):
                v = g[gk]
                k = sum(v)
                lo, hi = C.wilson(k, len(v))
                br.append([j, keyname, gk, len(v), k, fmt(k / len(v)), fmt(lo), fmt(hi)])
    write_table(C.TABLES / "t8_detection_breakdown",
                ["judge", "split", "group", "n_pairs", "detected", "rate_strict", "ci_lo", "ci_hi"], br,
                "Study 2: strict detection rate by domain, perturbation type and corpus")

    # ---------------- item-level join to the evaluated panel ----------------
    pa = C.load_panel_answers()
    join_rows, stat_rows = [], []
    for j in judges:
        for m in C.MODEL_ORDER:
            name = C.MODELS[m]["name"]
            for task, tag in (("binary_perturbed", "perturbed"), ("binary", "positive"),
                              ("__pair__", "pair")):
                xy, d_ok, u_ok = [], [], []
                for i, v in det[j].items():
                    if task == "__pair__":
                        a = pa.get((m, i, "binary_perturbed"))
                        b = pa.get((m, i, "binary"))
                        if not a or not b:
                            continue
                        y = (int(a["correct"]) + int(b["correct"])) / 2
                    else:
                        a = pa.get((m, i, task))
                        if not a:
                            continue
                        y = 1 if a["correct"] else 0
                    x = 1 if v["strict"] else 0
                    xy.append((x, y))
                    (d_ok if x else u_ok).append(y)
                if len(xy) < 20:
                    continue
                r = phi(xy)
                rlo, rhi, dflo, dfhi, dlo, dhi, ulo, uhi = _boot_xy(
                    [a for a, _ in xy], [b for _, b in xy])
                ad, au = acc(d_ok), acc(u_ok)
                if tag != "pair":            # binary outcome: Wilson is exact-ish and tighter
                    dlo, dhi = C.wilson(int(sum(d_ok)), len(d_ok))
                    ulo, uhi = C.wilson(int(sum(u_ok)), len(u_ok))
                diff_ci = (dflo, dfhi)
                stat_rows.append([j, name, tag, len(xy), len(d_ok), len(u_ok),
                                  fmt(r), fmt(rlo), fmt(rhi),
                                  fmt(ad), fmt(dlo), fmt(dhi), fmt(au), fmt(ulo), fmt(uhi),
                                  fmt(ad - au), fmt(diff_ci[0]), fmt(diff_ci[1])])
    write_table(C.TABLES / "t9_detection_x_accuracy",
                ["judge", "model", "task", "n_pairs", "n_detected", "n_undetected",
                 "phi", "phi_lo", "phi_hi",
                 "acc_detected", "det_lo", "det_hi", "acc_undetected", "und_lo", "und_hi",
                 "diff_detected_minus_undetected", "diff_lo", "diff_hi"], stat_rows,
                "Study 2: is binary accuracy explained by pair detectability?")

    # ---------------- item_level_join.csv ----------------
    cols = ["pair_id", "domain", "ptype", "corpus", "target_date", "len_original", "len_perturbed",
            "len_gap_orig_minus_pert", "shorter_is_perturbed"]
    for j in judges:
        cols += [f"{j}_detected_strict", f"{j}_detected_any", f"{j}_order_consistent", f"{j}_n_correct"]
    for m in C.MODEL_ORDER:
        cols += [f"{m}_perturbed_correct", f"{m}_positive_correct"]
    with open(C.S2 / "item_level_join.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i in ids:
            p = pairs[i]
            gap = p["len_original"] - p["len_perturbed"]
            row = [i, p["main_area"], p["ptype"], p["corpus"], p["target_human"],
                   p["len_original"], p["len_perturbed"], gap, int(gap > 0)]
            for j in judges:
                v = det[j].get(i)
                row += ["" if not v else int(v["strict"]), "" if not v else int(v["any"]),
                        "" if not v else int(v["consistent"]), "" if not v else v["n_correct"]]
            for m in C.MODEL_ORDER:
                a = pa.get((m, i, "binary_perturbed"))
                b = pa.get((m, i, "binary"))
                row += ["" if not a else int(a["correct"]), "" if not b else int(b["correct"])]
            w.writerow(row)

    # ---------------- length-gap control ----------------
    lg = []
    for m in C.MODEL_ORDER:
        xy = []
        for i in ids:
            a = pa.get((m, i, "binary_perturbed"))
            if a:
                xy.append((1 if pairs[i]["len_original"] > pairs[i]["len_perturbed"] else 0,
                           1 if a["correct"] else 0))
        if len(xy) < 20:
            continue
        r = phi(xy)
        lo, hi, *_ = _boot_xy([a for a, _ in xy], [b for _, b in xy])
        lg.append([C.MODELS[m]["name"], len(xy), fmt(r), fmt(lo), fmt(hi)])
    write_table(C.TABLES / "t10_lengthgap_x_accuracy",
                ["model", "n_pairs", "phi_shorter_perturbed_vs_correct", "ci_lo", "ci_hi"], lg,
                "Study 2 control: does the length artifact alone predict binary correctness?")

    out = dict(judges={j: dict(model=per_judge[j][0]["judge_model"] if per_judge[j] else None,
                               parsed=len(per_judge[j]),
                               accuracy=acc([1 if r["correct"] else 0 for r in per_judge[j]]),
                               pairs_both_orders=len(det[j]),
                               strict_rate=acc([1 if v["strict"] else 0 for v in det[j].values()]),
                               consistency=acc([1 if v["consistent"] else 0 for v in det[j].values()]))
                       for j in judges},
               length_baseline=sum(shorter) / len(shorter), n_pairs=len(ids))
    (C.S2 / "summary_stats.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
