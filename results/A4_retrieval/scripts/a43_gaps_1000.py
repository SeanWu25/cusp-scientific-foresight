"""
A4.3 — fixed-evidence-packet knowledge and forecasting gaps on all 1,000 events
(first 500 = results_sonnet5_run1/subset500_ids.txt; 500 added 2026-10-18 = ext500/, a43_ext_sample.py).

knowledge gap = fixed WS+Cutoff − base; forecasting gap = fixed WS − fixed WS+Cutoff (what Figure 3a plots).
Base = the Table 1 base run of each model (original-corpus report + Apr-Aug 2026 extension report).
Definitions as run_evaluation/gap_decomposition.py: post = publication month > cutoff month, pre = otherwise;
ids present in all three conditions; retrieval-failed rows dropped from the fixed runs; paired normal 95% CIs;
cells with n < 20 suppressed. The original-setup comparison (fixed − original) stays on the first 500 only
(a43_gaps.py / a43_pre_post_correlation.py), because the original self-query runs exist only for those events.

Writes tables/A4_3_gaps_fixed1000.json and A4_3_fixed_queries/gaps_fixed1000.md
"""
import json, sys, collections, math
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a42_common import ROOT, OUT, A43_SETS, load_events
from a43_ext_sample import BASES
sys.path.insert(0, str(ROOT / "run_evaluation")); import gap_decomposition as GD
TASKS = [("Binary", "binary"), ("Binary (pert.)", "binary_perturbed"), ("MCQ", "mcq"), ("FRQ (0-10)", "frq"), ("Date (0-1)", "date")]
MODELS = [("gpt4o", "GPT-4o", "2023-10"), ("llama33", "LLaMA 3.3 70B", "2023-12"), ("claude45", "Claude S4.5", "2025-01"),
          ("gpt54", "GPT-5.4", "2025-08"), ("sonnet5", "Claude Sonnet 5", "2026-01"), ("sol", "GPT-5.6 Sol", "2026-02")]
def load_fixed(mk, cond):
    d = {}
    for s, (ids_file, d3) in A43_SETS.items():
        p = d3 / "reports" / f"{mk}_{cond}.json"
        if p.exists():
            keep = {l.strip() for l in open(ids_file) if l.strip()}
            d.update({i: v for i, v in GD.load(str(p)).items() if i in keep})
    return d
def compute(pub, setof, only=None):
    """cells for all events (only=None) or for one event set ("main" / "ext500")."""
    cells = []
    for mk, name, cut in MODELS:
        B = {}
        for p in BASES[mk]: B.update(GD.load(str(ROOT / p), drop_retrieval_failures=False))
        FC, FW = load_fixed(mk, "fixed_ws_cutoff"), load_fixed(mk, "fixed_ws")
        shared = {i for i in set(B) & set(FC) & set(FW) & set(setof) if only is None or setof[i] == only}
        for scope in ("post", "pre"):
            ids = sorted(i for i in shared if (pub[i][:7] > cut) == (scope == "post"))
            ev_n = dict(collections.Counter(setof[i] for i in ids))
            for label, task in TASKS:
                b, fc, fw = [], [], []
                for i in ids:
                    v = (GD.field(B[i], task, "score"), GD.field(FC[i], task, "score"), GD.field(FW[i], task, "score"))
                    if any(x is None for x in v): continue
                    b.append(v[0]); fc.append(v[1]); fw.append(v[2])
                cell = dict(model=name, model_key=mk, cutoff=cut, scope=scope, task=label, n=len(b), n_events=len(ids), n_events_by_set=ev_n)
                if len(b) >= 20:
                    b, fc, fw = map(np.array, (b, fc, fw)); kf, ff = fc - b, fw - fc
                    cell.update(mean_base=float(b.mean()), mean_wscut_fixed=float(fc.mean()), mean_ws_fixed=float(fw.mean()),
                                know_fixed=float(kf.mean()), know_fixed_ci=list(GD.paired_ci(list(kf))), fore_fixed=float(ff.mean()), fore_fixed_ci=list(GD.paired_ci(list(ff))))
                else: cell["suppressed"] = True
                cells.append(cell)
    return cells

