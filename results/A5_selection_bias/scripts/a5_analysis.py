#!/usr/bin/env python3
"""
a5_analysis.py -- Reviewer 1 comment 5: benchmark selection bias.

Stratifies panel performance by source/repository, event visibility (citation
quartile) and publication latency, each reported PRE-CUTOFF, POST-CUTOFF and
OVERALL, with N and an event-clustered bootstrap CI in every cell and a
permutation test for a stratum effect.

Regenerates everything:  python results/A5_selection_bias/scripts/a5_analysis.py
"""
from __future__ import annotations
import argparse, csv, json, os, subprocess, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a5_common as C  # noqa: E402

OUT = os.path.dirname(HERE)
PARTS = ["pre", "post", "overall"]


def build(meta, args):
    """model -> list of per-event records, with stratum keys attached."""
    edges = C.citation_quartiles(meta)
    data = {}
    for name, cutoff, op, ep in C.PANEL:
        recs = C.load_model_events(name, cutoff, [op, ep], meta)
        for r in recs:
            m = meta[r["id"]]
            r["source"] = m["source"]
            r["visibility"] = C.cite_bin(m["citations"], edges)
            r["latency"] = C.latency_bin(m["latency"])
        data[name] = (cutoff, recs)
    return data, edges


def group(recs, dim, part):
    g = defaultdict(list)
    for r in recs:
        if part != "overall" and r["part"] != part:
            continue
        k = r.get(dim)
        if k is None:
            continue
        g[k].append(r)
    return g


def analyse(data, dim, order, args):
    """Returns cells[(model, part, task, stratum)] and tests[(model, part, task)]."""
    cells, tests = {}, {}
    raw_p, raw_key = [], []
    for name, (cutoff, recs) in data.items():
        for part in PARTS:
            g = group(recs, dim, part)
            if not g:
                continue
            for task in C.TASKS:
                for s in order:
                    if s not in g:
                        continue
                    cells[(name, part, task, s)] = C.cell(
                        g[s], task, n_boot=args.boot, seed=args.seed,
                        min_n=args.min_n)
                t = C.omnibus(g, task, n_perm=args.perm, seed=args.seed,
                              min_n=args.min_n)
                if t:
                    tests[(name, part, task)] = t
                    raw_p.append(t["p"])
                    raw_key.append((name, part, task))
    if raw_p:
        adj = C.holm(raw_p)
        for k, a in zip(raw_key, adj):
            tests[k]["p_holm"] = a
    return cells, tests


def write_dim(dim, title, order, labels, cells, tests, data, notes, outdir):
    os.makedirs(outdir, exist_ok=True)
    # ---- CSV: one row per model x partition x task x stratum
    with open(f"{outdir}/{dim}_cells.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "cutoff", "partition", "task", "stratum",
                    "statistic", "ci_lo", "ci_hi", "n_obs", "n_events",
                    "suppressed"])
        for (name, part, task, s), c in sorted(cells.items()):
            if c is None:
                continue
            cut = data[name][0]
            w.writerow([name, cut, part, task, labels.get(s, s),
                        f"{c['stat']:.6f}",
                        "" if c["lo"] is None else f"{c['lo']:.6f}",
                        "" if c["hi"] is None else f"{c['hi']:.6f}",
                        c["n"], c["n_events"], int(bool(c.get("suppressed")))])
    with open(f"{outdir}/{dim}_tests.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "partition", "task", "n_strata", "range",
                    "min_stratum", "max_stratum", "p_raw", "p_holm"])
        for (name, part, task), t in sorted(tests.items()):
            w.writerow([name, part, task, t["n_strata"], f"{t['range']:.6f}",
                        labels.get(t["min_stratum"], t["min_stratum"]),
                        labels.get(t["max_stratum"], t["max_stratum"]),
                        f"{t['p']:.6f}", f"{t.get('p_holm', float('nan')):.6f}"])

    # ---- markdown: one table per task, models x strata, three partitions
    lines = [f"# {title}", ""]
    lines += notes + [""]
    for part in PARTS:
        lines.append(f"## {part.upper()}-CUTOFF" if part != "overall" else "## OVERALL")
        lines.append("")
        for task in C.TASKS:
            present = [s for s in order
                       if any((n, part, task, s) in cells and cells[(n, part, task, s)]
                              for n in data)]
            if not present:
                continue
            lines.append(f"### {C.TASK_LABEL[task]}")
            lines.append("")
            head = ["model", "cutoff"] + [labels.get(s, s) for s in present] + \
                   ["p (perm)", "p (Holm)"]
            lines.append("| " + " | ".join(head) + " |")
            lines.append("|" + "---|" * len(head))
            for name, (cut, _) in data.items():
                row = [name, cut]
                any_cell = False
                for s in present:
                    c = cells.get((name, part, task, s))
                    row.append(C.fmt(c, 3 if task != "frq" else 2))
                    any_cell = any_cell or c is not None
                t = tests.get((name, part, task))
                row.append(f"{t['p']:.3f}" if t else "--")
                row.append(f"{t['p_holm']:.3f}" if t and "p_holm" in t else "--")
                if any_cell:
                    lines.append("| " + " | ".join(row) + " |")
            lines.append("")
    open(f"{outdir}/{dim}_tables.md", "w").write("\n".join(lines) + "\n")
    return f"{outdir}/{dim}_tables.md"


