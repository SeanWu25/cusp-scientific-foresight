"""a7_analyze_ab.py — analysis A (code prevalence) and analysis B (code -> outcome link)."""
from __future__ import annotations
import json, sys, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_stats as S, a7_prompts as P

# "binary_merged" pools the original and perturbed variants of the same event. It is the only
# binary outcome that separates discrimination from response bias: ground truth is Yes for every
# original item and No for every perturbed one, so a code that merely pushes a model toward "No"
# scores 0.00 on one variant and 1.00 on the other and cancels here, while a code that tracks the
# actual answer survives. Both single-variant fits are kept, clearly labelled as bias-sensitive.
OUTCOME = {"binary_merged": ("correct", "binomial", "merged binary accuracy (both variants pooled)"),
           "binary": ("correct", "binomial", "accuracy"),
           "binary_perturbed": ("correct", "binomial", "accuracy"),
           "mcq": ("correct", "binomial", "accuracy"),
           "date": ("score", "gaussian", "date score (exp(-0.1 x months off))"),
           "frq": ("frq_score", "gaussian", "FRQ rubric score (0-10)")}


def main():
    rows, coders = S.load_labels()
    rel = set(S.reliable_codes())
    by = collections.defaultdict(list)
    for r in rows:
        by[r["code"]].append(r)
    codes = [c for c in P.ALL_CODES if c in by]

    # ---------------- A: prevalence
    A = C.STUDY / "analyses" / "A_prevalence"
    csv = ["code,scope,model,task,condition,partition,n,rate,lo,hi"]
    def prev(sel, B=1000, seed=0):
        if not sel: return (float("nan"),) * 3 + (0,)
        y = np.array([r["label"] for r in sel], float)
        w = S.boot_events([r["id"] for r in sel], B, seed)
        d = S.wmean(y, w); lo, hi = np.percentile(d, [2.5, 97.5])
        return float(y.mean()), float(lo), float(hi), len(sel)
    tables = {}
    for code in codes:
        if code == "HEDGING": continue
        R = by[code]
        for scope, keyf in (("overall", lambda r: ("all", "all", "all", "all")),
                            ("by_task", lambda r: ("all", r["task"], "base", "all")),
                            ("by_model_task", lambda r: (r["model"], r["task"], "base", "all")),
                            ("by_condition", lambda r: ("all", r["task"], r["condition"], "all")),
                            ("by_partition", lambda r: ("all", r["task"], "base", r["partition"]))):
            g = collections.defaultdict(list)
            for r in R:
                if scope != "overall" and scope != "by_condition" and r["condition"] != "base": continue
                if scope == "by_partition" and r["partition"] is None: continue
                g[keyf(r)].append(r)
            for k, sel in sorted(g.items(), key=lambda kv: tuple(map(str, kv[0]))):
                rate, lo, hi, n = prev(sel)
                csv.append(f"{code},{scope},{k[0]},{k[1]},{k[2]},{k[3]},{n},{S.fmt(rate,4)},{S.fmt(lo,4)},{S.fmt(hi,4)}")
                tables[(code, scope) + k] = (rate, lo, hi, n)
    (C.STUDY / "tables" / "A_prevalence.csv").write_text("\n".join(csv) + "\n")

    md = ["# Analysis A — code prevalence\n",
          f"Consensus labels: a code counts as present only when **both coders agree** ({' and '.join(coders)}). "
          "Cells are the share of traces carrying the code, with a 1,000-draw event-cluster bootstrap 95% CI. "
          "Codes that failed the reliability rule are shown here for completeness but are excluded from every "
          "inferential analysis (see `agreement.md`).\n",
          "## By task, base condition\n",
          "| code | reliable | " + " | ".join(C.TASKS) + " |", "|---|---|" + "---|" * len(C.TASKS)]
    for code in codes:
        if code == "HEDGING": continue
        cells = []
        for t in C.TASKS:
            v = tables.get((code, "by_task", "all", t, "base", "all"))
            cells.append("--" if not v or not np.isfinite(v[0]) else f"{100*v[0]:.1f}%")
        md.append(f"| {code} | {'yes' if code in rel else 'no'} | " + " | ".join(cells) + " |")
    md.append("\n## By model, base condition, all tasks pooled\n")
    models = sorted({r["model"] for r in rows})
    md.append("| code | " + " | ".join(models) + " |"); md.append("|---|" + "---|" * len(models))
    for code in codes:
        if code == "HEDGING": continue
        cells = []
        for m in models:
            sel = [r for r in by[code] if r["model"] == m and r["condition"] == "base"]
            cells.append(f"{100*np.mean([r['label'] for r in sel]):.1f}%" if sel else "--")
        md.append(f"| {code} | " + " | ".join(cells) + " |")
    md.append("\n## Pre- vs post-cutoff, base condition, all tasks pooled\n")
    md.append("| code | pre-cutoff | post-cutoff | difference [95% CI] | p |"); md.append("|---|---|---|---|---|")
    ps, keep = [], []
    for code in codes:
        if code == "HEDGING": continue
        sel = [r for r in by[code] if r["condition"] == "base" and r["partition"] in ("pre", "post")]
        if not sel: continue
        y = np.array([r["label"] for r in sel], float); g = np.array([r["partition"] == "post" for r in sel])
        d = S.diff_ci(y, g, [r["id"] for r in sel], B=1000)
        keep.append((code, d)); ps.append(d["p"])
    adj = S.holm(ps)
    for (code, d), a in zip(keep, adj):
        md.append(f"| {code} | {100*d['m0']:.1f}% (n={d['n0']:,}) | {100*d['m1']:.1f}% (n={d['n1']:,}) | "
                  f"{100*d['diff']:+.1f} pts [{100*d['lo']:+.1f}, {100*d['hi']:+.1f}] | {S.fmtp(a)} |")
    md.append("\nDifferences are post minus pre; p-values are two-sided event-cluster bootstrap, Holm-adjusted across codes.\n")
    md.append("\n## By condition (pinned-500 paired subset only)\n")
    md.append("| code | base | WS+Cutoff | WS |"); md.append("|---|---|---|---|")
    for code in codes:
        if code == "HEDGING": continue
        cells = []
        for cond in ("base", "ws_cutoff", "ws"):
            sel = [r for r in by[code] if r["condition"] == cond]
            cells.append(f"{100*np.mean([r['label'] for r in sel]):.1f}%" if sel else "--")
        md.append(f"| {code} | " + " | ".join(cells) + " |")
    md.append("\nCondition columns are not matched here; analysis F uses the matched triples.\n")
    h = [r for r in by.get("HEDGING", []) if r["label"] is not None]
    if h:
        md.append("\n## HEDGING (mean of the two coders' 0-3 levels)\n")
        md.append("| task | mean level | n |"); md.append("|---|---|---|")
        for t in C.TASKS:
            sel = [r["label"] for r in h if r["task"] == t and r["condition"] == "base"]
            if sel: md.append(f"| {t} | {np.mean(sel):.2f} | {len(sel):,} |")
    (A / "results.md").write_text("\n".join(md) + "\n")
    print("A written")

    # ---------------- B: code -> outcome
    Bd = C.STUDY / "analyses" / "B_code_outcome"
    out_rows = []
    TASKS_B = ["binary_merged"] + C.TASKS
    def rows_for(task, base):
        if task == "binary_merged":
            return [r for r in base if r["task"] in ("binary", "binary_perturbed")]
        return [r for r in base if r["task"] == task]
    for task in TASKS_B:
        ycol, fam, lab = OUTCOME[task]
        for code in codes:
            if code not in rel or code == "HEDGING": continue
            sel = [r for r in rows_for(task, by[code]) if r["condition"] == "base"
                   and r[ycol] is not None and r["label"] is not None]
            if len(sel) < 100: continue
            y = np.array([float(r[ycol]) for r in sel]); x = np.array([r["label"] for r in sel], float)
            if x.sum() < 20 or (1 - x).sum() < 20: continue
            g = S.glmm_effect(y, x, [r["id"] for r in sel], models=[r["model"] for r in sel], family=fam)
            d = S.diff_ci(y, x, [r["id"] for r in sel], B=1000)
            out_rows.append(dict(scope="pooled", model="all", task=task, code=code, family=fam,
                                 outcome=lab, **{k: g[k] for k in ("beta", "se", "lo", "hi", "p", "n")},
                                 raw_diff=d["diff"], raw_lo=d["lo"], raw_hi=d["hi"], n_with=d["n1"], n_without=d["n0"],
                                 mean_with=d["m1"], mean_without=d["m0"]))
        for m in sorted({r["model"] for r in rows}):
            for code in codes:
                if code not in rel or code == "HEDGING": continue
                sel = [r for r in rows_for(task, by[code]) if r["condition"] == "base" and r["model"] == m
                       and r[ycol] is not None and r["label"] is not None]
                if len(sel) < 80: continue
                y = np.array([float(r[ycol]) for r in sel]); x = np.array([r["label"] for r in sel], float)
                if x.sum() < 15 or (1 - x).sum() < 15: continue
                g = S.glmm_effect(y, x, [r["id"] for r in sel], models=None, family=fam)
                d = S.diff_ci(y, x, [r["id"] for r in sel], B=500)
                out_rows.append(dict(scope="per_model", model=m, task=task, code=code, family=fam, outcome=lab,
                                     **{k: g[k] for k in ("beta", "se", "lo", "hi", "p", "n")},
                                     raw_diff=d["diff"], raw_lo=d["lo"], raw_hi=d["hi"], n_with=d["n1"],
                                     n_without=d["n0"], mean_with=d["m1"], mean_without=d["m0"]))
    # Holm within each (scope, model, task) family
    fam_idx = collections.defaultdict(list)
    for i, r in enumerate(out_rows):
        fam_idx[(r["scope"], r["model"], r["task"])].append(i)
    for idxs in fam_idx.values():
        adj = S.holm([out_rows[i]["p"] for i in idxs])
        for i, a in zip(idxs, adj): out_rows[i]["p_holm"] = a
    json.dump(out_rows, open(Bd / "results.json", "w"), indent=1, default=float)
    csv = ["scope,model,task,code,family,n,n_with,n_without,mean_with,mean_without,raw_diff,raw_lo,raw_hi,beta,se,ci_lo,ci_hi,p,p_holm"]
    for r in out_rows:
        csv.append(",".join(str(x) for x in [r["scope"], r["model"], r["task"], r["code"], r["family"], r["n"],
                   r["n_with"], r["n_without"], S.fmt(r["mean_with"],4), S.fmt(r["mean_without"],4),
                   S.fmt(r["raw_diff"],4), S.fmt(r["raw_lo"],4), S.fmt(r["raw_hi"],4), S.fmt(r["beta"],4),
                   S.fmt(r["se"],4), S.fmt(r["lo"],4), S.fmt(r["hi"],4), S.fmt(r["p"],5), S.fmt(r["p_holm"],5)]))
    (C.STUDY / "tables" / "B_code_outcome.csv").write_text("\n".join(csv) + "\n")

    md = ["# Analysis B — does a code predict the outcome?\n",
          "For each task, a random-intercept model of the outcome on the code: binary, perturbed binary and MCQ use "
          "a logistic GLMM with random intercepts for event and model (so item difficulty is absorbed); date and FRQ "
          "use the Gaussian analogue on the graded score. `beta` is the coefficient on the code, in log-odds for the "
          "binomial fits and in score units for the Gaussian ones. The raw difference in means (event-cluster "
          "bootstrap) is shown alongside for interpretation. p-values are Holm-adjusted across codes within each "
          "task. Only codes that passed the reliability rule are modelled.\n",
          "**This is observational.** A code is a property of what the model wrote, not a treatment. These "
          "associations describe which stated justifications accompany success or failure; they do not establish "
          "that reasoning one way causes the outcome.\n",
          "## Pooled across models\n",
          "| task | code | n | with code | without | raw difference [95% CI] | beta [95% CI] | p (Holm) |",
          "|---|---|---|---|---|---|---|---|"]
    for r in out_rows:
        if r["scope"] != "pooled": continue
        star = " **" if (np.isfinite(r["p_holm"]) and r["p_holm"] < 0.05) else " "
        md.append(f"| {r['task']} | {r['code']} | {r['n']:,} | {S.fmt(r['mean_with'])} (n={r['n_with']:,}) | "
                  f"{S.fmt(r['mean_without'])} (n={r['n_without']:,}) | {S.fmt(r['raw_diff'])} "
                  f"[{S.fmt(r['raw_lo'])}, {S.fmt(r['raw_hi'])}] | {S.fmt(r['beta'])} [{S.fmt(r['lo'])}, {S.fmt(r['hi'])}] | "
                  f"{S.fmtp(r['p_holm'])}{star}|")
    sig = [r for r in out_rows if r["scope"] == "pooled" and np.isfinite(r["p_holm"]) and r["p_holm"] < 0.05]
    pos = [r for r in sig if r["beta"] > 0]; neg = [r for r in sig if r["beta"] < 0]
    md.append(f"\n**Codes that predict success** ({len(pos)} pooled task-code pairs at Holm p < 0.05): " +
              (", ".join(f"{r['code']} on {r['task']} (beta {r['beta']:+.2f})" for r in pos) or "none") + ".")
    md.append(f"\n**Codes that predict failure** ({len(neg)}): " +
              (", ".join(f"{r['code']} on {r['task']} (beta {r['beta']:+.2f})" for r in neg) or "none") + ".")
    md.append("\n## Per model\n\nFull per-model table: `tables/B_code_outcome.csv` (rows with scope = per_model). "
              "Cells shown here are the code-task pairs significant after Holm adjustment within that model and task.\n")
    md.append("| model | task | code | with code | without | beta [95% CI] | p (Holm) |"); md.append("|---|---|---|---|---|---|---|")
    for r in out_rows:
        if r["scope"] != "per_model" or not np.isfinite(r["p_holm"]) or r["p_holm"] >= 0.05: continue
        md.append(f"| {r['model']} | {r['task']} | {r['code']} | {S.fmt(r['mean_with'])} | {S.fmt(r['mean_without'])} | "
                  f"{S.fmt(r['beta'])} [{S.fmt(r['lo'])}, {S.fmt(r['hi'])}] | {S.fmtp(r['p_holm'])} |")
    # ---- direction: does the code predict the ANSWER rather than its correctness?
    md.append("\n## Response bias versus discrimination\n")
    md.append("Ground truth is Yes for every original binary item and No for every perturbed one. A code that "
              "simply pushes a model toward \"No\" therefore scores near 0 on one variant and near 1 on the other, "
              "which is what the two single-variant rows above show for several codes. The merged-binary rows pool "
              "both variants of the same event, so that cancels and only genuine discrimination survives. The table "
              "below makes the bias explicit: the effect of each code on the probability of answering Yes, over both "
              "variants pooled.\n")
    md.append("| code | P(answer Yes) with code | without | difference [95% CI] | beta log-odds [95% CI] | p (Holm) |")
    md.append("|---|---|---|---|---|---|")
    dir_rows, dps = [], []
    for code in codes:
        if code not in rel or code == "HEDGING": continue
        sel = [r for r in by[code] if r["task"] in ("binary", "binary_perturbed") and r["condition"] == "base"
               and r["correct"] is not None and r["label"] is not None]
        if len(sel) < 100: continue
        # answered Yes == (original and correct) or (perturbed and wrong)
        yes = np.array([float((r["task"] == "binary") == bool(r["correct"])) for r in sel])
        x = np.array([r["label"] for r in sel], float)
        if x.sum() < 20: continue
        g = S.glmm_effect(yes, x, [r["id"] for r in sel], models=[r["model"] for r in sel], family="binomial")
        d = S.diff_ci(yes, x, [r["id"] for r in sel], B=1000)
        dir_rows.append((code, d, g)); dps.append(g["p"])
    for (code, d, g), a in zip(dir_rows, S.holm(dps)):
        md.append(f"| {code} | {S.fmt(d['m1'])} (n={d['n1']:,}) | {S.fmt(d['m0'])} | {d['diff']:+.3f} "
                  f"[{d['lo']:+.3f}, {d['hi']:+.3f}] | {S.fmt(g['beta'])} [{S.fmt(g['lo'])}, {S.fmt(g['hi'])}] | {S.fmtp(a)} |")
    mrows = [r for r in out_rows if r["scope"] == "pooled" and r["task"] == "binary_merged"]
    msig = [r for r in mrows if np.isfinite(r["p_holm"]) and r["p_holm"] < 0.05]
    md.append(f"\n**On merged binary accuracy, {len(msig)} of {len(mrows)} codes retain a significant association**"
              + (": " + ", ".join(f"{r['code']} (beta {r['beta']:+.2f})" for r in msig) if msig else "") + ".")
    (Bd / "results.md").write_text("\n".join(md) + "\n")
    json.dump(dict(fits=out_rows, direction=[(c, d, g) for c, d, g in dir_rows]), open(Bd / "results.json", "w"), indent=1, default=float)
    print(f"B written: {len(out_rows)} fits, {len(sig)} pooled significant, {len(msig)} on merged binary")


if __name__ == "__main__":
    main()
