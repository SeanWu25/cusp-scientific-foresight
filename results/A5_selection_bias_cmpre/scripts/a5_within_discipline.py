#!/usr/bin/env python3
"""
a5_within_discipline.py -- the confound control for A5.1.

CUSP's source strata are nested inside discipline by construction: the two
arXiv feeds and the leaderboard set are 99-100% Artificial Intelligence, while
Nature/Science/Cell are 0-1.3% AI. A raw "source effect" is therefore mostly a
discipline effect, and cannot be read as a venue effect.

This holds discipline FIXED and compares venues inside it. Seven disciplines
carry two or more venues at n >= 100:

  Biology, Medicine                 Nature / Science / Cell
  Materials Sci, Neuro, Physics,
  Chemistry                         Nature / Science
  Artificial Intelligence           HF Daily Papers / Top-10 AI Paper

Same statistics as the main analysis: N and an event-clustered bootstrap CI in
every cell, cells below --min-n suppressed, a permutation test across venues,
Holm-corrected within each discipline.
"""
from __future__ import annotations
import argparse, csv, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a5_common as C  # noqa: E402

OUT = os.path.dirname(HERE)
PARTS = ["pre", "post", "overall"]
MIN_VENUE = 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--perm", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--outdir", default=f"{OUT}/by_source")
    a = ap.parse_args()

    meta, _ = C.load_meta()

    # which (discipline -> venues) pairs are testable
    counts = defaultdict(lambda: defaultdict(int))
    for m in meta.values():
        counts[m["area"]][m["source"]] += 1
    disciplines = {}
    for area, c in counts.items():
        venues = [v for v, n in sorted(c.items(), key=lambda kv: -kv[1]) if n >= MIN_VENUE]
        if len(venues) >= 2:
            disciplines[area] = venues
    order = sorted(disciplines, key=lambda a_: -sum(counts[a_][v] for v in disciplines[a_]))

    rows, tests = [], []
    for name, cutoff, op, ep in C.PANEL:
        recs = C.load_model_events(name, cutoff, [op, ep], meta)
        for r in recs:
            r["area"] = meta[r["id"]]["area"]
            r["source"] = meta[r["id"]]["source"]
        for area in order:
            venues = disciplines[area]
            for part in PARTS:
                g = defaultdict(list)
                for r in recs:
                    if part != "overall" and r["part"] != part:
                        continue
                    if r["area"] == area and r["source"] in venues:
                        g[r["source"]].append(r)
                if not g:
                    continue
                for task in C.TASKS:
                    for v in venues:
                        if v not in g:
                            continue
                        c = C.cell(g[v], task, n_boot=a.boot, seed=a.seed,
                                   min_n=a.min_n)
                        if c is None:
                            continue
                        rows.append(dict(model=name, cutoff=cutoff, discipline=area,
                                         partition=part, task=task,
                                         venue=C.SOURCE_LABEL.get(v, v), **c))
                    t = C.omnibus(g, task, n_perm=a.perm, seed=a.seed, min_n=a.min_n)
                    if t:
                        tests.append(dict(model=name, discipline=area, partition=part,
                                          task=task, **t))
        print(f"  {name}: {len(rows)} cells so far", flush=True)

    # Holm within each discipline
    by_disc = defaultdict(list)
    for i, t in enumerate(tests):
        by_disc[t["discipline"]].append(i)
    for area, idxs in by_disc.items():
        adj = C.holm([tests[i]["p"] for i in idxs])
        for i, v in zip(idxs, adj):
            tests[i]["p_holm"] = v

    os.makedirs(a.outdir, exist_ok=True)
    with open(f"{a.outdir}/within_discipline_cells.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "cutoff", "discipline", "partition", "task", "venue",
                    "statistic", "ci_lo", "ci_hi", "n_obs", "n_events", "suppressed"])
        for r in rows:
            w.writerow([r["model"], r["cutoff"], r["discipline"], r["partition"],
                        r["task"], r["venue"], f"{r['stat']:.6f}",
                        "" if r["lo"] is None else f"{r['lo']:.6f}",
                        "" if r["hi"] is None else f"{r['hi']:.6f}",
                        r["n"], r["n_events"], int(bool(r.get("suppressed")))])
    with open(f"{a.outdir}/within_discipline_tests.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "discipline", "partition", "task", "n_venues", "range",
                    "min_venue", "max_venue", "p_raw", "p_holm"])
        for t in tests:
            w.writerow([t["model"], t["discipline"], t["partition"], t["task"],
                        t["n_strata"], f"{t['range']:.6f}",
                        C.SOURCE_LABEL.get(t["min_stratum"], t["min_stratum"]),
                        C.SOURCE_LABEL.get(t["max_stratum"], t["max_stratum"]),
                        f"{t['p']:.6f}", f"{t.get('p_holm', float('nan')):.6f}"])

    # markdown summary: how often does venue matter once discipline is fixed?
    md = ["# A5.1b — venue effect with discipline held fixed", "",
          "CUSP's source strata are nested inside discipline (the arXiv feeds are "
          "99–100% AI, the journals 0–1.3%), so the raw source effect in "
          "`source_tables.md` is largely a discipline effect. This table asks the "
          "narrower question: **within one discipline, does the venue matter?**", "",
          f"Venues are included when they carry ≥{MIN_VENUE} events in that "
          f"discipline. Cells below n={a.min_n} are suppressed. p is a {a.perm}-draw "
          "permutation test across venues, Holm-corrected within each discipline.", ""]
    md.append("| discipline | venues | events | tests | Holm-significant (p<0.05) |")
    md.append("|---|---|---|---|---|")
    for area in order:
        ts = [t for t in tests if t["discipline"] == area]
        sig = [t for t in ts if t.get("p_holm", 1) < 0.05]
        md.append(f"| {area} | {', '.join(C.SOURCE_LABEL.get(v, v) for v in disciplines[area])} "
                  f"| {sum(counts[area][v] for v in disciplines[area]):,} | {len(ts)} | "
                  f"**{len(sig)}** |")
    md += ["", "## Significant venue effects (discipline fixed)", ""]
    sig_all = sorted([t for t in tests if t.get("p_holm", 1) < 0.05],
                     key=lambda t: t["p_holm"])
    if not sig_all:
        md.append("None. With discipline held fixed, no model × task × partition "
                  "shows a venue effect surviving Holm correction.")
    else:
        md.append("| model | discipline | partition | task | range | lowest | highest | p (Holm) |")
        md.append("|---|---|---|---|---|---|---|---|")
        for t in sig_all:
            md.append(f"| {t['model']} | {t['discipline']} | {t['partition']} | "
                      f"{C.TASK_LABEL[t['task']]} | {t['range']:+.3f} | "
                      f"{C.SOURCE_LABEL.get(t['min_stratum'], t['min_stratum'])} | "
                      f"{C.SOURCE_LABEL.get(t['max_stratum'], t['max_stratum'])} | "
                      f"{t['p_holm']:.4f} |")
    open(f"{a.outdir}/within_discipline.md", "w").write("\n".join(md) + "\n")
    print(f"cells {len(rows)}  tests {len(tests)}  "
          f"Holm-significant {sum(1 for t in tests if t.get('p_holm', 1) < 0.05)}")
    print(f"-> {a.outdir}/within_discipline.md")


if __name__ == "__main__":
    main()
