"""
A4.3 step 4 — score the fixed-query runs with the repo's own report builder, then compute
knowledge gap (WS+Cutoff − base) and forecasting gap (WS − WS+Cutoff) under the ORIGINAL
(self-generated queries) and FIXED-QUERY setups on the same events, with paired CIs, and
the difference between setups (event bootstrap). Definitions and loaders are imported
from run_evaluation/gap_decomposition.py (unmodified): post-cutoff = publication_date >
cutoff month; ids shared by all conditions; retrieval-failed rows dropped.
Writes gaps.csv, results.md, tables/A4_3_gaps.json, figures/a43_gaps.png.
"""
import json, csv, os, subprocess, sys, math, statistics, collections
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); from a42_common import *
sys.path.insert(0, str(ROOT / "run_evaluation")); import gap_decomposition as GD
PY = "python3"; BENCH = ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl"
FR = ROOT / "run_evaluation/frq_results"
ORIG = {  # model_key: (name, cutoff, base, ws, wscut) — the original experiment's reports
    "gpt4o":    ("GPT-4o", "2023-10", FR / "gpt_4o_reeval.json", FR / "gpt_4o_web_search_no_cutoff_500.json", FR / "gpt-4o_web_search_with_cutoff_500.json"),
    "gpt54":    ("GPT-5.4", "2025-08", FR / "gpt_5_4_eval.json", FR / "gpt_5_4_web_subset_eval.json", FR / "gpt_5_4_500_web_cutoff.json"),
    "llama33":  ("LLaMA 3.3 70B", "2023-12", FR / "llama_3_3_full.json", ROOT / "results_llama33_run1/reports/ws_500.json", ROOT / "results_llama33_run1/reports/ws_cutoff_500.json"),  # ws run generated 2026-10-05 (same harness/endpoint as its ws_cutoff run)
    "deepseek_r1": ("DeepSeek R1", "2024-07", FR / "deepseek_r1.json", FR / "deepseek_r1_500_no_cutoff.json", FR / "deepseek_r1_500_web_cutoff.json"),  # fixed-packet runs added 2026-10 (Together endpoint)
    "claude45": ("Claude S4.5", "2025-01", FR / "claude_sonnet.json", FR / "claude_500_with_full.json", FR / "claude_500_with_cutoff.json"),
    "sonnet5":  ("Claude Sonnet 5", "2026-01", ROOT / "results_sonnet5_run1/reports/base_medium_run1.json", ROOT / "results_sonnet5_run1/reports/ws_500.json", ROOT / "results_sonnet5_run1/reports/ws_cutoff_500.json"),
    "sol":      ("GPT-5.6 Sol", "2026-02", ROOT / "results_sol_run1/reports/base_medium_run1.json", ROOT / "results_sol_run1/reports/ws_500.json", ROOT / "results_sol_run1/reports/ws_cutoff_500.json"),
}
TASKS = [("Binary", "binary"), ("Binary (pert.)", "binary_perturbed"), ("MCQ", "mcq"), ("FRQ (0-10)", "frq"), ("Date (0-1)", "date")]
D3 = OUT / "A4_3_fixed_queries"; RP = D3 / "reports"; RP.mkdir(exist_ok=True)

def build_reports():
    by = collections.defaultdict(list)
    for l in open(D3 / "model_outputs.jsonl"):
        r = json.loads(l)
        if r.get("fatal_error"): continue
        by[(r["model_key"], r["condition"])].append(r)
    for (m, c), rows in by.items():
        pred = RP / f"pred_{m}_{c}.jsonl"
        with open(pred, "w") as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        rep = RP / f"{m}_{c}.json"
        # FRQ: stage-2 rubric scores (legacy rubric, judged 2026-10-04 by a43_judge_frq.sh + a43_finalize_frq.sh) are
        # included whenever the merged judgement file exists; before that the FRQ task was generated but unscored.
        judged = D3 / "judgements_merged" / f"{m}_{c}.jsonl"
        extra = ["--judged", str(judged), "--frq-scores", "include"] if judged.exists() else []
        subprocess.run([PY, str(ROOT / "scripts/build_report.py"), "--predictions", str(pred), "--benchmark", str(BENCH), "--out", str(rep)] + extra, check=True, capture_output=True)
        print(f"  report {m} {c}: {len(rows)} rows", file=sys.stderr)

def boot_ci(diffs, B=10000, seed=0):
    d = np.asarray(diffs, float); rng = np.random.default_rng(seed); idx = rng.integers(0, len(d), (B, len(d))); m = d[idx].mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float(min(1, 2 * min((m <= 0).mean(), (m >= 0).mean())))

