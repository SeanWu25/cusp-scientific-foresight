#!/usr/bin/env python3
"""
a5_tables.py -- manuscript-ready tables for A5, CSV + markdown.

Every pooled column averages only over models that carry EVERY stratum
unsuppressed, so each column rests on the same model set.
"""
from __future__ import annotations
import csv, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
sys.path.insert(0, HERE); import a5_common as C  # noqa: E402
TAB = f"{OUT}/tables"; os.makedirs(TAB, exist_ok=True)

META, _ = C.load_meta()
REG = C.dim_registry(META, OUT)
DIMS = {d: [REG[d]["labels"].get(x, x) for x in REG[d]["order"]] for d in C.DIMS_ALL}
TITLE = {d: REG[d]["short"] for d in C.DIMS_ALL}
PARTS_OUT = ("pre", "post", "overall")


def load(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def pooled(cells, tests, dim, order, part):
    """rows: task, per-stratum mean over the balanced model set, n models, n sig."""
    out = []
    for task in ("binary", "mcq", "date", "frq"):
        sub = [r for r in cells if r["partition"] == part and r["task"] == task
               and r["suppressed"] == "0"]
        bym = defaultdict(dict)
        nby = defaultdict(dict)
        for r in sub:
            bym[r["model"]][r["stratum"]] = float(r["statistic"])
            nby[r["stratum"]][r["model"]] = int(r["n_obs"])
        cols = list(order)
        full = [m for m, d in bym.items() if all(s in d for s in cols)]
        if not full:
            # a stratum can be structurally absent for a task rather than merely
            # suppressed -- the leaderboard set carries 0 FRQ items. Drop strata
            # no model has at all, then re-balance over what remains.
            cols = [s for s in order if any(s in d for d in bym.values())]
            full = [m for m, d in bym.items() if all(s in d for s in cols)]
        if not full or not cols:
            continue
        ts = [t for t in tests if t["partition"] == part and t["task"] == task]
        sig = sum(1 for t in ts if float(t["p_holm"]) < 0.05)
        row = dict(task=task, n_models=len(full), n_tests=len(ts), n_sig=sig,
                   cols=cols)
        for s in cols:
            row[s] = sum(bym[m][s] for m in full) / len(full)
            row[s + " __n"] = sum(nby[s][m] for m in full)
        out.append(row)
    return out


def main():
    md_all = ["# A5 manuscript-ready tables", "",
              "Pooled columns average over models carrying **every** stratum "
              "unsuppressed, so all columns rest on the same model set. "
              "`n sig` counts model x task permutation tests surviving "
              "Holm correction within the stratification.", ""]
    index = {}

    for dim, order in DIMS.items():
        cells = load(f"{REG[dim]['outdir']}/{dim}_cells.csv")
        tests = load(f"{REG[dim]['outdir']}/{dim}_tests.csv")
        if not cells:
            continue
        for part in PARTS_OUT:
            rows = pooled(cells, tests, dim, order, part)
            if not rows:
                continue
            key = f"A5_{dim}_{part}"
            with open(f"{TAB}/{key}.csv", "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["task", "n_models_pooled", "n_tests", "n_holm_significant"]
                           + [x for s in order for x in (s, s + "_n_obs")])
                for r in rows:
                    w.writerow([C.TASK_LABEL[r["task"]], r["n_models"], r["n_tests"],
                                r["n_sig"]]
                               + [x for s in order
                                  for x in ((f"{r[s]:.4f}", r[s + " __n"])
                                            if s in r["cols"] else ("", ""))])
            md_all.append(f"## {TITLE[dim].title()} — {part.upper()}-cutoff")
            md_all.append("")
            md_all.append("| task | " + " | ".join(order)
                          + " | models pooled | tests | Holm-sig |")
            md_all.append("|" + "---|" * (len(order) + 4))
            for r in rows:
                dec = 2 if r["task"] == "frq" else 3
                cellsx = " | ".join(
                    (f"{r[s]:.{dec}f} ({r[s + ' __n']:,})" if s in r["cols"]
                     else "no items") for s in order)
                md_all.append(f"| {C.TASK_LABEL[r['task']]} | {cellsx} | "
                              f"{r['n_models']} | {r['n_tests']} | **{r['n_sig']}** |")
            md_all.append("")
            index[key] = f"tables/{key}.csv"

    # partition sizes
    man = json.load(open(f"{OUT}/MANIFEST.json"))
    with open(f"{TAB}/A5_partition_sizes.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "cutoff", "n_events", "pre_cutoff", "post_cutoff"])
        for r in man["partition_sizes"]:
            w.writerow([r["model"], r["cutoff"], r["n_events"], r["pre"], r["post"]])
    md_all += ["## Pre/post partition sizes (entire dataset)", "",
               "Partition rule: an event published in the cutoff month counts as POST. "
               "**These are very unequal, so OVERALL columns are not comparable "
               "between models.**", "",
               "| model | cutoff | n events | pre-cutoff | post-cutoff |",
               "|---|---|---|---|---|"]
    for r in man["partition_sizes"]:
        md_all.append(f"| {r['model']} | {r['cutoff']} | {r['n_events']:,} | "
                      f"{r['pre']:,} | {r['post']:,} |")
    md_all.append("")
    index["A5_partition_sizes"] = "tables/A5_partition_sizes.csv"

    open(f"{TAB}/A5_tables.md", "w").write("\n".join(md_all) + "\n")
    json.dump(index, open(f"{TAB}/index.json", "w"), indent=2)
    print(f"wrote {TAB}/A5_tables.md and {len(index)} CSVs")


if __name__ == "__main__":
    main()
