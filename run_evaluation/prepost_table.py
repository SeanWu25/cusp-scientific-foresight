#!/usr/bin/env python3
"""
prepost_table.py — pre- vs post-cutoff performance on the ENTIRE dataset.

Original corpus (Jan 2024-Mar 2026) + extension (Apr-Aug 2026), 5,575 events,
pooled at the report level. Partition rule "main": an event published in the
cutoff month counts as POST (matches make_latex_tables.py).

Per task, per model: pre value [95% CI] n | post value [95% CI] n | post-pre |
retrospective-ceiling ratio (post/pre). Binary is BALANCED ACCURACY (bias-
corrected merged binary) -- raw merged accuracy is confounded by class balance
x response bias and its pre/post ratio would mislead. Raw merged accuracy is
still emitted to JSON for reference. FRQ is the published-rubric mean score
(0-10) and is included now that every model is graded.

Reads finalized reports only. No inference.
"""
from __future__ import annotations
import argparse, json, math, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from full_corpus_tables import PANEL, mo, wilson, norm_ci, load_dates  # noqa: E402


def collect(name, cutoff, paths, pub, rule="main"):
    cm = mo(cutoff)
    acc = {p: defaultdict(list) for p in ("pre", "post")}
    cm4 = {p: dict(tp=0, fp=0, tn=0, fn=0) for p in ("pre", "post")}
    seen = set()
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        for x in json.load(open(path, encoding="utf-8")).get("results", []):
            rid = x.get("id")
            if rid in seen:
                continue
            seen.add(rid)
            pm = mo(pub.get(rid, ""))
            if pm is None or cm is None:
                continue
            part = ("pre" if pm < cm else "post") if rule == "main" else ("pre" if pm <= cm else "post")
            t = x.get("tasks") or {}
            b, bp, m, d, f = t.get("binary"), t.get("binary_perturbed"), t.get("mcq"), t.get("date"), t.get("frq")
            if b and not b.get("skipped") and "correct" in b:
                cm4[part]["tp" if b["correct"] else "fn"] += 1
                acc[part]["merged"].append(1.0 if b["correct"] else 0.0)
            if bp and not bp.get("skipped") and "correct" in bp:
                cm4[part]["tn" if bp["correct"] else "fp"] += 1
                acc[part]["merged"].append(1.0 if bp["correct"] else 0.0)
            if m and not m.get("skipped") and "correct" in m:
                acc[part]["mcq"].append(1.0 if m["correct"] else 0.0)
            if d and not d.get("skipped") and d.get("score") is not None:
                acc[part]["date"].append(float(d["score"]))
            if f and not f.get("skipped") and f.get("score") is not None:
                acc[part]["frq"].append(float(f["score"]))
            acc[part]["_events"].append(1)
    return acc, cm4


def bal_acc(c):
    """balanced accuracy and a bootstrap-free CI via the two Wilson halves (conservative)."""
    nb, nn = c["tp"] + c["fn"], c["tn"] + c["fp"]
    if not nb or not nn:
        return None
    rec, spec = c["tp"] / nb, c["tn"] / nn
    lo1, hi1 = wilson(c["tp"], nb); lo2, hi2 = wilson(c["tn"], nn)
    return (0.5 * (rec + spec), 0.5 * (lo1 + lo2), 0.5 * (hi1 + hi2), nb + nn)


def prop(vals):
    n = len(vals)
    if not n:
        return None
    k = int(round(sum(vals))); lo, hi = wilson(k, n)
    return (k / n, lo, hi, n)


def mean(vals):
    n = len(vals)
    if not n:
        return None
    lo, hi = norm_ci(vals) if n > 1 else (float("nan"),) * 2
    return (sum(vals) / n, lo, hi, n)


