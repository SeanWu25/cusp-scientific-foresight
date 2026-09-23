#!/usr/bin/env python3
"""
a5_verify.py -- assert that every figure quoted in response_A5.md still matches
the regenerated tables. Exits non-zero on any mismatch.
"""
import csv, json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
resp = open(f"{OUT}/response_A5.md").read()
tab = open(f"{OUT}/tables/A5_tables.md").read()
wd_md = open(f"{OUT}/by_source/within_discipline.md").read()
fails, checks = [], 0


def ck(desc, cond):
    global checks
    checks += 1
    if not cond:
        fails.append(desc)
    print(("PASS " if cond else "FAIL ") + desc)


def sig(dim):
    rows = list(csv.DictReader(open(f"{OUT}/by_{dim}/{dim}_tests.csv")))
    return sum(1 for r in rows if float(r["p_holm"]) < 0.05), len(rows)


def row_of(section, task):
    blk = tab.split(f"## {section}")[1].split("\n## ")[0]
    for line in blk.splitlines():
        if line.startswith(f"| {task} |"):
            return [x.strip() for x in line.strip().strip("|").split("|")][1:]
    return None


def vals(section, task, k):
    return [c.split(" ")[0] for c in row_of(section, task)[:k]]


ck("source 85/112", sig("source") == (85, 112) and "85 of 112" in resp)
ck("visibility 6/93", sig("visibility") == (6, 93) and "6 of 93" in resp)
ck("latency 0/72", sig("latency") == (0, 72) and "0 of 72" in resp)
wd = list(csv.DictReader(open(f"{OUT}/by_source/within_discipline_tests.csv")))
ck("within-discipline 4/705",
   (sum(1 for r in wd if float(r["p_holm"]) < 0.05), len(wd)) == (4, 705)
   and "4 of 705" in resp)
vrows = [r for r in csv.DictReader(open(f"{OUT}/by_visibility/visibility_tests.csv"))
         if r["task"] != "date"]
ck("visibility non-date 0/71",
   len(vrows) == 71 and sum(1 for r in vrows if float(r["p_holm"]) < 0.05) == 0
   and "0 of 71" in resp)

S = "Source / Venue — OVERALL-cutoff"
ck("source overall binary", vals(S, "Binary (bal. acc)", 6)
   == ["0.517", "0.508", "0.519", "0.512", "0.525", "0.679"]
   and "| Binary (bal. acc) | 0.517 | 0.508 | 0.519 | 0.512 | 0.525 | **0.679** |" in resp)
ck("source overall mcq", vals(S, "MCQ (acc)", 6)
   == ["0.711", "0.685", "0.696", "0.683", "0.700", "0.529"]
   and "| MCQ (acc) | 0.711 | 0.685 | 0.696 | 0.683 | 0.700 | **0.529** |" in resp)
ck("source overall date", vals(S, "Date (score)", 6)
   == ["0.280", "0.248", "0.291", "0.502", "0.538", "0.464"]
   and "| Date (score) | 0.280 | 0.248 | 0.291 | **0.502** | **0.538** | 0.464 |" in resp)
ck("source overall frq", vals(S, "FRQ (0-10)", 5)
   == ["4.16", "4.10", "4.32", "4.32", "4.34"]
   and "| FRQ (0–10) | 4.16 | 4.10 | 4.32 | 4.32 | 4.34 | no items |" in resp)

for task, exp, line in [
    ("Binary (bal. acc)", ["0.528", "0.509", "0.517", "0.521"],
     "| Binary (bal. acc) | 0.528 | 0.509 | 0.517 | 0.521 | 0 / 10 |"),
    ("MCQ (acc)", ["0.693", "0.712", "0.703", "0.740"],
     "| MCQ (acc) | 0.693 | 0.712 | 0.703 | 0.740 | 0 / 10 |"),
    ("Date (score)", ["0.319", "0.346", "0.298", "0.338"],
     "| Date (score) | 0.319 | 0.346 | 0.298 | 0.338 | 4 / 10 |"),
    ("FRQ (0-10)", ["4.26", "4.20", "4.27", "4.18"],
     "| FRQ (0–10) | 4.26 | 4.20 | 4.27 | 4.18 | 0 / 10 |")]:
    ck(f"visibility overall {task}",
       vals("Citation Quartile — OVERALL-cutoff", task, 4) == exp and line in resp)

for task, exp, line in [
    ("Binary (bal. acc)", ["0.499", "0.510", "0.519"],
     "| Binary (bal. acc) | 0.499 | 0.510 | 0.519 | 0 / 9 |"),
    ("MCQ (acc)", ["0.722", "0.658", "0.732"],
     "| MCQ (acc) | 0.722 | 0.658 | 0.732 | 0 / 9 |"),
    ("Date (score)", ["0.277", "0.267", "0.274"],
     "| Date (score) | 0.277 | 0.267 | 0.274 | 0 / 9 |"),
    ("FRQ (0-10)", ["4.12", "4.11", "4.27"],
     "| FRQ (0–10) | 4.12 | 4.11 | 4.27 | 0 / 9 |")]:
    ck(f"latency overall {task}",
       vals("Publication Latency — OVERALL-cutoff", task, 3) == exp and line in resp)

for disc, n, t, s in [("Biology", "1,438", "110", "2"),
                      ("Artificial Intelligence", "1,181", "95", "1"),
                      ("Medicine", "878", "105", "0"),
                      ("Materials Science", "460", "110", "1"),
                      ("Physics", "444", "98", "0"),
                      ("Neuroscience", "379", "93", "0"),
                      ("Chemistry", "226", "94", "0")]:
    ck(f"within-discipline row {disc}",
       f"| {n} | {t} | **{s}** |" in wd_md and f"| {n} | {t} | {s} |" in resp)

g = json.load(open(f"{OUT}/by_visibility/citation_gap_S19_S23.json"))
ck("S19-S23 101 cells / 32 suppressed / 7 models",
   len(g) == 101 and sum(1 for r in g if r["suppressed"]) == 32
   and len({r["model"] for r in g}) == 7
   and "101 cells, **32 are" in resp and "three models to the seven" in resp)
for s in ("481", "2026-05-12", "708", "34 of 1,274", "8.6%", "12.7%"):
    ck(f"metadata fact {s!r} present", s in resp)

print(f"\n{checks - len(fails)}/{checks} passed")
if fails:
    print("FAILURES:")
    for f in fails:
        print("  -", f)
sys.exit(1 if fails else 0)
