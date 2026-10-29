#!/usr/bin/env python3
"""
revision_facts.py — every number quoted in the main-text Results, computed from the stored reports.
  --corpus orig --six   reproduces the submitted manuscript (check)
  --corpus full         revision: nine models (Table 1 set), original + Apr-Aug 2026 extension; DeepSeek R1 original only
Population: post-cutoff (pub month > cutoff month; >= with CUTOFF_MONTH_PRE = False) unless a key says _all. Output JSON on stdout.
"""
import argparse, json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "run_evaluation")); import make_table1_overleaf as T
# Cutoff-month rule (2026-10-25): an event published in the model's knowledge-cutoff month counts as PRE-cutoff
# (post iff pub_month > cutoff_month), as in Table 1 and the information-access gaps. False = old rule (cutoff month = post).
CUTOFF_MONTH_PRE = True


def ece(pairs, nb=10):
    if not pairs: return None
    bins = defaultdict(list)
    for c, y in pairs: bins[min(int(c * nb), nb - 1)].append((c, y))
    return sum(len(b) / len(pairs) * abs(st.fmean(x for x, _ in b) - st.fmean(y for _, y in b)) for b in bins.values())


def run(corpus, six):
    pub, area = {}, {}
    for b in T.BENCH[: 1 if corpus == "orig" else 2]:
        for l in open(ROOT / b):
            if l.strip(): r = json.loads(l); pub[r["id"]] = str(r["publication_date"])[:7]; area[r["id"]] = r["main_area"]
    out = {"models": {}}
    for name, cut, icon, op, ep, new in T.MODELS:
        if six and new: continue
        cm = T.mo(cut); seen = set()
        acc = defaultdict(lambda: defaultdict(list))
        for p in [op] + ([ep] if corpus == "full" and ep else []):
            for r in json.load(open(ROOT / p))["results"]:
                if r["id"] in seen or r["id"] not in pub: continue
                seen.add(r["id"]); part = "post" if ((T.mo(pub[r["id"]]) > cm) if CUTOFF_MONTH_PRE else (T.mo(pub[r["id"]]) >= cm)) else "pre"; t = r.get("tasks", {})
                for P in (part, "all"):
                    for task in ("binary", "binary_perturbed"):
                        v = t.get(task)
                        if v and not v.get("skipped") and "correct" in v:
                            acc[P]["bin"].append(1.0 if v["correct"] else 0.0)
                            ans = str(v.get("parsed_answer", "")).lower()
                            if ans in ("yes", "no"): acc[P]["yes"].append(1.0 if ans == "yes" else 0.0)
                            if v.get("confidence") is not None: acc[P]["bin_cal"].append((float(v["confidence"]), 1.0 if v["correct"] else 0.0))
                            acc[P][task].append(1.0 if v["correct"] else 0.0)
                    v = t.get("mcq")
                    if v and not v.get("skipped") and "correct" in v:
                        acc[P]["mcq"].append(1.0 if v["correct"] else 0.0)
                        if v.get("confidence") is not None: acc[P]["mcq_cal"].append((float(v["confidence"]), 1.0 if v["correct"] else 0.0))
                    v = t.get("frq")
                    if v and not v.get("skipped") and v.get("score") is not None:
                        acc[P]["frq"].append(float(v["score"]))
                        for d in ("alignment", "specificity", "novelty", "feasibility"):
                            if v.get(d) is not None: acc[P][f"frq_{d}"].append(float(v[d]))
                    v = t.get("date")
                    if v and not v.get("skipped") and v.get("score") is not None:
                        acc[P]["date"].append(float(v["score"]))
                        pd, gt = T.mo(v.get("parsed_date")), T.mo(v.get("ground_truth"))
                        if pd is not None and gt is not None: acc[P]["err"].append(pd - gt); acc[P]["gt"].append(gt)
        m = {}
        for P in ("post", "all"):
            a = acc[P]; f = lambda k: st.fmean(a[k]) if a.get(k) else None
            d = dict(binary=f("bin"), yes_rate=f("yes"), acc_orig=f("binary"), acc_pert=f("binary_perturbed"), mcq=f("mcq"), frq=f("frq"),
                     **{f"frq_{k}": f(f"frq_{k}") for k in ("alignment", "specificity", "novelty", "feasibility")}, date=f("date"),
                     err_mean=f("err"), err_median=(st.median(a["err"]) if a.get("err") else None),
                     ece_bin=ece(a.get("bin_cal", [])), ece_mcq=ece(a.get("mcq_cal", [])), n_bin=len(a.get("bin", [])))
            # constant baseline: always predict the mean ground-truth month of this model's post-cutoff date events
            if a.get("gt"):
                mu = round(st.fmean(a["gt"])); d["const_date"] = st.fmean(math.exp(-0.1 * abs(g - mu)) for g in a["gt"])
            if d["acc_orig"] is not None and d["acc_pert"] is not None: d["bias_index"] = d["acc_orig"] - d["acc_pert"]
            m[P] = d
        out["models"][name] = m
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="full"); ap.add_argument("--six", action="store_true"); a = ap.parse_args()
    print(json.dumps(run(a.corpus, a.six), indent=1, default=lambda x: round(x, 4) if isinstance(x, float) else x))