def fam_rows(cells, scope, models):
    J = {(c["scope"], c["task"], c["model"]): c for c in cells}; out = []
    for mk, name, cut in models:
        row = []
        for fam, ts, sc in FAM:
            cs = [J.get((scope, t, name)) for t in ts]
            row.append("—" if any(c is None or c.get("suppressed") for c in cs) else
                       f"{np.mean([c['know_fixed'] for c in cs]) / sc:+.3f} / {np.mean([c['fore_fixed'] for c in cs]) / sc:+.3f}")
        out.append(f"| {name} | " + " | ".join(row) + " |")
    return out

# Figure 3a task families as make_fig3_overleaf.py draws them (Feasibility = mean of the original and perturbed binary
# gaps; Solution Design = FRQ / 10); a family is omitted if any member cell has n < 20.
FAM = [("Feasibility Assessment", ("Binary", "Binary (pert.)"), 1.0), ("Mechanistic Forecasting", ("MCQ",), 1.0),
       ("Temporal Prediction", ("Date (0-1)",), 1.0), ("Solution Design", ("FRQ (0-10)",), 10.0)]

def main():
    ev = load_events(); pub = {i: r["publication_date"] for i, r in ev.items()}
    setof = {}
    for s, (ids_file, _) in A43_SETS.items():
        for l in open(ids_file):
            if l.strip(): setof[l.strip()] = s
    cells = compute(pub, setof)
    json.dump(cells, open(OUT / "tables/A4_3_gaps_fixed1000.json", "w"), indent=1)
    f = lambda v, ci: f"{v:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}]"
    L = ["# A4.3 — fixed-evidence-packet gaps on 1,000 events (first 500 + 500 added 2026-10-18)", "", "Knowledge gap = " + __doc__.split("knowledge gap =")[1].split("Writes")[0].replace("\n", " ").strip(), "",
         "## Events per model", "", "| model | cutoff | pre-cutoff events | post-cutoff events | post-cutoff: first 500 | post-cutoff: added 500 |", "|---|---|---|---|---|---|"]
    for mk, name, cut in MODELS:
        pre = next(c for c in cells if c["model_key"] == mk and c["scope"] == "pre"); post = next(c for c in cells if c["model_key"] == mk and c["scope"] == "post")
        L.append(f"| {name} | {cut} | {pre['n_events']} | {post['n_events']} | {post['n_events_by_set'].get('main', 0)} | {post['n_events_by_set'].get('ext500', 0)} |")
    for scope, title in (("post", "Post-cutoff events (the paper's convention; Figure 3a)"), ("pre", "Pre-cutoff events (recall regime; supplementary)")):
        L += ["", f"## {title}", "", "| model | task | n | base | WS+Cutoff (fixed) | WS (fixed) | knowledge gap [95% CI] | forecasting gap [95% CI] |", "|---|---|---|---|---|---|---|---|"]
        for c in cells:
            if c["scope"] != scope or c["n"] == 0: continue
            if c.get("suppressed"): L.append(f"| {c['model']} | {c['task']} | {c['n']} | suppressed (n<20) | | | | |"); continue
            L.append(f"| {c['model']} | {c['task']} | {c['n']} | {c['mean_base']:.3f} | {c['mean_wscut_fixed']:.3f} | {c['mean_ws_fixed']:.3f} | {f(c['know_fixed'], c['know_fixed_ci'])} | {f(c['fore_fixed'], c['fore_fixed_ci'])} |")
    for scope in ("post", "pre"):
        L += ["", f"## Figure 3a values, {scope}-cutoff (knowledge gap / forecasting gap; FRQ on 0-1)", "", "| model | " + " | ".join(f[0] for f in FAM) + " |", "|---|" + "---|" * len(FAM)]
        L += fam_rows(cells, scope, MODELS)
    for only, title in (("main", "first 500 only"), ("ext500", "added 500 only")):
        sub = compute(pub, setof, only); json.dump(sub, open(OUT / f"tables/A4_3_gaps_fixed1000_{only}.json", "w"), indent=1)
        L += ["", f"## Consistency check: post-cutoff Figure 3a values, {title}", "", "| model | " + " | ".join(f[0] for f in FAM) + " |", "|---|" + "---|" * len(FAM)]
        L += fam_rows(sub, "post", MODELS)
    (OUT / "A4_3_fixed_queries/gaps_fixed1000.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:14]))
if __name__ == "__main__": main()
