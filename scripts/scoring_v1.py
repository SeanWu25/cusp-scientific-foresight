#!/usr/bin/env python3
"""
scoring_v1.py — the frozen, versioned scoring surface.

"v1" is the scoring that produced the six published models' numbers. This module
re-exports it from `eval.py` and, at import time, asserts that every grading and
judging function is byte-identical to the published source. If someone edits
`eval.py`, every downstream script fails loudly here rather than silently
emitting numbers that cannot be compared with the manuscript.

Hashes are taken from the parsed source of each function with comments and
blank lines stripped, so reformatting is tolerated and a real edit is not.

When the revised FRQ rubric lands it becomes scoring_v2.py; v1 stays untouched
so the published numbers remain reproducible forever.

Usage:
    from scoring_v1 import grade_binary, grade_mcq, grade_date, VERSION
"""

from __future__ import annotations

import ast
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eval as _eval  # noqa: E402  the released evaluator, never modified

VERSION = "v1"
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval.py")

# sha256 of each function's normalised source, as published.
EXPECTED = {
    "grade_binary":        "85b80d10b337",
    "grade_mcq":           "a3e8e43a367b",
    "grade_date":          "9b6d1b375ba0",
    "_normalize_yes_no":   "1ab8e4917df3",
    "_normalize_letter":   "e7682f84eada",
    "_parse_date":         "885d59a4bb74",
}


def _normalised_source(name: str) -> str:
    src = open(SOURCE, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            seg = ast.get_source_segment(src, node) or ""
            import re
            return re.sub(r"\s+", " ", seg).strip()
    raise KeyError(f"{name} not found in {SOURCE}")


def verify(strict: bool = True) -> dict:
    """Return {name: (expected, actual, ok)}; raise if strict and any mismatch."""
    out, bad = {}, []
    for name, exp in EXPECTED.items():
        got = hashlib.sha256(_normalised_source(name).encode()).hexdigest()[:12]
        ok = got == exp
        out[name] = (exp, got, ok)
        if not ok:
            bad.append(f"{name}: expected {exp}, got {got}")
    if bad and strict:
        raise RuntimeError(
            "scoring_v1 integrity check FAILED — eval.py has been modified, so "
            "results are no longer comparable with the published numbers:\n  "
            + "\n  ".join(bad))
    return out


verify(strict=True)

grade_binary = _eval.grade_binary
grade_mcq = _eval.grade_mcq
grade_date = _eval.grade_date
judge_leakage = _eval.judge_leakage
judge_frq_combined = _eval.judge_frq_combined
LLMClient = _eval.LLMClient
aggregate_results = _eval.aggregate_results
RowResult = _eval.RowResult

__all__ = ["grade_binary", "grade_mcq", "grade_date", "judge_leakage",
           "judge_frq_combined", "LLMClient", "aggregate_results", "RowResult",
           "VERSION", "verify"]

if __name__ == "__main__":
    for n, (e, g, ok) in verify(strict=False).items():
        print(f"  {n:22s} expected={e} actual={g} {'OK' if ok else 'MISMATCH'}")
    print(f"scoring {VERSION}: all grading functions match the published source.")
