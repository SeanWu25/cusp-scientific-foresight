#!/usr/bin/env python3
"""
binary_extended.py — Table S13 / S15 / S14 metrics for every model.

Additive companion to make_latex_tables.py. The released copy of that module
had `_binary_metrics`, `table_binary_extended` and `table_binary_pre_post_extended`
stripped out before publication; this restores the metric definitions verbatim
from the pre-release tree and computes them straight off the stored per-row
evaluation reports, so the released module is left untouched.

Confusion matrix convention (unchanged from the original):
  original binary questions  have ground truth Yes -> contribute TP / FN
  perturbed binary questions have ground truth No  -> contribute TN / FP

Emits:
  S13  bias index, balanced accuracy, precision, recall, specificity,
       per-class F1, macro F1, MCC          (overall and split pre/post cutoff)
  S14  ECE, Brier, confidence gap           (per task, overall and pre/post)
"""

from __future__ import annotations

import argparse, json, math, os, sys
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


# --- verbatim from the pre-release make_latex_tables.py ---------------------
def _binary_metrics(tp: int, fp: int, tn: int, fn: int) -> dict:
    """Return a dict of classification metrics from a 2x2 confusion matrix."""
    nan = float("nan")
    n = tp + fp + tn + fn
    if n == 0:
        return {k: nan for k in ("balanced_acc", "precision", "recall", "specificity",
                                 "f1_yes", "f1_no", "macro_f1", "mcc", "n")}
    tpr = tp / (tp + fn) if (tp + fn) > 0 else nan
    tnr = tn / (tn + fp) if (tn + fp) > 0 else nan
    prec = tp / (tp + fp) if (tp + fp) > 0 else nan
    bal_acc = (tpr + tnr) / 2 if not (math.isnan(tpr) or math.isnan(tnr)) else nan
    f1_yes = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else nan
    f1_no = 2 * tn / (2 * tn + fn + fp) if (2 * tn + fn + fp) > 0 else nan
    macro_f1 = (f1_yes + f1_no) / 2 if not (math.isnan(f1_yes) or math.isnan(f1_no)) else nan
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denom if denom > 0 else nan
    return {"balanced_acc": bal_acc, "precision": prec, "recall": tpr,
            "specificity": tnr, "f1_yes": f1_yes, "f1_no": f1_no,
            "macro_f1": macro_f1, "mcc": mcc, "n": n}
# ---------------------------------------------------------------------------


def ece(pairs, bins: int = 10, min_n: int = 20) -> float:
    """Expected calibration error, 10 equal-width bins (as make_latex_tables.py)."""
    if len(pairs) < min_n:
        return float("nan")
    tot, e = len(pairs), 0.0
    for i in range(bins):
        lo, hi = i / bins, (i + 1) / bins
        sel = [(c, o) for c, o in pairs if (lo <= c < hi) or (i == bins - 1 and c == 1.0)]
        if not sel:
            continue
        e += len(sel) / tot * abs(sum(o for _, o in sel) / len(sel)
                                  - sum(c for c, _ in sel) / len(sel))
    return e


def brier(pairs) -> float:
    return float("nan") if not pairs else sum((c - o) ** 2 for c, o in pairs) / len(pairs)


def gap(pairs) -> float:
    if not pairs:
        return float("nan")
    return sum(c for c, _ in pairs) / len(pairs) - sum(o for _, o in pairs) / len(pairs)


