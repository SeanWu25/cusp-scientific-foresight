#!/usr/bin/env python3
"""
postcutoff_panel.py — one row per model, POST-CUTOFF over the ENTIRE dataset.

Original (Jan 2024-Mar 2026) + extension (Apr-Aug 2026) pooled; for each model
only events published on/after its cutoff month (rule "main": the cutoff month
counts as post). All four tasks side by side with n and 95% CIs:

  binary   raw merged accuracy (for reference: confounded by class balance x
           response bias, see RUN2_RESULTS.md section 3), balanced accuracy
           (bias-corrected) and MCC over the merged binary items
  MCQ      accuracy
  FRQ      published-rubric mean score (0-10)
  date     mean exp(-0.1 |months off|)

Footnotes handle the three edge cases: models whose cutoff precedes the corpus
(post-cutoff == entire dataset), DeepSeek-V4-Pro's April overlap, and
DeepSeek-R1's missing extension.
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from full_corpus_tables import PANEL, mo, wilson, norm_ci, load_dates  # noqa: E402
from prepost_table import collect, bal_acc, prop, mean  # noqa: E402
from binary_extended import _binary_metrics  # noqa: E402

CORPUS_START = "2024-01"


def fmt(v, dec=3, ci=True):
    if v is None:
        return "—"
    m, lo, hi, n = v
    return f"{m:.{dec}f} [{lo:.{dec}f}, {hi:.{dec}f}]" if ci else f"{m:.{dec}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", choices=["main", "gap"], default="main")
    ap.add_argument("--out-md", default="results_extension_run2/tables/10_postcutoff_panel.md")
    ap.add_argument("--out-json", default="results_extension_run2/tables/10_postcutoff_panel.json")
    a = ap.parse_args()
    pub = load_dates(["archive/data/canonical/merged_validated_cusp_fixed.jsonl",
                      "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"])
    rows, out = [], {}
    for name, cutoff, op, ep in PANEL:
        if not any(p and os.path.exists(p) for p in (op, ep)):
            rows.append((name, cutoff, None)); continue
        acc, cm4 = collect(name, cutoff, [op, ep], pub, a.rule)
        c = cm4["post"]
        b = bal_acc(c)
        mcc = _binary_metrics(**c)["mcc"] if b else None
        r = {"binary": b, "mcc": mcc, "raw_merged": prop(acc["post"]["merged"]),
             "mcq": prop(acc["post"]["mcq"]),
             "frq": mean(acc["post"]["frq"]), "date": mean(acc["post"]["date"]),
             "n_events_post": len(acc["post"]["_events"]),
             "has_extension": bool(ep and os.path.exists(ep)),
             "all_post": mo(cutoff) <= mo(CORPUS_START)}
        rows.append((name, cutoff, r)); out[name] = {"cutoff": cutoff, **r}

    notes = {"all_post": "*", "no_ext": "†", "april": "‡"}
    md = ["# Post-cutoff performance on the entire dataset — one row per model\n",
          "Original + extension pooled; per model, only events published on/after its cutoff month "
          f"(rule `{a.rule}`). Binary: raw merged accuracy is shown for reference but is confounded by "
          "class balance × response bias (RUN2_RESULTS.md §3); **balanced accuracy** and MCC are the "
          "bias-corrected metrics. FRQ is the "
          "published-rubric mean (0–10). 95% CIs: Wilson for proportions (balanced accuracy = mean "
          "of the two Wilson halves), normal approximation for means. Refusals excluded.\n",
          "| Model | cutoff | events | binary n | raw merged acc | balanced acc | MCC | MCQ (n) | FRQ 0–10 (n) | date score (n) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for name, cutoff, r in rows:
        if r is None:
            md.append(f"| {name} | {cutoff} | — | — | — | — | — | (not yet run) | — | — |"); continue
        tag = ""
        if r["all_post"]: tag += notes["all_post"]
        if not r["has_extension"]: tag += notes["no_ext"]
        if name == "DeepSeek-V4-Pro": tag += notes["april"]
        b = r["binary"]
        def cell(v, dec=3):           # value [CI] (n), or a dash when the task is absent/ungraded
            return f"{fmt(v, dec)} ({v[3]:,})" if v else "—"
        md.append(f"| {name}{tag} | {cutoff} | {r['n_events_post']:,} | {b[3] if b else 0:,} | {fmt(r['raw_merged'])} | {fmt(b)} | "
                  f"{(f'{r[chr(109)+chr(99)+chr(99)]:+.3f}' if r['mcc'] is not None else '—')} | "
                  f"{cell(r['mcq'])} | {cell(r['frq'], 2)} | {cell(r['date'])} |")
    md.append("")
    md.append("\\* cutoff precedes the corpus (Jan 2024), so post-cutoff is the entire dataset — no retrospective rows exist for this model.  ")
    md.append("† original corpus only (4,760 events); no extension run exists (endpoint retired).  ")
    md.append("‡ cutoff 2026-04 overlaps the extension: April 2026 (176 events) counts as post under this rule; "
              "§2 of RUN2_RESULTS.md reports it May–Aug only, and the choice moves MCC by 0.003.")
    open(a.out_md, "w", encoding="utf-8").write("\n".join(md) + "\n")
    json.dump(out, open(a.out_json, "w", encoding="utf-8"), indent=2, default=lambda o: list(o) if isinstance(o, tuple) else o)
    print("\n".join(md)); print(f"\nwrote {a.out_md}\nwrote {a.out_json}")


if __name__ == "__main__":
    main()