def cell(v, dec=3):
    if v is None:
        return "—"
    m, lo, hi, n = v
    return f"{m:.{dec}f} [{lo:.{dec}f}, {hi:.{dec}f}] n={n:,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", choices=["main", "gap"], default="main")
    ap.add_argument("--out-md", default="results_extension_run2/tables/09_prepost_full_corpus.md")
    ap.add_argument("--out-json", default="results_extension_run2/tables/09_prepost_full_corpus.json")
    ap.add_argument("--exclude", default="", help="comma-separated model names to drop (e.g. DeepSeek-V4-Pro)")
    a = ap.parse_args()
    excl = {x.strip() for x in a.exclude.split(",") if x.strip()}
    panel = [p for p in PANEL if p[0] not in excl]
    pub = load_dates(["archive/data/canonical/merged_validated_cusp_fixed.jsonl",
                      "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"])

    TASKS = [("binary", "Binary (balanced accuracy, bias-corrected)", 3),
             ("mcq", "MCQ accuracy", 3), ("frq", "FRQ mean score (0–10, published rubric)", 2),
             ("date", "Date score", 3)]
    md = ["# Pre- vs post-cutoff performance on the entire dataset\n",
          "Original + extension, 5,575 events (DeepSeek-R1: original only, 4,760). Partition rule: "
          f"`{a.rule}` — an event published in the cutoff month counts as {'POST' if a.rule=='main' else 'PRE'}. "
          "GPT-4o and LLaMA 3.3 have cutoffs before the corpus starts, so they have no pre-cutoff rows. "
          + ("DeepSeek-V4-Pro (cutoff 2026-04) is the inverse profile: under this rule its 4,760 original-corpus "
          "events are all pre-cutoff and the 815 extension events (April included) are post; §2 of "
          "RUN2_RESULTS.md reports it May–Aug only, and the April choice moves MCC by 0.003.\n"
             if "DeepSeek-V4-Pro" not in excl else
             f"Models excluded: {', '.join(sorted(excl))}.\n"),
          "Binary is **balanced accuracy** (mean of recall on the real question and specificity on the perturbed "
          "twin): raw merged accuracy is confounded by class balance × response bias, and its pre/post ratio "
          "would mislead. FRQ is the published-rubric mean; every model is graded. Refusals excluded. "
          "Ratio = post / pre (the retrospective ceiling); a ratio near 1 means the task does not distinguish "
          "seen from unseen material.\n"]
    out = {}
    for key, title, dec in TASKS:
        md.append(f"\n## {title}\n")
        md.append("| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |\n|---|---|---|---|---|---|")
        for name, cutoff, op, ep in panel:
            acc, cm4 = collect(name, cutoff, [op, ep], pub, a.rule)
            if key == "binary":
                pre, post = bal_acc(cm4["pre"]), bal_acc(cm4["post"])
            elif key == "mcq":
                pre, post = prop(acc["pre"]["mcq"]), prop(acc["post"]["mcq"])
            else:
                pre, post = mean(acc["pre"][key]), mean(acc["post"][key])
            delta = f"{post[0]-pre[0]:+.{dec}f}" if pre and post else "—"
            ratio = f"{post[0]/pre[0]:.3f}" if pre and post and pre[0] else "—"
            md.append(f"| {name} | {cutoff} | {cell(pre, dec)} | {cell(post, dec)} | {delta} | {ratio} |")
            o = out.setdefault(name, {"cutoff": cutoff})
            o[key] = {"pre": pre, "post": post,
                      "raw_merged_pre": prop(acc["pre"]["merged"]) if key == "binary" else None,
                      "raw_merged_post": prop(acc["post"]["merged"]) if key == "binary" else None}
            if key == "binary":
                o["n_events_pre"] = len(acc["pre"]["_events"]); o["n_events_post"] = len(acc["post"]["_events"])
    md.append("\nCIs: Wilson for proportions (balanced-accuracy CI is the mean of the two Wilson halves, "
              "conservative), normal approximation for means. Pre-cutoff rows are retrospective: the model "
              "may have seen the paper in training.\n")
    open(a.out_md, "w", encoding="utf-8").write("\n".join(md) + "\n")
    json.dump(out, open(a.out_json, "w", encoding="utf-8"), indent=2)
    print("\n".join(md)); print(f"\nwrote {a.out_md}\nwrote {a.out_json}")


if __name__ == "__main__":
    main()
