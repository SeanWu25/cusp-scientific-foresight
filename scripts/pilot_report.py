#!/usr/bin/env python3
"""
pilot_report.py — Step-2 pilot diagnostics for a run_cusp.py predictions file.

Reports, without scoring anything as wrong that merely failed to parse:
  * per-task parse outcome (json / fallback / error) and parse-failure rate
  * date-format conformance to YYYY-MM
  * refusal and empty-response rates
  * retry counts, truncation, token usage and measured cost
  * closed-form accuracy split pre/post cutoff under BOTH partition conventions
"""

from __future__ import annotations

import argparse, collections, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval import grade_binary, grade_mcq, grade_date  # noqa: E402

TASKS = ["binary", "binary_perturbed", "mcq", "date"]
YYYYMM = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
PRICE_IN, PRICE_OUT = 2.00 / 1e6, 10.00 / 1e6     # Claude Sonnet 5 $/token


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - m), min(1.0, c + m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--benchmark", default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--cutoff", default="2026-01")
    a = ap.parse_args()

    bench = {json.loads(l)["id"]: json.loads(l)
             for l in open(a.benchmark, encoding="utf-8") if l.strip()}
    preds = [json.loads(l) for l in open(a.predictions, encoding="utf-8") if l.strip()]
    print(f"predictions : {a.predictions}")
    print(f"events      : {len(preds)}   fatal row errors: "
          f"{sum(1 for p in preds if p.get('fatal_error'))}")
    eff = {p.get("effort") for p in preds}
    print(f"effort      : {eff}   frq_max_tokens: {{{', '.join(str(p.get('frq_max_tokens')) for p in preds[:1])}}}")

    # ---------- parse outcomes, refusals, retries ----------
    print(f"\n{'task':18s}{'n':>6s}{'json':>7s}{'fallback':>10s}{'error':>7s}"
          f"{'parse_fail%':>12s}{'refusal':>9s}{'empty':>7s}{'retries>0':>11s}")
    for t in TASKS + ["frq"]:
        recs = [p for p in preds if f"{t}_raw" in p]
        if not recs:
            continue
        pm = collections.Counter(p.get(f"{t}_parse_method", "n/a") for p in recs)
        err = sum(1 for p in recs if p.get(f"{t}_error"))
        ref = sum(1 for p in recs if p.get(f"{t}_refusal"))
        emp = sum(1 for p in recs if not str(p.get(f"{t}_raw", "")).strip())
        rty = sum(1 for p in recs if (p.get(f"{t}_retries") or 0) > 0)
        fail = pm.get("fallback", 0) + pm.get("error", 0) + err
        print(f"{t:18s}{len(recs):6d}{pm.get('json',0):7d}{pm.get('fallback',0):10d}"
              f"{err:7d}{100*fail/len(recs):12.2f}{ref:9d}{emp:7d}{rty:11d}")

    # ---------- date format conformance ----------
    dr = [p for p in preds if "date_answer" in p]
    if dr:
        ok = sum(1 for p in dr if YYYYMM.match(str(p["date_answer"]).strip()))
        parsed = sum(1 for p in dr
                     if grade_date(str(p["date_answer"]), "2025-01")["parsed_date"])
        lo, hi = wilson(ok, len(dr))
        print(f"\ndate output conforms to YYYY-MM exactly : {ok}/{len(dr)} "
              f"({100*ok/len(dr):.2f}%, 95% CI {100*lo:.2f}-{100*hi:.2f})")
        print(f"date parseable by the scorer            : {parsed}/{len(dr)} "
              f"({100*parsed/len(dr):.2f}%)")
        bad = [str(p["date_answer"])[:70] for p in dr
               if not YYYYMM.match(str(p["date_answer"]).strip())][:5]
        if bad:
            print("  non-conforming examples:", bad)

    # ---------- FRQ truncation ----------
    fr = [p for p in preds if "frq_answer" in p]
    if fr:
        tr = sum(1 for p in fr if p.get("frq_truncated"))
        ch = [len(p["frq_answer"]) for p in fr]
        print(f"\nFRQ responses      : {len(fr)}   truncated at max_tokens: {tr} "
              f"({100*tr/len(fr):.1f}%)")
        print(f"FRQ chars          : mean={sum(ch)/len(ch):.0f} "
              f"median={sorted(ch)[len(ch)//2]} min={min(ch)} max={max(ch)}")

    # ---------- cost / usage ----------
    ti = sum(p.get(f"{t}_input_tokens") or 0 for p in preds for t in TASKS + ["frq"])
    to = sum(p.get(f"{t}_output_tokens") or 0 for p in preds for t in TASKS + ["frq"])
    calls = sum(1 for p in preds for t in TASKS + ["frq"] if f"{t}_raw" in p)
    cost = ti * PRICE_IN + to * PRICE_OUT
    print(f"\ncalls={calls}  input_tokens={ti}  output_tokens={to}")
    print(f"measured cost ${cost:.4f}  =>  ${cost/max(calls,1):.6f} per task instance")

    # ---------- accuracy, both partition conventions ----------
    def bucket(pub, conv):
        return ("pre" if pub < a.cutoff else "post") if conv == "main" \
            else ("pre" if pub <= a.cutoff else "post")

    for conv, label in (("main", "main-table rule (cutoff month = POST)"),
                        ("gap", "gap/inference rule (cutoff month = PRE)")):
        print(f"\n--- {label}  (API refusals excluded from denominators) ---")
        print(f"{'task':18s}{'part':>6s}{'n':>6s}{'correct':>9s}{'acc':>8s}{'95% CI':>18s}")
        for t in TASKS:
            for part in ("pre", "post"):
                vals = []
                for p in preds:
                    if f"{t}_answer" not in p:
                        continue
                    if p.get(f"{t}_refusal"):
                        continue   # API-level refusal: not an answer, never scored wrong
                    row = bench.get(p["id"])
                    if not row or bucket(p["publication_date"], conv) != part:
                        continue
                    if t == "binary":
                        vals.append(grade_binary(p[f"{t}_answer"],
                                                 row.get("binary_ground_truth", "Yes"))["correct"])
                    elif t == "binary_perturbed":
                        vals.append(grade_binary(p[f"{t}_answer"], "No")["correct"])
                    elif t == "mcq":
                        vals.append(grade_mcq(p["mcq_answer"], p["mcq_shuffled_answer_key"],
                                              choices=list(p["mcq_shuffled_choices"].values()))["correct"])
                    else:
                        vals.append(grade_date(p["date_answer"], row["ground_truth_date"])["score"])
                if not vals:
                    continue
                n = len(vals)
                if t == "date":
                    m = sum(vals) / n
                    print(f"{t:18s}{part:>6s}{n:6d}{'':>9s}{m:8.3f}{'(mean score)':>18s}")
                else:
                    k = sum(vals)
                    lo, hi = wilson(k, n)
                    print(f"{t:18s}{part:>6s}{n:6d}{k:9d}{k/n:8.3f}"
                          f"{f'[{lo:.3f}, {hi:.3f}]':>18s}")
        # merged binary, pooled, as the published tables compute it
        for part in ("pre", "post"):
            kk = nn = 0
            for t, gt in (("binary", None), ("binary_perturbed", "No")):
                for p in preds:
                    if f"{t}_answer" not in p or p.get(f"{t}_refusal"):
                        continue
                    row = bench.get(p["id"])
                    if not row or bucket(p["publication_date"], conv) != part:
                        continue
                    truth = gt or row.get("binary_ground_truth", "Yes")
                    kk += grade_binary(p[f"{t}_answer"], truth)["correct"]; nn += 1
            if nn:
                lo, hi = wilson(kk, nn)
                print(f"{'merged binary':18s}{part:>6s}{nn:6d}{kk:9d}{kk/nn:8.3f}"
                      f"{f'[{lo:.3f}, {hi:.3f}]':>18s}")


if __name__ == "__main__":
    main()
