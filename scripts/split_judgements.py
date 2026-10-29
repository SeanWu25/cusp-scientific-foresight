#!/usr/bin/env python3
"""
split_judgements.py — separate stage-1 leakage verdicts (reportable) from
stage-2 quality-rubric scores (archived, not reportable).

The FRQ rubric is under revision, so stage-2 scores produced with the current
rubric must not reach any table. They are still archived: re-running the judge
months from now would not reproduce today's web-search evidence, so the run is
worth keeping even though the numbers are superseded.
"""
from __future__ import annotations
import argparse, json, os

LEGACY_DIRNAME = "frq_scores_LEGACY_RUBRIC_DO_NOT_CITE"
BANNER = {
    "_WARNING": "DO NOT CITE. Produced with the pre-revision FRQ rubric.",
    "_why": "The 4-dimension rubric (alignment/specificity/novelty/feasibility) "
            "is being revised in response to reviewers. These scores are archived "
            "only because re-running the judge later would not reproduce the "
            "web-search evidence it used today.",
    "_reportable_instead": "stage-1 leakage verdicts, and FRQ generation "
                           "diagnostics (count, chars, truncation, refusals).",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judged", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()

    legacy_dir = os.path.join(a.outdir, LEGACY_DIRNAME)
    os.makedirs(legacy_dir, exist_ok=True)
    os.makedirs(a.outdir, exist_ok=True)
    base = os.path.basename(a.judged).replace(".jsonl", "")

    leak_path = os.path.join(a.outdir, f"{base}.leakage.jsonl")
    rub_path = os.path.join(legacy_dir, f"{base}.legacy_rubric.jsonl")
    n_l = n_r = 0
    with open(leak_path, "w", encoding="utf-8") as lf, \
         open(rub_path, "w", encoding="utf-8") as rf:
        for line in open(a.judged, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("leakage"):
                lf.write(json.dumps({"id": r["id"],
                                     "publication_date": r.get("publication_date"),
                                     "leakage": r["leakage"],
                                     "leakage_attempts": r.get("leakage_attempts"),
                                     "leakage_judge_s": r.get("leakage_judge_s")},
                                    ensure_ascii=False) + "\n")
                n_l += 1
            if r.get("frq"):
                rf.write(json.dumps({**BANNER, "id": r["id"],
                                     "publication_date": r.get("publication_date"),
                                     "frq_legacy_rubric": r["frq"],
                                     "frq_attempts": r.get("frq_attempts")},
                                    ensure_ascii=False) + "\n")
                n_r += 1
    with open(os.path.join(legacy_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write("# DO NOT CITE\n\n"
                "Stage-2 FRQ quality scores from the **pre-revision** rubric.\n\n"
                f"{BANNER['_why']}\n\n"
                "Nothing in this directory is read by any table generator. "
                "`build_report.py` defaults to `--frq-scores exclude`.\n")
    print(f"stage-1 leakage  -> {leak_path}  ({n_l} records)")
    print(f"stage-2 legacy   -> {rub_path}  ({n_r} records)  [archived, not reportable]")


if __name__ == "__main__":
    main()
