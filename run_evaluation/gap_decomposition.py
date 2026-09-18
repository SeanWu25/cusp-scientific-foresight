#!/usr/bin/env python3
"""
gap_decomposition.py — Table S18: knowledge gap and foresight gap per task.

    Delta_know = mean(WS + cutoff) - mean(base)     gain from pre-cutoff information
    Delta_fore = mean(WS, unrestricted) - mean(WS + cutoff)
                                                    gain from post-cutoff information

Both are computed on POST-CUTOFF instances only, over the ids shared by all
three conditions for that model. The post-cutoff filter is the gap-table
convention (`publication_date > cutoff`, so the cutoff month counts as pre),
matching filter_ids_by_cutoff in the generator that produced the published
table.

Unlike the published table this one reports N and a paired 95% CI for every
cell, and suppresses any cell below --min-n instead of printing a point
estimate that cannot be read.
"""

from __future__ import annotations

import argparse, json, math, os, statistics, sys

FR = "run_evaluation/frq_results"

MODELS = {
    "GPT-5.4":       dict(cutoff="2025-08",
                          base=f"{FR}/gpt_5_4_eval.json",
                          ws=f"{FR}/gpt_5_4_web_subset_eval.json",
                          wscut=f"{FR}/gpt_5_4_500_web_cutoff.json"),
    "DeepSeek-R1":   dict(cutoff="2024-07",
                          base=f"{FR}/deepseek_r1.json",
                          ws=f"{FR}/deepseek_r1_500_no_cutoff.json",
                          wscut=f"{FR}/deepseek_r1_500_web_cutoff.json"),
    "Claude Sonnet": dict(cutoff="2025-01",
                          base=f"{FR}/claude_sonnet.json",
                          ws=f"{FR}/claude_500_with_full.json",
                          wscut=f"{FR}/claude_500_with_cutoff.json"),
}

ROWS = [("Binary", "binary", "score"),
        ("Binary (pert.)", "binary_perturbed", "score"),
        ("MCQ", "mcq", "score"),
        ("FRQ (0-10)", "frq", "score"),
        ("Date (0-1)", "date", "score")]


def load(path: str) -> dict:
    rep = json.load(open(path, encoding="utf-8"))
    return {r["id"]: r for r in rep.get("results", [])}


def field(rec: dict, task: str, name: str):
    t = (rec.get("tasks") or {}).get(task)
    if not t or t.get("skipped"):
        return None
    v = t.get(name)
    return None if v is None else float(v)


def paired_ci(diffs: list[float], z: float = 1.96):
    n = len(diffs)
    if n < 2:
        return float("nan"), float("nan")
    m = statistics.fmean(diffs)
    se = statistics.stdev(diffs) / math.sqrt(n)
    return m - z * se, m + z * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark",
                    default="archive/data/canonical/merged_validated_cusp_fixed.jsonl")
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--extra", action="append", default=[],
                    help="'Name=YYYY-MM=base.json=ws.json=wscut.json'")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    pub = {}
    for l in open(a.benchmark, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            pub[r["id"]] = r.get("publication_date", "")

    models = dict(MODELS)
    for spec in a.extra:
        name, cut, b, w, c = spec.split("=", 4)
        models[name] = dict(cutoff=cut, base=b, ws=w, wscut=c)

    report = {"definition": {
        "delta_know": "mean(WS+cutoff) - mean(base), post-cutoff instances",
        "delta_fore": "mean(WS unrestricted) - mean(WS+cutoff), post-cutoff instances",
        "post_cutoff_rule": "publication_date > cutoff (cutoff month counts as pre)"},
        "min_n": a.min_n, "models": {}}

    for name, cfg in models.items():
        if not all(os.path.exists(cfg[k]) for k in ("base", "ws", "wscut")):
            print(f"  SKIP {name} (missing condition file)", file=sys.stderr)
            continue
        B, W, C = load(cfg["base"]), load(cfg["ws"]), load(cfg["wscut"])
        ids = sorted(set(B) & set(W) & set(C))
        post = [i for i in ids if pub.get(i, "") > cfg["cutoff"]]
        entry = {"cutoff": cfg["cutoff"], "n_shared_ids": len(ids),
                 "n_post_cutoff_ids": len(post), "tasks": {}}
        for label, task, fld in ROWS:
            b, w, c = [], [], []
            for i in post:
                vb, vw, vc = field(B[i], task, fld), field(W[i], task, fld), field(C[i], task, fld)
                if vb is None or vw is None or vc is None:
                    continue
                b.append(vb); w.append(vw); c.append(vc)
            n = len(b)
            cell = {"n": n}
            if n < a.min_n:
                cell["suppressed"] = True
                cell["reason"] = f"n < {a.min_n}"
            else:
                dk = [ci - bi for ci, bi in zip(c, b)]
                df = [wi - ci for wi, ci in zip(w, c)]
                cell["delta_know"] = statistics.fmean(dk)
                cell["delta_fore"] = statistics.fmean(df)
                cell["delta_know_ci"] = paired_ci(dk)
                cell["delta_fore_ci"] = paired_ci(df)
                cell["mean_base"] = statistics.fmean(b)
                cell["mean_wscut"] = statistics.fmean(c)
                cell["mean_ws"] = statistics.fmean(w)
            entry["tasks"][label] = cell
        report["models"][name] = entry

    names = list(report["models"])
    print(f"{'Metric':18s}" + "".join(
        f"{n + ' (' + report['models'][n]['cutoff'] + ')':>34s}" for n in names))
    print(f"{'':18s}" + "".join(f"{'d_know':>12s}{'d_fore':>12s}{'n':>10s}" for _ in names))
    for label, _, _ in ROWS:
        row = f"{label:18s}"
        for n in names:
            c = report["models"][n]["tasks"].get(label, {})
            if c.get("suppressed") or "delta_know" not in c:
                row += f"{'--':>12s}{'--':>12s}{c.get('n', 0):>10d}"
            else:
                row += f"{c['delta_know']:>+12.3f}{c['delta_fore']:>+12.3f}{c['n']:>10d}"
        print(row)
    for n in names:
        e = report["models"][n]
        print(f"\n{n}: shared ids={e['n_shared_ids']}  post-cutoff ids={e['n_post_cutoff_ids']}")

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(report, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
