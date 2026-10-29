#!/usr/bin/env python3
"""
verify_binary_answers_unchanged.py — prove finalize touched only FRQ/leakage.

Study A2 (results/A2_binary_validity, Reviewer 2 concern C2) reads the panel's
stored binary and binary_perturbed answers from the same report JSONs that
finalize_run2.sh rewrites. Its MANIFEST pins per-model answer counts under
panel_answer_counts. Rebuilding reports with rubric scores and leakage verdicts
joined in must leave those counts identical -- binary answers are deterministic
from the raw predictions and nothing in the join path reads them.

This reuses A2's own loader (results/A2_binary_validity/scripts/common.py)
rather than reimplementing its filter, so the comparison is exact: a record
counts only if tasks[task] exists, skipped is not truthy, refused is not
truthy, and "correct" is present; each model pools its original-corpus and
extension reports; DeepSeek R1 has no extension file. Read-only, no API calls.

Exit 0 on MATCH. Exit 1 on any difference, printing the per-model (pinned,
now) pairs -- in which case A2's corrected-accuracy table needs regenerating:
    bash results/A2_binary_validity/scripts/run_all.sh analyse
and the A2 session should be told.
"""

from __future__ import annotations

import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A2 = os.path.join(ROOT, "results", "A2_binary_validity")


def main() -> int:
    sys.path.insert(0, os.path.join(A2, "scripts"))
    try:
        import common as C  # A2's loader; owns the filter rule and report paths
    except ImportError as e:
        # to stdout on purpose: this must land in the finalize log body, not be
        # lost on stderr, because a skip is NOT a pass -- nothing was verified
        print(f"SKIPPED -- binary answers NOT verified: cannot import A2 loader ({e}); "
              f"results/A2_binary_validity is untracked and absent on this machine")
        return 0

    ref_path = os.path.join(A2, "MANIFEST.json")
    if not os.path.exists(ref_path):
        print("SKIPPED -- binary answers NOT verified: no results/A2_binary_validity/MANIFEST.json")
        return 0
    ref = json.load(open(ref_path, encoding="utf-8"))["panel_answer_counts"]

    c = Counter((k[0], k[2]) for k in C.load_panel_answers())
    now = {m: {"binary": c[(m, "binary")], "binary_perturbed": c[(m, "binary_perturbed")]}
           for m in C.MODEL_ORDER}

    diffs = {m: (ref[m], now.get(m)) for m in ref if ref[m] != now.get(m)}
    extra = sorted(set(now) - set(ref))
    if not diffs and not extra:
        print(f"MATCH: binary/binary_perturbed answer counts identical to A2 MANIFEST "
              f"for all {len(ref)} models")
        return 0
    print("MISMATCH against A2 MANIFEST panel_answer_counts:")
    for m, (r, n) in diffs.items():
        print(f"  {m}: pinned {r} now {n}")
    if extra:
        print(f"  models present now but not pinned: {extra}")
    print("A2 needs: bash results/A2_binary_validity/scripts/run_all.sh analyse  "
          "(no API calls) -- and tell the A2 session.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
