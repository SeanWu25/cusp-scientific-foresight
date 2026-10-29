#!/usr/bin/env python3
"""Numbers for the revised main-text Results (sean.tex): nine models, full corpus. Definitions match the submitted text
(checked on the original corpus): overall metrics post-cutoff; FRQ sub-dimensions and response priors over all events;
ECE as in the calibration figure (equal-width bins on [0.5,1) binary and [0.25,1) MCQ, all events); date median error and
constant baseline post-cutoff; domain values = post-cutoff cross-model means (Figure 3b)."""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
# Cutoff-month rule (2026-10-25): an event published in the model's knowledge-cutoff month counts as PRE-cutoff
# (post iff pub_month > cutoff_month), as in Table 1 and the information-access gaps. False = old rule (cutoff month = post).
CUTOFF_MONTH_PRE = True
def fece(cal, lo, n=10):
    tot = len(cal); e = 0; edges = [lo + (1 - lo) * i / n for i in range(n + 1)]
    for a, b in zip(edges[:-1], edges[1:]):
        pts = [(c, v) for c, v in cal if a <= c < b]
        if pts: e += len(pts) / tot * abs(st.fmean(v for _, v in pts) - st.fmean(c for c, _ in pts))
    return e
pub, area = {}, {}
for b in T.BENCH:
    for l in open(ROOT / b):
        if l.strip(): r = json.loads(l); pub[r["id"]] = r["publication_date"][:7]; area[r["id"]] = r["main_area"]
F = {"models": {}, "domains": {}}; dom = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
nbin_all = nno_all = 0
for name, cut, icon, op, ep, new in T.MODELS:
    cm = T.mo(cut); seen = set(); A = defaultdict(lambda: defaultdict(list))
    for p in [op] + ([ep] if ep else []):
        for r in json.load(open(ROOT / p))["results"]:
            if r["id"] in seen or r["id"] not in pub: continue
            seen.add(r["id"]); post = (T.mo(pub[r["id"]]) > cm) if CUTOFF_MONTH_PRE else (T.mo(pub[r["id"]]) >= cm); t = r.get("tasks", {}); ar = area[r["id"]]
            for P in ("all",) + (("post",) if post else ()):
                for k in ("binary", "binary_perturbed"):
                    v = t.get(k)
                    if v and not v.get("skipped") and "correct" in v:
                        A[P]["bin"].append(1.0 if v["correct"] else 0.0); A[P][k].append(1.0 if v["correct"] else 0.0)
                        ans = str(v.get("parsed_answer", "")).lower()
                        if ans in ("yes", "no"): A[P]["yes"].append(1.0 if ans == "yes" else 0.0)
                        if v.get("confidence") is not None: A[P]["bcal"].append((float(v["confidence"]), 1.0 if v["correct"] else 0.0))
                        if P == "post": dom[name][ar]["bin"].append(1.0 if v["correct"] else 0.0)
                v = t.get("mcq")
                if v and not v.get("skipped") and "correct" in v:
                    A[P]["mcq"].append(1.0 if v["correct"] else 0.0)
                    if v.get("confidence") is not None: A[P]["mcal"].append((float(v["confidence"]), 1.0 if v["correct"] else 0.0))
                    if P == "post": dom[name][ar]["mcq"].append(1.0 if v["correct"] else 0.0)
                v = t.get("frq")
                if v and not v.get("skipped") and v.get("score") is not None:
                    A[P]["frq"].append(float(v["score"]))
                    for d in ("alignment", "specificity", "novelty", "feasibility"):
                        if v.get(d) is not None: A[P][d].append(float(v[d]))
                    if P == "post": dom[name][ar]["frq"].append(float(v["score"]))
                v = t.get("date")
                if v and not v.get("skipped") and v.get("score") is not None:
                    A[P]["date"].append(float(v["score"]))
                    if P == "post": dom[name][ar]["date"].append(float(v["score"]))
                    pd, gt = T.mo(v.get("parsed_date")), T.mo(v.get("ground_truth"))
                    if pd is not None and gt is not None: A[P]["err"].append(pd - gt); A[P]["gt"].append(gt)
    f = lambda P, k: st.fmean(A[P][k]) if A[P].get(k) else None
    gt = A["post"]["gt"]; mu = round(st.fmean(gt))
    F["models"][name] = dict(
        binary_post=f("post", "bin"), mcq_post=f("post", "mcq"), frq_post=f("post", "frq"), date_post=f("post", "date"),
        acc_orig_post=f("post", "binary"), acc_pert_post=f("post", "binary_perturbed"),
        yes_rate_all=f("all", "yes"), bias_index_all=(f("all", "binary") - f("all", "binary_perturbed")),
        **{f"{d}_all": f("all", d) for d in ("alignment", "specificity", "novelty", "feasibility")},
        ece_mcq_all=fece(A["all"]["mcal"], .25), ece_bin_all=fece(A["all"]["bcal"], .5),
        err_median_post=st.median(A["post"]["err"]), err_mean_post=st.fmean(A["post"]["err"]),
        const_date_post=st.fmean(math.exp(-0.1 * abs(g - mu)) for g in gt), n_post_bin=len(A["post"]["bin"]))
# always-No baseline over all binary items in the benchmark
for b in T.BENCH:
    for l in open(ROOT / b):
        if l.strip():
            r = json.loads(l); nb = bool(r.get("binary_question")); npz = bool(r.get("binary_question_perturbed"))
            nbin_all += nb + npz; nno_all += npz
F["always_no_all"] = nno_all / nbin_all
AREAS = ["Artificial Intelligence", "Biology", "Chemistry", "Environmental Science", "Materials Science", "Medicine", "Neuroscience", "Physics"]
for ar in AREAS:
    F["domains"][ar] = {k: st.fmean([st.fmean(dom[m][ar][k]) for m in dom if len(dom[m][ar][k]) >= 20]) for k in ("bin", "mcq", "frq", "date")}
json.dump(F, open(ROOT / "manuscript_updates/revision_facts.json", "w"), indent=1)
M = F["models"]
for n, m in sorted(M.items(), key=lambda kv: -kv[1]["mcq_post"]):
    print(f"{n:16s} bin {100*m['binary_post']:.1f} mcq {100*m['mcq_post']:.1f} frq {m['frq_post']:.2f} date {m['date_post']:.3f} | A {m['alignment_all']:.1f} S {m['specificity_all']:.1f} N {m['novelty_all']:.1f} F {m['feasibility_all']:.1f} | eceM {m['ece_mcq_all']:.3f} eceB {m['ece_bin_all']:.3f} | yes {m['yes_rate_all']:.2f} bias {m['bias_index_all']:+.2f} | med {m['err_median_post']:+.0f} mean {m['err_mean_post']:+.1f} | const {m['const_date_post']:.3f}")
print("always-No (all binary items):", round(100 * F["always_no_all"], 2))
for ar, d in F["domains"].items(): print(f"{ar:24s} bin {100*d['bin']:.1f} mcq {100*d['mcq']:.1f} frq {d['frq']:.2f} date {d['date']:.3f}")