def partition_sizes(data, meta, dim=None):
    rows = []
    for name, (cut, recs) in data.items():
        pre = sum(1 for r in recs if r["part"] == "pre")
        post = sum(1 for r in recs if r["part"] == "post")
        d = dict(model=name, cutoff=cut, n_events=len(recs), pre=pre, post=post)
        if dim:
            d["pre_dim"] = sum(1 for r in recs if r["part"] == "pre" and r.get(dim))
            d["post_dim"] = sum(1 for r in recs if r["part"] == "post" and r.get(dim))
        rows.append(d)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--perm", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--only", default=None, help="source|visibility|latency")
    ap.add_argument("--smoke", action="store_true", help="1 model, few draws")
    args = ap.parse_args()
    if args.smoke:
        args.boot, args.perm = 200, 500

    meta, n_cite = C.load_meta()
    data, edges = build(meta, args)
    if args.smoke:
        data = {k: v for k, v in list(data.items())[:2]}

    sizes = partition_sizes(data, meta)
    print("pre/post partition sizes (entire dataset):")
    for r in sizes:
        print(f"  {r['model']:18s} {r['cutoff']}  n={r['n_events']:5d}  "
              f"pre={r['pre']:5d}  post={r['post']:5d}")

    manifest = dict(
        git_sha=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                               text=True, cwd=C.REPO).stdout.strip(),
        generated=subprocess.run(["date", "-Is"], capture_output=True,
                                 text=True).stdout.strip(),
        seed=args.seed, n_bootstrap=args.boot, n_permutations=args.perm,
        min_n=args.min_n, partition_rule="main (cutoff month counts as POST)",
        citation_retrieval_date=C.CITE_RETRIEVED,
        citation_source="Semantic Scholar batch API (OpenAlex fallback)",
        citation_file=C.CITE, n_events_with_citations=n_cite,
        citation_quartile_edges=dict(Q1_max=edges[0], Q2_max=edges[1], Q3_max=edges[2]),
        frq_scores="published rubric judge_frq_combined, sha256 fc24e69d... "
                   "(stage-2 complete for all 10 models; NOT the archived legacy scores)",
        binary_metric="balanced accuracy = mean(recall on real, specificity on perturbed)",
        panel=[dict(model=n, cutoff=c, original=o, extension=e) for n, c, o, e in C.PANEL],
        partition_sizes=sizes,
        benchmarks=dict(original=C.ORIG, extension=C.EXT),
    )

    dims = [
        ("source", "A5.1 -- performance by source / repository",
         C.SOURCE_ORDER, C.SOURCE_LABEL, f"{OUT}/by_source",
         ["Entire dataset (5,575 events); `source` is one-to-one with the venue "
          "(Nature = 10.1038/s41586, Science = 10.1126/science, Cell = "
          "10.1016/j.cell, both AI feeds = arXiv), so this is simultaneously the "
          "per-journal stratification. No stratum is a singleton, so no 'other' "
          "bucket is needed.",
          "", "Cells are `value [95% CI] (n observations)`; binary n counts the "
          "real and perturbed question separately. Cells below n=20 are printed "
          "as `n<20 (n)` with no point estimate. `p (perm)` is a 10,000-draw "
          "permutation test shuffling stratum labels across events; `p (Holm)` "
          "is Holm-Bonferroni corrected across every model x partition x task "
          "test in this stratification."]),
        ("visibility", "A5.2 -- performance by event visibility (citation quartile)",
         C.CITE_ORDER, {"Q1": f"Q1 (<={int(edges[0])})", "Q2": f"Q2 (<={int(edges[1])})",
                        "Q3": f"Q3 (<={int(edges[2])})", "Q4": f"Q4 (>{int(edges[2])})"},
         f"{OUT}/by_visibility",
         [f"Citation counts exist for {n_cite} events only ({100*n_cite/5575:.1f}% of "
          "the corpus), all in the original half, all inside the pinned 500-event "
          f"retrieval subset. Retrieved {C.CITE_RETRIEVED} from the Semantic Scholar "
          "batch API (OpenAlex fallback); counts move over time and this is a "
          "single snapshot.",
          "", f"Quartile edges over those {n_cite} events: Q1 <= {int(edges[0])}, "
          f"Q2 <= {int(edges[1])}, Q3 <= {int(edges[2])}, Q4 > {int(edges[2])} -- "
          "identical to the edges used in published Supplementary Tables S19-S23.",
          "", "Because the subset spans 2024-01 to 2026-03 only, models with early "
          "cutoffs have every citation-bearing event post-cutoff and models with "
          "late cutoffs have every one pre-cutoff; the missing partition is absent "
          "by construction, not by suppression."]),
        ("latency", "A5.3 -- performance by publication latency",
         C.LATENCY_ORDER, {s: s for s in C.LATENCY_ORDER}, f"{OUT}/by_latency",
         ["Latency = original_publication_date - first_date_found, computable for "
          "708 extension events (12.7% of the corpus). The original half carries no "
          "preprint/first-seen date at all, so it cannot contribute.",
          "", "Observed latency is 0-3 months (0: 442, 1: 156, 2: 101, 3: 9). The "
          "3-month cell has n=9, so 2 and 3 are pooled. The distribution is "
          "right-censored by the extension window (Apr-Aug 2026): a paper first "
          "seen in August cannot show a long latency inside the corpus.",
          "", "The extension is post-cutoff for every model in the panel, so this "
          "stratification has NO pre-cutoff partition for any model and OVERALL "
          "equals POST-CUTOFF."]),
    ]

    written = []
    for dim, title, order, labels, outdir, notes in dims:
        if args.only and args.only != dim:
            continue
        print(f"\n=== {dim} ===")
        cells, tests = analyse(data, dim, order, args)
        p = write_dim(dim, title, order, labels, cells, tests, data, notes, outdir)
        written.append(p)
        sig = [(k, t) for k, t in tests.items() if t.get("p_holm", 1) < 0.05]
        print(f"  cells {len(cells)}  tests {len(tests)}  "
              f"Holm-significant {len(sig)}")
        for (name, part, task), t in sorted(sig, key=lambda kv: kv[1]["p_holm"])[:12]:
            print(f"    {name:18s} {part:7s} {task:6s} "
                  f"range={t['range']:+.3f} ({t['min_stratum']}->{t['max_stratum']}) "
                  f"p_holm={t['p_holm']:.4f}")
        manifest.setdefault("outputs", []).append(p)

    if not args.smoke:
        json.dump(manifest, open(f"{OUT}/MANIFEST.json", "w"), indent=2)
        print(f"\nwrote {OUT}/MANIFEST.json")
    print("\n".join(["wrote " + p for p in written]))


if __name__ == "__main__":
    main()
