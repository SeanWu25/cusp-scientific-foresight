#!/usr/bin/env python3
"""
build_report.py — turn a run_cusp.py predictions file (+ its judged FRQ file)
into the same report JSON that eval.py emits, so every existing analysis script
reads Sonnet 5 exactly as it reads the six published models.

Scoring is done by eval.py's own graders, imported verbatim. Nothing here
re-implements a metric.

The one deliberate departure, applied only where it is true: an instance the
API refused (stop_reason="refusal") is NOT an answer. It is recorded with
`"refused": true` and excluded from every denominator, rather than being scored
as a wrong answer. Refusal counts are reported per task and per research area so
the exclusion is visible, never silent.
"""

from __future__ import annotations

import argparse, collections, json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval import grade_binary, grade_mcq, grade_date, aggregate_results, RowResult  # noqa: E402

TASKS = ("binary", "binary_perturbed", "mcq", "frq", "date")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--judged", default=None, help="judge_frq.py output JSONL")
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--score-refusals-as-wrong", action="store_true",
                    help="Diagnostic only: count refusals as incorrect, to quantify "
                         "how much the exclusion decision moves each metric.")
    a = ap.parse_args()

    bench = {}
    for l in open(a.benchmark, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            bench[r["id"]] = r

    judged = {}
    if a.judged and os.path.exists(a.judged):
        for l in open(a.judged, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                judged[r["id"]] = r

    preds = [json.loads(l) for l in open(a.predictions, encoding="utf-8") if l.strip()]
    results, refusals, areas = [], collections.Counter(), collections.defaultdict(collections.Counter)
    parse_fallback = collections.Counter()

    for p in preds:
        rid = p.get("id")
        row = bench.get(rid)
        if row is None:
            continue
        rr = RowResult(id=rid, available_tasks=[])
        found = False
        for t in TASKS:
            if f"{t}_raw" not in p:
                continue
            rr.available_tasks.append(t)
            area = p.get("main_area") or row.get("main_area", "Unknown")
            areas[area]["calls"] += 1
            refused = bool(p.get(f"{t}_refusal"))
            if refused:
                refusals[t] += 1
                areas[area]["refused"] += 1
                if not a.score_refusals_as_wrong:
                    rr.tasks[t] = {"skipped": True, "refused": True,
                                   "reason": "API refusal",
                                   "refusal_category": p.get(f"{t}_refusal_category")}
                    continue
            if p.get(f"{t}_parse_method") == "fallback" and not refused:
                parse_fallback[t] += 1
            found = True
            if t == "binary":
                g = grade_binary(p.get("binary_answer", ""),
                                 row.get("binary_ground_truth", "Yes"))
            elif t == "binary_perturbed":
                g = grade_binary(p.get("binary_perturbed_answer", ""), "No")
            elif t == "mcq":
                g = grade_mcq(p.get("mcq_answer", ""), p.get("mcq_shuffled_answer_key"),
                              choices=list((p.get("mcq_shuffled_choices") or {}).values()))
            elif t == "date":
                g = grade_date(p.get("date_answer", ""), row.get("ground_truth_date", ""))
            else:  # frq
                j = (judged.get(rid) or {}).get("frq") or {}
                g = {"score": j.get("frq_score"), "alignment": j.get("alignment"),
                     "specificity": j.get("specificity"), "novelty": j.get("novelty"),
                     "feasibility": j.get("feasibility"),
                     "rationale": j.get("frq_rationale", ""),
                     "urls": j.get("urls", []),
                     "web_search_used": j.get("web_search_used", False)}
            c = p.get(f"{t}_confidence")
            if c is not None and t != "frq":
                g["confidence"] = c
            if refused:
                g["refused"] = True
            rr.tasks[t] = g
        rr.prediction_found = found

        lk = (judged.get(rid) or {}).get("leakage")
        rr.reasoning["leakage"] = (
            {"verdict": lk["verdict"], "score": lk["score"], "reason": lk["reason"],
             "details": {"leakage_indicators": lk.get("indicators", [])}}
            if lk else {"verdict": "unclear", "score": 0.5,
                        "reason": "not judged", "details": {}})
        for nm in ("mechanistic", "constraint"):
            rr.reasoning[nm] = {"verdict": "unclear", "score": 0.5,
                                "reason": "not judged", "details": {}}

        outcome = [v.get("score") for k, v in rr.tasks.items()
                   if not v.get("skipped") and v.get("score") is not None]
        outcome = [s / 10.0 if k == "frq" else s
                   for k, v in rr.tasks.items() if not v.get("skipped")
                   and v.get("score") is not None
                   for s in [v["score"]]]
        passes = []
        for k, v in rr.tasks.items():
            if v.get("skipped"):
                continue
            if k == "frq" and v.get("score") is not None:
                passes.append(v["score"] >= 5.0)
            elif k == "date":
                passes.append(bool(v.get("exact_match")))
            elif "correct" in v:
                passes.append(bool(v["correct"]))
        rr.outcome_pass = any(passes) if passes else False
        rr.reasoning_pass = rr.reasoning["leakage"]["verdict"] != "fail"
        rr.joint_pass = rr.outcome_pass and rr.reasoning_pass
        rr.overall_score = round(0.6 * (sum(outcome) / len(outcome) if outcome else 0.0)
                                 + 0.4 * 0.5, 4)
        results.append(rr)

    report = aggregate_results(results, list(bench.values()))
    report["run_metadata"] = {
        "built_utc": datetime.now(timezone.utc).isoformat(),
        "predictions": a.predictions, "judged": a.judged,
        "model": preds[0].get("model") if preds else None,
        "condition": preds[0].get("condition") if preds else None,
        "run_index": preds[0].get("run_index") if preds else None,
        "effort": preds[0].get("effort") if preds else None,
        "frq_max_tokens": preds[0].get("frq_max_tokens") if preds else None,
        "refusals_excluded_from_denominators": not a.score_refusals_as_wrong,
    }
    report["refusals"] = {
        "per_task": dict(refusals),
        "total": sum(refusals.values()),
        "per_area": {k: dict(v) for k, v in sorted(areas.items())},
    }
    report["parse_fallbacks_excluding_refusals"] = dict(parse_fallback)
    report["errors"] = []

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    json.dump(report, open(a.out, "w", encoding="utf-8"), indent=1)

    tm = report["task_metrics"]
    print(f"wrote {a.out}   rows={len(results)}")
    print(f"refusals: {sum(refusals.values())} {dict(refusals)}")
    print(f"genuine parse fallbacks (non-refusal): {dict(parse_fallback)}")
    for t in ("binary", "binary_perturbed", "mcq"):
        if t in tm:
            print(f"  {t:18s} n={tm[t]['count']:5d} acc={tm[t]['accuracy']:.4f}")
    if "frq" in tm:
        print(f"  {'frq':18s} n={tm['frq']['scored']:5d} mean={tm['frq']['mean_score']:.4f} "
              f"pass={tm['frq']['pass_rate']:.4f}")
    if "date" in tm:
        print(f"  {'date':18s} n={tm['date']['count']:5d} score={tm['date']['mean_score']:.4f}")


if __name__ == "__main__":
    main()
