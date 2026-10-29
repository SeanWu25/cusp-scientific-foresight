#!/usr/bin/env python3
"""
merge_runs.py — pool run 1 (Jan 2024 - Mar 2026) with run 2 (Apr - Aug 2026)
and recompute every table over the union.

The merge is refused unless the two runs agree on everything RUN2_CONTRACT.md
freezes. That check is the point of this script: silently pooling numbers
produced under different prompts, a different judge, or different decoding
parameters is exactly the failure it exists to prevent.

  python scripts/merge_runs.py \
      --run1-manifest results_sonnet5_run1/MANIFEST.json \
      --run2-manifest results_sonnet5_run2/MANIFEST.json \
      --run1 'results_sonnet5_run1/raw/*.jsonl' \
      --run2 'results_sonnet5_run2/raw/*.jsonl' \
      --out  results_sonnet5_merged/
"""

from __future__ import annotations

import argparse, glob, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone

# (dotted manifest path, human label, hard?) — hard failures cannot be waived
# without naming the field explicitly in --allow-mismatch.
CONTRACT = [
    ("prompt_templates",                 "prompt template hashes",       True),
    ("judge_rubrics",                    "judge rubric hashes",          True),
    ("code_sha256.scripts/eval.py",      "scoring code sha256",          True),
    ("judge.judge_model",                "judge model id",               True),
    ("judge.endpoint_host",              "judge serving stack",          True),
    ("judge.api_surface",                "judge API surface",            True),
    ("model_under_test.model_id",        "model under test",             True),
    ("model_under_test.api_probe.api_reported_model",
                                         "model snapshot echoed by API", True),
    ("model_under_test.knowledge_cutoff","knowledge cutoff",             True),
    ("decoding.effort",                  "reasoning effort",             True),
    ("decoding.temperature",             "temperature",                  True),
    ("decoding.top_p",                   "top_p",                        True),
    ("decoding.max_tokens",              "max_tokens",                   True),
    ("decoding.frq_max_tokens",          "FRQ max_tokens",               True),
    ("partition_rule",                   "pre/post partition rule",      True),
    ("scoring_constants",                "scoring constants",            True),
    ("code_sha256.scripts/run_cusp.py",  "runner sha256",                False),
    ("code_sha256.scripts/test_LLM.py",  "prompt module sha256",         False),
]


def dig(obj, path):
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return "<missing>"
        obj = obj[part]
    return obj


def check_contract(m1, m2, allow):
    hard, soft = [], []
    for path, label, is_hard in CONTRACT:
        a, b = dig(m1, path), dig(m2, path)
        if a != b:
            entry = {"field": path, "label": label, "run1": a, "run2": b}
            if path in allow:
                entry["waived"] = True
                soft.append(entry)
            elif is_hard:
                hard.append(entry)
            else:
                soft.append(entry)
    return hard, soft


def load_jsonl(patterns):
    recs, files = [], []
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            files.append(p)
            for l in open(p, encoding="utf-8"):
                if l.strip():
                    recs.append(json.loads(l))
    return recs, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run1-manifest", required=True)
    ap.add_argument("--run2-manifest", required=True)
    ap.add_argument("--run1", action="append", required=True)
    ap.add_argument("--run2", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-mismatch", action="append", default=[],
                    help="Waive one contract field by dotted path. The waiver is "
                         "stamped into the merged manifest.")
    ap.add_argument("--skip-tables", action="store_true")
    a = ap.parse_args()

    m1 = json.load(open(a.run1_manifest, encoding="utf-8"))
    m2 = json.load(open(a.run2_manifest, encoding="utf-8"))
    hard, soft = check_contract(m1, m2, set(a.allow_mismatch))

    print("=== RUN2_CONTRACT check ===")
    if not hard and not soft:
        print("  all contract fields match")
    for e in soft:
        print(f"  WAIVED/soft  {e['label']:32s} run1={e['run1']!r} run2={e['run2']!r}")
    for e in hard:
        print(f"  VIOLATION    {e['label']:32s} run1={e['run1']!r} run2={e['run2']!r}")
    if hard:
        print(f"\nABORTING: {len(hard)} contract violation(s). These runs are not "
              f"poolable. Re-run run 2 under the frozen configuration, or waive a "
              f"field explicitly with --allow-mismatch <dotted.path> if you have a "
              f"documented reason.", file=sys.stderr)
        sys.exit(2)

    r1, f1 = load_jsonl(a.run1)
    r2, f2 = load_jsonl(a.run2)
    print(f"\nrun1: {len(r1)} records from {len(f1)} file(s)")
    print(f"run2: {len(r2)} records from {len(f2)} file(s)")

    # event-id scheme: ids must not collide across runs within a condition/run index
    def key(r):
        return (r.get("id"), r.get("condition"), r.get("run_index"))
    k1, k2 = {key(r) for r in r1}, {key(r) for r in r2}
    dup = k1 & k2
    if dup:
        print(f"ABORTING: {len(dup)} (id, condition, run_index) collisions between "
              f"runs; the event-ID scheme is violated. Example: {sorted(dup)[:3]}",
              file=sys.stderr)
        sys.exit(2)

    os.makedirs(a.out, exist_ok=True)
    merged_path = os.path.join(a.out, "merged_predictions.jsonl")
    with open(merged_path, "w", encoding="utf-8") as f:
        for r in r1 + r2:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    sha = hashlib.sha256(open(merged_path, "rb").read()).hexdigest()
    print(f"\nwrote {merged_path}  ({len(r1)+len(r2)} records, sha256 {sha[:16]}...)")

    months = sorted({r.get("publication_date", "") for r in r1 + r2} - {""})
    merged_manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run1_manifest": a.run1_manifest,
        "run2_manifest": a.run2_manifest,
        "run1_records": len(r1), "run2_records": len(r2),
        "merged_sha256": sha,
        "corpus_window": f"{months[0]}..{months[-1]}" if months else None,
        "n_months": len(months),
        "contract": {"violations": hard, "waived_or_soft": soft,
                     "waived_fields": a.allow_mismatch},
        "frozen_from_run1": {p: dig(m1, p) for p, _, _ in CONTRACT},
    }
    mpath = os.path.join(a.out, "MERGED_MANIFEST.json")
    json.dump(merged_manifest, open(mpath, "w", encoding="utf-8"), indent=2)
    print(f"wrote {mpath}")

    if a.skip_tables:
        return
    print("\n=== recomputing tables over the union ===")
    for cmd in (
        ["run_evaluation/horizon_stratified.py", "--out",
         os.path.join(a.out, "horizon_stratified.json")],
        ["run_evaluation/binary_extended.py", "--out",
         os.path.join(a.out, "binary_extended.json")],
        ["run_evaluation/gap_decomposition.py", "--out",
         os.path.join(a.out, "gap_decomposition.json")],
    ):
        print(f"  $ python {' '.join(cmd)}")
        try:
            subprocess.run([sys.executable] + cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"    FAILED: {e}", file=sys.stderr)
    print("\nMerge complete. Nothing was re-run against an API.")


if __name__ == "__main__":
    main()
