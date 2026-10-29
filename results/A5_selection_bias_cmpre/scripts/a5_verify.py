#!/usr/bin/env python3
"""
a5_verify.py -- integrity checks for study A5. Exits non-zero on any failure.

1. response_A5.md is byte-identical to a fresh run of a5_make_response.py
   (so no number in it can have drifted from the CSVs).
2. Every markdown table in the response has a consistent column count.
3. The first-pass (legacy) dimensions still reproduce their published counts:
   source 85/112, legacy visibility 6/93, legacy latency 0/72, within-discipline
   4/705, S19-S23 fold-in 101 cells / 32 suppressed / 7 models.
4. Coverage facts quoted in metadata_audit.md match MANIFEST.json.
5. No stratification table prints a point estimate for a cell with n < 20.
"""
import csv, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
PY = sys.executable
fails, checks = [], 0


def ck(desc, cond):
    global checks
    checks += 1
    if not cond:
        fails.append(desc)
    print(("PASS " if cond else "FAIL ") + desc)


def sig(path):
    rows = list(csv.DictReader(open(path)))
    return sum(1 for r in rows if float(r["p_holm"]) < 0.05), len(rows)


# 1. regenerate and diff
tmp = tempfile.NamedTemporaryFile(suffix=".md", delete=False).name
subprocess.run([PY, f"{HERE}/a5_make_response.py", "--out", tmp], check=True,
               capture_output=True)
resp = open(f"{OUT}/response_A5.md").read()
ck("response_A5.md identical to a fresh a5_make_response.py run", open(tmp).read() == resp)
os.unlink(tmp)

# 2. table integrity
bad, n_tab = 0, 0
for block in re.split(r"\n\s*\n", resp):
    lines = [l for l in block.splitlines() if l.startswith("|")]
    if len(lines) >= 2 and lines[1].startswith("|---"):
        n_tab += 1
        w = lines[0].count("|")
        bad += sum(1 for l in lines if l.count("|") != w)
ck(f"{n_tab} markdown tables, all rows have consistent column counts", n_tab > 30 and bad == 0)

# 3. legacy reproduction
ck("source 85/112", sig(f"{OUT}/by_source/source_tests.csv") == (85, 112))
ck("legacy visibility 6/93", sig(f"{OUT}/by_legacy/visibility_481/legacy_visibility_tests.csv") == (6, 93))
ck("legacy latency 0/72", sig(f"{OUT}/by_legacy/latency_708/legacy_latency_tests.csv") == (0, 72))
ck("within-discipline 4/705", sig(f"{OUT}/by_source/within_discipline_tests.csv") == (4, 705))
g = json.load(open(f"{OUT}/by_visibility/citation_gap_S19_S23.json"))
ck("S19-S23 101 cells / 32 suppressed / 7 models",
   len(g) == 101 and sum(1 for r in g if r["suppressed"]) == 32 and len({r["model"] for r in g}) == 7)

# 4. audit facts vs manifest
man = json.load(open(f"{OUT}/MANIFEST.json"))
audit = open(f"{OUT}/metadata_audit.md").read()
for key, label in (("n_events_with_citations", "citations"), ("n_events_with_latency", "latency"),
                   ("n_events_with_editorial_latency", "editorial latency")):
    v = man[key]
    ck(f"audit quotes {label} coverage {v:,}", f"{v:,}" in audit)
ck("audit quotes snapshot date", man["metadata_snapshot_date"] in audit)
ck("response quotes snapshot date", man["metadata_snapshot_date"] in resp)
for dim in ("visibility", "vis_rate", "latency", "lat_review"):
    ck(f"{dim} tables exist with all three partitions",
       {r["partition"] for r in csv.DictReader(open(f"{man['dimensions'][dim]['outdir']}/{dim}_cells.csv"))}
       >= {"pre", "post", "overall"})

# 5. suppression honoured everywhere
leak = 0
for dim, spec in man["dimensions"].items():
    p = f"{spec['outdir']}/{dim}_cells.csv"
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            if int(r["n_obs"]) < man["min_n"] and r["suppressed"] != "1":
                leak += 1
ck("no cell below min_n carries an unsuppressed estimate", leak == 0)
ck("response prints no unsuppressed n<20 cell",
   not re.search(r"\d\.\d{3} \[[^\]]+\] \((?:1?\d)\)", resp))

print(f"\n{checks - len(fails)}/{checks} passed")
if fails:
    print("FAILURES:")
    for f in fails:
        print("  -", f)
sys.exit(1 if fails else 0)
