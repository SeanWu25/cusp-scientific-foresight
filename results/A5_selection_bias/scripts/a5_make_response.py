#!/usr/bin/env python3
"""
a5_make_response.py -- assemble response_A5.md from the stored CSVs.

Every number in the response is read from by_*/<dim>_cells.csv,
by_*/<dim>_tests.csv, tables/, by_source/within_discipline*.csv and
MANIFEST.json; nothing is typed by hand. The narrative sections live in
a5_response_text.py and reference figures through the same accessors, so
a5_verify.py can re-run this generator and diff the output against the
committed file.

  python results/A5_selection_bias/scripts/a5_make_response.py [--out PATH]
"""
from __future__ import annotations
import argparse, csv, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import a5_common as C  # noqa: E402

META, _ = C.load_meta()
REG = C.dim_registry(META, OUT)
MAN = json.load(open(f"{OUT}/MANIFEST.json"))
MODELS = [p[0] for p in C.PANEL]
TASKS = ["binary", "mcq", "date", "frq"]
PART_TITLE = {"overall": "whole dataset (OVERALL)", "post": "POST-CUTOFF only",
              "pre": "PRE-CUTOFF only"}


def load(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def cells(dim):
    return load(f"{REG[dim]['outdir']}/{dim}_cells.csv")


def tests(dim):
    return load(f"{REG[dim]['outdir']}/{dim}_tests.csv")


def labels(dim):
    return [REG[dim]["labels"].get(x, x) for x in REG[dim]["order"]]


def sig_count(dim, part=None, task=None, exclude_task=None):
    t = tests(dim)
    if part:
        t = [r for r in t if r["partition"] == part]
    if task:
        t = [r for r in t if r["task"] == task]
    if exclude_task:
        t = [r for r in t if r["task"] != exclude_task]
    return sum(1 for r in t if float(r["p_holm"]) < 0.05), len(t)


def balanced(dim, part, task):
    """(models, {stratum: mean}, {stratum: n_obs}) over models carrying every
    non-structurally-absent stratum unsuppressed -- same rule as a5_tables."""
    order = labels(dim)
    sub = [r for r in cells(dim) if r["partition"] == part and r["task"] == task
           and r["suppressed"] == "0"]
    bym, nby = defaultdict(dict), defaultdict(dict)
    for r in sub:
        bym[r["model"]][r["stratum"]] = float(r["statistic"])
        nby[r["stratum"]][r["model"]] = int(r["n_obs"])
    cols = list(order)
    full = [m for m, d in bym.items() if all(s in d for s in cols)]
    if not full:
        cols = [s for s in order if any(s in d for d in bym.values())]
        full = [m for m, d in bym.items() if all(s in d for s in cols)]
    if not full or not cols:
        return None
    return (full, {s: sum(bym[m][s] for m in full) / len(full) for s in cols},
            {s: sum(nby[s][m] for m in full) for s in cols}, cols)


def pooled_table(dim, part):
    order = labels(dim)
    lines = ["| task | " + " | ".join(order) + " | models pooled | Holm-sig |",
             "|" + "---|" * (len(order) + 3)]
    for task in TASKS:
        b = balanced(dim, part, task)
        if not b:
            continue
        full, means, ns, cols = b
        dec = 2 if task == "frq" else 3
        row = " | ".join(f"{means[s]:.{dec}f} ({ns[s]:,})" if s in cols else "no items"
                         for s in order)
        k, n = sig_count(dim, part, task)
        lines.append(f"| {C.TASK_LABEL[task]} | {row} | {len(full)} | {k} / {n} |")
    return "\n".join(lines)


def per_model_table(dim, part, task):
    order = labels(dim)
    cs = {(r["model"], r["stratum"]): r for r in cells(dim)
          if r["partition"] == part and r["task"] == task}
    ts = {r["model"]: r for r in tests(dim) if r["partition"] == part and r["task"] == task}
    present = [s for s in order if any((m, s) in cs for m in MODELS)]
    if not present:
        return None
    head = ["model", "cutoff"] + present + ["p (perm)", "p (Holm)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    dec = 2 if task == "frq" else 3
    for name, cut, _, _ in C.PANEL:
        row, any_cell = [name, cut], False
        for s in present:
            r = cs.get((name, s))
            if r is None:
                row.append("--")
            elif r["suppressed"] == "1":
                row.append(f"n<20 ({r['n_obs']})"); any_cell = True
            else:
                row.append(f"{float(r['statistic']):.{dec}f} [{float(r['ci_lo']):.{dec}f}, "
                           f"{float(r['ci_hi']):.{dec}f}] ({int(r['n_obs']):,})")
                any_cell = True
        t = ts.get(name)
        row.append(f"{float(t['p_raw']):.3f}" if t else "--")
        star = "**" if t and float(t["p_holm"]) < 0.05 else ""
        row.append(f"{star}{float(t['p_holm']):.3f}{star}" if t else "--")
        if any_cell:
            lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def per_model_section(dim, part):
    out = []
    for task in TASKS:
        t = per_model_table(dim, part, task)
        if t:
            out += [f"**{C.TASK_LABEL[task]}**", "", t, ""]
    return "\n".join(out)


def direction_count(dim, part, task, hi, lo):
    """How many models score higher on stratum `hi` than on `lo` (unsuppressed both)."""
    cs = {(r["model"], r["stratum"]): float(r["statistic"]) for r in cells(dim)
          if r["partition"] == part and r["task"] == task and r["suppressed"] == "0"}
    pairs = [(cs[(m, hi)], cs[(m, lo)]) for m in MODELS if (m, hi) in cs and (m, lo) in cs]
    ups = sum(1 for a, b in pairs if a > b)
    diffs = sorted(a - b for a, b in pairs)
    med = diffs[len(diffs) // 2] if diffs else float("nan")
    return ups, len(pairs), med, (diffs[0] if diffs else None), (diffs[-1] if diffs else None)


def coverage(dim, part):
    return MAN["dimensions"][dim]["coverage"][part]


def partition_table():
    lines = ["| model | cutoff | n events | pre-cutoff | post-cutoff |", "|---|---|---|---|---|"]
    for r in MAN["partition_sizes"]:
        lines.append(f"| {r['model']} | {r['cutoff']} | {r['n_events']:,} | {r['pre']:,} | {r['post']:,} |")
    return "\n".join(lines)


def within_discipline_table():
    rows = load(f"{OUT}/by_source/within_discipline_tests.csv")
    md = open(f"{OUT}/by_source/within_discipline.md").read()
    blk = md.split("| discipline |", 1)[1] if "| discipline |" in md else ""
    lines = ["| discipline |" + blk.split("\n\n")[0]] if blk else []
    k = sum(1 for r in rows if float(r["p_holm"]) < 0.05)
    return "\n".join(lines), k, len(rows)


def meta_coverage_table():
    N = len(META)

    def cov(f):
        return sum(1 for m in META.values() if m.get(f) is not None)
    rows = [("Journal / repository (`source`)", N, "100%", "both halves", "pre / post / overall"),
            ("Event visibility -- citation quartile", cov("cites"), f"{100*cov('cites')/N:.1f}%",
             "both halves", "pre / post / overall"),
            ("Event visibility -- citation-rate quartile", cov("cite_rate"), f"{100*cov('cite_rate')/N:.1f}%",
             "both halves", "pre / post / overall"),
            ("Publication latency (observable before journal version)", cov("lat_obs"),
             f"{100*cov('lat_obs')/N:.1f}%", "all journal events, both halves", "pre / post / overall"),
            ("Editorial latency (received -> online)", cov("lat_review"), f"{100*cov('lat_review')/N:.1f}%",
             "Nature + Science, both halves", "pre / post / overall"),
            ("Novelty", 0, "--", "not computed (section 8)", "--")]
    lines = ["| stratification | events | share of 5,575 | scope | partitions |", "|---|---|---|---|---|"]
    for a, b, c, d, e in rows:
        lines.append(f"| {a} | {b:,} | {c} | {d} | {e} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=f"{OUT}/response_A5.md")
    a = ap.parse_args()
    import a5_response_text as T  # noqa: E402  (narrative, uses the accessors above)
    ctx = dict(pooled_table=pooled_table, per_model_section=per_model_section,
               sig_count=sig_count, balanced=balanced, direction_count=direction_count,
               coverage=coverage, partition_table=partition_table,
               within_discipline_table=within_discipline_table,
               meta_coverage_table=meta_coverage_table, labels=labels, REG=REG, MAN=MAN,
               META=META, C=C, MODELS=MODELS)
    text = T.render(ctx)
    open(a.out, "w").write(text)
    n_tables = sum(1 for l in text.splitlines() if l.startswith("|---"))
    print(f"wrote {a.out}: {len(text.split()):,} words, {n_tables} tables")


if __name__ == "__main__":
    main()
