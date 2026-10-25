#!/usr/bin/env python3
"""
a5_citation_gap.py -- fold in published Supplementary Tables S19-S23.

Those tables report the knowledge gap and foresight gap per citation quartile:

    Delta_know = mean(WS + cutoff) - mean(base)      pre-cutoff information
    Delta_fore = mean(WS, unrestricted) - mean(WS + cutoff)   post-cutoff info

on POST-CUTOFF instances, over the ids shared by all three conditions. Several
published cells rest on n = 1-3 and print a point estimate that cannot be read
(e.g. GPT-5.4 Q4 "+0.000 (n=1)"). This regenerates them with N, a paired
bootstrap CI, and suppression below --min-n, and extends the panel from the
three published models to every model with a complete web-search triple on the
pinned 500.

Post-cutoff convention here is the GAP-TABLE convention (`publication_date >
cutoff`, so the cutoff month counts as PRE), matching the generator that
produced the published tables -- NOT the "main" rule used elsewhere in A5.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a5_common as C  # noqa: E402

FR = f"{C.REPO}/run_evaluation/frq_results"

TRIPLES = {
    "GPT-4o":          dict(cutoff="2023-10", base=f"{FR}/gpt_4o_reeval.json",
                            ws=f"{FR}/gpt_4o_web_search_no_cutoff_500.json",
                            wscut=f"{FR}/gpt-4o_web_search_with_cutoff_500.json"),
    "DeepSeek-R1":     dict(cutoff="2024-07", base=f"{FR}/deepseek_r1.json",
                            ws=f"{FR}/deepseek_r1_500_no_cutoff.json",
                            wscut=f"{FR}/deepseek_r1_500_web_cutoff.json"),
    "Claude S4.5":     dict(cutoff="2025-01", base=f"{FR}/claude_sonnet.json",
                            ws=f"{FR}/claude_500_with_full.json",
                            wscut=f"{FR}/claude_500_with_cutoff.json"),
    "GPT-5.4":         dict(cutoff="2025-08", base=f"{FR}/gpt_5_4_eval.json",
                            ws=f"{FR}/gpt_5_4_web_subset_eval.json",
                            wscut=f"{FR}/gpt_5_4_500_web_cutoff.json"),
    "Claude Sonnet 5": dict(cutoff="2026-01",
                            base=f"{C.REPO}/results_sonnet5_run1/reports/base_medium_run1.json",
                            ws=f"{C.REPO}/results_sonnet5_run1/reports/ws_500.json",
                            wscut=f"{C.REPO}/results_sonnet5_run1/reports/ws_cutoff_500.json"),
    "GPT-5.6 Sol":     dict(cutoff="2026-02",
                            base=f"{C.REPO}/results_sol_run1/reports/base_medium_run1.json",
                            ws=f"{C.REPO}/results_sol_run1/reports/ws_500.json",
                            wscut=f"{C.REPO}/results_sol_run1/reports/ws_cutoff_500.json"),
    "Claude Opus 4.8": dict(cutoff="2026-01",
                            base=f"{C.REPO}/results_opus48_run1/reports/base_medium_run1.json",
                            ws=f"{C.REPO}/results_opus48_run1/reports/ws_500.json",
                            wscut=f"{C.REPO}/results_opus48_run1/reports/ws_cutoff_500.json"),
}

ROWS = [("Binary", "binary"), ("Binary (pert.)", "binary_perturbed"),
        ("MCQ", "mcq"), ("FRQ (0-10)", "frq"), ("Date (0-1)", "date")]


def load(path):
    if not os.path.exists(path):
        return None
    out = {}
    for r in json.load(open(path, encoding="utf-8")).get("results", []):
        if r.get("retrieval_failed"):
            continue
        out[r["id"]] = r
    return out


def score(rec, task):
    t = (rec.get("tasks") or {}).get(task)
    if not t or t.get("skipped") or t.get("score") is None:
        return None
    return float(t["score"])


def paired_boot(diffs, n_boot, rng):
    d = np.asarray(diffs, float)
    idx = rng.integers(0, d.size, size=(n_boot, d.size))
    draws = d[idx].mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--out", default=f"{os.path.dirname(HERE)}/by_visibility")
    a = ap.parse_args()

    meta, n_cite = C.load_meta()
    edges = C.citation_quartiles(meta)
    rng = np.random.default_rng(a.seed)

    rows_out, md = [], []
    md.append("# S19-S23 fold-in — knowledge and foresight gap by citation quartile")
    md.append("")
    md.append(f"Δ_know = mean(WS+cutoff) − mean(base); Δ_fore = mean(WS) − mean(WS+cutoff). "
              f"Post-cutoff instances only, over ids shared by all three conditions. "
              f"Quartiles over the {n_cite} citation-bearing events "
              f"(Q1 ≤ {int(edges[0])}, Q2 ≤ {int(edges[1])}, Q3 ≤ {int(edges[2])}, "
              f"Q4 > {int(edges[2])}); retrieved {C.CITE_RETRIEVED}.")
    md.append("")
    md.append(f"Cells are `Δ [95% CI] (n)` from a {a.boot}-draw paired bootstrap. "
              f"Cells below n={a.min_n} print `n<{a.min_n} (n)` and no estimate — "
              "the published tables printed point estimates at n = 1–3.")
    md.append("")
    md.append("Post-cutoff rule: `publication_date > cutoff` (gap-table convention, "
              "cutoff month counts as PRE), matching the published tables.")
    md.append("")

    for name, cfg in TRIPLES.items():
        base, ws, wscut = load(cfg["base"]), load(cfg["ws"]), load(cfg["wscut"])
        if not all((base, ws, wscut)):
            print(f"  SKIP {name}: missing report", file=sys.stderr)
            continue
        cm = C.mo(cfg["cutoff"])
        shared = [i for i in (set(base) & set(ws) & set(wscut))
                  if i in meta and meta[i]["citations"] is not None
                  and C.mo(meta[i]["pub"]) is not None
                  and C.mo(meta[i]["pub"]) > cm]
        if not shared:
            print(f"  SKIP {name}: no shared post-cutoff citation-bearing ids", file=sys.stderr)
            continue
        md.append(f"## {name} (cutoff {cfg['cutoff']}) — {len(shared)} shared post-cutoff events")
        md.append("")
        md.append("| task | quartile | Δ_know [95% CI] | Δ_fore [95% CI] | n |")
        md.append("|---|---|---|---|---|")
        for label, task in ROWS:
            for q in C.CITE_ORDER:
                dk, df = [], []
                for i in shared:
                    if C.cite_bin(meta[i]["citations"], edges) != q:
                        continue
                    b, w, c = score(base[i], task), score(ws[i], task), score(wscut[i], task)
                    if b is None or w is None or c is None:
                        continue
                    dk.append(c - b)
                    df.append(w - c)
                n = len(dk)
                if n == 0:
                    continue
                if n < a.min_n:
                    md.append(f"| {label} | {q} | n<{a.min_n} | n<{a.min_n} | {n} |")
                    rows_out.append(dict(model=name, task=task, quartile=q, n=n,
                                         suppressed=True))
                    continue
                kl, kh = paired_boot(dk, a.boot, rng)
                fl, fh = paired_boot(df, a.boot, rng)
                md.append(f"| {label} | {q} | {np.mean(dk):+.3f} [{kl:+.3f}, {kh:+.3f}] "
                          f"| {np.mean(df):+.3f} [{fl:+.3f}, {fh:+.3f}] | {n} |")
                rows_out.append(dict(model=name, task=task, quartile=q, n=n,
                                     suppressed=False,
                                     d_know=float(np.mean(dk)), know_lo=kl, know_hi=kh,
                                     d_fore=float(np.mean(df)), fore_lo=fl, fore_hi=fh))
        md.append("")

    os.makedirs(a.out, exist_ok=True)
    open(f"{a.out}/citation_gap_S19_S23.md", "w").write("\n".join(md) + "\n")
    json.dump(rows_out, open(f"{a.out}/citation_gap_S19_S23.json", "w"), indent=2)
    n_sup = sum(1 for r in rows_out if r["suppressed"])
    print(f"cells {len(rows_out)}  suppressed {n_sup}  "
          f"-> {a.out}/citation_gap_S19_S23.md")


if __name__ == "__main__":
    main()