def main():
    build_reports()
    pub = {i: r["publication_date"] for i, r in load_events().items()}
    rows_out = []; results = {}
    for mk, (name, cut, base, ws, wscut) in ORIG.items():
        fws, fwscut = RP / f"{mk}_fixed_ws.json", RP / f"{mk}_fixed_ws_cutoff.json"
        if not (fws.exists() and fwscut.exists() and base.exists() and wscut.exists()):
            print(f"  skip {name}: missing reports", file=sys.stderr); continue
        B = GD.load(str(base), drop_retrieval_failures=False); C = GD.load(str(wscut)); FC = GD.load(str(fwscut)); FW = GD.load(str(fws))
        W = GD.load(str(ws)) if ws and ws.exists() else None
        shared = set(B) & set(C) & set(FC) & set(FW) & (set(W) if W else set(FW))
        for scope in ("post", "all"):
            ids = sorted(i for i in shared if (scope == "all" or pub.get(i, "") > cut))
            for label, task in TASKS:
                vals = collections.defaultdict(list)
                for i in ids:
                    v = dict(b=GD.field(B[i], task, "score"), c=GD.field(C[i], task, "score"), fc=GD.field(FC[i], task, "score"), fw=GD.field(FW[i], task, "score"), w=(GD.field(W[i], task, "score") if W else None))
                    if any(v[k] is None for k in ("b", "c", "fc", "fw")) or (W and v["w"] is None): continue
                    for k, x in v.items():
                        if x is not None: vals[k].append(x)
                n = len(vals["b"]); cell = dict(model=name, model_key=mk, cutoff=cut, scope=scope, task=label, n=n)
                if n >= 20:
                    b, c, fc, fw = (np.array(vals[k]) for k in ("b", "c", "fc", "fw")); w = np.array(vals["w"]) if W else None
                    know_o, know_f = c - b, fc - b; fore_f = fw - fc
                    cell.update(know_orig=float(know_o.mean()), know_orig_ci=list(GD.paired_ci(list(know_o))), know_fixed=float(know_f.mean()), know_fixed_ci=list(GD.paired_ci(list(know_f))),
                                fore_fixed=float(fore_f.mean()), fore_fixed_ci=list(GD.paired_ci(list(fore_f))),
                                mean_base=float(b.mean()), mean_wscut_orig=float(c.mean()), mean_wscut_fixed=float(fc.mean()), mean_ws_fixed=float(fw.mean()))
                    lo, hi, p = boot_ci(know_f - know_o); cell.update(diff_know=float((know_f - know_o).mean()), diff_know_ci=[lo, hi], diff_know_p=p)
                    if W is not None:
                        fore_o = w - c; cell.update(fore_orig=float(fore_o.mean()), fore_orig_ci=list(GD.paired_ci(list(fore_o))), mean_ws_orig=float(w.mean()))
                        lo, hi, p = boot_ci(fore_f - fore_o); cell.update(diff_fore=float((fore_f - fore_o).mean()), diff_fore_ci=[lo, hi], diff_fore_p=p)
                else:
                    cell["suppressed"] = True
                rows_out.append(cell); results.setdefault(name, {}).setdefault(scope, {})[label] = cell
    keys = ["model", "cutoff", "scope", "task", "n", "mean_base", "mean_wscut_orig", "mean_ws_orig", "mean_wscut_fixed", "mean_ws_fixed", "know_orig", "know_orig_ci", "know_fixed", "know_fixed_ci", "diff_know", "diff_know_ci", "diff_know_p", "fore_orig", "fore_orig_ci", "fore_fixed", "fore_fixed_ci", "diff_fore", "diff_fore_ci", "diff_fore_p", "suppressed"]
    with open(D3 / "gaps.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); wr.writeheader()
        for r in rows_out: wr.writerow({k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()})
    json.dump(results, open(OUT / "tables/A4_3_gaps.json", "w"), indent=1)
    # results.md
    def f(v, ci=None): return "—" if v is None else (f"{v:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}]" if ci else f"{v:+.3f}")
    L = ["# A4.3 — Fixed queries from a model outside the panel", "",
         "Queries: one per event, written by Claude Opus 4.8 with the same combined-query prompt as the original pipeline (`queries.jsonl`). Evidence: one You.com call per event and per freshness bound, "
         "filtered and formatted by the unmodified `scripts/web_search.py` code (`evidence/<bound>.jsonl`); every evaluated model received the SAME retrieved text for a given bound. Models were run with the "
         "unmodified harness code path (`scripts/run_cusp.py process_row`) and their original decoding parameters; scored with the frozen scoring code via `scripts/build_report.py`. "
         "Gaps follow `run_evaluation/gap_decomposition.py`: knowledge gap = WS+Cutoff − base, forecasting gap = WS − WS+Cutoff, post-cutoff events (publication month > cutoff month), "
         "ids shared by every condition, retrieval-failed rows dropped, paired normal 95% CIs; the between-setup difference carries a 10k item-bootstrap CI and two-sided p. FRQ is scored with the legacy stage-2 rubric on a 0-10 scale (judged 2026-10-04; the fixed-packet FRQ answers were capped at 250 tokens for GPT-4o, GPT-5.4 and Claude S4.5, 384 for Sonnet 5, 2048 otherwise). "
         "Original-setup numbers are recomputed on exactly the same events, so they can differ slightly from the published table. Cells with n < 20 are suppressed.", ""]
    for scope, title in (("post", "Post-cutoff events (the paper's convention)"), ("all", "All shared events (pre- and post-cutoff; supplementary, mostly recall for late-cutoff models)")):
        L += [f"\n## {title}\n", "| model | task | n | knowledge gap: original | knowledge gap: fixed queries | fixed − original [CI] (p) | forecasting gap: original | forecasting gap: fixed | fixed − original [CI] (p) |", "|---|---|---|---|---|---|---|---|---|"]
        for r in rows_out:
            if r["scope"] != scope: continue
            if r.get("suppressed"): L.append(f"| {r['model']} | {r['task']} | {r['n']} | suppressed (n<20) | | | | | |"); continue
            L.append(f"| {r['model']} | {r['task']} | {r['n']} | {f(r['know_orig'], r['know_orig_ci'])} | {f(r['know_fixed'], r['know_fixed_ci'])} | {f(r['diff_know'], r['diff_know_ci'])} ({r['diff_know_p']:.2g}) | {f(r.get('fore_orig'), r.get('fore_orig_ci'))} | {f(r['fore_fixed'], r['fore_fixed_ci'])} | {f(r.get('diff_fore'), r.get('diff_fore_ci'))}{(' (%.2g)' % r['diff_fore_p']) if r.get('diff_fore_p') is not None else ''} |")
    (D3 / "results.md").write_text("\n".join(L) + "\n")
    # figure
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    post = [r for r in rows_out if r["scope"] == "post" and not r.get("suppressed")]
    if post:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.6)); models = list(dict.fromkeys(r["model"] for r in post)); tasks = [t for t, _ in TASKS]
        cols = {"Binary": "#0072B2", "Binary (pert.)": "#56B4E9", "MCQ": "#D55E00", "FRQ (0-10)": "#CC79A7", "Date (0-1)": "#009E73"}
        for ax, (gk, title) in zip(axes, (("know", "knowledge gap (WS+Cutoff − base)"), ("fore", "forecasting gap (WS − WS+Cutoff)"))):
            for ti, t in enumerate(tasks):
                for mi, m in enumerate(models):
                    r = next((x for x in post if x["model"] == m and x["task"] == t), None)
                    if not r or r.get(f"{gk}_orig") is None: continue
                    x = mi + (ti - (len(tasks) - 1) / 2) * 0.15
                    ax.errorbar(x - 0.04, r[f"{gk}_orig"], yerr=[[r[f"{gk}_orig"] - r[f"{gk}_orig_ci"][0]], [r[f"{gk}_orig_ci"][1] - r[f"{gk}_orig"]]], fmt="o", color=cols[t], ms=4, mfc="white", capsize=2, lw=1, label=f"{t} (original)" if mi == 0 else None)
                    ax.errorbar(x + 0.04, r[f"{gk}_fixed"], yerr=[[r[f"{gk}_fixed"] - r[f"{gk}_fixed_ci"][0]], [r[f"{gk}_fixed_ci"][1] - r[f"{gk}_fixed"]]], fmt="s", color=cols[t], ms=4, capsize=2, lw=1, label=f"{t} (fixed queries)" if mi == 0 else None)
            ax.axhline(0, color="#888888", lw=0.8, ls="--"); ax.set_xticks(range(len(models))); ax.set_xticklabels(models, fontsize=7, rotation=20); ax.set_title(title, fontsize=9); ax.tick_params(labelsize=7); ax.grid(color="#EEEEEE", lw=0.5)
            ax.legend(fontsize=6, ncol=2, frameon=False)
        fig.suptitle("Post-cutoff gaps under self-generated (open markers) vs fixed external (filled) queries; bars = paired 95% CI", fontsize=8); fig.tight_layout(); fig.savefig(OUT / "figures/a43_gaps.png", dpi=200); fig.savefig(OUT / "figures/a43_gaps.pdf"); plt.close(fig)
    print("\n".join(L[:40]))
if __name__ == "__main__": main()
