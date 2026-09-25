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


def build(meta, args, R):
    """model -> list of per-event records, with every stratum key attached."""
    data = {}
    for name, cutoff, op, ep in C.PANEL:
        recs = C.load_model_events(name, cutoff, [op, ep], meta)
        for r in recs:
            m = meta[r["id"]]
            for dim, spec in R.items():
                r[dim] = spec["key"](m)
        data[name] = (cutoff, recs)
    return data


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
    ap.add_argument("--only", default=None, help="comma-separated dims from C.DIMS_ALL")
    ap.add_argument("--smoke", action="store_true", help="1 model, few draws")
    ap.add_argument("--manifest-only", action="store_true", help="write MANIFEST.json, run no dimension")
    args = ap.parse_args()
    if args.smoke:
        args.boot, args.perm = 200, 500

    meta, n_cite = C.load_meta()
    R = C.dim_registry(meta, OUT)
    data = build(meta, args, R)
    if args.smoke:
        data = {k: v for k, v in list(data.items())[:2]}

    sizes = partition_sizes(data, meta)
    print("pre/post partition sizes (entire dataset):")
    for r in sizes:
        print(f"  {r['model']:18s} {r['cutoff']}  n={r['n_events']:5d}  "
              f"pre={r['pre']:5d}  post={r['post']:5d}")

    def cov(field):
        return sum(1 for m in meta.values() if m.get(field) is not None)

    manifest = dict(
        git_sha=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                               text=True, cwd=C.REPO).stdout.strip(),
        generated=subprocess.run(["date", "-Is"], capture_output=True,
                                 text=True).stdout.strip(),
        seed=args.seed, n_bootstrap=args.boot, n_permutations=args.perm,
        min_n=args.min_n, partition_rule="main (cutoff month counts as POST)",
        metadata_snapshot_date=C.SNAPSHOT,
        citation_source="Semantic Scholar batch API (primary), OpenAlex (fallback); "
                        "metadata/s2_citations.jsonl, metadata/openalex_citations.jsonl",
        n_events_with_citations=cov("cites"),
        citation_quartile_edges=C.quartile_edges(meta, "cites"),
        citation_rate_quartile_edges=C.quartile_edges(meta, "cite_rate"),
        latency_source="Crossref works API; metadata/crossref_dates.jsonl and "
                       "metadata/crossref_preprints.jsonl",
        n_events_with_latency=cov("lat_obs"),
        n_events_with_editorial_latency=cov("lat_review"),
        latency_bins=dict(observable=C.LAT_OBS_ORDER, editorial=C.LAT_REVIEW_ORDER),
        legacy_citation_file=C.CITE, legacy_citation_retrieval_date=C.CITE_RETRIEVED,
        legacy_n_events_with_citations=n_cite,
        legacy_n_events_with_latency=cov("latency"),
        frq_scores="published rubric judge_frq_combined, sha256 fc24e69d... "
                   "(stage-2 complete for all 10 models; NOT the archived legacy scores)",
        binary_metric="balanced accuracy = mean(recall on real, specificity on perturbed)",
        panel=[dict(model=n, cutoff=c, original=o, extension=e) for n, c, o, e in C.PANEL],
        partition_sizes=sizes,
        benchmarks=dict(original=C.ORIG, extension=C.EXT),
        dimensions={k: dict(title=v["title"], order=[v["labels"].get(x, x) for x in v["order"]],
                            outdir=v["outdir"]) for k, v in R.items()},
        n_journal_doi=sum(1 for m in meta.values() if m.get("kind") == "doi"),
        n_crossref_resolved=sum(1 for m in meta.values() if m.get("online") is not None),
        n_arxiv=sum(1 for m in meta.values() if m.get("kind") == "arxiv"),
        n_linked=sum(1 for m in meta.values() if m.get("doi")),
        n_citations_by_source={src: sum(1 for m in meta.values() if m.get("cite_src") == src)
                               for src in ("s2", "openalex")},
        n_linked_without_citation=sum(1 for m in meta.values() if m.get("doi") and m.get("cites") is None),
    )
    lat = [m["lat_obs"] for m in meta.values() if m.get("lat_obs") is not None]
    if lat:
        manifest["latency_distribution"] = dict(
            n=len(lat), share_0=sum(1 for v in lat if v == 0) / len(lat),
            share_1_6=sum(1 for v in lat if 1 <= v <= 6) / len(lat),
            share_gt6=sum(1 for v in lat if v > 6) / len(lat),
            share_gt3=sum(1 for v in lat if v > 3) / len(lat),
            share_gt12=sum(1 for v in lat if v > 12) / len(lat),
            n_clipped_negative=sum(1 for m in meta.values() if m.get("lat_obs_raw") is not None and m["lat_obs_raw"] < 0),
            histogram={str(k): sum(1 for v in lat if v == k) for k in range(0, 13)}, max=int(max(lat)),
            by_source={src: dict(n=sum(1 for m in meta.values() if m.get("lat_obs") is not None and m["source"] == src),
                                 share_0=(sum(1 for m in meta.values() if m.get("lat_obs") == 0 and m["source"] == src)
                                          / max(1, sum(1 for m in meta.values() if m.get("lat_obs") is not None and m["source"] == src))))
                       for src in ("nature", "science", "cell")})
        rev = [m["lat_review"] for m in meta.values() if m.get("lat_review") is not None]
        manifest["editorial_latency_distribution"] = dict(
            n=len(rev), quartiles=[float(np.percentile(rev, q)) for q in (25, 50, 75)],
            share_by_bin={lab: sum(1 for v in rev if C.edge_bin(v, C.LAT_REVIEW_BINS) == lab) / len(rev)
                          for lab in C.LAT_REVIEW_ORDER}) if rev else None
        n_pre = sum(1 for m in meta.values() if m.get("preprint") is not None)
        manifest["n_events_with_crossref_preprint_link"] = n_pre
        gaps = [m["preprint_gap"] for m in meta.values() if m.get("preprint_gap") is not None and m["preprint_gap"] > 0]
        manifest["n_preprint_earlier_than_cusp_date"] = len(gaps)
        manifest["preprint_gap_months_quartiles"] = [float(np.percentile(gaps, q)) for q in (25, 50, 75)] if gaps else None
        manifest["preprint_gap_months_max"] = max(gaps) if gaps else None
    # events a model sees as post-cutoff whose Crossref-linked preprint predates
    # its cutoff: observable before the cutoff, so leakage-prone under the
    # benchmark's own dating. Reported, not corrected (the partition rule is the
    # benchmark's).
    manifest["preprint_before_cutoff_among_post"] = {}
    for name, cutoff, _, _ in C.PANEL:
        cm = C.mo(cutoff)
        post = [m for m in meta.values() if C.mo(m["pub"]) is not None and C.mo(m["pub"]) >= cm
                and m.get("kind") == "doi"]
        leak = [m for m in post if m.get("preprint") and C.mo(m["preprint"]) < cm]
        manifest["preprint_before_cutoff_among_post"][name] = dict(
            cutoff=cutoff, post_journal_events=len(post), preprint_before_cutoff=len(leak))
    pairs = [(m["citations"], m["cites"]) for m in meta.values()
             if m.get("citations") is not None and m.get("cites") is not None]
    if len(pairs) > 10:
        from scipy.stats import spearmanr
        manifest["legacy_vs_new_spearman"] = float(spearmanr([a for a, _ in pairs], [b for _, b in pairs]).correlation)
        manifest["legacy_vs_new_n"] = len(pairs)
    for dim, spec in R.items():
        manifest["dimensions"][dim]["coverage"] = {
            part: sum(1 for _, (_, recs) in data.items() for r in recs
                      if r.get(dim) is not None and (part == "overall" or r["part"] == part))
            for part in PARTS}

    dims = [(dim, spec["title"], spec["order"], spec["labels"], spec["outdir"], spec["notes"])
            for dim, spec in R.items()]

    written = []
    for dim, title, order, labels, outdir, notes in dims:
        if args.manifest_only or (args.only and dim not in args.only.split(",")):
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