def analyse(path: str, cutoff: str, pub: dict, rule: str) -> dict:
    rep = json.load(open(path, encoding="utf-8"))
    cm = months(cutoff)
    cmats = {"all": dict(tp=0, fp=0, tn=0, fn=0),
             "pre": dict(tp=0, fp=0, tn=0, fn=0),
             "post": dict(tp=0, fp=0, tn=0, fn=0)}
    calib = defaultdict(lambda: defaultdict(list))
    acc_raw = defaultdict(lambda: defaultdict(list))

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

        b = t.get("binary")
        if b and not b.get("skipped") and "correct" in b:
            for p in parts:
                cmats[p]["tp" if b["correct"] else "fn"] += 1
            if b.get("confidence") is not None:
                for p in parts:
                    calib["binary"][p].append((float(b["confidence"]), 1.0 if b["correct"] else 0.0))
            for p in parts:
                acc_raw["binary"][p].append(1 if b["correct"] else 0)

        bp = t.get("binary_perturbed")
        if bp and not bp.get("skipped") and "correct" in bp:
            for p in parts:
                cmats[p]["tn" if bp["correct"] else "fp"] += 1
            if bp.get("confidence") is not None:
                for p in parts:
                    calib["binary_perturbed"][p].append(
                        (float(bp["confidence"]), 1.0 if bp["correct"] else 0.0))
            for p in parts:
                acc_raw["binary_perturbed"][p].append(1 if bp["correct"] else 0)

        m = t.get("mcq")
        if m and not m.get("skipped") and m.get("confidence") is not None:
            for p in parts:
                calib["mcq"][p].append((float(m["confidence"]), 1.0 if m["correct"] else 0.0))

        d = t.get("date")
        if d and not d.get("skipped") and d.get("confidence") is not None:
            md = d.get("month_distance")
            if md is not None:
                for p in parts:
                    calib["date"][p].append((float(d["confidence"]), 1.0 if md <= 12 else 0.0))

    out = {"cutoff": cutoff, "partition_rule": rule, "binary_extended": {}, "calibration": {}}
    for p in ("all", "pre", "post"):
        c = cmats[p]
        mm = _binary_metrics(c["tp"], c["fp"], c["tn"], c["fn"])
        ba = acc_raw["binary"][p]
        bpa = acc_raw["binary_perturbed"][p]
        mm["binary_acc"] = sum(ba) / len(ba) if ba else float("nan")
        mm["perturbed_acc"] = sum(bpa) / len(bpa) if bpa else float("nan")
        mm["bias_index"] = mm["binary_acc"] - mm["perturbed_acc"]
        mm["merged_binary"] = ((sum(ba) + sum(bpa)) / (len(ba) + len(bpa))
                               if (ba or bpa) else float("nan"))
        mm["confusion"] = c
        out["binary_extended"][p] = mm
    for task in ("binary", "binary_perturbed", "mcq", "date"):
        out["calibration"][task] = {
            p: {"n": len(calib[task][p]), "ece": ece(calib[task][p]),
                "brier": brier(calib[task][p]), "gap": gap(calib[task][p])}
            for p in ("all", "pre", "post")}
    return out


def fmt(v, dp=3):
    return "---" if (isinstance(v, float) and math.isnan(v)) else f"{v:.{dp}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="run_evaluation/frq_results")
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--extra", action="append", default=[],
                    help="'Name=YYYY-MM=path/to/report.json'")
    ap.add_argument("--rule", choices=["main", "gap"], default="main",
                    help="main: cutoff month counts as POST (make_latex_tables.py). "
                         "gap: cutoff month counts as PRE (filter_ids_by_cutoff).")
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
            print(f"  SKIP extra {n} ({p} not found)", file=sys.stderr)

    report = {"partition_rule": a.rule, "models": {}}
    for n, c, p in models:
        report["models"][n] = analyse(p, c, pub, a.rule)

    print(f"=== S13 binary extended metrics (partition rule: {a.rule}) ===")
    print(f"{'model':14s}{'part':>6s}{'n':>7s}{'bias':>8s}{'bal_acc':>9s}{'prec':>7s}"
          f"{'recall':>8s}{'spec':>7s}{'F1_yes':>8s}{'F1_no':>7s}{'macroF1':>9s}{'MCC':>8s}")
    for n, c, _ in models:
        for p in ("all", "pre", "post"):
            m = report["models"][n]["binary_extended"][p]
            nn = m["n"]
            if not nn or (isinstance(nn, float) and math.isnan(nn)):
                continue
            print(f"{n if p=='all' else '':14s}{p:>6s}{int(nn):7d}{fmt(m['bias_index']):>8s}"
                  f"{fmt(m['balanced_acc']):>9s}{fmt(m['precision']):>7s}{fmt(m['recall']):>8s}"
                  f"{fmt(m['specificity']):>7s}{fmt(m['f1_yes']):>8s}{fmt(m['f1_no']):>7s}"
                  f"{fmt(m['macro_f1']):>9s}{fmt(m['mcc']):>8s}")

    print(f"\n=== S14 calibration: ECE / Brier / confidence gap ===")
    print(f"{'model':14s}{'part':>6s}" + "".join(f"{t:>26s}" for t in
          ("binary", "binary_perturbed", "mcq", "date")))
    print(f"{'':20s}" + "".join(f"{'ECE':>8s}{'Brier':>9s}{'Gap':>9s}" for _ in range(4)))
    for n, c, _ in models:
        for p in ("all", "pre", "post"):
            cells = report["models"][n]["calibration"]
            if all(cells[t][p]["n"] == 0 for t in ("binary", "mcq", "date")):
                continue
            row = f"{n if p=='all' else '':14s}{p:>6s}"
            for t in ("binary", "binary_perturbed", "mcq", "date"):
                d = cells[t][p]
                row += f"{fmt(d['ece']):>8s}{fmt(d['brier']):>9s}{fmt(d['gap']):>9s}"
            print(row)

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(report, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
